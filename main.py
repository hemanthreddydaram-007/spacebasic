import os
import requests
from supabase import create_client, Client

# Fetch Supabase environment variables from GitHub Secrets
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY environment variable is missing!")
    exit(1)

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_active_users():
    try:
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error fetching users from Supabase: {e}")
        return []

def process_user_booking(user):
    name = user.get("name", "Unknown")
    user_id = user.get("user_id")
    token = user.get("token")
    skip_days = user.get("skip_days", {})

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id})")
    print(f"==========================================")

    if not token:
        print(f"⚠️ Token missing for user {name}. Skipping...")
        return

    # --- Add your SpaceBasic API booking/cancellation request logic here using 'token' and 'user_id' ---
    print(f"✅ Successfully retrieved preferences & token for {name}.")

def main():
    users = get_active_users()
    
    if not users:
        print("⚠️ No users found in Supabase database!")
        return

    print(f"📋 Found {len(users)} user(s) in Supabase to process.")
    for user in users:
        process_user_booking(user)

if __name__ == "__main__":
    main()
