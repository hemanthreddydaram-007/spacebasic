import os
import re
import streamlit as st
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# SYSTEM CORE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mess Conquers • Automation Hub",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# STABLE 3D FLOATING CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* Dark Spatial Stage */
    .stApp {
        background-color: #070a13 !important;
        background-image: 
            radial-gradient(circle at 50% -10%, rgba(14, 165, 233, 0.22) 0%, transparent 60%),
            radial-gradient(circle at 10% 90%, rgba(99, 102, 241, 0.12) 0%, transparent 50%) !important;
        color: #f8fafc !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Floating Keyframe Animation */
    @keyframes floatingBob {
        0%, 100% {
            transform: translateY(0px);
            box-shadow: 
                0 20px 40px -10px rgba(0, 0, 0, 0.9),
                0 0 25px rgba(14, 165, 233, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }
        50% {
            transform: translateY(-8px);
            box-shadow: 
                0 32px 55px -12px rgba(0, 0, 0, 0.95),
                0 0 40px rgba(14, 165, 233, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.25);
        }
    }

    /* 3D Floating Hero Banner */
    .floating-hero {
        background: linear-gradient(145deg, #111827 0%, #0c1220 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 1px solid rgba(56, 189, 248, 0.5);
        border-radius: 20px;
        padding: 2.2rem 1.8rem;
        margin-bottom: 2rem;
        text-align: center;
        animation: floatingBob 5s ease-in-out infinite;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #38bdf8;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.25);
        margin-bottom: 0.75rem;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.02em;
        text-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
    }

    .hero-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    /* 3D Elevated Form Surface */
    div[data-testid="stForm"] {
        background: linear-gradient(160deg, #0f172a 0%, #090e1a 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 2.2rem !important;
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.85),
            0 0 30px rgba(14, 165, 233, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }

    div[data-testid="stForm"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 
            0 35px 65px -15px rgba(0, 0, 0, 0.95),
            0 0 40px rgba(14, 165, 233, 0.18),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    /* Inset Tactile Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #030712 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.7) !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #38bdf8 !important;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.8),
            0 0 0 3px rgba(56, 189, 248, 0.25) !important;
    }

    /* 3D Elevated Button */
    .stButton>button {
        background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-bottom: 3px solid #0369a1 !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.8rem !important;
        box-shadow: 0 10px 22px -4px rgba(2, 132, 199, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.15s ease !important;
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 16px 28px -4px rgba(2, 132, 199, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.45) !important;
    }

    .stButton>button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35) !important;
    }

    /* Tab Controls */
    .stTabs [data-baseweb="tab-list"] {
        background: #0f172a;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 6px;
        gap: 8px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #94a3b8;
        border-radius: 8px;
        padding: 8px 16px;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .guide-box {
        background: #030712;
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 4px solid #38bdf8;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .status-card-active {
        background: linear-gradient(145deg, rgba(6, 78, 59, 0.5) 0%, rgba(6, 95, 70, 0.3) 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 12px 25px -5px rgba(16, 185, 129, 0.2);
    }

    .status-card-paused {
        background: linear-gradient(145deg, rgba(120, 53, 15, 0.5) 0%, rgba(146, 64, 14, 0.3) 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 12px 25px -5px rgba(245, 158, 11, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FLOATING HERO BANNER
# ==========================================
st.markdown("""
<div class="floating-hero">
    <div class="hero-badge">⚡ AUTONOMOUS SYNC ENGINE</div>
    <div class="hero-title">Mess Conquers</div>
    <p class="hero-sub">High-availability automated meal reservations & session vault</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("System configuration error: Supabase credentials not found in secrets.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

tab_telemetry, tab_register = st.tabs(["⚡ Service Status & Vacation", "🛠️ Account Setup & Credentials"])

# ==========================================
# TAB 1: STATUS & CONTROLS
# ==========================================
with tab_telemetry:
    st.markdown("##### Account Status & Controls")
    st.caption("Inspect your active daily schedule or pause automation when leaving campus.")

    lookup_protocol = st.radio(
        "Identifier Protocol",
        [
            "🔑 SpaceBasic User ID (Token / Magic Link Users)",
            "✉️ Direct Login Email (Password Users)"
        ],
        horizontal=True
    )

    if "User ID" in lookup_protocol:
        query_val = st.text_input("SpaceBasic User ID", placeholder="e.g. 123456").strip()
        query_field = "spacebasic_id"
    else:
        query_val = st.text_input("Login Email", placeholder="e.g. student@example.com").strip().lower()
        query_field = "email"

    if query_val:
        try:
            record_query = supabase.table("users").select("*").eq(query_field, query_val).execute()
            if record_query.data and len(record_query.data) > 0:
                user_info = record_query.data[0]
                user_name = user_info.get("name", "Student")
                is_active = user_info.get("is_active", True)
                auth_type = user_info.get("auth_type", "password").upper()
                notif_email = user_info.get("notification_email") or user_info.get("email") or "Not configured"
                row_id = user_info.get("id")

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="status-card-active">
                        <div style="font-weight: 700; color: #34d399; font-size: 1.1rem; margin-bottom: 6px;">
                            ● STATUS: ACTIVE & SCHEDULED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.94rem; line-height: 1.6;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Protocol: <code>{auth_type}</code> | Alert Receiver: <code>{notif_email}</code><br>
                            Daily execution window triggers automatically at 08:00 AM IST.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🏖️ Pause Bookings (Vacation Mode)"):
                        supabase.table("users").update({"is_active": False}).eq("id", row_id).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="status-card-paused">
                        <div style="font-weight: 700; color: #fbbf24; font-size: 1.1rem; margin-bottom: 6px;">
                            ⏸️ STATUS: PAUSED / EXPIRED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.94rem; line-height: 1.6;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Bookings are paused. Daily runners bypass this profile until resumed.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("▶️ Resume Autopilot"):
                        supabase.table("users").update({"is_active": True}).eq("id", row_id).execute()
                        st.rerun()
            else:
                st.info(f"No configured profile found for '{query_val}'. Register in Tab 2.")
        except Exception as e:
            st.error(f"Status query error: {e}")

# ==========================================
# TAB 2: REGISTRATION & PREFERENCES
# ==========================================
with tab_register:
    st.markdown("##### Configuration & Registration")
    st.caption("Credentials and tokens are encrypted with AES-128 before syncing to Supabase.")

    auth_choice = st.radio(
        "Authentication Protocol",
        [
            "Option A: SpaceBasic Direct Email & Password (Recommended)",
            "Option B: SpaceBasic Auth Link / Bearer Token"
        ],
        index=0
    )

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 1.2rem 0;'>", unsafe_allow_html=True)

    with st.form("autopilot_registration_form"):
        if "Option A" in auth_choice:
            st.markdown("#### 1. Identity & Credentials")
            st.markdown("""
            <div class="guide-box">
                <b>Direct Dispatch Mode:</b><br>
                Enter your SpaceBasic login email and password. The system dynamically generates fresh session tokens during daily runs—no user IDs or manual link updates required.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("Full Name", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("SpaceBasic Tenant ID", value="143").strip()

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                email_input = st.text_input("SpaceBasic Login Email", placeholder="student@example.com").strip().lower()
            with col_a2:
                secret_input = st.text_input("SpaceBasic Password", type="password", placeholder="••••••••").strip()

            spacebasic_id = None
            notification_email = None

        else:
            st.markdown("#### 1. User ID & Token Setup")
            st.markdown("""
            <div class="guide-box">
                <b>Token Retrieval Steps:</b><br>
                1. Open SpaceBasic and go to <b>Mess -> Booking</b>.<br>
                2. Right-click anywhere and select <b>Inspect</b> (or F12) -> open <b>Network</b> tab.<br>
                3. Click on <b>Tomorrow</b> on the calendar list.<br>
                4. Select <code>mealsmenu?userId=123456...</code> and copy the <code>Authorization</code> header value.<br>
                5. Your <b>User ID</b> is the number after <code>userId=</code> (e.g. <code>123456</code>).
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("Full Name", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("SpaceBasic Tenant ID", value="143").strip()

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                spacebasic_id = st.text_input(
                    "SpaceBasic User ID",
                    placeholder="123456",
                    help="Numeric ID found after userId= in network requests."
                ).strip()
            with col_b2:
                notification_email = st.text_input(
                    "Alert Email Address",
                    placeholder="student@gmail.com",
                    help="Used to alert you if your session token expires."
                ).strip().lower()

            secret_input = st.text_area(
                "SpaceBasic Authentication Link or Bearer Token",
                placeholder="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                help="Paste the full Authorization Bearer string copied from Developer Tools."
            ).strip()
            email_input = None

        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 1.4rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 2. Meal Preferences & Skip Schedule")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("Lunch Preference", ["Non Veg", "Eggetarian", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("Dinner Preference", ["Non Veg", "Eggetarian", "Veg"], index=0)

        st.caption("Select recurring days when automated bookings should be skipped:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            skips = st.multiselect(f"Skip on {day.capitalize()}", ["Breakfast", "Lunch", "Dinner"], key=f"skip_{day}")
            if skips:
                skip_config[day] = [s.lower() for s in skips]

        st.write("")
        submit = st.form_submit_button("⚡ Save & Activate Autopilot")

    if submit:
        is_direct_email = "Option A" in auth_choice

        if is_direct_email:
            if not email_input or not secret_input:
                st.error("SpaceBasic Login Email and Password are required.")
                st.stop()
        else:
            if not spacebasic_id or not secret_input or not notification_email:
                st.error("SpaceBasic User ID, Auth Token/Link, and Alert Email are required.")
                st.stop()
            if "@" not in notification_email:
                st.error("Please enter a valid alert email address.")
                st.stop()

        try:
            token_to_encrypt = secret_input
            if not is_direct_email:
                if "http://" in token_to_encrypt or "https://" in token_to_encrypt:
                    match = re.search(r"[?&](?:token|jwt|auth)=([^&#\s]+)", token_to_encrypt)
                    if match:
                        token_to_encrypt = match.group(1)
                    else:
                        token_to_encrypt = token_to_encrypt.strip()
                else:
                    token_to_encrypt = token_to_encrypt.replace("Bearer ", "").strip()

            encrypted_secret = encrypt_value(token_to_encrypt)

            record = {
                "name": name_input or "Student",
                "tenant_id": tenant_id or "143",
                "auth_type": "password" if is_direct_email else "token",
                "email": email_input if is_direct_email else None,
                "password": encrypted_secret if is_direct_email else None,
                "spacebasic_id": str(spacebasic_id).strip() if not is_direct_email else None,
                "auth_token": encrypted_secret if not is_direct_email else None,
                "notification_email": notification_email if not is_direct_email else email_input,
                "lunch_preference": lunch_pref,
                "dinner_preference": dinner_pref,
                "skip_days": skip_config,
                "is_active": True
            }

            conflict_col = "email" if is_direct_email else "spacebasic_id"
            supabase.table("users").upsert(record, on_conflict=conflict_col).execute()

            target_display = email_input if is_direct_email else f"SpaceBasic ID {spacebasic_id}"
            st.success(f"System profile registered for {target_display}! Autopilot is active.")
        except Exception as err:
            st.error(f"Synchronization failure: {err}")
