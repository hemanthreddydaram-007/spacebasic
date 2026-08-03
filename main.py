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
    name = user.get("name", "Hemanth")
    user_id = str(user.get("userId", "380170"))
    
    # Sanitize JWT token
    raw_token = str(user.get("token", "")).strip().replace('"', '').replace("'", "")
    if raw_token.lower().startswith("bearer "):
        clean_jwt = raw_token[7:].strip()
    else:
        clean_jwt = raw_token

    auth_header = f"Bearer {clean_jwt}"
    meal_ids = user.get("mealIds", [307802, 307810, 307808])

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
            data = res.json()
            
            if data.get("statusCode") == "S" or data.get("status") == "Success":
                print(f"  🎉 SUCCESS! Booked mealId {meal_id} for {name}!")
            else:
                reason = data.get("result", "Unknown error")
                print(f"  ❌ FAILED for mealId {meal_id}: {reason} (Response: {res.text})")

        except Exception as e:
            print(f"  ❌ Error processing request for mealId {meal_id}: {e}")
