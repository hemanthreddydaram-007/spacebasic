import os
import json
import requests
from datetime import datetime, timezone, timedelta

# SpaceBasic Base API Endpoints
MEALS_MENU_URL = "https://api.spacebasic.com/api/v3/messmanager/mealsmenu"
RSVP_URL = "https://api.spacebasic.com/api/v3/messmanager/rsvpmeal"

# IST Timezone (+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_target_date_info():
    """
    Returns tomorrow's date string (YYYY-MM-DD) and day name (e.g., 'sunday').
    SpaceBasic requires booking 1 day in advance.
    """
    now_ist = datetime.now(IST)
    target_date = now_ist.date() + timedelta(days=1)
    
    target_date_str = target_date.strftime("%Y-%m-%d")
    target_day_name = target_date.strftime("%A").lower()  # 'monday', 'sunday', etc.
    
    return target_date_str, target_day_name

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

def cancel_meal_rsvp(headers, user_id, meal_id, meal_name):
    """
    Sends RSVP payload with status '0' to unbook/cancel a meal on SpaceBasic.
    """
    payload = {
        "mealId": meal_id,
        "userId": user_id,
        "status": "0",  # Status 0 indicates cancellation/unbooking
        "createdBy": user_id,
        "isSpecial": 0
    }
    
    try:
        rsvp_res = requests.post(RSVP_URL, headers=headers, json=payload)
        rsvp_data = rsvp_res.json()

        if rsvp_data.get("statusCode") == "S" or rsvp_data.get("status") == "Success":
            print(f"   🚫 SUCCESS! Cancelled {meal_name} (ID: {meal_id}) on SpaceBasic!")
        else:
            reason = rsvp_data.get("result", "Unknown Error")
            print(f"   ❌ FAILED to cancel {meal_name} (ID: {meal_id}): {reason}")
    except Exception as e:
        print(f"   ❌ Error cancelling {meal_name} (ID: {meal_id}): {e}")

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

    target_date, target_day = get_target_date_info()
    print(f"📅 Target Booking Date (IST): {target_date} ({target_day.title()})")

    for user in users:
        name = user.get("name", "Sai Krishna")
        user_id = str(user.get("userId", "380180"))
        tenant_id = str(user.get("tenantId", "143"))

        # Retrieve day-based skip rules (e.g., {"sunday": ["Breakfast"]})
        skip_days_config = user.get("skip_days", {})
        today_meal_skips = [m.lower() for m in skip_days_config.get(target_day, [])]

        # Clean Authorization Bearer Token
        raw_token = str(user.get("token", "")).strip().strip('"').strip("'")
        clean_jwt = raw_token[7:].strip() if raw_token.lower().startswith("bearer ") else raw_token
        auth_header = f"Bearer {clean_jwt}"

        print(f"\n==========================================")
        print(f"👤 Processing User: {name} (ID: {user_id})")
        print(f"==========================================")

        # Check whole-day skip rule
        if "all" in today_meal_skips:
            print(f"🌴 {target_day.title()} is set to skip ALL meals for {name}! Skipping day.")
            continue

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

            to_process = []

            # 1. Breakfast
            if breakfast_opts:
                to_process.append(("breakfast", breakfast_opts[0]))

            # 2. Lunch (Priority: Non-Veg -> Egg -> Veg)
            selected_lunch = select_preferred_meal(lunch_opts)
            if selected_lunch:
                to_process.append(("lunch", selected_lunch))

            # 3. Dinner (Priority: Non-Veg -> Egg -> Veg)
            selected_dinner = select_preferred_meal(dinner_opts)
            if selected_dinner:
                to_process.append(("dinner", selected_dinner))

            print(f"🔍 Meal options evaluated for {target_date} ({target_day.title()}):")
            for category, m in to_process:
                status_text = "Already Booked" if m.get("status") == 1 else "Unbooked"
                skip_flag = " [CANCEL REQUESTED]" if category in today_meal_skips else ""
                print(f"   • {m.get('mealName')} (ID: {m.get('mealId')}) -> [{status_text}]{skip_flag}")

        except Exception as e:
            print(f"❌ Exception fetching meal schedule: {e}")
            continue

        # Step 2: Book or Cancel meals based on weekly rules
        for category, meal in to_process:
            meal_id = meal.get("mealId")
            meal_name = meal.get("mealName")
            is_booked = (meal.get("status") == 1)

            # Check if user configured a skip/cancel rule for this meal on this day
            if category in today_meal_skips:
                if is_booked:
                    print(f"🛑 {category.title()} is set to SKIP on {target_day.title()}s for {name}. Cancelling booking...")
                    cancel_meal_rsvp(headers, user_id, meal_id, meal_name)
                else:
                    print(f"   ℹ️ Skipping {category.title()} ({target_day.title()} skip rule) - meal is not booked.")
                continue

            # Normal Booking Execution
            if is_booked:
                print(f"   ℹ️ Skipping {meal_name} (ID: {meal_id}) - already booked.")
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
                    print(f"   🎉 SUCCESS! Booked {meal_name} (ID: {meal_id})!")
                else:
                    reason = rsvp_data.get("result", "Unknown Error")
                    print(f"   ❌ FAILED for {meal_name} (ID: {meal_id}): {reason}")

            except Exception as e:
                print(f"   ❌ Request error for {meal_name} (ID: {meal_id}): {e}")

if __name__ == "__main__":
    run_automation()
