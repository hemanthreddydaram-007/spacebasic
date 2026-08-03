import os
import json
import requests

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

URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

for user in users:
    name = user.get("name", "Unknown")
    user_id = str(user.get("userId"))
    
    # Clean the token: remove spaces/newlines/extra 'Bearer ' prefixes
    raw_token = str(user.get("token", "")).strip()
    if raw_token.lower().startswith("bearer "):
        clean_jwt = raw_token[7:].strip()
    else:
        clean_jwt = raw_token

    auth_header = f"Bearer {clean_jwt}"
    meal_ids = user.get("mealIds", [307800 if name != "Wafiq" else 307790])

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id})")
    print(f"==========================================")

    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for meal_id in meal_ids:
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
