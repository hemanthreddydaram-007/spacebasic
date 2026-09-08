import os
import sys
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import jwt as pyjwt
from supabase import create_client, Client
from security import decrypt_value

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[FATAL] Supabase credentials missing from environment.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BASE_URL = "https://api.spacebasic.com"

ALERT_SENDER_EMAIL = os.getenv("ALERT_SENDER_EMAIL")
ALERT_SENDER_PASSWORD = os.getenv("ALERT_SENDER_PASSWORD")

def send_expiration_notification(recipient_email, spacebasic_id):
    """Dispatches an email alert to the user when their credentials/link fail."""
    if not ALERT_SENDER_EMAIL or not ALERT_SENDER_PASSWORD:
        print(f"[ALERT WARNING] Sender credentials missing. Skipping notification to {recipient_email}.")
        return

    subject = "⚠️ MessConquers: SpaceBasic Link Expired / Authentication Failed"
    body = (
        f"Hi Hunter,\n\n"
        f"Your SpaceBasic session link or credentials for User ID [{spacebasic_id}] have expired or failed.\n\n"
        f"Automated daily meal bookings are currently PAUSED for your account.\n\n"
        f"To restore daily bookings, re-enroll with your updated link or credentials here:\n"
        f"https://messconquers.streamlit.app\n\n"
        f"— MessConquers Automated Bot"
    )

    msg = MIMEMultipart()
    msg["From"] = ALERT_SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(ALERT_SENDER_EMAIL, ALERT_SENDER_PASSWORD)
            server.sendmail(ALERT_SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"[{spacebasic_id}] Alert email sent successfully to {recipient_email}.")
    except Exception as e:
        print(f"[{spacebasic_id}] Failed to dispatch alert email: {e}")

def get_target_date_info():
    target_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    return target_dt.strftime("%Y-%m-%d"), target_dt.strftime("%A").lower()

def resolve_authentication(user):
    auth_type = user.get("auth_type", "token")

    # Link / Token Authentication
    if auth_type == "token" and user.get("auth_token"):
        raw_token = decrypt_value(user["auth_token"]).strip()
        if not raw_token:
            raise Exception("Decrypted session token was empty.")
        return raw_token.replace("Bearer ", "").strip()

    # SpaceBasic Email & Password Authentication
    if user.get("password") and user.get("email"):
        raw_password = decrypt_value(user["password"]).strip()
        login_url = f"{BASE_URL}/authenticate/email"
        payload = {"username": user["email"].strip(), "password": raw_password}
        clean_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://web.spacebasic.com",
            "Referer": "https://web.spacebasic.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.post(login_url, json=payload, headers=clean_headers, timeout=20)
        if resp.status_code in (200, 201):
            data = resp.json()
            token = data.get("jwt") or data.get("accessToken")
            if token:
                return token.replace("Bearer ", "").strip()
        raise Exception(f"Login failed: HTTP {resp.status_code} - {resp.text}")

    raise Exception("No valid authentication record found for this profile.")

def fetch_menu_and_book(session, token, user_id, tenant_id, date_str, meal_type, preference):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://web.spacebasic.com",
        "Referer": "https://web.spacebasic.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Step 1: Query mealsmenu
    menu_url = f"{BASE_URL}/api/v3/messmanager/mealsmenu?userId={user_id}&tenantId={tenant_id}&mealDate={date_str}"
    menu_resp = session.get(menu_url, headers=headers, timeout=20)
    if menu_resp.status_code != 200:
        return False, f"HTTP {menu_resp.status_code} on mealsmenu fetch"

    meals_list = menu_resp.json().get("result", {}).get("meals", [])
    target_meal_id = None
    pref_clean = preference.strip().lower()

    for meal in meals_list:
        m_name = (meal.get("mealName") or "").lower()
        if meal_type.lower() in m_name:
            if pref_clean in m_name:
                target_meal_id = meal.get("mealId")
                break
            elif not target_meal_id:
                target_meal_id = meal.get("mealId")

    if not target_meal_id:
        return False, f"No matching mealId for {meal_type} ({preference})"

    # Step 2: Book via rsvpmeal
    rsvp_url = f"{BASE_URL}/api/v3/messmanager/rsvpmeal"
    payload = {
        "mealId": target_meal_id,
        "userId": str(user_id),
        "status": "1",
        "createdBy": str(user_id),
        "isSpecial": 0
    }
    rsvp_resp = session.post(rsvp_url, json=payload, headers=headers, timeout=20)
    return rsvp_resp.status_code in (200, 201), rsvp_resp.text

def process_user(user, date_str, day_name):
    uid = str(user.get("spacebasic_id"))
    alert_email = user.get("notification_email")

    print(f"\n--- Processing SpaceBasic ID: {uid} ---")

    try:
        token = resolve_authentication(user)
    except Exception as auth_err:
        print(f"[{uid}] Authentication error: {auth_err}")
        
        # Trigger email alert to user
        if alert_email and "@" in alert_email:
            send_expiration_notification(alert_email, uid)
        
        # Mark inactive in Supabase using the spacebasic_id primary key
        try:
            supabase.table("users").update({"is_active": False}).eq("spacebasic_id", uid).execute()
            print(f"[{uid}] Deactivated in Supabase until user updates link.")
        except Exception as db_e:
            print(f"[{uid}] DB update error: {db_e}")
        return

    tenant_id = user.get("tenant_id", "143")
    skips = user.get("skip_days") or {}
    day_skips = [s.lower() for s in skips.get(day_name, [])]

    meals_plan = [
        ("Breakfast", "Veg"),
        ("Lunch", user.get("lunch_preference", "Non Veg")),
        ("Dinner", user.get("dinner_preference", "Non Veg"))
    ]

    session = requests.Session()
    for meal_type, pref in meals_plan:
        if meal_type.lower() in day_skips:
            print(f"[{uid}] Skipping {meal_type} based on preferences.")
            continue

        try:
            success, msg = fetch_menu_and_book(session, token, uid, tenant_id, date_str, meal_type, pref)
            if success:
                print(f"[{uid}] SUCCESS: {meal_type} ({pref}) booked.")
            else:
                print(f"[{uid}] FAILED: {meal_type} -> {msg}")
        except Exception as net_err:
            print(f"[{uid}] Exception during {meal_type}: {net_err}")

def main():
    date_str, day_name = get_target_date_info()
    print(f"[START] Processing bookings for: {date_str} ({day_name.capitalize()})")

    try:
        res = supabase.table("users").select("*").eq("is_active", True).execute()
        active_users = res.data or []
    except Exception as db_err:
        print(f"[FATAL] Could not retrieve users from Supabase: {db_err}")
        sys.exit(1)

    print(f"[ROSTER] Found {len(active_users)} active user profiles.")
    for user in active_users:
        process_user(user, date_str, day_name)
    print("\n[COMPLETE] Daily run finished.")

if __name__ == "__main__":
    main()
