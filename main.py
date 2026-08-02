import os
import requests
from datetime import datetime, timedelta

BASE_URL = "https://api.spacebasic.com/api/v3/messmanager"
USER_ID = "380170"
TENANT_ID = "143"

TOKEN = os.getenv("SPACEBASIC_TOKEN")

# Format token correctly
if TOKEN and not TOKEN.startswith("Bearer "):
    TOKEN = f"Bearer {TOKEN}"

HEADERS = {
    "Authorization": TOKEN or "",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_upcoming_meals(target_date):
    """Fetch the menu for a specific date (YYYY-MM-DD)."""
    url = f"{BASE_URL}/mealsmenu?userId={USER_ID}&tenantId={TENANT_ID}&mealDate={target_date}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("❌ Token Expired! Grab a fresh Bearer token from DevTools.")
            return None
        else:
            print(f"⚠️ Failed to fetch menu for {target_date}. Status Code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error fetching menu: {e}")
        return None

def book_meal(meal_id, is_special=0):
    """Book the meal using mealId."""
    url = f"{BASE_URL}/rsvpmeal"
    payload = {
        "mealId": int(meal_id),
        "userId": str(USER_ID),
        "status": "1",
        "createdBy": str(USER_ID),
        "isSpecial": int(is_special)
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"✅ Successfully booked Meal ID: {meal_id}")
            return True
        else:
            print(f"❌ Booking failed for Meal ID {meal_id}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error executing booking: {e}")
        return False

def run_auto_booking():
    if not TOKEN:
        print("❌ Error: SPACEBASIC_TOKEN secret is missing!")
        return

    # Check meals for both Today and Tomorrow
    dates_to_check = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ]

    for meal_date in dates_to_check:
        print(f"🔍 Fetching meals for date: {meal_date}...")
        menu_data = get_upcoming_meals(meal_date)
        
        if not menu_data:
            continue

        # Handle array or object response formats
        meals_list = menu_data.get("data", []) if isinstance(menu_data, dict) else menu_data
        if isinstance(meals_list, dict):
            meals_list = meals_list.get("meals", []) or meals_list.get("menu", [])

        if not meals_list:
            print(f"ℹ️ No meals found for {meal_date}.")
            continue

        for meal in meals_list:
            meal_id = meal.get("mealId") or meal.get("id")
            if meal_id:
                print(f"🚀 RSVPing for Meal ID: {meal_id} on {meal_date}")
                book_meal(meal_id)

if __name__ == "__main__":
    run_auto_booking()
