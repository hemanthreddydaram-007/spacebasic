import os
import streamlit as st
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="SpaceBasic Mess Autopilot",
    page_icon="🍱",
    layout="centered"
)

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
    st.error("🔒 Configuration Error: SUPABASE_URL and SUPABASE_KEY must be configured in secrets!")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("🍱 SpaceBasic Mess Autopilot")
st.caption("Automatic Session Generation: No manual Bearer tokens or User IDs required.")

st.markdown("---")

# ==========================================
# REGISTRATION FORM
# ==========================================
with st.form("account_form"):
    st.subheader("👤 SpaceBasic Account Login")
    
    col1, col2 = st.columns(2)
    with col1:
        name_input = st.text_input("Full Name", placeholder="e.g. Alex Kumar")
        email_input = st.text_input("SpaceBasic Registered Email", placeholder="student@example.com")
    with col2:
        tenant_id = st.text_input("Tenant ID", value="143")
        password_input = st.text_input(
            "SpaceBasic Password",
            placeholder="••••••••",
            type="password",
            help="Your password is encrypted with AES-128 before saving."
        )

    st.markdown("---")
    st.subheader("🥗 Dietary Preferences")
    col_pref1, col_pref2 = st.columns(2)
    with col_pref1:
        lunch_pref = st.selectbox("Lunch Preference", ["Non Veg", "Egg", "Veg"], index=0)
    with col_pref2:
        dinner_pref = st.selectbox("Dinner Preference", ["Non Veg", "Egg", "Veg"], index=0)

    st.markdown("---")
    st.subheader("📅 Skip Days Schedule")
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

    submit = st.form_submit_button("🔒 Save Account & Enable Autopilot")

if submit:
    if not name_input or not email_input or not password_input:
        st.error("Please fill in Name, Email, and Password.")
    else:
        try:
            # Encrypt password before sending to database
            encrypted_password = encrypt_value(password_input)

            payload = {
                "name": name_input.strip(),
                "email": email_input.strip().lower(),
                "password": encrypted_password,
                "tenant_id": str(tenant_id).strip(),
                "lunch_preference": lunch_pref,
                "dinner_preference": dinner_pref,
                "skip_days": skip_config
            }

            supabase.table("users").insert(payload).execute()
            st.success("🎉 Account saved! The system will log in and book meals automatically.")
        except Exception as err:
            st.error(f"❌ Failed to save account: {err}")
