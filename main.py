import os
import time
import requests
import pytz
from datetime import datetime, timedelta
from supabase import create_client, Client

# ==========================================
# ENVIRONMENT VARIABLES & CONFIGURATION
# ==========================================
SPACEBASIC_PUBLISHABLE_KEY = "sb_publishable_vw0I2KilIjFmtr1mm3Wl0A_sbbtaF1_"

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ywljhdtygqzgvzrnognn.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("❌ Error: SUPABASE_KEY environment variable is missing!")
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
    """
    Checks if current day in IST is set to skip.
    Supports both boolean format {'monday': True} and list format {'monday': ['Breakfast', 'Lunch', 'Dinner']}.
    Only skips the entire runner process if ALL three main meals are explicitly marked for skipping today.
    """
    if not isinstance(skip_days, dict):
        return False
        
    ist = pytz.timezone("Asia/Kolkata")
    today_name = datetime.now(ist).strftime("%A").lower()
    
    day_skips = skip_days.get(today_name, [])
    
    if day_skips is True:
        return True
        
    if isinstance(day_skips, list):
        skips_lower = [str(item).lower() for item in day_skips]
        if "breakfast" in skips_lower and "lunch" in skips_lower and "dinner" in skips_lower:
            return True
            
    return False

def extract_all_meals_from_data(data):
    """Parses SpaceBasic menu response array and extracts all bookable meal items."""
    meals_to_book = []
    
    if isinstance(data, dict):
        result = data.get("result", {})
        meals = result.get("meals", []) if isinstance(result, dict) else []
        
        for meal in meals:
            # Pick meals where booking is enabled
            if str(meal.get("allowBooking")) == "1":
                meal_id = meal.get("mealId")
                meal_name = meal.get("mealName", "Unknown Meal")
                if meal_id:
                    meals_to_book.append({"id": meal_id, "name": meal_name})
                    
    return meals_to_book

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

    if not user_id or user_id == "None" or not raw_token or len(raw_token) < 10:
        print(f"⚠️ Skipping {name}: Invalid credentials.")
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

    ist = pytz.timezone("Asia/Kolkata")
    tomorrow_date = (datetime.now(ist) + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"{SPACEBASIC_MENU_URL}?userId={user_id}&tenantId={tenant_id}&mealDate={tomorrow_date}"

    try:
        print(f"🔍 Fetching menu for User {user_id} on {tomorrow_date}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            meals = extract_all_meals_from_data(response.json())
            if not meals:
                print(f"⚠️ No bookable meals found for {name} on {tomorrow_date}.")
                return False

            print(f"💡 Found {len(meals)} bookable meal slot(s) for tomorrow.")
            
            all_success = True
            for meal in meals:
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
