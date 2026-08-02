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

if isinstance(users, dict):
    users = [users]

# SpaceBasic RSVP Endpoint
URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

# 3. Process each user
for user in users:
    name = user.get("name", "Unknown")
    user_id = user.get("userId")
    token = str(user.get("token", "")).strip().replace("\n", "").replace("\r", "")

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id})")
    print(f"==========================================")

    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Example target dates (Today & Tomorrow)
    dates_to_book = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ]

    for target_date in dates_to_book:
        print(f"🔍 Sending RSVP request for date: {target_date}...")

        # Typical JSON payload expected by rsvpmeal endpoint
        payload = {
            "userId": user_id,
            "date": target_date
        }

        try:
            # Note: Changed from GET to POST
            response = requests.post(URL, headers=headers, json=payload)

            if response.status_code == 200:
                print(f"✅ Success for {name} on {target_date}: {response.text}")
            else:
                print(f"⚠️ Failed with status code {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Exception occurred: {e}")
