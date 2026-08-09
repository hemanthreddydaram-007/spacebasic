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

# Updated SpaceBasic v3 Endpoint
SPACEBASIC_BOOKING_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

# ==========================================
# SUPABASE UTILITIES
# ==========================================
def get_supabase_client() -> Client:
    """Creates a fresh Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_active_users(max_retries=3, delay=5):
    """
    Fetches user records from Supabase with retry logic 
    to handle connection drops or cold starts.
    """
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
    """
    Checks if current day in IST is set to True inside the user's skip_days dict.
    Example skip_days format in DB: {"monday": false, "tuesday": true, ...}
    """
    if not isinstance(skip_days, dict):
        return False
        
    ist = pytz.timezone("Asia/Kolkata")
    today_name = datetime.now(ist).strftime("%A").lower()  # e.g., 'sunday', 'monday'
    
    return skip_days.get(today_name, False)

# ==========================================
# BOOKING PROCESSING LOGIC
# ==========================================
def process_user_booking(user, max_retries=3, delay=3):
    name = user.get("name", "Unknown")
    
    # Flexible column resolution matching your Supabase fields
    user_id = user.get("user_id") or user.get("userid")
    token = user.get("token") or user.get("auth_token")
    skip_days = user.get("skip_days", {})

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id or 'Missing'})")
    print(f"==========================================")

    # Credential validations
    if not user_id and not token:
        print(f"⚠️ Skipping {name}: Missing both User-ID and Token in database.")
        return False
    elif not user_id:
        print(f"⚠️ Skipping {name}: User-ID field is missing or null.")
        return False
    elif not token:
        print(f"⚠️ Skipping {name}: Token field is missing or null.")
        return False

    # Check day skipping preference
    if should_skip_today(skip_days):
        print(f"⏭️ Skipping booking for {name} today based on 'skip_days' preference.")
        return True

    # Build Headers
    headers = {
        "Authorization": f"Bearer {token}" if not str(token).startswith("Bearer ") else str(token),
        "User-ID": str(user_id),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Current date in IST (YYYY-MM-DD)
    ist = pytz.timezone("Asia/Kolkata")
    today_date = datetime.now(ist).strftime("%Y-%m-%d")

    # SpaceBasic v3 Payload
    payload = {
        "date": today_date,
        "status": 1
    }

    # Execute SpaceBasic API Request with Retries
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
                print(f"🎉 SUCCESS: Mess booked for {name}!")
                return True
            elif response.status_code in [401, 403]:
                print(f"⛔ AUTH ERROR ({response.status_code}): Token expired or invalid for {name}.")
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
