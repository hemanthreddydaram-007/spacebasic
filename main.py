import os
import json
import requests
from datetime import datetime, timezone, timedelta

# SpaceBasic Base API Endpoints
MEALS_MENU_URL = "https://api.spacebasic.com/api/v3/messmanager/mealsmenu"
RSVP_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

# IST Timezone (+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_target_date_str():
    """
    Returns tomorrow's date in YYYY-MM-DD format (IST).
    SpaceBasic requires booking 1 day in advance before 9:30 PM IST.
    """
    now_ist = datetime.now(IST)
    target_date = now_ist.date() + timedelta(days=1)
    return target_date.strftime("%Y-%m-%d")

def select_preferred_meal(meal_options):
    """
    Selects meal based on strict priority:
    1. Non-Veg (Chicken, Fish, Mutton, Meat, Non Veg)
    2. Egg
    3. Fallback (Veg / First available)
    """
    if not meal_options:
        return None

    non_veg_keywords = ["non veg", "non-veg", "nonveg", "chicken", "fish", "mutton", "meat"]
    egg_keywords = ["egg", "eg"]

    # Priority 1: Check for Non-Veg
    for m in meal_options:
        name = m.get("mealName", "").lower()
        if any(k in name for k in non_veg_keywords):
            return m

    # Priority 2: Check for Egg
    for m in meal_options:
        name = m.get("mealName", "").lower()
        if any(k in name for k in egg_keywords):
            return m

    # Priority 3: Fallback (Veg)
    return meal_options[0]

def run_automation():
    raw_secret = os.getenv("SPACEBASIC_TOKEN")
    if not raw_secret:
        print("❌ Error: SPACEBASIC_TOKEN environment variable is missing!")
        exit(1)

    try:
        users = json.loads(raw_secret)
        if isinstance(users, dict):
            users = [users]
    except Exception as e:
        print(f"❌ Error parsing JSON secret: {e}")
        exit(1)

    target_date = get_target_date_str()
    print(f"📅 Target Booking Date (IST): {target_date}")

    for user in users:
        name = user.get("name", "Sai Krishna")
        user_id = str(user.get("userId", "380180"))
        tenant_id = str(user.get("tenantId", "143"))

        # Clean Authorization Bearer Token
        raw_token = str(user.get("token", "")).strip().strip('"').strip("'")
        clean_jwt = raw_token[7:].strip() if raw_token.lower().startswith("bearer ") else raw_token
        auth_header = f"Bearer {clean_jwt}"

        print(f"\n==========================================")
        print(f"👤 Processing User: {name} (ID: {user_id})")
        print(f"==========================================")

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # Query Parameters for SpaceBasic /mealsmenu
        params = {
            "userId": user_id,
            "tenantId": tenant_id,
            "mealDate": target_date
        }

        try:
            res = requests.get(MEALS_MENU_URL, headers=headers, params=params)
            
            if res.status_code != 200:
                print(f"❌ HTTP Error {res.status_code} fetching meals: {res.text}")
                continue

            data = res.json()

            if data.get("statusCode") != "S":
                print(f"❌ Failed to fetch meals for {target_date}: {data}")
                continue

            # Parse menu response
            result = data.get("result", {})
            available_meals = result.get("meals", []) if isinstance(result, dict) else result

            if not available_meals:
                print(f"⚠️ No meals available for booking on {target_date}.")
                continue

            # Separate into categories
            breakfast_opts = [m for m in available_meals if "Breakfast" in m.get("mealName", "")]
            lunch_opts = [m for m in available_meals if "Lunch" in m.get("mealName", "")]
            dinner_opts = [m for m in available_meals if "Dinner" in m.get("mealName", "")]

            to_book = []

            # 1. Breakfast (Take first available)
            if breakfast_opts:
                to_book.append(breakfast_opts[0])

            # 2. Lunch (Priority: Non-Veg -> Egg -> Veg)
            selected_lunch = select_preferred_meal(lunch_opts)
            if selected_lunch:
                to_book.append(selected_lunch)

            # 3. Dinner (Priority: Non-Veg -> Egg -> Veg)
            selected_dinner = select_preferred_meal(dinner_opts)
            if selected_dinner:
                to_book.append(selected_dinner)

            print(f"🔍 Meals selected for booking on {target_date}:")
            for m in to_book:
                status_text = "Already Booked" if m.get("status") == 1 else "Unbooked"
                print(f"   • {m.get('mealName')} (ID: {m.get('mealId')}) -> [{status_text}]")

        except Exception as e:
            print(f"❌ Exception fetching meal schedule: {e}")
            continue

        # Step 2: Book unbooked slots via RSVP
        for meal in to_book:
            meal_id = meal.get("mealId")
            meal_name = meal.get("mealName")

            if meal.get("status") == 1:
                print(f"  ℹ️ Skipping {meal_name} (ID: {meal_id}) - already booked.")
                continue

            payload = {
                "mealId": meal_id,
                "userId": user_id,
                "status": "1",
                "createdBy": user_id,
                "isSpecial": 0
            }

            try:
                rsvp_res = requests.post(RSVP_URL, headers=headers, json=payload)
                rsvp_data = rsvp_res.json()

                if rsvp_data.get("statusCode") == "S" or rsvp_data.get("status") == "Success":
                    print(f"  🎉 SUCCESS! Booked {meal_name} (ID: {meal_id})!")
                else:
                    reason = rsvp_data.get("result", "Unknown Error")
                    print(f"  ❌ FAILED for {meal_name} (ID: {meal_id}): {reason}")

            except Exception as e:
                print(f"  ❌ Request error for {meal_name} (ID: {meal_id}): {e}")

if __name__ == "__main__":
    run_automation()
