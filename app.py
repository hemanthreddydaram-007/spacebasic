import os
import streamlit as st
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mess Conquers • SpaceBasic Autopilot",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ANIMATED CYBER-NEON CSS ENGINE
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Ambient Animated Mesh Background */
    .stApp {
        background-color: #06070c;
        background-image: 
            radial-gradient(at 10% 20%, rgba(124, 58, 237, 0.22) 0px, transparent 40%),
            radial-gradient(at 90% 15%, rgba(236, 72, 153, 0.2) 0px, transparent 40%),
            radial-gradient(at 50% 85%, rgba(14, 165, 233, 0.18) 0px, transparent 50%);
        background-attachment: fixed;
        color: #f8fafc;
    }

    /* Animated Aurora Hero Badge */
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 15px rgba(168, 85, 247, 0.35); transform: scale(1); }
        50% { box-shadow: 0 0 25px rgba(236, 72, 153, 0.55); transform: scale(1.02); }
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #e9d5ff;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 12px;
        backdrop-filter: blur(12px);
        animation: pulseGlow 4s infinite ease-in-out;
    }

    /* Shimmering Brand Title */
    @keyframes titleGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: 6px;
        background: linear-gradient(90deg, #ffffff, #c084fc, #38bdf8, #f472b6, #ffffff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGradient 8s ease infinite;
    }

    /* Glass Container with Floating Entry */
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stForm"], .glass-card {
        background: rgba(15, 18, 30, 0.6) !important;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 1.8rem !important;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.6);
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Tabs Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        border: none !important;
        transition: all 0.25s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox select {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 12px 14px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTextInput input:focus {
        border-color: #c084fc !important;
        box-shadow: 0 0 0 4px rgba(192, 132, 252, 0.25) !important;
        transform: translateY(-1px);
    }

    /* Vibrant Buttons with Animated Glow */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%) !important;
        background-size: 200% 200%;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.4rem !important;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 8px 24px -4px rgba(168, 85, 247, 0.5) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 14px 30px -4px rgba(236, 72, 153, 0.65) !important;
        filter: brightness(1.1);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    /* Live Animated Radar Dot */
    @keyframes radarPing {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.4); opacity: 0; }
        100% { transform: scale(0.95); opacity: 0; }
    }

    .radar-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        position: relative;
    }

    .radar-dot::after {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 50%;
        border: 2px solid inherit;
        animation: radarPing 1.8s cubic-bezier(0, 0.2, 0.8, 1) infinite;
    }

    .dot-green { background: #10b981; }
    .dot-green::after { border-color: #10b981; }
    .dot-amber { background: #f59e0b; }
    .dot-amber::after { border-color: #f59e0b; }

    /* Custom Live Status Cards */
    .status-card-active {
        padding: 1.2rem 1.4rem;
        background: radial-gradient(circle at top left, rgba(16, 185, 129, 0.16), rgba(15, 23, 42, 0.6));
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 16px;
        color: #6ee7b7;
        margin-bottom: 1.2rem;
        animation: slideUpFade 0.5s ease;
    }

    .status-card-paused {
        padding: 1.2rem 1.4rem;
        background: radial-gradient(circle at top left, rgba(245, 158, 11, 0.16), rgba(15, 23, 42, 0.6));
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 16px;
        color: #fcd34d;
        margin-bottom: 1.2rem;
        animation: slideUpFade 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("🔒 Security Config Missing: SUPABASE_URL and SUPABASE_KEY must be set in secrets!")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# HERO SECTION
# ==========================================
st.markdown('<div class="hero-badge">⚔️ SpaceBasic Autopilot • 6:00 PM Daily</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-title">Mess Conquers.</div>', unsafe_allow_html=True)
st.markdown('<p style="color: #94a3b8; margin-bottom: 2rem; font-size: 0.98rem;">Automate dinner, conquer mornings. Zero missed bookings on campus.</p>', unsafe_allow_html=True)

tab_manage, tab_register = st.tabs(["⚡ Fast Switch & Status", "🛡️ Setup & Dietary Preferences"])

# ==========================================
# TAB 1: PAUSE / RESUME AUTOPILOT
# ==========================================
with tab_manage:
    st.markdown("#### ✈️ Vacation Toggle")
    st.caption("Heading home or skipping hostel food? Pause auto-booking with a single tap.")

    search_email = st.text_input(
        "Registered SpaceBasic Email",
        placeholder="student@example.com",
        key="status_email_box"
    ).strip().lower()

    if search_email:
        try:
            res = supabase.table("users").select("*").eq("email", search_email).execute()
            
            if res.data and len(res.data) > 0:
                user_record = res.data[0]
                user_name = user_record.get("name", "Student")
                is_active = user_record.get("is_active", True)

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="status-card-active">
                        <div style="font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                            <span class="radar-dot dot-green"></span> {user_name} is ON AUTOPILOT
                        </div>
                        <p style="margin: 6px 0 0 0; color: #a7f3d0; font-size: 0.9rem;">
                            Your meals will be booked automatically every day at <b>6:00:00 PM IST</b>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🏖️ Heading Home (Pause Auto-Booking)"):
                        supabase.table("users").update({"is_active": False}).eq("email", search_email).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="status-card-paused">
                        <div style="font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                            <span class="radar-dot dot-amber"></span> {user_name} is PAUSED
                        </div>
                        <p style="margin: 6px 0 0 0; color: #fde68a; font-size: 0.9rem;">
                            Auto-booking is paused. The daily runner will bypass this account.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🎒 Back on Campus (Resume Auto-Booking)"):
                        supabase.table("users").update({"is_active": True}).eq("email", search_email).execute()
                        st.rerun()
            else:
                st.info("No profile registered under this email. Switch to **Setup** tab to register.")
        except Exception as e:
            st.error(f"Error fetching account status: {e}")

# ==========================================
# TAB 2: REGISTER / UPDATE DETAILS
# ==========================================
with tab_register:
    st.markdown("#### ⚙️ Profile & Food Order Priority")
    st.caption("Credentials are encrypted with Fernet AES-128 before syncing to Supabase.")
    
    with st.form("account_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input("Full Name", placeholder="Alex Kumar")
            email_input = st.text_input("SpaceBasic Email", placeholder="student@example.com")
        with col2:
            tenant_id = st.text_input("Tenant ID", value="143")
            password_input = st.text_input(
                "SpaceBasic Password",
                placeholder="••••••••",
                type="password"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🍱 Meal Preference Fallback")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("Lunch Hierarchy", ["Non Veg", "Egg", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("Dinner Hierarchy", ["Non Veg", "Egg", "Veg"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🚫 Scheduled Weekly Skips")
        st.caption("Select meals you want the autopilot to skip automatically:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            st.write(f"**{day.capitalize()}**")
            c1, c2, c3 = st.columns(3)
            b_skip = c1.checkbox("Breakfast", key=f"{day}_b")
            l_skip = c2.checkbox("Lunch", key=f"{day}_l")
            d_skip = c3.checkbox("Dinner", key=f"{day}_d")
            
            day_skips_list = []
            if b_skip: day_skips_list.append("breakfast")
            if l_skip: day_skips_list.append("lunch")
            if d_skip: day_skips_list.append("dinner")
            
            if day_skips_list:
                skip_config[day] = day_skips_list

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("⚔️ Arm Mess Conquers")

    if submit:
        if not name_input or not email_input or not password_input:
            st.error("Please enter your Name, Email, and Password.")
        else:
            try:
                encrypted_password = encrypt_value(password_input)

                payload = {
                    "name": name_input.strip(),
                    "email": email_input.strip().lower(),
                    "password": encrypted_password,
                    "tenant_id": str(tenant_id).strip(),
                    "lunch_preference": lunch_pref,
                    "dinner_preference": dinner_pref,
                    "skip_days": skip_config,
                    "is_active": True
                }

                supabase.table("users").upsert(payload, on_conflict="email").execute()
                st.success("⚔️ Profile locked in! Mess Conquers is active for 6:00 PM IST.")
            except Exception as err:
                st.error(f"Failed to sync credentials: {err}")
