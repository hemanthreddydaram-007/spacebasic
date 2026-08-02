import os
import requests

BASE_URL = "https://api.spacebasic.com/api/v3/messmanager"
USER_ID = "380170"

TOKEN = os.getenv("SPACEBASIC_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}" if TOKEN and not TOKEN.startswith("Bearer") else (TOKEN or ""),
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_upcoming_meals():
    """Fetch the menu to retrieve dynamic mealIds."""
    url = f"{BASE_URL}/mealsmenu?userId={USER_ID}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("❌ Token Expired! Please grab a fresh Bearer token from browser DevTools.")
            return None
        else:
            print(f"⚠️ Failed to fetch menu. Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching menu: {e}")
        return None

def book_meal(meal_id, is_special=0):
    """Book the meal using the fetched mealId."""
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
        print("❌ Error: SPACEBASIC_TOKEN environment variable is missing!")
        return

    print("🔍 Fetching upcoming meals...")
    menu_data = get_upcoming_meals()
    
    if not menu_data:
        return

    # Extract meals list
    meals_list = menu_data.get("data", []) or (menu_data if isinstance(menu_data, list) else [])
    
    if not meals_list:
        print("ℹ️ No available meals found to book.")
        return

    for meal in meals_list:
        meal_id = meal.get("mealId") or meal.get("id")
        if meal_id:
            print(f"🚀 Attempting to RSVP for Meal ID: {meal_id}")
            book_meal(meal_id)

if __name__ == "__main__":
    run_auto_booking()
