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
    st.error("🔒 Security Config Missing: SUPABASE_URL and SUPABASE_KEY must be set in secrets!")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("🍱 SpaceBasic Mess Autopilot")
st.caption("Automatic daily meal reservations with self-service schedule controls.")

st.markdown("---")

tab_manage, tab_register = st.tabs(["🏠 Manage Status (Pause / Resume)", "👤 Register / Update Details"])

# ==========================================
# TAB 1: PAUSE / RESUME AUTOPILOT
# ==========================================
with tab_manage:
    st.subheader("Pause or Resume Auto-Booking")
    st.write("Going home or taking leave? Pause your bookings with one click.")

    search_email = st.text_input("Enter your registered SpaceBasic Email", placeholder="student@example.com").strip().lower()

    if search_email:
        try:
            res = supabase.table("users").select("*").eq("email", search_email).execute()
            
            if res.data and len(res.data) > 0:
                user_record = res.data[0]
                user_name = user_record.get("name", "Student")
                is_active = user_record.get("is_active", True)

                st.markdown("---")
                if is_active:
                    st.success(f"🟢 **Status for {user_name}: ACTIVE**\n\nThe bot will book your meals automatically every evening at 6:00 PM IST.")
                    if st.button("🏠 I am Going Home (Pause Auto-Booking)"):
                        supabase.table("users").update({"is_active": False}).eq("email", search_email).execute()
                        st.warning("⏸️ Auto-booking has been paused! The bot will skip booking your meals.")
                        st.rerun()
                else:
                    st.warning(f"⏸️ **Status for {user_name}: PAUSED**\n\nDaily automated bookings are currently turned OFF for your account.")
                    if st.button("🎒 I am Back at Campus (Resume Auto-Booking)"):
                        supabase.table("users").update({"is_active": True}).eq("email", search_email).execute()
                        st.success("🟢 Auto-booking is now ACTIVE again! Your meals will be reserved at 6:00 PM IST today.")
                        st.rerun()
            else:
                st.info("No account found with this email. Please register in the next tab.")
        except Exception as e:
            st.error(f"Error fetching account status: {e}")

# ==========================================
# TAB 2: REGISTER / UPDATE DETAILS
# ==========================================
with tab_register:
    st.subheader("Account Registration & Meal Preferences")
    
    with st.form("account_form"):
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
                help="Your password is encrypted with Fernet AES-128 before saving."
            )

        st.markdown("---")
        st.subheader("🥗 Dietary Preferences")
        col_pref1, col_pref2 = st.columns(2)
        with col_pref1:
            lunch_pref = st.selectbox("Lunch Preference", ["Non Veg", "Egg", "Veg"], index=0)
        with col_pref2:
            dinner_pref = st.selectbox("Dinner Preference", ["Non Veg", "Egg", "Veg"], index=0)

        st.markdown("---")
        st.subheader("📅 Weekly Skip Days")
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

        submit = st.form_submit_button("🔒 Save Account Details")

    if submit:
        if not name_input or not email_input or not password_input:
            st.error("Please fill in Name, Email, and Password.")
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

                # Upsert into users table based on unique email
                supabase.table("users").upsert(payload, on_conflict="email").execute()
                st.success("🎉 Account saved successfully! Auto-booking is enabled.")
            except Exception as err:
                st.error(f"❌ Failed to save account: {err}")
