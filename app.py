import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpaceBasic Mess Automator",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 720px;
    }
    
    /* Header card styling */
    .header-card {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .header-title {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 0px;
    }
    
    /* Day card styling for skip rules */
    .day-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }

    /* Primary Button Custom Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- SUPABASE INITIALIZATION ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- HEADER SECTION ---
st.markdown("""
    <div class="header-card">
        <div class="header-title">🍱 Mess Automator Dashboard</div>
        <div class="header-subtitle">Autopilot mess RSVPs and custom weekly schedule manager</div>
    </div>
""", unsafe_allow_html=True)

# --- SECTION 1: ACCOUNT CREDENTIALS ---
st.subheader("🔑 Account Credentials")

with st.expander("📺 Video Tutorial: How to find User ID & Token", expanded=False):
    st.write("Follow this quick screencast to copy your credentials from DevTools (`F12`):")
    st.video("Screen Recording 2026-08-08 151423.mp4")

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Your Name", placeholder="e.g. Hemanth")
with col2:
    user_id = st.text_input("SpaceBasic User ID", placeholder="e.g. 380170")

bearer_token = st.text_input(
    "SpaceBasic Authorization Token", 
    type="password", 
    placeholder="eyJhbGciOiJIUzI1NiJ9...",
    help="Paste token string with or without 'Bearer'"
)

st.divider()

# --- SECTION 2: MEAL PREFERENCES ---
st.subheader("🍽️ Preference Chain")

priority_option = st.selectbox(
    "Select preferred fallback order for Lunch & Dinner:",
    options=[
        "Non-Veg ➔ Egg ➔ Veg (Default)",
        "Egg ➔ Veg",
        "Veg Only"
    ],
    help="If your top preference is unavailable, the system fallbacks to the next choice automatically."
)

st.divider()

# --- SECTION 3: WEEKLY SKIP SCHEDULE ---
st.subheader("📅 Weekly Skip Schedule")
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
            with st.spinner("Connecting to Supabase..."):
                supabase.table("users").upsert(user_data, on_conflict="user_id").execute()
            
            st.success(f"🎉 **{user_name}** is now configured!")
            st.toast("Autopilot profile updated successfully!", icon="✅")
        except Exception as e:
            st.error(f"❌ Connection Error: {e}")
