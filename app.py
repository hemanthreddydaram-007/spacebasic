import os
import streamlit as st
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SYSTEM • HUNTER QUEST LOG",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# SOLO LEVELING BLUE-SYSTEM CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    * {
        font-family: 'Rajdhani', sans-serif;
    }

    /* System Void Dimension */
    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.22) 0%, transparent 65%),
            linear-gradient(rgba(3, 7, 18, 0.95), rgba(3, 7, 18, 0.95));
        background-size: 100% 100%;
        color: #e0f2fe;
    }

    /* System Notification Window Badge */
    .system-badge {
        font-family: 'Orbitron', monospace;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid #38bdf8;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
        margin-bottom: 0.8rem;
    }

    /* Solo Leveling Blue Window Title */
    .system-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #ffffff;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.85), 0 0 30px rgba(14, 165, 233, 0.65);
        margin-bottom: 0.2rem;
    }

    .system-subtitle {
        font-family: 'Rajdhani', sans-serif;
        color: #7dd3fc;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* System Window Panel */
    div[data-testid="stForm"], .system-panel {
        background: rgba(7, 23, 48, 0.75) !important;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1.5px solid #0284c7 !important;
        border-radius: 6px !important;
        padding: 1.8rem !important;
        box-shadow: inset 0 0 25px rgba(14, 165, 233, 0.15), 0 0 35px rgba(2, 132, 199, 0.4) !important;
        position: relative;
    }

    /* Corner accents for System UI */
    div[data-testid="stForm"]::before {
        content: "[ SYSTEM QUEST: DAILY RATION ]";
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        color: #38bdf8;
        letter-spacing: 0.2em;
        position: absolute;
        top: -10px;
        left: 18px;
        background: #030712;
        padding: 0 8px;
        border-left: 2px solid #38bdf8;
        border-right: 2px solid #38bdf8;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(3, 15, 38, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 4px;
        padding: 5px;
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Orbitron', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #64748b;
        border-radius: 3px;
        border: none !important;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(14, 165, 233, 0.25) !important;
        color: #38bdf8 !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.45);
    }

    /* Inputs styled as System Param Fields */
    .stTextInput input, .stSelectbox select {
        background: rgba(3, 15, 38, 0.85) !important;
        border: 1px solid #0369a1 !important;
        border-radius: 4px !important;
        color: #e0f2fe !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em;
    }

    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.65) !important;
    }

    /* Blue System Buttons */
    .stButton>button {
        font-family: 'Orbitron', monospace !important;
        background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 4px !important;
        padding: 0.75rem 1.4rem !important;
        box-shadow: 0 0 18px rgba(14, 165, 233, 0.5) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%) !important;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.9) !important;
        transform: translateY(-1px);
    }

    /* Status Windows */
    .quest-active {
        background: rgba(6, 44, 40, 0.65);
        border: 1.5px solid #10b981;
        border-radius: 4px;
        padding: 1.2rem;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
        margin-bottom: 1.2rem;
    }

    .quest-paused {
        background: rgba(45, 20, 10, 0.65);
        border: 1.5px solid #f59e0b;
        border-radius: 4px;
        padding: 1.2rem;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.35);
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SYSTEM MALFUNCTION: Supabase credentials missing from dimension core.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# HERO SECTION & SYSTEM BANNER (SELF-CONTAINED)
# ==========================================
if os.path.exists("jinwoo.png"):
    st.image("jinwoo.png", use_container_width=True)
else:
    st.markdown("""
        <div style="
            position: relative;
            width: 100%;
            height: 180px;
            border-radius: 8px;
            border: 1.5px solid #0284c7;
            background: radial-gradient(circle at 50% 30%, rgba(14, 165, 233, 0.35) 0%, rgba(3, 7, 18, 0.95) 75%),
                        repeating-linear-gradient(0deg, rgba(56, 189, 248, 0.05) 0px, rgba(56, 189, 248, 0.05) 1px, transparent 1px, transparent 4px);
            box-shadow: 0 0 25px rgba(14, 165, 233, 0.4), inset 0 0 30px rgba(2, 132, 199, 0.25);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            margin-bottom: 1.5rem;
        ">
            <div style="
                font-family: 'Orbitron', monospace;
                font-size: 2.6rem;
                filter: drop-shadow(0 0 16px #38bdf8);
                margin-bottom: 6px;
            ">⚔️ 👁️‍🗨️ ⚔️</div>
            <div style="
                font-family: 'Orbitron', monospace;
                font-size: 1.35rem;
                font-weight: 900;
                letter-spacing: 0.35em;
                color: #ffffff;
                text-shadow: 0 0 10px #38bdf8, 0 0 22px #0284c7;
            ">SUNG JIN-WOO</div>
            <div style="
                font-family: 'Rajdhani', sans-serif;
                font-size: 0.88rem;
                font-weight: 700;
                letter-spacing: 0.25em;
                color: #7dd3fc;
                text-transform: uppercase;
                margin-top: 4px;
            ">[ SHADOW MONARCH • SYSTEM INTERFACE ]</div>
            <div style="
                position: absolute;
                bottom: 8px;
                right: 14px;
                font-family: 'Orbitron', monospace;
                font-size: 0.62rem;
                color: rgba(56, 189, 248, 0.7);
                letter-spacing: 0.15em;
            ">STATUS: AWAKENED</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="system-badge">[ SYSTEM ALERT: MISSION ACTIVE ]</div>', unsafe_allow_html=True)
st.markdown('<div class="system-title">QUEST: MESS CONQUER</div>', unsafe_allow_html=True)
st.markdown('<div class="system-subtitle">Target Execution Window: 18:00:00 IST Sharp</div>', unsafe_allow_html=True)

tab_manage, tab_register = st.tabs(["[ CURRENT HUNTER STATUS ]", "[ STAT ALLOCATION & SETUP ]"])

# ==========================================
# TAB 1: HUNTER STATUS (PAUSE / RESUME)
# ==========================================
with tab_manage:
    st.markdown("##### 📍 HUNTER IDENTIFICATION")
    st.caption("Input your SpaceBasic identifier to inspect automated reservation status.")

    search_email = st.text_input(
        "REGISTERED IDENTIFIER (EMAIL)",
        placeholder="hunter@system.com",
        key="status_email_box"
    ).strip().lower()

    if search_email:
        try:
            res = supabase.table("users").select("*").eq("email", search_email).execute()
            
            if res.data and len(res.data) > 0:
                user_record = res.data[0]
                user_name = user_record.get("name", "Hunter").upper()
                is_active = user_record.get("is_active", True)

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="quest-active">
                        <div style="font-family: 'Orbitron'; font-size: 1rem; font-weight: 700; color: #6ee7b7; letter-spacing: 0.1em;">
                            STATUS: AWAKENED • {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #a7f3d0; font-size: 0.95rem;">
                            Autopilot routine engaged. Daily ration claim will fire at <b>18:00:00 IST</b>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("REST MODE: RETURN TO SAFE ZONE (PAUSE)"):
                        supabase.table("users").update({"is_active": False}).eq("email", search_email).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="quest-paused">
                        <div style="font-family: 'Orbitron'; font-size: 1rem; font-weight: 700; color: #fcd34d; letter-spacing: 0.1em;">
                            STATUS: DORMANT • {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #fde68a; font-size: 0.95rem;">
                            Hunter is in rest mode. System execution routines will bypass this identifier.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("AWAKEN: RE-ENTER DUNGEON (RESUME AUTOPILOT)"):
                        supabase.table("users").update({"is_active": True}).eq("email", search_email).execute()
                        st.rerun()
            else:
                st.info("No registered hunter profile found with this identifier. Allocate your stats in the next tab.")
        except Exception as e:
            st.error(f"System scan error: {e}")

# ==========================================
# TAB 2: ALLOCATION & PROFILE SETUP
# ==========================================
with tab_register:
    st.markdown("##### ⚙️ HUNTER REGISTRATION & RATION RULES")
    st.caption("All raw credentials are encrypted via Fernet AES-128 before storage in database core.")
    
    with st.form("account_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input("HUNTER CODENAME", placeholder="Sung Jin-Woo")
            email_input = st.text_input("SPACEBASIC IDENTIFIER (EMAIL)", placeholder="hunter@domain.com")
        with col2:
            tenant_id = st.text_input("GATE TENANT ID", value="143")
            password_input = st.text_input(
                "DUNGEON PASSKEY (PASSWORD)",
                placeholder="••••••••",
                type="password"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🥩 RATION TYPE PRIORITY")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("LUNCH PRIORITY ORDER", ["Non Veg", "Egg", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("DINNER PRIORITY ORDER", ["Non Veg", "Egg", "Veg"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🛡️ REST DAYS (SKIP AUTO-CLAIM)")
        st.caption("Select scheduled days to bypass meal claims automatically:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            st.write(f"**{day.upper()}**")
            c1, c2, c3 = st.columns(3)
            b_skip = c1.checkbox("Skip Breakfast", key=f"{day}_b")
            l_skip = c2.checkbox("Skip Lunch", key=f"{day}_l")
            d_skip = c3.checkbox("Skip Dinner", key=f"{day}_d")
            
            day_skips_list = []
            if b_skip: day_skips_list.append("breakfast")
            if l_skip: day_skips_list.append("lunch")
            if d_skip: day_skips_list.append("dinner")
            
            if day_skips_list:
                skip_config[day] = day_skips_list

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("ACCEPT SYSTEM CONTRACT")

    if submit:
        if not name_input or not email_input or not password_input:
            st.error("Parameters incomplete: Hunter Codename, Identifier, and Dungeon Passkey required.")
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
                st.success("SYSTEM UPDATE: Hunter status synchronized. Contract locked for 18:00:00 IST execution.")
            except Exception as err:
                st.error(f"System synchronization failure: {err}")
