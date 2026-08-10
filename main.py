def extract_all_meal_ids(data):
    """Parses SpaceBasic menu array and returns a list of all bookable meal objects."""
    meals_to_book = []
    
    if isinstance(data, dict):
        result = data.get("result", {})
        meals = result.get("meals", []) if isinstance(result, dict) else []
        
        for meal in meals:
            # Only pick meals where booking is allowed
            if str(meal.get("allowBooking")) == "1":
                meal_id = meal.get("mealId")
                meal_name = meal.get("mealName", "Unknown Meal")
                if meal_id:
                    meals_to_book.append({"id": meal_id, "name": meal_name})
                    
    return meals_to_book

def process_user_booking(user, max_retries=3, delay=3):
    name = user.get("name", "Unknown")
    user_id = str(user.get("user_id") or user.get("userid") or "")
    tenant_id = str(user.get("tenant_id") or "143")
    raw_token = str(user.get("token") or user.get("auth_token") or "")
    skip_days = user.get("skip_days", {})

    print(f"\n==========================================")
    print(f"👤 Processing User: {name} (ID: {user_id or 'Missing'})")
    print(f"==========================================")

    if not user_id or user_id == "None" or not raw_token or len(raw_token) < 10:
        print(f"⚠️ Skipping {name}: Invalid credentials.")
        return False

    if should_skip_today(skip_days):
        print(f"⏭️ Skipping booking for {name} today based on 'skip_days' configuration.")
        return True

    token_header = raw_token if raw_token.startswith("Bearer ") else f"Bearer {raw_token}"
    headers = {
        "Authorization": token_header,
        "User-ID": user_id,
        "x-publishable-key": SPACEBASIC_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Fetch menu list for tomorrow
    ist = pytz.timezone("Asia/Kolkata")
    tomorrow_date = (datetime.now(ist) + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"{SPACEBASIC_MENU_URL}?userId={user_id}&tenantId={tenant_id}&mealDate={tomorrow_date}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            meals = extract_all_meal_ids(response.json())
            if not meals:
                print(f"⚠️ No bookable meals found for {name} on {tomorrow_date}.")
                return False

            all_success = True
            for meal in meals:
                meal_id = meal["id"]
                meal_name = meal["name"]
                
                payload = {
                    "mealId": int(meal_id),
                    "userId": user_id,
                    "status": "1",
                    "createdBy": user_id,
                    "isSpecial": 0
                }

                print(f"🚀 Booking {meal_name} (ID: {meal_id}) for {name}...")
                res = requests.post(SPACEBASIC_BOOKING_URL, json=payload, headers=headers, timeout=15)
                
                if res.status_code in [200, 201]:
                    print(f"  └─ 🎉 {meal_name} RSVP confirmed!")
                else:
                    print(f"  └─ ⚠️ Failed to book {meal_name}: HTTP {res.status_code}")
                    all_success = False

            return all_success
    except Exception as e:
        print(f"❌ Network error processing {name}: {e}")

    return False
