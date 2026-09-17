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
    page_title="MESS CONQUERS • SPATIAL 3D",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# PARENT-LEVEL 3D SPATIAL WEBGL INJECTION
# ==========================================
components.html("""
<script>
    (function() {
        const parentDoc = window.parent.document;
        
        // Prevent duplicate instances during Streamlit reruns
        if (parentDoc.getElementById('threejs-spatial-canvas')) {
            return;
        }

        // 1. Create and attach canvas to parent body
        const canvas = parentDoc.createElement('canvas');
        canvas.id = 'threejs-spatial-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '0';
        parentDoc.body.prepend(canvas);

        // 2. Load Three.js into the parent window
        function initSpatialThree() {
            const THREE = window.parent.THREE;
            if (!THREE) {
                const script = parentDoc.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                script.onload = () => build3DScene(window.parent.THREE);
                parentDoc.head.appendChild(script);
            } else {
                build3DScene(THREE);
            }
        }

        function build3DScene(THREE) {
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(55, window.parent.innerWidth / window.parent.innerHeight, 0.1, 1000);
            camera.position.z = 26;

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
            renderer.setSize(window.parent.innerWidth, window.parent.innerHeight);
            renderer.setPixelRatio(Math.min(window.parent.devicePixelRatio, 2));

            // Outer Dynamic Geometric Lattice
            const knotGeo = new THREE.TorusKnotGeometry(8, 1.9, 130, 18);
            const knotMat = new THREE.MeshStandardMaterial({
                color: 0x38bdf8,
                wireframe: true,
                transparent: true,
                opacity: 0.28,
                roughness: 0.1,
                metalness: 0.85
            });
            const knotMesh = new THREE.Mesh(knotGeo, knotMat);
            scene.add(knotMesh);

            // Floating Volumetric Particle Cloud
            const particleCount = 280;
            const particleGeo = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);

            for (let i = 0; i < particleCount * 3; i += 3) {
                positions[i] = (Math.random() - 0.5) * 55;
                positions[i + 1] = (Math.random() - 0.5) * 55;
                positions[i + 2] = (Math.random() - 0.5) * 35;
            }

            particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const particleMat = new THREE.PointsMaterial({
                size: 0.32,
                color: 0x818cf8,
                transparent: true,
                opacity: 0.5
            });
            const particleCloud = new THREE.Points(particleGeo, particleMat);
            scene.add(particleCloud);

            // 3D Spatial Point Lights
            const lightA = new THREE.PointLight(0x38bdf8, 3.2, 80);
            lightA.position.set(12, 14, 15);
            scene.add(lightA);

            const lightB = new THREE.PointLight(0x6366f1, 2.5, 80);
            lightB.position.set(-15, -12, 10);
            scene.add(lightB);

            scene.add(new THREE.AmbientLight(0xffffff, 0.45));

            // Responsive Parallax
            let mouseX = 0, mouseY = 0;
            window.parent.addEventListener('mousemove', (e) => {
                mouseX = (e.clientX / window.parent.innerWidth - 0.5) * 1.5;
                mouseY = (e.clientY / window.parent.innerHeight - 0.5) * 1.5;
            });

            window.parent.addEventListener('resize', () => {
                camera.aspect = window.parent.innerWidth / window.parent.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.parent.innerWidth, window.parent.innerHeight);
            });

            function render() {
                requestAnimationFrame(render);
                knotMesh.rotation.x += 0.003;
                knotMesh.rotation.y += 0.005;
                particleCloud.rotation.y -= 0.001;

                camera.position.x += (mouseX * 6 - camera.position.x) * 0.04;
                camera.position.y += (-mouseY * 6 - camera.position.y) * 0.04;
                camera.lookAt(scene.position);

                renderer.render(scene, camera);
            }
            render();
        }

        initSpatialThree();
    })();
</script>
""", height=0)

# ==========================================
# STREAMLIT GLASSMORPHIC OVERRIDES
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* Force background transparent so the parent 3D canvas is visible */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: transparent !important;
        background-color: transparent !important;
        color: #f8fafc !important;
    }

    /* Header Panel */
    .spatial-banner {
        position: relative;
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.28) !important;
        border-radius: 18px !important;
        padding: 2.2rem 1.6rem;
        margin-bottom: 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85),
                    0 0 25px rgba(56, 189, 248, 0.18) !important;
        text-align: center;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #38bdf8;
        margin-bottom: 0.65rem;
    }

    .title-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .sub-text {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    /* 3D Glass Surface for Form & Panels */
    div[data-testid="stForm"], .glass-box {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.24) !important;
        border-radius: 18px !important;
        padding: 2rem !important;
        box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.9) !important;
    }

    /* 3D Tactile Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(3, 7, 18, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.8),
                    0 0 0 3px rgba(56, 189, 248, 0.25) !important;
    }

    /* 3D Elevated Button */
    .stButton>button {
        background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.96rem !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-bottom: 2px solid #0369a1 !important;
        border-radius: 10px !important;
        padding: 0.8rem 1.6rem !important;
        box-shadow: 0 10px 25px -4px rgba(2, 132, 199, 0.55),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 16px 30px -4px rgba(2, 132, 199, 0.75) !important;
    }

    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 6px;
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #94a3b8;
        border-radius: 8px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.16) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
    }

    .guide-box {
        background: rgba(2, 6, 23, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 4px solid #38bdf8;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .status-card-active {
        background: rgba(6, 78, 59, 0.4);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .status-card-paused {
        background: rgba(120, 53, 15, 0.4);
        border: 1px solid #f59e0b;
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
# HERO BANNER
# ==========================================
st.markdown("""
<div class="spatial-banner">
    <div class="badge-pill">⚡ AUTONOMOUS MEAL SYNC ENGINE</div>
    <div class="title-text">Mess Conquers</div>
    <p class="sub-text">Automated SpaceBasic reservations, credentials vault, and vacation management</p>
</div>
""", unsafe_allow_html=True)

tab_telemetry, tab_register = st.tabs(["⚡ Service Status & Vacation", "🛠️ Account Setup & Credentials"])

# ==========================================
# TAB 1: TELEMETRY & VACATION MODE
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
                        <div style="font-weight: 700; color: #34d399; font-size: 1.05rem; margin-bottom: 4px;">
                            ● STATUS: ACTIVE & RUNNING
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.94rem; line-height: 1.5;">
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
                        <div style="font-weight: 700; color: #fbbf24; font-size: 1.05rem; margin-bottom: 4px;">
                            ⏸️ STATUS: PAUSED / EXPIRED
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.94rem; line-height: 1.5;">
                            Account: <b>{user_name}</b> ({query_val})<br>
                            Bookings are paused. Daily runners bypass this profile until resumed.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("▶️ Resume Autopilot"):
                        supabase.table("users").update({"is_active": True}).eq("id", row_id).execute()
                        st.rerun()
            else:
                st.info(f"No configured profile located for '{query_val}'. Register in Tab 2.")
        except Exception as e:
            st.error(f"Status query error: {e}")

# ==========================================
# TAB 2: CREDENTIAL ALLOCATION & RULES
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

    st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 1.2rem 0;'>", unsafe_allow_html=True)

    with st.form("spatial_registration_console"):
        # OPTION A: DIRECT CREDENTIALS
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

        # OPTION B: BEARER / MAGIC LINK
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
                "SpaceBasic Authorization Token or Link",
                placeholder="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                help="Paste the full Authorization Bearer string copied from Developer Tools."
            ).strip()
            email_input = None

        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 1.4rem 0;'>", unsafe_allow_html=True)
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
