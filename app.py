import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="SpaceBasic Mess Automator", page_icon="🍱", layout="centered")

# Retrieve credentials from Streamlit Secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🍱 SpaceBasic Mess Automator")
st.caption("Configure your daily mess booking autopilot once and forget it!")

# --- 1. USER LOGIN / CREDENTIALS ---
st.header("1. Account Setup")

with st.expander("🎥 How to find your User ID and Authorization Token (Video Guide)", expanded=False):
    st.write("Follow the quick step-by-step video below to grab your credentials:")
    st.video("Screen Recording 2026-08-08 151423.mp4")

user_name = st.text_input("Your Name", placeholder="e.g. Bob")
user_id = st.text_input("SpaceBasic User ID", placeholder="e.g. 123456")
bearer_token = st.text_input("SpaceBasic Authorization Token", type="password", help="Paste your Bearer token starting with 'Bearer ...'")

# --- 2. MEAL PREFERENCES ---
st.header("2. Meal Preferences")
priority_option = st.selectbox(
    "Preferred Fallback Chain for Lunch & Dinner:",
    options=[
        "Non-Veg ➔ Egg ➔ Veg (Default)",
        "Egg ➔ Veg",
        "Veg Only"
    ]
)

# --- 3. DAY-BASED CANCELLATION RULES ---
st.header("3. Day-Based Skip Rules")
st.write("Select which meals you **DO NOT** want to book every week:")

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
skip_days = {}

cols = st.columns(2)
for idx, day in enumerate(days):
    col = cols[idx % 2]
    with col:
        st.subheader(day.title())
        skip_b = st.checkbox("Skip Breakfast", key=f"{day}_b")
        skip_l = st.checkbox("Skip Lunch", key=f"{day}_l")
        skip_d = st.checkbox("Skip Dinner", key=f"{day}_d")
        
        skips = []
        if skip_b: skips.append("Breakfast")
        if skip_l: skips.append("Lunch")
        if skip_d: skips.append("Dinner")
        
        if skips:
            skip_days[day] = skips

# --- 4. SAVE CONFIGURATION TO DATABASE ---
st.divider()
if st.button("💾 Save Configuration", type="primary", use_container_width=True):
    if not user_name or not user_id or not bearer_token:
        st.error("⚠️ Please fill in your Name, User ID, and Authorization Token!")
    else:
        user_data = {
            "name": user_name,
            "user_id": user_id,
            "tenant_id": "143",
            "token": bearer_token,
            "lunch_preference": "Non Veg",
            "dinner_preference": "Non Veg",
            "skip_days": skip_days
        }
        
        try:
            supabase.table("users").upsert(user_data, on_conflict="user_id").execute()
            st.success(f"🎉 Success! {user_name} is active in the automated mess booking system!")
            st.info("🤖 Your preferences are live. The automated runner will process your meals daily.")
        except Exception as e:
            st.error(f"❌ Failed to save configuration: {e}")
