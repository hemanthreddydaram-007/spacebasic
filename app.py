import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpaceBasic Mess Automator",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MATCHED THEME CSS ---
st.markdown("""
    <style>
    /* Global App Background */
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 60%, #080a10 100%) !important;
        color: #f8fafc;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 720px;
    }
    
    /* Header Card */
    .header-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        text-align: center;
    }
    .header-title {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 1rem;
    }

    /* Video Banner Card */
    .video-highlight-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(168, 85, 247, 0.18) 100%);
        border: 1.5px solid rgba(168, 85, 247, 0.45);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.25);
    }
    .video-title {
        color: #f472b6;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    /* Streamlit Expander Match */
    div[data-testid="stExpander"] {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    /* Input Field Labels */
    .stTextInput > label, .stSelectbox > label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Input Fields (Matched with Cards) */
    div[data-baseweb="input"] {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #818cf8 !important;
        box-shadow: 0 0 12px rgba(129, 140, 248, 0.35) !important;
    }
    
    /* Select Box Styling */
    div[data-baseweb="select"] > div {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }

    /* Custom Checkbox Alignment */
    div[data-testid="stCheckbox"] {
        background: rgba(30, 41, 59, 0.4);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 6px;
    }

    /* Neon Deploy Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 6px 28px rgba(168, 85, 247, 0.6) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SUPABASE INITIALIZATION ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://YOUR_PROJECT_REF.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- HEADER SECTION ---
st.markdown("""
    <div class="header-card">
        <div class="header-title">🍱 SpaceBasic Mess Automator</div>
        <div class="header-subtitle">Set your daily mess booking preferences on autopilot</div>
    </div>
""", unsafe_allow_html=True)

# --- HIGHLIGHTED VIDEO GUIDE CONTAINER ---
st.markdown("""
    <div class="video-highlight-card">
        <div class="video-title">🎥 Video Tutorial: Get Your User ID & Token</div>
        <span style="color: #cbd5e1; font-size: 0.9rem;">
            Watch this quick guide to copy your <b>User ID</b> and <b>Bearer Token</b> from DevTools (<code>F12</code>) in 30 seconds.
        </span>
    </div>
""", unsafe_allow_html=True)

with st.expander("▶️ Watch Setup Guide Video", expanded=True):
    st.video("Screen Recording 2026-08-08 151423.mp4")

st.divider()

# --- SECTION 1: ACCOUNT CREDENTIALS ---
st.subheader("🔑 1. Account Credentials")

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Your Name", placeholder="e.g. Bob")
with col2:
    user_id = st.text_input("SpaceBasic User ID", placeholder="e.g. 123456")

bearer_token = st.text_input(
    "SpaceBasic Authorization Token", 
    type="password", 
    placeholder="Paste Bearer token here...",
    help="Paste token string starting with or without 'Bearer'"
)

st.divider()

# --- SECTION 2: MEAL PREFERENCES ---
st.subheader("🍽️ 2. Preference Chain")

priority_option = st.selectbox(
    "Preferred fallback order for Lunch & Dinner:",
    options=[
        "Non-Veg ➔ Egg ➔ Veg (Default)",
        "Egg ➔ Veg",
        "Veg Only"
    ],
    help="If your top preference is unavailable, the runner falls back automatically."
)

st.divider()

# --- SECTION 3: WEEKLY SKIP SCHEDULE ---
st.subheader("📅 3. Weekly Skip Schedule")
st.caption("Check any meals you **DO NOT** want the autopilot to book:")

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
skip_days = {}

cols = st.columns(2)
for idx, day in enumerate(days):
    col = cols[idx % 2]
    with col:
        st.markdown(f"**{day.title()}**")
        skip_b = st.checkbox("Breakfast", key=f"{day}_b")
        skip_l = st.checkbox("Lunch", key=f"{day}_l")
        skip_d = st.checkbox("Dinner", key=f"{day}_d")
        
        skips = []
        if skip_b: skips.append("Breakfast")
        if skip_l: skips.append("Lunch")
        if skip_d: skips.append("Dinner")
        
        if skips:
            skip_days[day] = skips

st.divider()

# --- SECTION 4: SAVE ACTION ---
if st.button("🚀 Deploy Autopilot Preferences", use_container_width=True):
    if not user_name or not user_id or not bearer_token:
        st.error("⚠️ Please fill in all required fields: Name, User ID, and Authorization Token!")
    else:
        clean_token = bearer_token.strip()
        if not clean_token.startswith("Bearer "):
            clean_token = f"Bearer {clean_token}"

        user_data = {
            "name": user_name.strip(),
            "user_id": str(user_id).strip(),
            "tenant_id": "143",
            "token": clean_token,
            "lunch_preference": "Non Veg",
            "dinner_preference": "Non Veg",
            "skip_days": skip_days
        }
        
        try:
            with st.spinner("Saving preferences to Supabase..."):
                supabase.table("users").upsert(user_data, on_conflict="user_id").execute()
            
            st.success(f"🎉 **{user_name}** is active in the autopilot queue!")
            st.toast("Autopilot configuration deployed successfully!", icon="✅")
        except Exception as e:
            st.error(f"❌ Supabase Connection Error: {e}")
