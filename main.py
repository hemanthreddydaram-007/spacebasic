import os
import json
import requests
from datetime import datetime, timedelta

# 1. Fetch raw secret string from environment
raw_secret = os.getenv("SPACEBASIC_TOKEN")

if not raw_secret:
    print("❌ Error: SPACEBASIC_TOKEN environment variable is missing or empty!")
    exit(1)

# 2. Parse JSON
try:
    users = json.loads(raw_secret)
except Exception as e:
    print(f"❌ Error parsing JSON from SPACEBASIC_TOKEN: {e}")
    exit(1)

# Ensure users is a list even if a single dict was provided
if isinstance(users, dict):
    users = [users]

# 3. Process each user
for user in users:
    name = user.get("name", "Unknown")
    user_id = user.get("userId")
    # CRITICAL: Clean whitespace, carriage returns, and newlines from token string
    token = str(user.get("token", "")).strip().replace("\n", "").replace("\r", "")

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id})")
    print(f"==========================================")

    # Example date loop (Today & Tomorrow)
    dates_to_check = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ]

    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    for target_date in dates_to_check:
        print(f"🔍 Fetching meals for date: {target_date}...")
        
        # Replace this URL with your actual SpaceBasic endpoint
        url = f"https://api.spacebasic.com/v1/mealsmenu?date={target_date}&userId={user_id}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"✅ Success for {name} on {target_date}")
            else:
                print(f"⚠️ Failed with status code: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error fetching menu: {e}")
