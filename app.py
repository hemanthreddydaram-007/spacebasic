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
    page_title="MESS CONQUERS • SPATIAL SYSTEM",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# PROCEDURAL 3D WEBGL SPATIAL ENGINE
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
            background: #020617;
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
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 28;

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Spatial 3D Icosahedron Core with Wireframe + Points
        const geoCore = new THREE.IcosahedronGeometry(9, 3);
        const matWire = new THREE.MeshStandardMaterial({
            color: 0x38bdf8,
            wireframe: true,
            transparent: true,
            opacity: 0.22,
            roughness: 0.1,
            metalness: 0.9
        });
        const meshCore = new THREE.Mesh(geoCore, matWire);
        scene.add(meshCore);

        // Core Inner Pulsing Solid
        const innerGeo = new THREE.OctahedronGeometry(4, 2);
        const innerMat = new THREE.MeshStandardMaterial({
            color: 0x6366f1,
            wireframe: true,
            transparent: true,
            opacity: 0.35
        });
        const innerCore = new THREE.Mesh(innerGeo, innerMat);
        scene.add(innerCore);

        // Ambient Volumetric Particle Ring
        const pCount = 300;
        const pGeo = new THREE.BufferGeometry();
        const coords = new Float32Array(pCount * 3);

        for(let i = 0; i < pCount * 3; i += 3) {
            const rad = 14 + Math.random() * 12;
            const theta = Math.random() * Math.PI * 2;
            const phi = (Math.random() - 0.5) * Math.PI;
            coords[i] = rad * Math.cos(theta) * Math.cos(phi);
            coords[i+1] = rad * Math.sin(phi);
            coords[i+2] = rad * Math.sin(theta) * Math.cos(phi);
        }

        pGeo.setAttribute('position', new THREE.BufferAttribute(coords, 3));
        const pMat = new THREE.PointsMaterial({
            size: 0.28,
            color: 0x38bdf8,
            transparent: true,
            opacity: 0.6
        });
        const pField = new THREE.Points(pGeo, pMat);
        scene.add(pField);

        // Dynamic 3D Spatial Lights
        const lightA = new THREE.PointLight(0x0ea5e9, 3, 50);
        lightA.position.set(12, 14, 10);
        scene.add(lightA);

        const lightB = new THREE.PointLight(0x818cf8, 2.5, 50);
        lightB.position.set(-14, -10, 8);
        scene.add(lightB);

        scene.add(new THREE.AmbientLight(0xffffff, 0.3));

        // Interactive Viewport Tracking
        let targetX = 0, targetY = 0;
        window.addEventListener('mousemove', (e) => {
            targetX = (e.clientX / window.innerWidth - 0.5) * 1.2;
            targetY = (e.clientY / window.innerHeight - 0.5) * 1.2;
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        let clock = new THREE.Clock();
        function renderLoop() {
            requestAnimationFrame(renderLoop);
            const delta = clock.getElapsedTime();

            meshCore.rotation.y = delta * 0.08;
            meshCore.rotation.x = delta * 0.05;
            innerCore.rotation.y = -delta * 0.12;

            pField.rotation.y = delta * 0.03;
            pField.rotation.z = delta * 0.02;

            camera.position.x += (targetX * 8 - camera.position.x) * 0.04;
            camera.position.y += (-targetY * 8 - camera.position.y) * 0.04;
            camera.lookAt(scene.position);

            renderer.render(scene, camera);
        }
        renderLoop();
    </script>
</body>
</html>
""", height=0)

# ==========================================
# 3D SPATIAL NEUMORPHIC GLASSCRAFT CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    .stApp {
        background-color: transparent !important;
        color: #f8fafc;
    }

    /* 3D Floating Spatial Console Header */
    .spatial-head-card {
        position: relative;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.75) 0%, rgba(30, 41, 59, 0.45) 100%);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-top: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 2.2rem 1.6rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.85),
            0 0 30px rgba(14, 165, 233, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        text-align: center;
        transform: perspective(1000px) translateZ(0);
        transition: transform 0.3s ease;
    }

    .spatial-head-card:hover {
        transform: perspective(1000px) translateZ(8px);
    }

    .core-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #38bdf8;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
        margin-bottom: 0.8rem;
    }

    .console-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        margin-bottom: 0.4rem;
    }

    .console-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 500;
        margin: 0;
    }

    /* 3D Glass Surface for Forms & Tabs */
    div[data-testid="stForm"], .spatial-surface {
        background: linear-gradient(160deg, rgba(15, 23, 42, 0.82) 0%, rgba(10, 15, 30, 0.72) 100%) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 2.2rem !important;
        box-shadow: 
            0 30px 60px -15px rgba(0, 0, 0, 0.9),
            inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    }

    /* Tactile 3D Inset Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(3, 7, 18, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 0.8rem 1.1rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stTextInput input:hover, .stTextArea textarea:hover, .stSelectbox select:hover {
        border-color: rgba(56, 189, 248, 0.4) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        background: rgba(3, 7, 18, 0.95) !important;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.8),
            0 0 0 3px rgba(56, 189, 248, 0.25) !important;
        transform: translateY(-1px);
    }

    /* 3D Elevated Solid Button */
    .stButton>button {
        position: relative;
        background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        letter-spacing: 0.02em !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-bottom: 2px solid #0369a1 !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.8rem !important;
        box-shadow: 
            0 12px 25px -4px rgba(2, 132, 199, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 18px 30px -4px rgba(2, 132, 199, 0.7),
            inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
    }

    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
    }

    /* 3D Floating Nav Segment Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 6px;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.88rem;
        font-weight: 600;
        color: #94a3b8;
        border-radius: 10px;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.18) 0%, rgba(14, 165, 233, 0.08) 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.25) !important;
    }

    /* Step Card with 3D Depth Specular Edge */
    .step-box {
        background: rgba(3, 7, 18, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 14px 0 20px 0;
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.6;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    /* Status Visual Telemetry Shields */
    .telemetry-active {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.45) 0%, rgba(6, 95, 70, 0.25) 100%);
        border: 1px solid #10b981;
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 30px -5px rgba(16, 185, 129, 0.2);
    }

    .telemetry-paused {
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.45) 0%, rgba(146, 64, 14, 0.25) 100%);
        border: 1px solid #f59e0b;
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 30px -5px rgba(245, 158, 11, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE CLIENT INITIALIZATION
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
# SPATIAL HUD BANNER
# ==========================================
st.markdown("""
<div class="spatial-head-card">
    <div class="core-pill">⚡ AUTONOMOUS MEAL SYNC ENGINE</div>
    <div class="console-title">MESS CONQUERS</div>
    <p class="console-subtitle">High-availability automated meal reservations & session vault</p>
</div>
""", unsafe_allow_html=True)

tab_telemetry, tab_register = st.tabs(["[ TELEMETRY & REST GATE ]", "[ CREDENTIAL ALLOCATION ]"])

# ==========================================
# TAB 1: TELEMETRY RADAR & VACATION MODE
# ==========================================
with tab_telemetry:
    st.markdown("##### Account Telemetry & State Control")
    st.caption("Inspect live automated booking queues or enter rest mode during vacations.")

    lookup_protocol = st.radio(
        "ACCOUNT LOOKUP PROTOCOL",
        [
            "🔑 SpaceBasic User ID (Token / Link Protocol)",
            "✉️ Direct Registered Email (Password Protocol)"
        ],
        horizontal=True
    )

    if "User ID" in lookup_protocol:
        query_val = st.text_input("SPACEBASIC USER ID", placeholder="e.g. 123456").strip()
        query_field = "spacebasic_id"
    else:
        query_val = st.text_input("REGISTERED LOGIN EMAIL", placeholder="e.g. student@example.com").strip().lower()
        query_field = "email"

    if query_val:
        try:
            record_query = supabase.table("users").select("*").eq(query_field, query_val).execute()
            if record_query.data and len(record_query.data) > 0:
                user_info = record_query.data[0]
                user_name = user_info.get("name", "Student").upper()
                is_active = user_info.get("is_active", True)
                auth_type = user_info.get("auth_type", "password").upper()
                notif_email = user_info.get("notification_email") or user_info.get("email") or "Not configured"
                row_id = user_info.get("id")

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="telemetry-active">
                        <div style="font-family: 'Space Grotesk'; font-weight: 700; color: #34d399; font-size: 1.15rem; letter-spacing: 0.04em;">
                            ● RADAR STATUS: AUTONOMOUS BOOKING ENGAGED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.95rem; margin-top: 8px; line-height: 1.6;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Auth Protocol: <code>{auth_type}</code> | Alert Receiver: <code>{notif_email}</code><br>
                            Daily execution window is active daily at 08:00 AM IST.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("⏸️ ENGAGE REST MODE (PAUSE AUTOMATION)"):
                        supabase.table("users").update({"is_active": False}).eq("id", row_id).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="telemetry-paused">
                        <div style="font-family: 'Space Grotesk'; font-weight: 700; color: #fbbf24; font-size: 1.15rem; letter-spacing: 0.04em;">
                            ⏸️ RADAR STATUS: REST GATE ACTIVE (PAUSED)
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.95rem; margin-top: 8px; line-height: 1.6;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Daily dispatch is bypassed during vacation. Resuming reactivates bookings immediately.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("⚡ DISENGAGE REST MODE (RESUME AUTOMATION)"):
                        supabase.table("users").update({"is_active": True}).eq("id", row_id).execute()
                        st.rerun()
            else:
                st.info(f"No configured profile located for '{query_val}'. Configure credentials in the allocation tab.")
        except Exception as e:
            st.error(f"Telemetry radar query failure: {e}")

# ==========================================
# TAB 2: CREDENTIAL ALLOCATION & RULES
# ==========================================
with tab_register:
    st.markdown("##### Credential Allocation & Meal Protocol")
    st.caption("Passwords and session tokens are encrypted with AES-128 before writing to database.")

    auth_choice = st.radio(
        "CHOOSE AUTHENTICATION METHOD",
        [
            "Option A: SpaceBasic Direct Email & Password (Recommended)",
            "Option B: SpaceBasic Auth Link / Bearer Token"
        ],
        index=0
    )

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 1.2rem 0;'>", unsafe_allow_html=True)

    with st.form("spatial_registration_console"):
        # OPTION A: DIRECT CREDENTIALS
        if "Option A" in auth_choice:
            st.markdown("#### 1. Identity & Credentials")
            st.markdown("""
            <div class="step-box">
                <b>Direct Dispatch Mode:</b><br>
                Enter your SpaceBasic login email and password. The system dynamically generates fresh session tokens during daily runs—no user IDs or manual link updates required.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("FULL NAME", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("SPACEBASIC TENANT ID", value="143").strip()

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                email_input = st.text_input("SPACEBASIC EMAIL", placeholder="student@example.com").strip().lower()
            with col_a2:
                secret_input = st.text_input("SPACEBASIC PASSWORD", type="password", placeholder="••••••••").strip()

            spacebasic_id = None
            notification_email = None

        # OPTION B: BEARER / MAGIC LINK
        else:
            st.markdown("#### 1. User ID & Token Setup")
            st.markdown("""
            <div class="step-box">
                <b>Token Retrieval Protocol:</b><br>
                1. Open SpaceBasic and go to <b>Mess -> Booking</b>.<br>
                2. Right-click anywhere and select <b>Inspect</b> (or F12) -> open <b>Network</b> tab.<br>
                3. Click on <b>Tomorrow</b> on the calendar list.<br>
                4. Select <code>mealsmenu?userId=123456...</code> and copy the <code>Authorization</code> header value.<br>
                5. Your <b>User ID</b> is the number after <code>userId=</code> (e.g. <code>123456</code>).
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input("FULL NAME", placeholder="Your Name").strip()
            with col2:
                tenant_id = st.text_input("SPACEBASIC TENANT ID", value="143").strip()

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                spacebasic_id = st.text_input(
                    "SPACEBASIC USER ID",
                    placeholder="123456",
                    help="Numeric ID found in your portal URL or network requests."
                ).strip()
            with col_b2:
                notification_email = st.text_input(
                    "ALERT EMAIL ADDRESS",
                    placeholder="student@gmail.com",
                    help="Used to alert you if your session token expires."
                ).strip().lower()

            secret_input = st.text_area(
                "SPACEBASIC AUTHENTICATION LINK OR BEARER TOKEN",
                placeholder="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                help="Paste the full Authorization Bearer string copied from Developer Tools."
            ).strip()
            email_input = None

        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 1.4rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 2. Meal Preferences & Skip Routine")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("LUNCH PREFERENCE", ["Non Veg", "Eggetarian", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("DINNER PREFERENCE", ["Non Veg", "Eggetarian", "Veg"], index=0)

        st.caption("Select recurring days when automated bookings should be skipped:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            skips = st.multiselect(f"Skip on {day.capitalize()}", ["Breakfast", "Lunch", "Dinner"], key=f"skip_{day}")
            if skips:
                skip_config[day] = [s.lower() for s in skips]

        st.write("")
        submit = st.form_submit_button("💠 LOCK CREDENTIALS & INITIALIZE AUTOPILOT")

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
            st.success(f"System profile locked for {target_display}! Autonomous sync is now scheduled.")
        except Exception as err:
            st.error(f"Synchronization failure: {err}")
