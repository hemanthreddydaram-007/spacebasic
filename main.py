import os
import json
import requests

# 1. Load multi-user JSON secret
raw_secret = os.getenv("SPACEBASIC_TOKEN")

if not raw_secret:
    print("❌ Error: SPACEBASIC_TOKEN secret is missing!")
    exit(1)

try:
    users = json.loads(raw_secret)
except Exception as e:
    print(f"❌ Error parsing JSON secret: {e}")
    exit(1)

if isinstance(users, dict):
    users = [users]

# SpaceBasic RSVP Endpoint
URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

# Replace or expand this list with any active meal IDs for the day
MEAL_IDS = [307800]

# 2. Iterate through all users
for user in users:
    name = user.get("name", "Unknown")
    user_id = str(user.get("userId"))
    token = str(user.get("token", "")).strip().replace("\n", "").replace("\r", "")

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id})")
    print(f"==========================================")

    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for meal_id in MEAL_IDS:
        payload = {
            "mealId": meal_id,
            "userId": user_id,
            "status": "1",
            "createdBy": user_id,
            "isSpecial": 0
        }

        try:
            res = requests.post(URL, headers=headers, json=payload)
            if res.status_code == 200:
                print(f"  ✅ Successfully booked mealId {meal_id} for {name}!")
            else:
                print(f"  ⚠️ Failed for mealId {meal_id}: Status {res.status_code} - {res.text}")
        except Exception as e:
            print(f"  ❌ Error for mealId {meal_id}: {e}")
