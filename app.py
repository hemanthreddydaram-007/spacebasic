import os
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# SYSTEM CORE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SYSTEM • HUNTER COMMAND CONSOLE",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# FLOATING MANA PARTICLE ENGINE (CANVAS)
# ==========================================
components.html("""
<canvas id="systemParticles" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0;"></canvas>
<script>
    const canvas = document.getElementById('systemParticles');
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = 45;

    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2 + 0.8,
            speedY: Math.random() * 1.2 + 0.3,
            speedX: (Math.random() - 0.5) * 0.4,
            alpha: Math.random() * 0.7 + 0.2
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        particles.forEach(p => {
            p.y -= p.speedY;
            p.x += p.speedX;

            if (p.y < 0) {
                p.y = height + 10;
                p.x = Math.random() * width;
            }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(56, 189, 248, ${p.alpha})`;
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#0284c7';
            ctx.fill();
        });

        requestAnimationFrame(animate);
    }
    animate();
</script>
""", height=0)

# ==========================================
# INTERACTIVE MOTION ANIMATION CSS ENGINE
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    * {
        font-family: 'Rajdhani', sans-serif;
    }

    /* Dungeon Void Ambient Background */
    @keyframes backgroundPulse {
        0%, 100% {
            background-color: #030712;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.28) 0%, transparent 70%),
                linear-gradient(rgba(3, 7, 18, 0.95), rgba(3, 7, 18, 0.95));
        }
        50% {
            background-color: #050d1e;
            background-image: 
                radial-gradient(circle at 50% 10%, rgba(56, 189, 248, 0.38) 0%, transparent 75%),
                linear-gradient(rgba(3, 7, 18, 0.92), rgba(3, 7, 18, 0.92));
        }
    }

    .stApp {
        animation: backgroundPulse 8s infinite alternate ease-in-out;
        background-size: 100% 100%;
        color: #e0f2fe;
    }

    /* System Window Header Glow */
    @keyframes systemGlow {
        0%, 100% {
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.7), 0 0 25px rgba(14, 165, 233, 0.5);
            letter-spacing: 0.08em;
        }
        50% {
            text-shadow: 0 0 18px rgba(56, 189, 248, 1), 0 0 40px rgba(14, 165, 233, 0.85);
            letter-spacing: 0.10em;
        }
    }

    .system-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.3rem;
        font-weight: 900;
        text-transform: uppercase;
        color: #ffffff;
        animation: systemGlow 3s infinite ease-in-out;
        margin-bottom: 0.2rem;
    }

    /* Radar Scan Line & Container Glow for Gate Banner */
    @keyframes bannerBreathing {
        0%, 100% {
            border-color: #0284c7;
            box-shadow: 0 0 20px rgba(14, 165, 233, 0.35);
        }
        50% {
            border-color: #38bdf8;
            box-shadow: 0 0 35px rgba(56, 189, 248, 0.7), inset 0 0 15px rgba(14, 165, 233, 0.3);
        }
    }

    @keyframes scanLineMotion {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(1000%); }
    }

    .animated-banner-box {
        position: relative;
        overflow: hidden;
        border-radius: 8px;
        border: 1.5px solid #0284c7;
        margin-bottom: 1.4rem;
        animation: bannerBreathing 4s infinite ease-in-out;
    }

    .animated-banner-box::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 25px;
        background: linear-gradient(180deg, transparent, rgba(56, 189, 248, 0.4), transparent);
        opacity: 0.7;
        animation: scanLineMotion 3.5s linear infinite;
        pointer-events: none;
    }

    div[data-testid="stImage"] > img {
        border-radius: 8px;
        object-fit: cover;
        max-height: 230px;
        width: 100%;
        transition: transform 0.5s ease;
    }

    .animated-banner-box:hover img {
        transform: scale(1.03);
    }

    /* Monarch Seal Badge Pulse */
    @keyframes badgePing {
        0%, 100% { transform: scale(1); box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
        50% { transform: scale(1.02); box-shadow: 0 0 20px rgba(56, 189, 248, 0.8); }
    }

    .system-badge {
        font-family: 'Orbitron', monospace;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        background: rgba(14, 165, 233, 0.15);
        border: 1px solid #38bdf8;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        animation: badgePing 2.5s infinite ease-in-out;
        margin-bottom: 0.8rem;
    }

    .system-subtitle {
        font-family: 'Rajdhani', sans-serif;
        color: #7dd3fc;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* System Quest Window Form */
    @keyframes panelEntry {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stForm"], .system-panel {
        background: rgba(7, 23, 48, 0.78) !important;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1.5px solid #0284c7 !important;
        border-radius: 6px !important;
        padding: 1.8rem !important;
        box-shadow: inset 0 0 25px rgba(14, 165, 233, 0.15), 0 0 35px rgba(2, 132, 199, 0.4) !important;
        position: relative;
        animation: panelEntry 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    div[data-testid="stForm"]::before {
        content: "[ SYSTEM QUEST: HUNTER CONTRACT INSCRIBED ]";
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        color: #38bdf8;
        letter-spacing: 0.2em;
        position: absolute;
        top: -10px;
        left: 18px;
        background: #030712;
        padding: 0 8px;
        border-left: 2px solid #38bdf8;
        border-right: 2px solid #38bdf8;
    }

    /* System Window Tabs Navigation */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(3, 15, 38, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 6px;
        padding: 6px;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Orbitron', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #64748b;
        border-radius: 4px;
        border: 1px solid transparent !important;
        padding: 8px 18px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8 !important;
        background: rgba(14, 165, 233, 0.1) !important;
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(14, 165, 233, 0.25) !important;
        color: #38bdf8 !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Mana-Infused Interactive Action Buttons */
    .stButton>button {
        font-family: 'Orbitron', monospace !important;
        background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 4px !important;
        padding: 0.75rem 1.4rem !important;
        box-shadow: 0 0 16px rgba(14, 165, 233, 0.5) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton>button:hover {
        background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%) !important;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.95), inset 0 0 12px rgba(255, 255, 255, 0.4) !important;
        transform: translateY(-3px) scale(1.02);
    }

    .stButton>button:active {
        transform: translateY(1px) scale(0.97) !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
    }

    /* Hunter Parameter Input Nodes */
    .stTextInput input, .stSelectbox select {
        background: rgba(3, 15, 38, 0.85) !important;
        border: 1px solid #0369a1 !important;
        border-radius: 4px !important;
        color: #e0f2fe !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stTextInput input:hover, .stSelectbox select:hover {
        border-color: #0284c7 !important;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.35) !important;
        transform: translateY(-1px);
    }

    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.8) !important;
        transform: translateY(-2px);
    }

    /* Gate Skip Matrix Nodes */
    div[data-testid="stCheckbox"] {
        padding: 4px 6px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }

    div[data-testid="stCheckbox"]:hover {
        background: rgba(14, 165, 233, 0.08);
        transform: translateX(4px);
    }

    div[data-testid="stCheckbox"] label p {
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        transition: color 0.2s ease;
    }

    div[data-testid="stCheckbox"]:hover label p {
        color: #38bdf8 !important;
    }

    /* Hunter Deployment State Cards */
    @keyframes statusGlowGreen {
        0%, 100% { box-shadow: 0 0 18px rgba(16, 185, 129, 0.3); }
        50% { box-shadow: 0 0 30px rgba(16, 185, 129, 0.6); }
    }

    @keyframes statusGlowAmber {
        0%, 100% { box-shadow: 0 0 18px rgba(245, 158, 11, 0.3); }
        50% { box-shadow: 0 0 30px rgba(245, 158, 11, 0.6); }
    }

    .quest-active {
        background: rgba(6, 44, 40, 0.65);
        border: 1.5px solid #10b981;
        border-radius: 4px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        animation: statusGlowGreen 3s infinite ease-in-out;
        transition: transform 0.3s ease;
    }

    .quest-active:hover {
        transform: scale(1.01);
    }

    .quest-paused {
        background: rgba(45, 20, 10, 0.65);
        border: 1.5px solid #f59e0b;
        border-radius: 4px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        animation: statusGlowAmber 3s infinite ease-in-out;
        transition: transform 0.3s ease;
    }

    .quest-paused:hover {
        transform: scale(1.01);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE CORE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SYSTEM ANOMALY: Monarch Core connection credentials missing from dimension matrix.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# MOTION-ANIMATED MONARCH BANNER
# ==========================================
banner_file = None
for filename in ["sung-jinwoo.png", "sung-jinwoo.jpg", "sung-jinwoo.jpeg", "jinwoo.png"]:
    if os.path.exists(filename):
        banner_file = filename
        break

st.markdown('<div class="animated-banner-box">', unsafe_allow_html=True)
if banner_file:
    st.image(banner_file, use_container_width=True)
else:
    st.markdown("""
        <div style="
            width: 100%;
            height: 190px;
            background: radial-gradient(circle at 50% 30%, rgba(14, 165, 233, 0.35) 0%, rgba(3, 7, 18, 0.95) 75%),
                        repeating-linear-gradient(0deg, rgba(56, 189, 248, 0.05) 0px, rgba(56, 189, 248, 0.05) 1px, transparent 1px, transparent 4px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        ">
            <div style="font-family: 'Orbitron', monospace; font-size: 2.8rem; filter: drop-shadow(0 0 16px #38bdf8);">⚔️ 👁️‍🗨️ ⚔️</div>
            <div style="font-family: 'Orbitron', monospace; font-size: 1.35rem; font-weight: 900; letter-spacing: 0.35em; color: #ffffff; text-shadow: 0 0 12px #38bdf8;">SUNG JIN-WOO</div>
            <div style="font-family: 'Rajdhani', sans-serif; font-size: 0.88rem; font-weight: 700; letter-spacing: 0.25em; color: #7dd3fc;">[ SHADOW MONARCH • SYSTEM INTERFACE ]</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="system-badge">[ SYSTEM ANNOUNCEMENT: AUTOMATED PROTOCOL ENGAGED ]</div>', unsafe_allow_html=True)
st.markdown('<div class="system-title">QUEST: MESS CONQUER</div>', unsafe_allow_html=True)
st.markdown('<div class="system-subtitle">Dungeon Gate Infiltration Window: 18:00:00 IST Sharp</div>', unsafe_allow_html=True)

tab_manage, tab_register = st.tabs([
    "[ ⚡ HUNTER STATUS & REST GATE ]", 
    "[ 🛠️ HUNTER REGISTRATION & STAT ALLOCATION ]"
])

# ==========================================
# TAB 1: HUNTER STATUS & REST GATE
# ==========================================
with tab_manage:
    st.markdown("##### 📍 GUILD TELEMETRY & STATUS INSPECTION")
    st.caption("Inspect active automated quest extraction or enter rest mode during campus leave.")

    search_email = st.text_input(
        "HUNTER SOUL SIGNATURE (REGISTERED EMAIL)",
        placeholder="shadow_monarch@system.com",
        key="status_email_box"
    ).strip().lower()

    if search_email:
        try:
            res = supabase.table("users").select("*").eq("email", search_email).execute()
            
            if res.data and len(res.data) > 0:
                user_record = res.data[0]
                user_name = user_record.get("name", "Hunter").upper()
                is_active = user_record.get("is_active", True)

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="quest-active">
                        <div style="font-family: 'Orbitron'; font-size: 1rem; font-weight: 700; color: #6ee7b7; letter-spacing: 0.1em;">
                            STATUS: AWAKENED • HUNTER {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #a7f3d0; font-size: 0.95rem;">
                            Shadow extraction routine armed. Next daily ration conquest fires precisely at <b>18:00:00 IST</b>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🏖️ RETURN TO SAFE ZONE (ENTER REST MODE)"):
                        supabase.table("users").update({"is_active": False}).eq("email", search_email).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="quest-paused">
                        <div style="font-family: 'Orbitron'; font-size: 1rem; font-weight: 700; color: #fcd34d; letter-spacing: 0.1em;">
                            STATUS: DORMANT • HUNTER {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #fde68a; font-size: 0.95rem;">
                            Hunter is resting in the safe zone. The 18:00:00 IST automated raid script will bypass this profile.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("⚔️ RE-ENTER THE DUNGEON (AWAKEN HUNTER)"):
                        supabase.table("users").update({"is_active": True}).eq("email", search_email).execute()
                        st.rerun()
            else:
                st.info("No Hunter profile located with this Soul Signature. Shift to **Hunter Registration & Stat Allocation** to inscribe your contract.")
        except Exception as e:
            st.error(f"System scan anomaly: {e}")

# ==========================================
# TAB 2: HUNTER REGISTRATION & STAT ALLOCATION
# ==========================================
with tab_register:
    st.markdown("##### ⚙️ HUNTER GUILD CONTRACT & STAT REGISTRATION")
    st.caption("All Dungeon Passkeys are sealed via AES-128 cryptographic shielding before being stored in the core database.")
    
    with st.form("account_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input("HUNTER CODENAME", placeholder="Sung Jin-Woo")
            email_input = st.text_input("HUNTER SOUL SIGNATURE (EMAIL)", placeholder="hunter@domain.com")
        with col2:
            tenant_id = st.text_input("DUNGEON SECTOR ID (TENANT)", value="143")
            password_input = st.text_input(
                "GATE PASSKEY (PASSWORD)",
                placeholder="••••••••",
                type="password"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🥩 RATION ACQUISITION PRIORITY")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("MIDDAY RAID RATION HIERARCHY", ["Non Veg", "Egg", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("NIGHTFALL RAID RATION HIERARCHY", ["Non Veg", "Egg", "Veg"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🛡️ DUNGEON REST SCHEDULE (GATE SKIPS)")
        st.caption("Select designated days where the automated raid team must bypass meal claims:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            st.write(f"**{day.upper()} GATE CYCLE**")
            c1, c2, c3 = st.columns(3)
            b_skip = c1.checkbox("Skip Dawn Ration (Breakfast)", key=f"{day}_b")
            l_skip = c2.checkbox("Skip Midday Ration (Lunch)", key=f"{day}_l")
            d_skip = c3.checkbox("Skip Dusk Ration (Dinner)", key=f"{day}_d")
            
            day_skips_list = []
            if b_skip: day_skips_list.append("breakfast")
            if l_skip: day_skips_list.append("lunch")
            if d_skip: day_skips_list.append("dinner")
            
            if day_skips_list:
                skip_config[day] = day_skips_list

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("⚔️ ACCEPT CONTRACT & AWAKEN HUNTER")

    if submit:
        if not name_input or not email_input or not password_input:
            st.error("SYSTEM ERROR: Hunter Codename, Soul Signature, and Gate Passkey are strictly required to seal this contract.")
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

                supabase.table("users").upsert(payload, on_conflict="email").execute()
                st.success("CONTRACT SEALED: Hunter credentials encrypted and synced into the Monarch Core. Armed for 18:00:00 IST extraction.")
            except Exception as err:
                st.error(f"System synchronization failure: {err}")
