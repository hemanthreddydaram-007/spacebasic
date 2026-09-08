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

# Supabase Initialization
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[FATAL] SUPABASE_URL or SUPABASE_KEY is missing from environment variables.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BASE_URL = "https://api.spacebasic.com"

# Email Alert Configuration (Add to GitHub Secrets)
ALERT_SENDER_EMAIL = os.getenv("ALERT_SENDER_EMAIL")
ALERT_SENDER_PASSWORD = os.getenv("ALERT_SENDER_PASSWORD")


def send_expiration_notification(recipient_email, user_identifier):
    """Sends an email alert to the user when their credentials/session expire."""
    if not ALERT_SENDER_EMAIL or not ALERT_SENDER_PASSWORD:
        print(f"[ALERT WARNING] Sender credentials missing. Could not notify {recipient_email}.")
        return

    subject = "⚠️ MessConquers: SpaceBasic Session Expired / Authentication Failed"
    body = (
        f"Hi,\n\n"
        f"Your SpaceBasic session token or authentication link for account ({user_identifier}) has expired.\n\n"
        f"Because your credentials could not be authenticated, your automated daily meal bookings are currently PAUSED.\n\n"
        f"Please visit the portal to paste your new link or re-enter your credentials to resume bookings:\n"
        f"https://messconquers.streamlit.app\n\n"
        f"— MessConquers Bot"
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
        print(f"[{recipient_email}] Expiration alert email dispatched successfully.")
    except Exception as e:
        print(f"[{recipient_email}] Failed to dispatch alert email: {e}")


def get_target_date_info():
    # Target next calendar day
    target_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    date_str = target_dt.strftime("%Y-%m-%d")
    day_name = target_dt.strftime("%A").lower()
    return date_str, day_name


def extract_user_id(token, fallback_val=None):
    try:
        decoded = pyjwt.decode(token, options={"verify_signature": False})
        uid = decoded.get("uid") or decoded.get("sub") or decoded.get("userId")
        if uid:
            return str(uid)
    except Exception:
        pass
    return str(fallback_val) if fallback_val else ""


def resolve_authentication(user):
    auth_type = user.get("auth_type", "password")

    # Persistent Session / Link / Token
    if auth_type == "token" and user.get("auth_token"):
        print(f"[{user.get('email')}] Authenticating via stored persistent session token/link.")
        try:
            raw_token = decrypt_value(user["auth_token"]).strip()
        except Exception as dec_err:
            raise Exception(f"Session token decryption failed: {dec_err}")

        if not raw_token:
            raise Exception("Decrypted session token was empty.")
        if raw_token.startswith("Bearer "):
            raw_token = raw_token.replace("Bearer ", "").strip()
        return raw_token

    # SpaceBasic Email / Password Authentication
    if user.get("password"):
        print(f"[{user.get('email')}] Authenticating via SpaceBasic /authenticate/email endpoint.")
        try:
            raw_password = decrypt_value(user["password"]).strip()
        except Exception as dec_err:
            raise Exception(f"Password decryption failed: {dec_err}")

        if not raw_password:
            raise Exception("Decrypted password was empty. Re-register on the web portal.")

        login_url = f"{BASE_URL}/authenticate/email"
        payload = {
            "username": user["email"].strip(),
            "password": raw_password
        }
        clean_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://web.spacebasic.com",
            "Referer": "https://web.spacebasic.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        resp = requests.post(login_url, json=payload, headers=clean_headers, timeout=20)
        if resp.status_code in (200, 201):
            data = resp.json()
            token = data.get("jwt") or data.get("accessToken")
            if token:
                return token.replace("Bearer ", "").strip()
            raise Exception(f"Login succeeded but token was missing: {resp.text}")

        raise Exception(f"Login failed: HTTP {resp.status_code} - {resp.text}")

    raise Exception("No valid credentials or session token found for this profile.")


def fetch_menu_and_book(session, token, user_id, tenant_id, date_str, meal_type, preference):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://web.spacebasic.com",
        "Referer": "https://web.spacebasic.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Step 1: Query mealsmenu
    menu_url = f"{BASE_URL}/api/v3/messmanager/mealsmenu?userId={user_id}&tenantId={tenant_id}&mealDate={date_str}"
    menu_resp = session.get(menu_url, headers=headers, timeout=20)

    if menu_resp.status_code != 200:
        return False, f"Failed to fetch menu: HTTP {menu_resp.status_code} - {menu_resp.text}"

    menu_data = menu_resp.json()
    meals_list = menu_data.get("result", {}).get("meals", [])
    if not meals_list:
        return False, "No meals found for this date."

    # Step 2: Match dynamic mealId
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
        return False, f"Could not match mealId for {meal_type} ({preference})"

    # Step 3: POST to rsvpmeal
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
    ident = user.get("email", "")
    target_alert_email = user.get("notification_email") or ident

    print(f"\n--- Initiating sequence for: {ident} ---")

    try:
        token = resolve_authentication(user)
    except Exception as auth_err:
        print(f"[ERROR] Authentication failed for {ident}: {auth_err}")

        # Send expiration email if an address is available
        if "@" in target_alert_email:
            send_expiration_notification(target_alert_email, ident)
        else:
            print(f"[{ident}] No valid notification email found to alert user.")

        # Pause active status in Supabase so subsequent runs don't repeatedly fail
        try:
            supabase.table("users").update({"is_active": False}).eq("email", ident).execute()
            print(f"[{ident}] Account set to inactive in database until updated.")
        except Exception as db_e:
            print(f"[{ident}] Database update failed: {db_e}")
        return

    tenant_id = user.get("tenant_id", "143")
    user_id = extract_user_id(token, fallback_val=user.get("spacebasic_id"))

    if not user_id:
        print(f"[ERROR] Could not resolve user ID for {ident}")
        return

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
            print(f"[{ident}] Skipping {meal_type} based on preferences.")
            continue

        try:
            success, msg = fetch_menu_and_book(session, token, user_id, tenant_id, date_str, meal_type, pref)
            if success:
                print(f"[{ident}] SUCCESS: {meal_type} ({pref}) reserved.")
            else:
                print(f"[{ident}] FAILED: {meal_type} -> {msg}")
        except Exception as net_err:
            print(f"[{ident}] EXCEPTION during {meal_type} booking: {net_err}")


def main():
    date_str, day_name = get_target_date_info()
    print(f"[START] Processing Automated Bookings for: {date_str} ({day_name.capitalize()})")

    try:
        res = supabase.table("users").select("*").eq("is_active", True).execute()
        active_users = res.data or []
    except Exception as db_err:
        print(f"[FATAL] Failed to retrieve users from Supabase: {db_err}")
        sys.exit(1)

    print(f"[ROSTER] Found {len(active_users)} active user profiles.")

    for user in active_users:
        process_user(user, date_str, day_name)

    print("\n[COMPLETE] All user pipelines completed.")


if __name__ == "__main__":
    main()
