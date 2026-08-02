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

# SpaceBasic Endpoints
MENU_URL = "https://api.spacebasic.com/api/v3/messmanager/getstudentmeals"
RSVP_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

# 3. Process each user
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

    dates_to_book = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ]

    for target_date in dates_to_book:
        print(f"\n🔍 Checking meals for date: {target_date}...")

        # Step 3a: Fetch available meals for this date
        try:
            menu_res = requests.get(f"{MENU_URL}?date={target_date}&userId={user_id}", headers=headers)
            
            if menu_res.status_code != 200:
                print(f"⚠️ Failed to fetch menu: Status {menu_res.status_code}")
                continue

            menu_data = menu_res.json()
            
            # Extract meals list (handles common SpaceBasic response structures)
            meals = []
            if isinstance(menu_data, list):
                meals = menu_data
            elif isinstance(menu_data, dict):
                meals = menu_data.get("data", []) or menu_data.get("meals", [])

            if not meals:
                print(f"ℹ️ No meals found for date {target_date}.")
                continue

            # Step 3b: Loop through each meal and RSVP
            for meal in meals:
                meal_id = meal.get("mealId") or meal.get("id")
                meal_name = meal.get("mealName") or meal.get("name", "Meal")

                if not meal_id:
                    continue

                payload = {
                    "mealId": int(meal_id),
                    "userId": user_id,
                    "status": "1",
                    "createdBy": user_id,
                    "isSpecial": 0
                }

                rsvp_res = requests.post(RSVP_URL, headers=headers, json=payload)

                if rsvp_res.status_code == 200:
                    print(f"  ✅ Booked {meal_name} (ID: {meal_id}) successfully!")
                else:
                    print(f"  ⚠️ Failed to book {meal_name} (ID: {meal_id}): {rsvp_res.text}")

        except Exception as e:
            print(f"❌ Exception occurred for date {target_date}: {e}")
