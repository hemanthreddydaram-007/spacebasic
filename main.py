import os
import sys
import json
import pytz
import requests
from datetime import datetime, timedelta
from supabase import create_client, Client
from security import decrypt_value

BASE_URL = "https://api.spacebasic.com"

def get_ist_tomorrow():
    tz = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(tz)
    tomorrow = now_ist + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d"), tomorrow.strftime("%A").lower()

def resolve_authentication(user):
    """Branches between Password Login and Direct Session Bearer Token."""
    auth_type = user.get("auth_type", "password")

    # Branch 1: Direct Session / Bearer Token
    if auth_type == "token" and user.get("auth_token"):
        print(f"[{user.get('email')}] Authenticating via stored persistent session token.")
        return decrypt_value(user["auth_token"])

    # Branch 2: Standard Email + Password
    if user.get("password"):
        print(f"[{user.get('email')}] Authenticating via SpaceBasic login endpoint.")
        raw_password = decrypt_value(user["password"])
        login_url = f"{BASE_URL}/api/v1/authenticate"
        payload = {
            "email": user["email"],
            "password": raw_password,
            "tenant_id": user.get("tenant_id", "143")
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        resp = requests.post(login_url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token") or data.get("data", {}).get("token")
            if token:
                return token
        raise Exception(f"Login failed: HTTP {resp.status_code} - {resp.text}")

    raise Exception("No valid authentication credential found on user record.")

def book_meal(token, tenant_id, date_str, meal_type, food_type):
    url = f"{BASE_URL}/api/v1/mess/book"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "date": date_str,
        "meal_type": meal_type,
        "food_type": food_type,
        "tenant_id": tenant_id
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    return resp.status_code in [200, 201], resp.text

def main():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[CRITICAL ERROR] Missing SUPABASE_URL or SUPABASE_KEY in environment.")
        sys.exit(1)

    supabase: Client = create_client(supabase_url, supabase_key)
    users_resp = supabase.table("users").select("*").eq("is_active", True).execute()
    users = users_resp.data

    if not users:
        print("[SYSTEM INFO] No active user accounts found to process today.")
        return

    target_date, target_weekday = get_ist_tomorrow()
    print(f"[MISSION START] Processing Automated Bookings for: {target_date} ({target_weekday.capitalize()})")

    for user in users:
        email = user.get("email")
        tenant = user.get("tenant_id", "143")
        skip_days = user.get("skip_days", {}) or {}

        day_skips = skip_days.get(target_weekday, [])

        try:
            auth_token = resolve_authentication(user)
            
            # Breakfast
            if "breakfast" not in day_skips:
                success, msg = book_meal(auth_token, tenant, target_date, "breakfast", "Veg")
                print(f"[{email}] Breakfast booked: {success} ({msg})")
            else:
                print(f"[{email}] Skipping breakfast (Scheduled Skip).")

            # Lunch
            if "lunch" not in day_skips:
                pref = user.get("lunch_preference", "Veg")
                success, msg = book_meal(auth_token, tenant, target_date, "lunch", pref)
                print(f"[{email}] Lunch booked ({pref}): {success} ({msg})")
            else:
                print(f"[{email}] Skipping lunch (Scheduled Skip).")

            # Dinner
            if "dinner" not in day_skips:
                pref = user.get("dinner_preference", "Veg")
                success, msg = book_meal(auth_token, tenant, target_date, "dinner", pref)
                print(f"[{email}] Dinner booked ({pref}): {success} ({msg})")
            else:
                print(f"[{email}] Skipping dinner (Scheduled Skip).")

        except Exception as e:
            print(f"[ERROR] Booking sequence failed for {email}: {e}")

if __name__ == "__main__":
    main()
