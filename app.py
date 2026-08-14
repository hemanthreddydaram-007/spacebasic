import os
import streamlit as st
from supabase import create_client, Client
from security import encrypt_token

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
# HEADER & TUTORIAL SECTION
# ==========================================
st.title("🍱 SpaceBasic Mess Autopilot")
st.caption("Configure your automated daily mess RSVP preferences securely.")

with st.expander("📹 How to get your Token & User ID (Video Guide & Steps)", expanded=False):
    st.markdown("""
    **Follow these simple steps:**
    1. Log into SpaceBasic in your browser (Chrome/Edge).
    2. Press `F12` or Right Click $\\rightarrow$ **Inspect** $\\rightarrow$ Go to the **Network** tab.
    3. Click on any meal or refresh the mess menu page.
    4. Click on the `mealsmenu` request.
    5. Under **Request Headers**, copy the full `Authorization` value (starts with `Bearer eyJ...`).
    6. Under the URL query parameters, find your `userId` (e.g. `380170`).
    """)
    # If you have a video link/file, replace the URL below:
    # st.video("https://www.youtube.com/watch?v=YOUR_VIDEO_ID")

st.markdown("---")

# ==========================================
# FRESH USER REGISTRATION / UPDATE FORM
# ==========================================
with st.form("fresh_user_form"):
    st.subheader("👤 Account Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="e.g. Hemanth Reddy")
        user_id = st.text_input("SpaceBasic User ID", placeholder="e.g. 380170")
    with col2:
        tenant_id = st.text_input("Tenant ID", value="143")

    token_input = st.text_input(
        "Authorization Token (Bearer Token)",
        placeholder="Bearer eyJhbGciOiJIUzI1Ni...",
        help="Paste your active SpaceBasic Bearer token copied from DevTools headers.",
        type="password"
    )

    st.markdown("---")
    st.subheader("🥗 Dietary Preferences")
    col_pref1, col_pref2 = st.columns(2)
    
    with col_pref1:
        lunch_pref = st.selectbox("Lunch Preference Chain", ["Non Veg", "Egg", "Veg"], index=0)
    with col_pref2:
        dinner_pref = st.selectbox("Dinner Preference Chain", ["Non Veg", "Egg", "Veg"], index=0)

    st.markdown("---")
    st.subheader("📅 Skip Days Schedule")
    st.caption("Select meals or full days you want the autopilot to skip automatically.")

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    skip_config = {}
    for day in days:
        st.write(f"**{day.capitalize()}**")
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

    submit = st.form_submit_button("🔒 Save Preferences & Encrypt Token")

if submit:
    if not name or not user_id or not token_input:
        st.error("Please fill in all required fields (Name, User ID, and Authorization Token).")
    else:
        try:
            # Encrypt raw input token before saving to database
            encrypted_token_str = encrypt_token(token_input)

            payload = {
                "name": name.strip(),
                "user_id": str(user_id).strip(),
                "tenant_id": str(tenant_id).strip(),
                "token": encrypted_token_str,
                "lunch_preference": lunch_pref,
                "dinner_preference": dinner_pref,
                "skip_days": skip_config
            }

            supabase.table("users").upsert(payload, on_conflict="user_id").execute()
            st.success("🎉 Preferences saved securely with encrypted token protection!")
        except Exception as err:
            st.error(f"❌ Failed to save preferences to database: {err}")
