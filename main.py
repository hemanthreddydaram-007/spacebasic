import os
import time
import requests
import pytz
from datetime import datetime, timedelta
from supabase import create_client, Client

# ==========================================
# ENVIRONMENT VARIABLES & CONFIGURATION
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY environment variable is missing!")
    exit(1)

# SpaceBasic Endpoints
SPACEBASIC_BOOKING_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"
SPACEBASIC_MENU_URL = "https://api.spacebasic.com/api/v3/messmanager/mealsmenu"
SPACEBASIC_PUBLISHABLE_KEY = "sb_publishable_vw0I2KilIjFmtr1mm3Wl0A_sbbtaF1_"

# ==========================================
# SUPABASE UTILITIES
# ==========================================
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_active_users(max_retries=3, delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Connecting to Supabase (Attempt {attempt}/{max_retries})...")
            supabase = get_supabase_client()
            response = supabase.table("users").select("*").execute()
            
            if response.data:
                print(f"✅ Successfully retrieved {len(response.data)} user record(s).")
                return response.data
            else:
                print("⚠️ Query succeeded, but no user records were found in database.")
                return []
                
        except Exception as e:
            print(f"❌ Attempt {attempt} failed fetching users: {e}")
            if attempt < max_retries:
                time.sleep(delay)

    print("❌ Critical Error: Could not connect to Supabase after retries.")
    return []

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def should_skip_today(skip_days):
    if not isinstance(skip_days, dict):
        return False
        
    ist = pytz.timezone("Asia/Kolkata")
    today_name = datetime.now(ist).strftime("%A").lower()
    
    day_skips = skip_days.get(today_name, [])
    if isinstance(day_skips, list) and len(day_skips) > 0:
        return True
    return False

def fetch_live_meal_id(user_id, tenant_id, headers):
    """Dynamically queries SpaceBasic's mealsmenu endpoint for tomorrow's date."""
    ist = pytz.timezone("Asia/Kolkata")
    tomorrow_date = (datetime.now(ist) + timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = f"{SPACEBASIC_MENU_URL}?userId={user_id}&tenantId={tenant_id}&mealDate={tomorrow_date}"
    
    try:
        print(f"🔍 Fetching menu for User {user_id} on {tomorrow_date}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract mealId from SpaceBasic menu response array or dictionary
            meals_list = data if isinstance(data, list) else data.get("data") or data.get("meals") or []
            
            if meals_list and len(meals_list) > 0:
                # Retrieve the active mealId (or first available meal slot)
                meal_id = meals_list[0].get("mealId") or meals_list[0].get("id")
                if meal_id:
                    print(f"💡 Successfully retrieved active mealId: {meal_id}")
                    return meal_id
            print(f"⚠️ Response received, but no active meal items found for date {tomorrow_date}.")
        else:
            print(f"⚠️ Failed to fetch menu: HTTP {response.status_code} - {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ Error fetching live meal ID for User {user_id}: {e}")
        
    return None

# ==========================================
# BOOKING PROCESSING LOGIC
# ==========================================
def process_user_booking(user, max_retries=3, delay=3):
    name = user.get("name", "Unknown")
    user_id = str(user.get("user_id") or user.get("userid") or "")
    tenant_id = str(user.get("tenant_id") or "143")
    raw_token = str(user.get("token") or user.get("auth_token") or "")
    skip_days = user.get("skip_days", {})

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id or 'Missing'})")
    print(f"==========================================")

    if not user_id or user_id == "None":
        print(f"⚠️ Skipping {name}: Invalid or missing User-ID.")
        return False
    if not raw_token or len(raw_token) < 10:
        print(f"⚠️ Skipping {name}: Invalid or missing Token.")
        return False

    if should_skip_today(skip_days):
        print(f"⏭️ Skipping booking for {name} today based on 'skip_days' configuration.")
        return True

    token_header = raw_token if raw_token.startswith("Bearer ") else f"Bearer {raw_token}"

    headers = {
        "Authorization": token_header,
        "User-ID": user_id,
        "x-publishable-key": SPACEBASIC_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Automatically fetch live mealId from SpaceBasic
    meal_id = fetch_live_meal_id(user_id, tenant_id, headers)

    if not meal_id:
        print(f"❌ Error: Could not retrieve a valid live mealId for {name}. Skipping...")
        return False

    print(f"📌 Targeted Live Meal ID: {meal_id}")

    payload = {
        "mealId": int(meal_id),
        "userId": user_id,
        "status": "1",
        "createdBy": user_id,
        "isSpecial": 0
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🚀 Sending RSVP request for {name} (Attempt {attempt}/{max_retries})...")
            response = requests.post(
                SPACEBASIC_BOOKING_URL,
                json=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code in [200, 201]:
                res_json = response.json() if response.text else {}
                if res_json.get("Status") == "FAILED" or "error" in str(res_json).lower():
                    print(f"⚠️ API Response Failure: {response.text}")
                    return False
                else:
                    print(f"🎉 SUCCESS: Mess RSVP confirmed for {name}!")
                    return True
            elif response.status_code in [401, 403]:
                print(f"⛔ AUTH ERROR ({response.status_code}): Token expired for {name}.")
                return False
            else:
                print(f"⚠️ API Response ({response.status_code}): {response.text}")

        except requests.exceptions.RequestException as req_err:
            print(f"❌ Network error on attempt {attempt}: {req_err}")

        if attempt < max_retries:
            time.sleep(delay)

    print(f"❌ Failed to process booking for {name} after {max_retries} attempts.")
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
