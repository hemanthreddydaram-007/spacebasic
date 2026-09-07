import os
import sys
import datetime
import requests
from supabase import create_client, Client
from security import decrypt_value

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[FATAL] SUPABASE_URL or SUPABASE_KEY is missing from environment.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BASE_URL = "https://api.spacebasic.com"

def get_target_date_info():
    # Targets tomorrow's date for 17:30 IST booking
    target_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    date_str = target_dt.strftime("%Y-%m-%d")
    day_name = target_dt.strftime("%A").lower()
    return date_str, day_name

def resolve_authentication(user):
    auth_type = user.get("auth_type", "password")

    # Path 1: Persistent Session / Bearer Token (Option B)
    if auth_type == "token" and user.get("auth_token"):
        print(f"[{user.get('email')}] Authenticating via stored persistent session token.")
        raw_token = decrypt_value(user["auth_token"]).strip()
        if raw_token.startswith("Bearer "):
            raw_token = raw_token.replace("Bearer ", "").strip()
        return raw_token

    # Path 2: SpaceBasic Email + Password Endpoint (Option A)
    if user.get("password"):
        print(f"[{user.get('email')}] Authenticating via SpaceBasic login endpoint.")
        raw_password = decrypt_value(user["password"]).strip()
        login_url = f"{BASE_URL}/api/v1/authenticate"

        payload = {
            "email": user["email"],
            "password": raw_password,
            "tenant_id": str(user.get("tenant_id", "143"))
        }

        # Clear, isolated headers without stale bearer authorization
        clean_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        resp = requests.post(login_url, json=payload, headers=clean_headers, timeout=20)

        if resp.status_code in (200, 201):
            data = resp.json()
            token = (
                data.get("token") or 
                data.get("data", {}).get("token") or 
                data.get("jwt") or 
                data.get("access_token")
            )
            if token:
                return token.replace("Bearer ", "").strip()
            raise Exception(f"Login succeeded but token missing in payload: {resp.text}")

        raise Exception(f"Login failed: HTTP {resp.status_code} - {resp.text}")

    raise Exception("No valid authentication credential (password or auth_token) found for user.")

def book_meal(session, token, tenant_id, date_str, meal_type, preference):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    booking_url = f"{BASE_URL}/api/v1/cafeteria/book"
    payload = {
        "tenant_id": str(tenant_id),
        "date": date_str,
        "meal_type": meal_type,
        "preference": preference
    }

    resp = session.post(booking_url, json=payload, headers=headers, timeout=20)
    return resp.status_code in (200, 201), resp.text

def process_user(user, date_str, day_name):
    ident = user.get("email")
    print(f"\n--- Initiating sequence for: {ident} ---")

    try:
        token = resolve_authentication(user)
    except Exception as auth_err:
        print(f"[ERROR] Authentication failed for {ident}: {auth_err}")
        return

    tenant_id = user.get("tenant_id", "143")
    skips = user.get("skip_days") or {}
    day_skips = [s.lower() for s in skips.get(day_name, [])]

    meals_plan = [
        ("breakfast", "Veg"),
        ("lunch", user.get("lunch_preference", "Non Veg")),
        ("dinner", user.get("dinner_preference", "Non Veg"))
    ]

    session = requests.Session()
    for meal_type, pref in meals_plan:
        if meal_type in day_skips:
            print(f"[{ident}] Skipping {meal_type} per preference schedule.")
            continue

        try:
            success, msg = book_meal(session, token, tenant_id, date_str, meal_type, pref)
            if success:
                print(f"[{ident}] SUCCESS: {meal_type.capitalize()} ({pref}) reserved.")
            else:
                print(f"[{ident}] FAILED: {meal_type.capitalize()} -> {msg}")
        except Exception as net_err:
            print(f"[{ident}] EXCEPTION during {meal_type} claim: {net_err}")

def main():
    date_str, day_name = get_target_date_info()
    print(f"[MISSION START] Processing Automated Bookings for: {date_str} ({day_name.capitalize()})")

    try:
        res = supabase.table("users").select("*").eq("is_active", True).execute()
        active_users = res.data or []
    except Exception as db_err:
        print(f"[FATAL] Failed to retrieve user roster from Supabase: {db_err}")
        sys.exit(1)

    print(f"[ROSTER] Found {len(active_users)} active user profiles.")

    for user in active_users:
        process_user(user, date_str, day_name)

    print("\n[MISSION COMPLETE] All eligible user bookings executed.")

if __name__ == "__main__":
    main()
