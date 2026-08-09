import os
import time
import requests
import pytz
from datetime import datetime
from supabase import create_client, Client

# ==========================================
# ENVIRONMENT VARIABLES & CONFIGURATION
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY environment variable is missing!")
    exit(1)

# SpaceBasic v3 Endpoints
SPACEBASIC_BOOKING_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"
# Replace with the exact GET endpoint URL from DevTools Network tab
SPACEBASIC_GET_MEALS_URL = "https://api.spacebasic.com/api/v3/messmanager/getupcomingmeals"

SPACEBASIC_PUBLISHABLE_KEY = "sb_publishable_vw0I2KilIjFmtr1mm3Wl0A_sbbtaF1_"

# Fallback meal ID when auto-fetching is unavailable
DEFAULT_MEAL_ID = 307872 

# ==========================================
# SUPABASE UTILITIES
# ==========================================
def get_supabase_client() -> Client:
    """Creates a fresh Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_active_users(max_retries=3, delay=5):
    """Fetches user records from Supabase with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Connecting to Supabase (Attempt {attempt}/{max_retries})...")
            supabase = get_supabase_client()
            response = supabase.table("users").select("*").execute()
            
            if response.data:
                print(f"✅ Successfully retrieved {len(response.data)} user record(s).")
                return response.data
            else:
                print("⚠️ Query succeeded, but no user records were found in the database.")
                return []
                
        except Exception as e:
            print(f"❌ Attempt {attempt} failed fetching users: {e}")
            if attempt < max_retries:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)

    print("❌ Critical Error: Could not connect to Supabase after retries.")
    return []

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def should_skip_today(skip_days):
    """Checks if current day in IST is set to True inside skip_days dict."""
    if not isinstance(skip_days, dict):
        return False
        
    ist = pytz.timezone("Asia/Kolkata")
    today_name = datetime.now(ist).strftime("%A").lower()
    return skip_days.get(today_name, False)

def fetch_dynamic_meal_id(user_id, token, headers):
    """Fetches the exact active mealId for a specific user from SpaceBasic."""
    try:
        response = requests.get(SPACEBASIC_GET_MEALS_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("mealId") or data[0].get("id")
            elif isinstance(data, dict):
                meals = data.get("data") or data.get("meals") or []
                if meals:
                    return meals[0].get("mealId") or meals[0].get("id")
    except Exception as e:
        print(f"⚠️ Could not auto-fetch dynamic meal ID for {user_id}: {e}")
    return None

# ==========================================
# BOOKING PROCESSING LOGIC
# ==========================================
def process_user_booking(user, max_retries=3, delay=3):
    name = user.get("name", "Unknown")
    
    user_id = str(user.get("user_id") or user.get("userid"))
    token = user.get("token") or user.get("auth_token")
    skip_days = user.get("skip_days", {})

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id or 'Missing'})")
    print(f"==========================================")

    if not user_id or user_id == "None":
        print(f"⚠️ Skipping {name}: User-ID field is missing or null.")
        return False
    elif not token:
        print(f"⚠️ Skipping {name}: Token field is missing or null.")
        return False

    if should_skip_today(skip_days):
        print(f"⏭️ Skipping booking for {name} today based on 'skip_days' preference.")
        return True

    headers = {
        "Authorization": f"Bearer {token}" if not str(token).startswith("Bearer ") else str(token),
        "User-ID": user_id,
        "x-publishable-key": SPACEBASIC_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Resolution order: Supabase 'meal_id' column -> Live API fetch -> DEFAULT_MEAL_ID
    meal_id = user.get("meal_id") or fetch_dynamic_meal_id(user_id, token, headers) or DEFAULT_MEAL_ID

    if not meal_id:
        print(f"❌ Error: Could not determine valid mealId for {name}. Skipping...")
        return False

    print(f"📌 Targeted Meal ID: {meal_id}")

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
                    print(f"⚠️ API Warning ({response.status_code}): {response.text}")
                else:
                    print(f"🎉 SUCCESS: Mess RSVP confirmed for {name}!")
                    return True
            elif response.status_code in [401, 403]:
                print(f"⛔ AUTH ERROR ({response.status_code}): Token expired/invalid for {name}.")
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
