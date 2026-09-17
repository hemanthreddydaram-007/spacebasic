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
    page_title="Mess Conquers • Automation Suite",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# INTERACTIVE 3D WEBGL ENGINE (THREE.JS)
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
        }
        #webgl-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 0;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <canvas id="webgl-canvas"></canvas>
    <script>
        const canvas = document.getElementById('webgl-canvas');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 24;

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // 3D Geometric Torus Knot (Floating Hub Core)
        const knotGeometry = new THREE.TorusKnotGeometry(7.5, 1.8, 120, 16);
        const knotMaterial = new THREE.MeshStandardMaterial({
            color: 0x38bdf8,
            wireframe: true,
            transparent: true,
            opacity: 0.18,
            roughness: 0.2,
            metalness: 0.8
        });
        const knotMesh = new THREE.Mesh(knotGeometry, knotMaterial);
        scene.add(knotMesh);

        // Ambient floating data nodes (Particles)
        const particleCount = 180;
        const particleGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 60;
            positions[i + 1] = (Math.random() - 0.5) * 60;
            positions[i + 2] = (Math.random() - 0.5) * 40;
        }

        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particleMaterial = new THREE.PointsMaterial({
            size: 0.35,
            color: 0x818cf8,
            transparent: true,
            opacity: 0.45
        });
        const particleCloud = new THREE.Points(particleGeometry, particleMaterial);
        scene.add(particleCloud);

        // Lighting
        const pointLight = new THREE.PointLight(0x38bdf8, 2, 80);
        pointLight.position.set(10, 15, 15);
        scene.add(pointLight);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);

        // Mouse Parallax
        let mouseX = 0, mouseY = 0;
        window.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth - 0.5) * 0.8;
            mouseY = (e.clientY / window.innerHeight - 0.5) * 0.8;
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        function animate() {
            requestAnimationFrame(animate);

            knotMesh.rotation.x += 0.0025;
            knotMesh.rotation.y += 0.004;

            particleCloud.rotation.y -= 0.0008;

            camera.position.x += (mouseX * 5 - camera.position.x) * 0.05;
            camera.position.y += (-mouseY * 5 - camera.position.y) * 0.05;
            camera.lookAt(scene.position);

            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
""", height=0)

# ==========================================
# 3D GLASSMORPHISM MODERN STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 60%),
            radial-gradient(circle at 10% 80%, rgba(99, 102, 241, 0.08) 0%, transparent 50%);
        color: #f8fafc;
    }

    .glass-header {
        position: relative;
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2.2rem 1.6rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.8),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        text-align: center;
    }

    .system-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.04em;
        margin-bottom: 0.75rem;
    }

    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
        margin-bottom: 0.35rem;
    }

    .sub-title {
        color: #94a3b8;
        font-size: 0.98rem;
        margin: 0;
    }

    div[data-testid="stForm"], .glass-panel {
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(2, 6, 23, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        font-size: 0.96rem !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
        background: rgba(2, 6, 23, 0.9) !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 10px !important;
        padding: 0.78rem 1.6rem !important;
        box-shadow: 0 10px 20px -5px rgba(2, 132, 199, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 28px -4px rgba(2, 132, 199, 0.7),
                    inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 6px;
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #94a3b8;
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.14) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }

    .info-card {
        background: rgba(2, 6, 23, 0.55);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .status-badge-active {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .status-badge-paused {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 12px;
        padding: 1.2rem;
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
    st.error("System configuration missing: Supabase credentials not found in secrets.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# HERO HEADER
# ==========================================
st.markdown("""
<div class="glass-header">
    <div class="system-badge">⚡ SPACEBASIC AUTOPILOT ENGINE</div>
    <div class="main-title">Mess Conquers</div>
    <p class="sub-title">Zero-maintenance automated meal bookings & vacation management</p>
</div>
""", unsafe_allow_html=True)

tab_status, tab_config = st.tabs(["⚡ Service Status & Vacation", "🛠️ Account Setup & Preferences"])

# ==========================================
# TAB 1: TELEMETRY & VACATION CONTROL
# ==========================================
with tab_status:
    st.markdown("##### Account Status & Telemetry")
    st.caption("Inspect your active daily booking schedule or pause autopilot during holidays.")

    lookup_choice = st.radio(
        "Account Identifier Type",
        [
            "🔑 SpaceBasic User ID (Token / Magic Link Users)",
            "✉️ Email Address (Direct Credentials Users)"
        ],
        horizontal=True
    )

    if "User ID" in lookup_choice:
        search_val = st.text_input("SpaceBasic User ID", placeholder="e.g. 123456").strip()
        field_to_query = "spacebasic_id"
    else:
        search_val = st.text_input("Login Email", placeholder="e.g. student@example.com").strip().lower()
        field_to_query = "email"

    if search_val:
        try:
            res = supabase.table("users").select("*").eq(field_to_query, search_val).execute()
            if res.data and len(res.data) > 0:
                user_rec = res.data[0]
                user_name = user_rec.get("name", "Student")
                is_active = user_rec.get("is_active", True)
                auth_type_stored = user_rec.get("auth_type", "password").upper()
                notif_email = user_rec.get("notification_email") or user_rec.get("email") or "Not configured"
                row_id = user_rec.get("id")

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="status-badge-active">
                        <div style="font-weight: 700; color: #34d399; font-size: 1.1rem; margin-bottom: 4px;">
                            ● STATUS: ACTIVE & RUNNING
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.95rem;">
                            Profile: <b>{user_name}</b> ({search_val})<br>
                            Authentication: <code>{auth_type_stored}</code><br>
                            Alert Dispatch: <code>{notif_email}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🏖️ Pause Bookings (Vacation Mode)"):
                        supabase.table("users").update({"is_active": False}).eq("id", row_id).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="status-badge-paused">
                        <div style="font-weight: 700; color: #fbbf24; font-size: 1.1rem; margin-bottom: 4px;">
                            ⏸️ STATUS: PAUSED / EXPIRED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.95rem;">
                            Profile: <b>{user_name}</b> ({search_val})<br>
                            Autopilot is currently paused. No daily bookings will be dispatched.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("▶️ Resume Autopilot"):
                        supabase.table("users").update({"is_active": True}).eq("id", row_id).execute()
                        st.rerun()
            else:
                st.info(f"No registered account found for '{search_val}'. Configure your account in Tab 2.")
        except Exception as e:
            st.error(f"Status query error: {e}")

# ==========================================
# TAB 2: PROFILE REGISTRATION & PREFERENCES
# ==========================================
with tab_config:
    st.markdown("##### Configuration & Registration")
    st.caption("Credentials and tokens are encrypted with AES-128 before syncing to Supabase.")

    login_method = st.radio(
        "Authentication Protocol",
        [
            "Option A: SpaceBasic Direct Email & Password (Recommended)",
            "Option B: SpaceBasic Auth Link / Bearer Token"
        ],
        index=0
    )

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 1.2rem 0;'>", unsafe_allow_html=True)

    with st.form("autopilot_registration_form"):
        # ===============================================
        # OPTION A: DIRECT CREDENTIALS
        # ===============================================
        if "Option A" in login_method:
            st.markdown("#### 1. Account Credentials")
            st.markdown("""
            <div class="info-card">
                <b>Direct Login Mode:</b> Enter your SpaceBasic portal email and password. The system logs in dynamically on schedule—no manual tokens or user IDs required.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("Full Name", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("Tenant ID", value="143").strip()

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                email_input = st.text_input("SpaceBasic Email", placeholder="student@example.com").strip().lower()
            with col_a2:
                secret_input = st.text_input("SpaceBasic Password", type="password", placeholder="••••••••").strip()

            spacebasic_id = None
            notification_email = None

        # ===============================================
        # OPTION B: AUTH LINK / BEARER TOKEN
        # ===============================================
        else:
            st.markdown("#### 1. User ID & Token Details")
            st.markdown("""
            <div class="info-card">
                <b>Steps to Retrieve Token & User ID:</b><br>
                1. Open SpaceBasic and navigate to <b>Mess -> Booking</b>.<br>
                2. Right-click anywhere and select <b>Inspect</b> (or F12) -> go to the <b>Network</b> tab.<br>
                3. Click on <b>Tomorrow</b> on the left calendar list.<br>
                4. Find <code>mealsmenu?userId=...</code> in the list and click it.<br>
                5. Open the <b>Headers</b> subtab, scroll down to <code>Authorization</code>, and copy the full value.<br>
                6. Your <b>SpaceBasic User ID</b> is the number after <code>userId=</code> (e.g. <code>123456</code>).
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("Full Name", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("Tenant ID", value="143").strip()

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                spacebasic_id = st.text_input("SpaceBasic User ID", placeholder="123456").strip()
            with col_b2:
                notification_email = st.text_input("Alert Email (For Expiration Warnings)", placeholder="student@gmail.com").strip().lower()

            secret_input = st.text_area(
                "SpaceBasic Authorization Token or Link",
                placeholder="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                help="Paste the full Authorization Bearer string copied from Developer Tools."
            ).strip()
            email_input = None

        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 1.4rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 2. Meal Preferences & Skip Schedule")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("Lunch Preference", ["Non Veg", "Eggetarian", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("Dinner Preference", ["Non Veg", "Eggetarian", "Veg"], index=0)

        st.caption("Select any recurring days when specific meals should be automatically skipped:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            skips = st.multiselect(f"Skip on {day.capitalize()}", ["Breakfast", "Lunch", "Dinner"], key=f"skip_{day}")
            if skips:
                skip_config[day] = [s.lower() for s in skips]

        st.write("")
        submit = st.form_submit_button("⚡ Save & Activate Autopilot")

    if submit:
        is_direct_email = "Option A" in login_method

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

            target_label = email_input if is_direct_email else f"SpaceBasic ID {spacebasic_id}"
            st.success(f"Autopilot activated for {target_label}! Daily bookings are now scheduled.")
        except Exception as err:
            st.error(f"Database synchronization error: {err}")
