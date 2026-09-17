import os
import re
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# SYSTEM CORE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mess Conquers • Automation Hub",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# MODERN HIGH-CONTRAST DARK UI STYLES
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #080c15 !important;
        color: #f8fafc !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Container Card Layout */
    div[data-testid="stForm"], .panel-box {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    }

    /* Input Field Styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #020617 !important;
        border: 1px solid #334155 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    }

    /* Primary Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 0.8rem 1.6rem !important;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.35) !important;
        width: 100%;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(2, 132, 199, 0.5) !important;
    }

    /* Clean Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 6px;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #94a3b8;
        border-radius: 8px;
        padding: 8px 16px;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .guide-box {
        background: #020617;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .status-card-active {
        background: rgba(6, 78, 59, 0.5);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .status-card-paused {
        background: rgba(120, 53, 15, 0.5);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INTERACTIVE 3D COMPONENT (THREE.JS HERO)
# ==========================================
components.html("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: transparent;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        }

        .hero-3d-stage {
            position: relative;
            width: 100%;
            height: 250px;
            background: radial-gradient(circle at center, #1e293b 0%, #0b0f19 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 20px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        }

        #canvas3d {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        .hero-overlay {
            position: relative;
            z-index: 2;
            text-align: center;
            pointer-events: none;
            padding: 0 20px;
        }

        .badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: #38bdf8;
            margin-bottom: 0.5rem;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            text-shadow: 0 4px 20px rgba(0,0,0,0.8);
            letter-spacing: -0.02em;
        }

        .hero-sub {
            color: #94a3b8;
            font-size: 0.92rem;
            margin-top: 6px;
            font-weight: 500;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div class="hero-3d-stage">
        <canvas id="canvas3d"></canvas>
        <div class="hero-overlay">
            <div class="badge-pill">⚡ AUTONOMOUS ENGINE</div>
            <h1 class="hero-title">Mess Conquers</h1>
            <p class="hero-sub">Autonomous SpaceBasic meal bookings & scheduling autopilot</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas3d');
        const container = canvas.parentElement;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
        camera.position.z = 18;

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // 3D Gyroscope Group
        const gyroGroup = new THREE.Group();
        scene.add(gyroGroup);

        // Ring 1 (Outer)
        const ring1Geo = new THREE.TorusGeometry(6.5, 0.12, 16, 100);
        const ring1Mat = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.8, roughness: 0.2 });
        const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
        gyroGroup.add(ring1);

        // Ring 2 (Middle)
        const ring2Geo = new THREE.TorusGeometry(5.2, 0.14, 16, 100);
        const ring2Mat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.9, roughness: 0.15 });
        const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
        gyroGroup.add(ring2);

        // Core Glowing Crystal (Center)
        const coreGeo = new THREE.OctahedronGeometry(2.4, 0);
        const coreMat = new THREE.MeshStandardMaterial({
            color: 0x0ea5e9,
            metalness: 0.2,
            roughness: 0.1,
            wireframe: true
        });
        const core = new THREE.Mesh(coreGeo, coreMat);
        gyroGroup.add(core);

        // Ambient Lighting
        const lightPrimary = new THREE.PointLight(0x38bdf8, 3, 30);
        lightPrimary.position.set(6, 6, 8);
        scene.add(lightPrimary);

        const lightSecondary = new THREE.PointLight(0x6366f1, 2, 30);
        lightSecondary.position.set(-6, -6, 6);
        scene.add(lightSecondary);

        scene.add(new THREE.AmbientLight(0xffffff, 0.4));

        // Cursor Reactive Tracking
        let mouseX = 0, mouseY = 0;
        window.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = ((e.clientX - rect.left) / container.clientWidth - 0.5) * 2;
            mouseY = -((e.clientY - rect.top) / container.clientHeight - 0.5) * 2;
        });

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });

        function animate() {
            requestAnimationFrame(animate);

            ring1.rotation.x += 0.008;
            ring1.rotation.y += 0.005;

            ring2.rotation.y += 0.012;
            ring2.rotation.z += 0.007;

            core.rotation.x -= 0.015;
            core.rotation.y -= 0.015;

            gyroGroup.rotation.y += (mouseX * 0.8 - gyroGroup.rotation.y) * 0.08;
            gyroGroup.rotation.x += (mouseY * 0.8 - gyroGroup.rotation.x) * 0.08;

            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
""", height=270)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("System configuration error: Supabase credentials not found in secrets.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

tab_telemetry, tab_register = st.tabs(["⚡ Service Status & Vacation", "🛠️ Account Setup & Credentials"])

# ==========================================
# TAB 1: STATUS & CONTROLS
# ==========================================
with tab_telemetry:
    st.markdown("##### Account Status & Controls")
    st.caption("Inspect your active daily schedule or pause automation when leaving campus.")

    lookup_protocol = st.radio(
        "Identifier Protocol",
        [
            "🔑 SpaceBasic User ID (Token / Magic Link Users)",
            "✉️ Direct Login Email (Password Users)"
        ],
        horizontal=True
    )

    if "User ID" in lookup_protocol:
        query_val = st.text_input("SpaceBasic User ID", placeholder="e.g. 123456").strip()
        query_field = "spacebasic_id"
    else:
        query_val = st.text_input("Login Email", placeholder="e.g. student@example.com").strip().lower()
        query_field = "email"

    if query_val:
        try:
            record_query = supabase.table("users").select("*").eq(query_field, query_val).execute()
            if record_query.data and len(record_query.data) > 0:
                user_info = record_query.data[0]
                user_name = user_info.get("name", "Student")
                is_active = user_info.get("is_active", True)
                auth_type = user_info.get("auth_type", "password").upper()
                notif_email = user_info.get("notification_email") or user_info.get("email") or "Not configured"
                row_id = user_info.get("id")

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="status-card-active">
                        <div style="font-weight: 700; color: #34d399; font-size: 1.05rem; margin-bottom: 6px;">
                            ● STATUS: ACTIVE & SCHEDULED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.94rem; line-height: 1.6;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Protocol: <code>{auth_type}</code> | Alert Receiver: <code>{notif_email}</code><br>
                            Daily execution window triggers automatically at 08:00 AM IST.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🏖️ Pause Bookings (Vacation Mode)"):
                        supabase.table("users").update({"is_active": False}).eq("id", row_id).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="status-card-paused">
                        <div style="font-weight: 700; color: #fbbf24; font-size: 1.05rem; margin-bottom: 6px;">
                            ⏸️ STATUS: PAUSED / EXPIRED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.94rem; line-height: 1.6;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Bookings are paused. Daily runners bypass this profile until resumed.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("▶️ Resume Autopilot"):
                        supabase.table("users").update({"is_active": True}).eq("id", row_id).execute()
                        st.rerun()
            else:
                st.info(f"No configured profile found for '{query_val}'. Register in Tab 2.")
        except Exception as e:
            st.error(f"Status query error: {e}")

# ==========================================
# TAB 2: REGISTRATION & PREFERENCES
# ==========================================
with tab_register:
    st.markdown("##### Configuration & Registration")
    st.caption("Credentials and tokens are encrypted with AES-128 before syncing to Supabase.")

    auth_choice = st.radio(
        "Authentication Protocol",
        [
            "Option A: SpaceBasic Direct Email & Password (Recommended)",
            "Option B: SpaceBasic Auth Link / Bearer Token"
        ],
        index=0
    )

    st.markdown("<hr style='border: 0.5px solid #1e293b; margin: 1.2rem 0;'>", unsafe_allow_html=True)

    with st.form("autopilot_registration_form"):
        if "Option A" in auth_choice:
            st.markdown("#### 1. Identity & Credentials")
            st.markdown("""
            <div class="guide-box">
                <b>Direct Dispatch Mode:</b><br>
                Enter your SpaceBasic login email and password. The system dynamically generates fresh session tokens during daily runs—no user IDs or manual link updates required.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("Full Name", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("SpaceBasic Tenant ID", value="143").strip()

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                email_input = st.text_input("SpaceBasic Login Email", placeholder="student@example.com").strip().lower()
            with col_a2:
                secret_input = st.text_input("SpaceBasic Password", type="password", placeholder="••••••••").strip()

            spacebasic_id = None
            notification_email = None

        else:
            st.markdown("#### 1. User ID & Token Setup")
            st.markdown("""
            <div class="guide-box">
                <b>Token Retrieval Steps:</b><br>
                1. Open SpaceBasic and go to <b>Mess -> Booking</b>.<br>
                2. Right-click anywhere and select <b>Inspect</b> (or F12) -> open <b>Network</b> tab.<br>
                3. Click on <b>Tomorrow</b> on the calendar list.<br>
                4. Select <code>mealsmenu?userId=123456...</code> and copy the <code>Authorization</code> header value.<br>
                5. Your <b>User ID</b> is the number after <code>userId=</code> (e.g. <code>123456</code>).
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("Full Name", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("SpaceBasic Tenant ID", value="143").strip()

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                spacebasic_id = st.text_input(
                    "SpaceBasic User ID",
                    placeholder="123456",
                    help="Numeric ID found after userId= in network requests."
                ).strip()
            with col_b2:
                notification_email = st.text_input(
                    "Alert Email Address",
                    placeholder="student@gmail.com",
                    help="Used to alert you if your session token expires."
                ).strip().lower()

            secret_input = st.text_area(
                "SpaceBasic Authentication Link or Bearer Token",
                placeholder="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                help="Paste the full Authorization Bearer string copied from Developer Tools."
            ).strip()
            email_input = None

        st.markdown("<hr style='border: 0.5px solid #1e293b; margin: 1.4rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 2. Meal Preferences & Skip Schedule")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("Lunch Preference", ["Non Veg", "Eggetarian", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("Dinner Preference", ["Non Veg", "Eggetarian", "Veg"], index=0)

        st.caption("Select recurring days when automated bookings should be skipped:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            skips = st.multiselect(f"Skip on {day.capitalize()}", ["Breakfast", "Lunch", "Dinner"], key=f"skip_{day}")
            if skips:
                skip_config[day] = [s.lower() for s in skips]

        st.write("")
        submit = st.form_submit_button("⚡ Save & Activate Autopilot")

    if submit:
        is_direct_email = "Option A" in auth_choice

        if is_direct_email:
            if not email_input or not secret_input:
                st.error("SpaceBasic Login Email and Password are required.")
                st.stop()
        else:
            if not spacebasic_id or not secret_input or not notification_email:
                st.error("SpaceBasic User ID, Auth Token/Link, and Alert Email are required.")
                st.stop()
            if "@" not in notification_email:
                st.error("Please enter a valid alert email address.")
                st.stop()

        try:
            token_to_encrypt = secret_input
            if not is_direct_email:
                if "http://" in token_to_encrypt or "https://" in token_to_encrypt:
                    match = re.search(r"[?&](?:token|jwt|auth)=([^&#\s]+)", token_to_encrypt)
                    if match:
                        token_to_encrypt = match.group(1)
                    else:
                        token_to_encrypt = token_to_encrypt.strip()
                else:
                    token_to_encrypt = token_to_encrypt.replace("Bearer ", "").strip()

            encrypted_secret = encrypt_value(token_to_encrypt)

            record = {
                "name": name_input or "Student",
                "tenant_id": tenant_id or "143",
                "auth_type": "password" if is_direct_email else "token",
                "email": email_input if is_direct_email else None,
                "password": encrypted_secret if is_direct_email else None,
                "spacebasic_id": str(spacebasic_id).strip() if not is_direct_email else None,
                "auth_token": encrypted_secret if not is_direct_email else None,
                "notification_email": notification_email if not is_direct_email else email_input,
                "lunch_preference": lunch_pref,
                "dinner_preference": dinner_pref,
                "skip_days": skip_config,
                "is_active": True
            }

            conflict_col = "email" if is_direct_email else "spacebasic_id"
            supabase.table("users").upsert(record, on_conflict=conflict_col).execute()

            target_display = email_input if is_direct_email else f"SpaceBasic ID {spacebasic_id}"
            st.success(f"System profile registered for {target_display}! Autopilot is active.")
        except Exception as err:
            st.error(f"Synchronization failure: {err}")
