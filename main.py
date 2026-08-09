import os
import time
import requests
from supabase import create_client, Client

# ==========================================
# SUPABASE CONFIGURATION
# ==========================================
SUPABASE_URL = os.environ.get(
    "SUPABASE_URL", 
    "https://ywljhdtygqzgvzrnognn.supabase.co"
)
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY", 
    "sb_publishable_vw0I2KilIjFmtr1mm3Wl0A_sbbtaF1_"
)

SPACEBASIC_BOOKING_URL = "https://api.spacebasic.com/v1/mess/book"  # Update if your API endpoint path differs

# ==========================================
# SUPABASE UTILITIES
# ==========================================
def get_supabase_client() -> Client:
    """Creates a fresh Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_users_with_retry(max_retries=3, delay=5):
    """
    Fetches all active users from Supabase with connection retry logic
    to prevent 'Server disconnected' errors.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Attempting to connect to Supabase (Attempt {attempt}/{max_retries})...")
            supabase = get_supabase_client()
            
            # Fetch users from the 'users' table
            response = supabase.table("users").select("*").execute()
            
            if response.data:
                print(f"✅ Successfully retrieved {len(response.data)} user(s) from database.")
                return response.data
            else:
                print("⚠️ No users found in Supabase database!")
                return []
                
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"⏳ Waiting {delay} seconds before retrying...")
                time.sleep(delay)

    print("❌ Critical: Failed to establish stable connection with Supabase after retries.")
    return []

# ==========================================
# SPACEBASIC BOOKING LOGIC
# ==========================================
def book_mess_for_user(user, max_retries=3, delay=3):
    """
    Executes the SpaceBasic API booking request for a given user.
    """
    user_id = user.get("user_id")
    auth_token = user.get("auth_token")

    if not user_id or not auth_token:
        print(f"⚠️ Skipping user record ID {user.get('id', 'Unknown')}: Missing User-ID or Auth Token.")
        return False

    headers = {
        "Authorization": f"Bearer {auth_token}" if not auth_token.startswith("Bearer ") else auth_token,
        "User-ID": str(user_id),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    payload = {
        # Adjust payload keys based on your SpaceBasic API requirements
        "status": "booked"
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🚀 Booking mess for User ID {user_id} (Attempt {attempt}/{max_retries})...")
            response = requests.post(
                SPACEBASIC_BOOKING_URL, 
                json=payload, 
                headers=headers, 
                timeout=15
            )

            if response.status_code in [200, 201]:
                print(f"🎉 SUCCESS: Mess booked for User ID {user_id}!")
                return True
            elif response.status_code in [401, 403]:
                print(f"⛔ AUTH ERROR ({response.status_code}): Token expired or invalid for User ID {user_id}.")
                return False
            else:
                print(f"⚠️ API returned status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Network error on attempt {attempt}: {req_err}")

        if attempt < max_retries:
            time.sleep(delay)

    print(f"❌ Failed to book mess for User ID {user_id} after {max_retries} attempts.")
    return False

# ==========================================
# MAIN EXECUTION ENTRY POINT
# ==========================================
def main():
    print("=" * 50)
    print("🤖 STARTING AUTOMATED MESS BOOKING PROCESS")
    print("=" * 50)

    users = fetch_users_with_retry()

    if not users:
        print("🛑 Execution stopped: No users to process.")
        return

    success_count = 0
    failure_count = 0

    for user in users:
        success = book_mess_for_user(user)
        if success:
            success_count += 1
        else:
            failure_count += 1

    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {success_count} Succeeded | {failure_count} Failed")
    print("=" * 50)

if __name__ == "__main__":
    main()
