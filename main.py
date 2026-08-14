import os
import time
import requests
import pytz
from datetime import datetime, timedelta
from supabase import create_client, Client
from security import decrypt_token

# ==========================================
# ENVIRONMENT VARIABLES & CONFIGURATION
# ==========================================
SPACEBASIC_PUBLISHABLE_KEY = "sb_publishable_vw0I2KilIjFmtr1mm3Wl0A_sbbtaF1_"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⛔ CRITICAL SECURITY ERROR: SUPABASE_URL or SUPABASE_KEY is missing from environment variables!")
    exit(1)

SPACEBASIC_BOOKING_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"
SPACEBASIC_MENU_URL = "https://api.spacebasic.com/api/v3/messmanager/mealsmenu"

# ==========================================
# SUPABASE UTILITIES
# ==========================================
def get_supabase_client() -> Client:
    """Creates a fresh Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_active_users(max_retries=3, delay=5):
    """Fetches user records securely without logging raw table contents."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Connecting to Supabase securely (Attempt {attempt}/{max_retries})...")
            supabase = get_supabase_client()
            response = supabase.table("users").select("*").execute()
            if response.data:
                print(f"✅ Securely retrieved {len(response.data)} user record(s).")
                return response.data
            else:
                print("⚠️ Database connection established, but 0 user records were found.")
                return []
        except Exception as e:
            print(f"❌ Attempt {attempt} failed connecting to database: {e}")
            if attempt < max_retries:
                time.sleep(delay)
    return []

# ==========================================
# HELPER & SKIP FILTER FUNCTIONS
# ==========================================
def should_skip_tomorrow(skip_days):
    """
    Checks if TOMORROW (the target booking date) in IST is set for a full day skip.
    """
    if not isinstance(skip_days, dict):
        return False
        
    ist = pytz.timezone("Asia/Kolkata")
    tomorrow_name = (datetime.now(ist) + timedelta(days=1)).strftime("%A").lower()
    
    day_skips = skip_days.get(tomorrow_name, [])
    
    if day_skips is True:
        return True
        
    if isinstance(day_skips, list):
        skips_lower = [str(item).lower() for item in day_skips]
        if "breakfast" in skips_lower and "lunch" in skips_lower and "dinner" in skips_lower:
            return True
            
    return False

def is_meal_skipped_tomorrow(skip_days, meal_type):
    """Checks if a specific meal type (breakfast/lunch/dinner) is set to skip for tomorrow."""
    if not isinstance(skip_days, dict):
        return False
        
    ist = pytz.timezone("Asia/Kolkata")
    tomorrow_name = (datetime.now(ist) + timedelta(days=1)).strftime("%A").lower()
    
    day_skips = skip_days.get(tomorrow_name, [])
    
    if day_skips is True:
        return True
        
    if isinstance(day_skips, list):
        skips_lower = [str(item).lower() for item in day_skips]
        if meal_type.lower() in skips_lower:
            return True
            
    return False

def extract_all_meals_from_data(data):
    """Parses SpaceBasic menu response array and extracts all bookable meal items."""
    meals_to_book = []
    if isinstance(data, dict):
        result = data.get("result", {})
        meals = result.get("meals", []) if isinstance(result, dict) else []
        for meal in meals:
            if str(meal.get("allowBooking")) == "1":
                meal_id = meal.get("mealId")
                meal_name = meal.get("mealName", "Unknown Meal")
                if meal_id:
                    meals_to_book.append({"id": meal_id, "name": meal_name})
    return meals_to_book

def filter_by_preference(meal_list, preference):
    """Filters a list of meal options based on dietary preference chain."""
    pref = str(preference).lower()
    if "non" in pref:
        for meal in meal_list:
            if "non" in meal["name"].lower(): return meal
        for meal in meal_list:
            if "egg" in meal["name"].lower(): return meal
        for meal in meal_list:
            if "veg" in meal["name"].lower(): return meal
    elif "egg" in pref:
        for meal in meal_list:
            if "egg" in meal["name"].lower(): return meal
        for meal in meal_list:
            if "veg" in meal["name"].lower(): return meal
    else:
        for meal in meal_list:
            if "veg" in meal["name"].lower() and "non" not in meal["name"].lower(): return meal
    return meal_list[0] if meal_list else None

def select_preferred_meals(meals, lunch_pref, dinner_pref, skip_days):
    """Selects preferred meals while omitting any explicitly skipped meal types for tomorrow."""
    categorized = {"breakfast": [], "lunch": [], "dinner": []}
    for meal in meals:
        name = meal["name"].lower()
        if "breakfast" in name:
            categorized["breakfast"].append(meal)
        elif "lunch" in name:
            categorized["lunch"].append(meal)
        elif "dinner" in name:
            categorized["dinner"].append(meal)
            
    selected_meals = []

    # 1. Breakfast check
    if categorized["breakfast"]:
        if is_meal_skipped_tomorrow(skip_days, "breakfast"):
            print("  └─ ⏭️ Skipping Breakfast based on user schedule for tomorrow.")
        else:
            selected_meals.append(categorized["breakfast"][0])

    # 2. Lunch check
    if categorized["lunch"]:
        if is_meal_skipped_tomorrow(skip_days, "lunch"):
            print("  └─ ⏭️ Skipping Lunch based on user schedule for tomorrow.")
        else:
            sel = filter_by_preference(categorized["lunch"], lunch_pref)
            if sel: selected_meals.append(sel)

    # 3. Dinner check
    if categorized["dinner"]:
        if is_meal_skipped_tomorrow(skip_days, "dinner"):
            print("  └─ ⏭️ Skipping Dinner based on user schedule for tomorrow.")
        else:
            sel = filter_by_preference(categorized["dinner"], dinner_pref)
            if sel: selected_meals.append(sel)

    return selected_meals

# ==========================================
# BOOKING PROCESSING LOGIC
# ==========================================
def process_user_booking(user, max_retries=3, delay=3):
    name = user.get("name", "Unknown")
    user_id = str(user.get("user_id") or user.get("userid") or "")
    tenant_id = str(user.get("tenant_id") or "143")
    raw_encrypted_token = str(user.get("token") or user.get("auth_token") or "")
    skip_days = user.get("skip_days", {})
    lunch_pref = user.get("lunch_preference", "Non Veg")
    dinner_pref = user.get("dinner_preference", "Non Veg")

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id or 'Missing'})")
    print(f"==========================================")

    # Decrypt token in memory
    raw_token = decrypt_token(raw_encrypted_token)

    if not user_id or user_id == "None" or not raw_token or len(raw_token) < 10:
        print(f"⚠️ Skipping {name}: Invalid credentials or decryption failed.")
        return False

    if should_skip_tomorrow(skip_days):
        print(f"⏭️ Skipping all bookings for {name} tomorrow based on 'skip_days' configuration.")
        return True

    token_header = raw_token if raw_token.startswith("Bearer ") else f"Bearer {raw_token}"
    headers = {
        "Authorization": token_header,
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
        if response.status_code == 200:
            all_meals = extract_all_meals_from_data(response.json())
            if not all_meals:
                print(f"⚠️ No bookable meals found for {name} on {tomorrow_date}.")
                return False

            # Filter meals based on preferences and tomorrow's skip schedule
            target_meals = select_preferred_meals(all_meals, lunch_pref, dinner_pref, skip_days)
            
            if not target_meals:
                print(f"⏭️ All available meals for {name} on {tomorrow_date} are marked as skipped.")
                return True

            print(f"💡 Selected {len(target_meals)} meal(s) for tomorrow.")

            all_success = True
            for meal in target_meals:
                meal_id = meal["id"]
                meal_name = meal["name"]
                
                payload = {
                    "mealId": int(meal_id),
                    "userId": user_id,
                    "status": "1",
                    "createdBy": user_id,
                    "isSpecial": 0
                }

                print(f"🚀 Booking '{meal_name}' (Meal ID: {meal_id}) for {name}...")
                res = requests.post(SPACEBASIC_BOOKING_URL, json=payload, headers=headers, timeout=15)
                
                if res.status_code in [200, 201]:
                    res_json = res.json() if res.text else {}
                    if res_json.get("status") == "Failed" or res_json.get("statusCode") == "F":
                        print(f"  └─ ❌ Internal API Rejection: {res_json.get('message') or res.text}")
                        all_success = False
                    else:
                        print(f"  └─ 🎉 {meal_name} RSVP confirmed!")
                else:
                    print(f"  └─ ⚠️ Failed to book {meal_name}: HTTP {res.status_code}")
                    all_success = False

            return all_success
        else:
            print(f"⚠️ Failed to fetch menu: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing booking for {name}: {e}")

    return False

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    print("=" * 50)
    print("🤖 STARTING AUTOMATED MESS BOOKING PROCESS")
    print("=" * 50)

    users = get_active_users()
    if not users:
        print("🛑 Execution stopped: No active users retrieved from Supabase.")
        return

    print(f"📋 Found {len(users)} user(s) in Supabase to process.")
    
    success_count = 0
    failure_count = 0

    for user in users:
        is_success = process_user_booking(user)
        if is_success:
            success_count += 1
        else:
            failure_count += 1

    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {success_count} Succeeded | {failure_count} Failed/Skipped")
    print("=" * 50)

if __name__ == "__main__":
    main()
