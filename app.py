import os
import streamlit as st
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="mess master• SpaceBasic Autopilot",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ADVANCED GEN-Z THEME & COMPONENT STYLES
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Ambient Aurora Dark Background */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 90% 10%, rgba(236, 72, 153, 0.12) 0%, transparent 35%),
            radial-gradient(circle at 50% 90%, rgba(139, 92, 246, 0.1) 0%, transparent 45%);
        color: #f8fafc;
    }

    /* Header styling */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: rgba(168, 85, 247, 0.1);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #d8b4fe;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.15;
        margin-bottom: 0.4rem;
        background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.8rem;
        font-weight: 400;
    }

    /* Tabs Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 5px;
        border-radius: 14px;
        backdrop-filter: blur(8px);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #64748b;
        font-weight: 600;
        padding: 8px 18px;
        border: none !important;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Bento / Form Container */
    div[data-testid="stForm"] {
        background: rgba(17, 24, 39, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 20px !important;
        padding: 1.8rem !important;
        backdrop-filter: blur(14px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    /* Clean Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease-in-out;
    }

    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
    }

    /* Status Bento Cards */
    .card-status-active {
        border-radius: 16px;
        padding: 1.2rem;
        background: radial-gradient(circle at top left, rgba(16, 185, 129, 0.12), rgba(15, 23, 42, 0.7));
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #6ee7b7;
        margin-bottom: 1.2rem;
    }

    .card-status-paused {
        border-radius: 16px;
        padding: 1.2rem;
        background: radial-gradient(circle at top left, rgba(245, 158, 11, 0.12), rgba(15, 23, 42, 0.7));
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #fcd34d;
        margin-bottom: 1.2rem;
    }

    /* Modern Glow Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.7rem 1.4rem !important;
        letter-spacing: 0.01em;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px -4px rgba(124, 58, 237, 0.5) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px -2px rgba(219, 39, 119, 0.6) !important;
        filter: brightness(1.08);
    }

    .stButton > button:active {
        transform: translateY(0px);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("🔒 Configuration Error: SUPABASE_URL and SUPABASE_KEY are missing.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# HERO HEADER
# ==========================================
st.markdown('<div class="hero-badge">⚡ Auto-Pilot • 6:00 PM Daily</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">NomNom.</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Automated SpaceBasic meal booking. Never miss dinner again.</div>', unsafe_allow_html=True)

tab_manage, tab_register = st.tabs(["✨ Status Switch", "⚙️ Preferences & Setup"])

# ==========================================
# TAB 1: PAUSE / RESUME AUTOPILOT
# ==========================================
with tab_manage:
    st.markdown("##### 🏖️ Going off-campus?")
    st.caption("Pause auto-booking instantly so you do not waste meals when you are away.")

    search_email = st.text_input(
        "Enter your registered email",
        placeholder="you@example.com",
        key="status_email_input"
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
                    <div class="card-status-active">
                        <div style="font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                            <span>●</span> {user_name} is ACTIVE
                        </div>
                        <p style="margin: 6px 0 0 0; color: #a7f3d0; font-size: 0.88rem;">
                            The bot will automatically reserve meals every evening at <b>6:00 PM IST</b>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("✈️ Heading Home (Pause Auto-Booking)"):
                        supabase.table("users").update({"is_active": False}).eq("email", search_email).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="card-status-paused">
                        <div style="font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                            <span>⏸</span> {user_name} is PAUSED
                        </div>
                        <p style="margin: 6px 0 0 0; color: #fde68a; font-size: 0.88rem;">
                            Auto-booking is currently paused. No meals will be reserved for this account.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🎒 Back on Campus (Resume Auto-Booking)"):
                        supabase.table("users").update({"is_active": True}).eq("email", search_email).execute()
                        st.rerun()
            else:
                st.info("No registered account found for this email. Switch to **Preferences & Setup** to get started.")
        except Exception as e:
            st.error(f"Error fetching account status: {e}")

# ==========================================
# TAB 2: REGISTER / UPDATE DETAILS
# ==========================================
with tab_register:
    st.markdown("##### 🛠️ Setup Credentials & Dietary Orders")
    st.caption("Passwords are encrypted with Fernet AES-128 before saving to database.")
    
    with st.form("account_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input("Your Name", placeholder="Alex Kumar")
            email_input = st.text_input("SpaceBasic Email", placeholder="student@example.com")
        with col2:
            tenant_id = st.text_input("Tenant ID", value="143")
            password_input = st.text_input(
                "SpaceBasic Password",
                placeholder="••••••••",
                type="password"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🥗 Meal Priority Hierarchy")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("Lunch Priority", ["Non Veg", "Egg", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("Dinner Priority", ["Non Veg", "Egg", "Veg"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🚫 Weekly Skip Rules")
        st.caption("Check any meals you consistently skip throughout the week:")

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
        submit = st.form_submit_button("🚀 Lock In & Activate Autopilot")

    if submit:
        if not name_input or not email_input or not password_input:
            st.error("Please enter your name, email, and SpaceBasic password.")
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
                st.success("✨ Preferences saved! Your autopilot is armed for 6:00 PM IST.")
            except Exception as err:
                st.error(f"Failed to update profile: {err}")
