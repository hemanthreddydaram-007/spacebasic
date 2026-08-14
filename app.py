import os
import streamlit as st
from supabase import create_client, Client
from security import encrypt_token, decrypt_token

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="SpaceBasic Mess Autopilot",
    page_icon="🍱",
    layout="centered"
)

# Dark Glassmorphism CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("🔒 Security Config Missing: SUPABASE_URL and SUPABASE_KEY must be set in Secrets!")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# HEADER SECTION
# ==========================================
st.title("🍱 SpaceBasic Mess Autopilot")
st.caption("Configure your automated daily mess RSVP preferences securely.")

# ==========================================
# USER IDENTIFICATION (NO PUBLIC LIST)
# ==========================================
st.subheader("👤 User Authentication")

col_search1, col_search2 = st.columns([3, 1])
with col_search1:
    entered_user_id = st.text_input(
        "Enter your SpaceBasic User ID",
        value=st.session_state.get("current_user_id", ""),
        placeholder="e.g. 380170",
        help="Enter your User ID to load existing preferences or register freshly."
    ).strip()

with col_search2:
    st.write("") # Spacer
    st.write("")
    lookup_clicked = st.button("🔍 Load Account")

# Fetch specific user data only if User ID is entered
selected_user_data = {}
if entered_user_id:
    st.session_state["current_user_id"] = entered_user_id
    try:
        res = supabase.table("users").select("*").eq("user_id", entered_user_id).execute()
        if res.data and len(res.data) > 0:
            selected_user_data = res.data[0]
            st.info(f"👋 Welcome back, **{selected_user_data.get('name', 'User')}**! Your saved preferences have been loaded.")
        else:
            st.info("✨ New User ID detected. Fill in the form below to register freshly.")
    except Exception as e:
        st.error(f"Error fetching account data: {e}")

st.markdown("---")

# ==========================================
# PREFERENCES & CONFIGURATION FORM
# ==========================================
with st.form("user_config_form"):
    st.subheader("⚙️ Account & Booking Details")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Your Full Name", 
            value=selected_user_data.get("name", ""),
            placeholder="e.g. John Doe"
        )
        user_id_final = st.text_input(
            "User ID", 
            value=entered_user_id, 
            disabled=bool(entered_user_id), 
            help="Locked to the User ID entered above."
        )
    with col2:
        tenant_id = st.text_input(
            "Tenant ID", 
            value=selected_user_data.get("tenant_id", "143")
        )

    raw_token_val = selected_user_data.get("token", "")
    display_token = decrypt_token(raw_token_val) if raw_token_val else ""
    
    token_input = st.text_input(
        "Authorization Token (Bearer Token)",
        value=display_token,
        help="Paste your active SpaceBasic Bearer token copied from DevTools headers.",
        type="password",
        placeholder="Paste Bearer token here..."
    )

    st.markdown("---")
    st.subheader("🥗 Dietary Preferences")
    col_pref1, col_pref2 = st.columns(2)
    
    with col_pref1:
        saved_lunch = selected_user_data.get("lunch_preference", "Non Veg")
        lunch_index = ["Non Veg", "Egg", "Veg"].index(saved_lunch) if saved_lunch in ["Non Veg", "Egg", "Veg"] else 0
        lunch_pref = st.selectbox("Lunch Preference Chain", ["Non Veg", "Egg", "Veg"], index=lunch_index)
        
    with col_pref2:
        saved_dinner = selected_user_data.get("dinner_preference", "Non Veg")
        dinner_index = ["Non Veg", "Egg", "Veg"].index(saved_dinner) if saved_dinner in ["Non Veg", "Egg", "Veg"] else 0
        dinner_pref = st.selectbox("Dinner Preference Chain", ["Non Veg", "Egg", "Veg"], index=dinner_index)

    st.markdown("---")
    st.subheader("📅 Skip Days Schedule")
    st.caption("Select meals or full days you want the autopilot to skip automatically.")

    saved_skips = selected_user_data.get("skip_days", {})
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    skip_config = {}
    for day in days:
        existing_day_skips = saved_skips.get(day, [])
        if existing_day_skips is True:
            existing_day_skips = ["breakfast", "lunch", "dinner"]
        elif not isinstance(existing_day_skips, list):
            existing_day_skips = []

        st.write(f"**{day.capitalize()}**")
        c1, c2, c3 = st.columns(3)
        b_skip = c1.checkbox("Skip Breakfast", value="breakfast" in [x.lower() for x in existing_day_skips], key=f"{day}_b")
        l_skip = c2.checkbox("Skip Lunch", value="lunch" in [x.lower() for x in existing_day_skips], key=f"{day}_l")
        d_skip = c3.checkbox("Skip Dinner", value="dinner" in [x.lower() for x in existing_day_skips], key=f"{day}_d")
        
        day_skips_list = []
        if b_skip: day_skips_list.append("breakfast")
        if l_skip: day_skips_list.append("lunch")
        if d_skip: day_skips_list.append("dinner")
        
        if day_skips_list:
            skip_config[day] = day_skips_list

    submit = st.form_submit_button("🔒 Save Preferences & Encrypt Token")

if submit:
    effective_user_id = entered_user_id or user_id_final
    if not name or not effective_user_id or not token_input:
        st.error("Please provide your User ID, Name, and Authorization Token before saving.")
    else:
        try:
            # Encrypt raw input token before writing to Supabase
            encrypted_token_str = encrypt_token(token_input)

            payload = {
                "name": name.strip(),
                "user_id": str(effective_user_id).strip(),
                "tenant_id": str(tenant_id).strip(),
                "token": encrypted_token_str,
                "lunch_preference": lunch_pref,
                "dinner_preference": dinner_pref,
                "skip_days": skip_config
            }

            supabase.table("users").upsert(payload, on_conflict="user_id").execute()
            st.success("🎉 Preferences saved securely with encrypted token protection!")
            st.rerun()
        except Exception as err:
            st.error(f"❌ Failed to save preferences to database: {err}")
