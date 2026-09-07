import os
import time
import requests
import pytz
from datetime import datetime, timedelta
from supabase import create_client, Client
from security import decrypt_value

SPACEBASIC_AUTH_URL = "https://api.spacebasic.com/authenticate/email"
SPACEBASIC_BOOKING_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"
SPACEBASIC_MENU_URL = "https://api.spacebasic.com/api/v3/messmanager/mealsmenu"
SPACEBASIC_PUBLISHABLE_KEY = "sb_publishable_vw0I2KilIjFmtr1mm3Wl0A_sbbtaF1_"

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ywljhdtygqzgvzrnognn.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("❌ Error: SUPABASE_KEY environment variable is missing!")
    exit(1)

# ==========================================
# TIME SYNC & SLEEP BUFFER FUNCTION
# ==========================================
def wait_until_exact_time(target_hour=18, target_minute=0, target_second=0):
    """
    Holds execution until precisely target_hour:target_minute:target_second IST.
    Defaults to 18:00:00 (6:00:00 PM IST).
    Skips waiting if started manually or if target time has already elapsed.
    """
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    target = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
    
    seconds_to_wait = (target - now).total_seconds()

    # Wait only if runner starts within a 20-minute window ahead of target time
    if 0 < seconds_to_wait <= 1200:
        print(f"🕒 Current time: {now.strftime('%H:%M:%S')} IST")
        print(f"🎯 Target booking time: {target_hour:02d}:{target_minute:02d}:{target_second:02d} IST")
        print(f"⏳ Holding execution for {int(seconds_to_wait)} seconds...")
        time.sleep(seconds_to_wait)
        print(f"⚡ Reached {datetime.now(ist).strftime('%H:%M:%S')} IST! Firing booking requests now.\n")
    else:
        print(f"⚡ Running immediately at {now.strftime('%H:%M:%S')} IST without delay.\n")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_active_users():
    try:
        supabase = get_supabase_client()
        res = supabase.table("users").select("*").execute()
        return res.data or []
    except Exception as e:
        print(f"❌ Failed to fetch users: {e}")
        return []

def login_spacebasic(email, raw_password):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {
        "username": email,
        "password": raw_password
    }
    try:
        res = requests.post(SPACEBASIC_AUTH_URL, json=payload, headers=headers, timeout=12)
        if res.status_code in [200, 201]:
            data = res.json()
            token = data.get("accessToken") or data.get("jwt")
            user_id = str(data.get("studentRoomSelectionId") or "")
            
            # Extract directly from JWT token payload if missing
            if token and (not user_id or user_id == "0"):
                import base64, json
                try:
                    payload_b64 = token.split(".")[1]
                    payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
                    jwt_data = json.loads(base64.b64decode(payload_b64).decode())
                    user_id = str(jwt_data.get("uid"))
                except Exception:
                    pass

            return token, user_id
        else:
            print(f"  └─ ❌ Login failed for {email}: HTTP {res.status_code} - {res.text}")
    except Exception as e:
        print(f"  └─ ❌ Login request error for {email}: {e}")
    return None, None

def should_skip_tomorrow(skip_days):
    if not isinstance(skip_days, dict): return False
    ist = pytz.timezone("Asia/Kolkata")
    tomorrow = (datetime.now(ist) + timedelta(days=1)).strftime("%A").lower()
    day_skips = skip_days.get(tomorrow, [])
    if day_skips is True: return True
    if isinstance(day_skips, list):
        s = [str(x).lower() for x in day_skips]
        return "breakfast" in s and "lunch" in s and "dinner" in s
    return False

def is_meal_skipped_tomorrow(skip_days, meal_type):
    if not isinstance(skip_days, dict): return False
    ist = pytz.timezone("Asia/Kolkata")
    tomorrow = (datetime.now(ist) + timedelta(days=1)).strftime("%A").lower()
    day_skips = skip_days.get(tomorrow, [])
    if day_skips is True: return True
    if isinstance(day_skips, list):
        return meal_type.lower() in [str(x).lower() for x in day_skips]
    return False

def extract_all_meals(data):
    meals_to_book = []
    if isinstance(data, dict):
        result = data.get("result", {})
        meals = result.get("meals", []) if isinstance(result, dict) else []
        for m in meals:
            if str(m.get("allowBooking")) == "1":
                meals_to_book.append({"id": m.get("mealId"), "name": m.get("mealName", "Unknown")})
    return meals_to_book

def filter_by_preference(meal_list, preference):
    pref = str(preference).lower()
    if "non" in pref:
        for m in meal_list:
            if "non" in m["name"].lower(): return m
        for m in meal_list:
            if "egg" in m["name"].lower(): return m
        for m in meal_list:
            if "veg" in m["name"].lower(): return m
    elif "egg" in pref:
        for m in meal_list:
            if "egg" in m["name"].lower(): return m
        for m in meal_list:
            if "veg" in m["name"].lower(): return m
    else:
        for m in meal_list:
            if "veg" in m["name"].lower() and "non" not in m["name"].lower(): return m
    return meal_list[0] if meal_list else None

def select_preferred_meals(meals, lunch_pref, dinner_pref, skip_days):
    categorized = {"breakfast": [], "lunch": [], "dinner": []}
    for m in meals:
        n = m["name"].lower()
        if "breakfast" in n: categorized["breakfast"].append(m)
        elif "lunch" in n: categorized["lunch"].append(m)
        elif "dinner" in n: categorized["dinner"].append(m)

    selected = []
    if categorized["breakfast"]:
        if not is_meal_skipped_tomorrow(skip_days, "breakfast"):
            selected.append(categorized["breakfast"][0])
    if categorized["lunch"]:
        if not is_meal_skipped_tomorrow(skip_days, "lunch"):
            m = filter_by_preference(categorized["lunch"], lunch_pref)
            if m: selected.append(m)
    if categorized["dinner"]:
        if not is_meal_skipped_tomorrow(skip_days, "dinner"):
            m = filter_by_preference(categorized["dinner"], dinner_pref)
            if m: selected.append(m)
    return selected

def process_user(user):
    name = user.get("name", "Unknown")
    email = user.get("email")
    encrypted_pw = user.get("password")
    tenant_id = str(user.get("tenant_id") or "143")
    is_active = user.get("is_active", True)
    skip_days = user.get("skip_days", {})
    lunch_pref = user.get("lunch_preference", "Non Veg")
    dinner_pref = user.get("dinner_preference", "Non Veg")

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} ({email})")
    print(f"==========================================")

    # 1. Check if user paused auto-booking
    if not is_active:
        print(f"⏸️ Auto-booking is PAUSED by user. Skipping all operations for {name}.")
        return True

    if not email or not encrypted_pw:
        print(f"⚠️ Missing email or password for {name}.")
        return False

    if should_skip_tomorrow(skip_days):
        print(f"⏭️ Skipping all bookings for {name} tomorrow based on skip schedule.")
        return True

    # 2. Decrypt password and perform automatic login
    raw_password = decrypt_value(encrypted_pw)
    print("🔑 Authenticating with SpaceBasic API...")
    token, user_id = login_spacebasic(email, raw_password)

    if not token or not user_id:
        print(f"❌ Could not obtain session token for {name}.")
        return False

    print(f"✅ Logged in successfully! SpaceBasic User ID: {user_id}")

    # 3. Query tomorrow's menu
    headers = {
        "Authorization": f"Bearer {token}",
        "User-ID": user_id,
        "x-publishable-key": SPACEBASIC_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    ist = pytz.timezone("Asia/Kolkata")
    tomorrow_date = (datetime.now(ist) + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"{SPACEBASIC_MENU_URL}?userId={user_id}&tenantId={tenant_id}&mealDate={tomorrow_date}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch menu: HTTP {response.status_code}")
            return False

        all_meals = extract_all_meals(response.json())
        target_meals = select_preferred_meals(all_meals, lunch_pref, dinner_pref, skip_days)

        if not target_meals:
            print("⏭️ No meals to book for tomorrow (skipped or none available).")
            return True

        print(f"💡 Selected {len(target_meals)} meal(s) for tomorrow.")

        success = True
        for meal in target_meals:
            payload = {
                "mealId": int(meal["id"]),
                "userId": user_id,
                "status": "1",
                "createdBy": user_id,
                "isSpecial": 0
            }
            res = requests.post(SPACEBASIC_BOOKING_URL, json=payload, headers=headers, timeout=15)
            if res.status_code in [200, 201]:
                print(f"  └─ 🎉 {meal['name']} confirmed!")
            else:
                print(f"  └─ ⚠️ Failed to book {meal['name']}: HTTP {res.status_code}")
                success = False

        return success
    except Exception as e:
        print(f"❌ Error during booking for {name}: {e}")
        return False

def main():
    # Sync and wait until exactly 6:00:00 PM (18:00:00) IST
    wait_until_exact_time(18, 0, 0)

    print("=" * 50)
    print("🤖 STARTING AUTOMATED MESS BOOKING PROCESS")
    print("=" * 50)

    users = get_active_users()
    if not users:
        print("🛑 No users found in database.")
        return

    success_count = sum(1 for u in users if process_user(u))
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {success_count}/{len(users)} User(s) Processed Successfully")
    print("=" * 50)

if __name__ == "__main__":
    main()
