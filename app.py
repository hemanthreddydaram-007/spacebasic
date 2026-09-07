import os
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
from security import encrypt_value

# ==========================================
# SYSTEM CORE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="MESS CONQUERS • MULTI-VERSE HUB",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# THEME & VOCABULARY DICTIONARY
# ==========================================
THEMES = {
    "Solo Leveling": {
        "primary": "#38bdf8",
        "secondary": "#0284c7",
        "accent": "#6ee7b7",
        "bg_radial": "rgba(14, 165, 233, 0.28)",
        "bg_base": "#030712",
        "font_family": "'Orbitron', monospace",
        "body_font": "'Rajdhani', sans-serif",
        "title": "QUEST: MESS CONQUER",
        "badge": "[ SYSTEM ALERT: MONARCH CORE ARMED ]",
        "subtitle": "Dungeon Gate Infiltration Window: 18:00:00 IST Sharp",
        "role_title": "HUNTER",
        "identity_label": "HUNTER SOUL SIGNATURE (EMAIL)",
        "identity_placeholder": "sung_jinwoo@hunterassociation.com",
        "name_label": "HUNTER CODENAME",
        "name_placeholder": "Sung Jin-Woo",
        "pass_label": "DUNGEON PASSKEY (PASSWORD)",
        "tenant_label": "DUNGEON SECTOR ID (TENANT)",
        "tab1_title": "[ ⚡ HUNTER STATUS & REST GATE ]",
        "tab2_title": "[ 🛠️ HUNTER REGISTRATION & STAT ALLOCATION ]",
        "tab1_header": "📍 GUILD TELEMETRY & HUNTER RADAR",
        "tab1_caption": "Inspect active automated quest extraction or enter rest mode during campus leave.",
        "tab2_header": "⚙️ HUNTER GUILD CONTRACT & STAT REGISTRATION",
        "tab2_caption": "All Dungeon Passkeys are sealed via AES-128 cryptographic shielding.",
        "ration_section": "🥩 RATION ACQUISITION PRIORITY",
        "lunch_label": "MIDDAY RAID RATION HIERARCHY",
        "dinner_label": "NIGHTFALL RAID RATION HIERARCHY",
        "skip_section": "🛡️ DUNGEON REST SCHEDULE (GATE SKIPS)",
        "skip_caption": "Select designated days where the raid party must bypass meal claims:",
        "meal_dawn": "Skip Dawn Ration (Breakfast)",
        "meal_midday": "Skip Midday Ration (Lunch)",
        "meal_dusk": "Skip Dusk Ration (Dinner)",
        "submit_btn": "⚔️ ACCEPT CONTRACT & AWAKEN HUNTER",
        "pause_btn": "🏖️ ENTER REST GATE (PAUSE RAID)",
        "resume_btn": "⚔️ AWAKEN HUNTER (RESUME RAID)",
        "active_title": "STATUS: AWAKENED",
        "active_desc": "Shadow extraction routine armed. Next ration conquest fires precisely at 18:00:00 IST.",
        "paused_title": "STATUS: DORMANT IN REST GATE",
        "paused_desc": "Hunter is resting in the safe zone. The 18:00:00 IST raid script will bypass this profile.",
        "not_found": "No Hunter profile located. Shift to Hunter Registration to inscribe your contract.",
        "success_msg": "CONTRACT SEALED: Hunter credentials encrypted and synced into the Monarch Core.",
        "particle_color": "56, 189, 248",
        "banner_tag": "SUNG JIN-WOO",
        "banner_sub": "[ SHADOW MONARCH • SYSTEM INTERFACE ]"
    },
    "Naruto": {
        "primary": "#f97316",
        "secondary": "#c2410c",
        "accent": "#38bdf8",
        "bg_radial": "rgba(249, 115, 22, 0.25)",
        "bg_base": "#0a0604",
        "font_family": "'Impact', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "SCROLL: MESS CONQUEST",
        "badge": "🍥 [ HIDDEN LEAF MISSION PROTOCOL ]",
        "subtitle": "Chakra Infiltration Window: 18:00:00 IST Sharp",
        "role_title": "SHINOBI",
        "identity_label": "SHINOBI REGISTRATION ID (EMAIL)",
        "identity_placeholder": "naruto.uzumaki@konohagakure.org",
        "name_label": "SHINOBI ALIAS / CLAN NAME",
        "name_placeholder": "Naruto Uzumaki",
        "pass_label": "SECRET JUTSU CIPHER (PASSWORD)",
        "tenant_label": "VILLAGE SECTOR CODE (TENANT)",
        "tab1_title": "[ 🍥 MISSION STATUS & RECOVERY ]",
        "tab2_title": "[ 📜 SHINOBI ARCHIVE & RATION JUTSU ]",
        "tab1_header": "📍 HOKAGE DESK TELEMETRY",
        "tab1_caption": "Check active ration supply missions or request medical recovery leave.",
        "tab2_header": "⚙️ BINDING CHAKRA PACT & RATION PREPARATION",
        "tab2_caption": "Secret Jutsu Ciphers are locked with AES-128 Sealing Jutsu before storage.",
        "ration_section": "🍜 ICHIRAKU SUPPLY PRIORITY",
        "lunch_label": "MIDDAY MISSION BENTO",
        "dinner_label": "EVENING CHAKRA FEAST",
        "skip_section": "🍃 OFF-DUTY DAYS (BYPASS PROVISIONS)",
        "skip_caption": "Select days where the ninja squad does not require mess provisions:",
        "meal_dawn": "Skip Morning Rice (Breakfast)",
        "meal_midday": "Skip Mission Bento (Lunch)",
        "meal_dusk": "Skip Evening Ramen (Dinner)",
        "submit_btn": "🔥 INSCRIBE INTO BINDING SCROLL",
        "pause_btn": "🍃 ENTER RECOVERY LEAVE (PAUSE)",
        "resume_btn": "🍥 DEPLOY ON MISSION (RESUME)",
        "active_title": "STATUS: MISSION ACTIVE",
        "active_desc": "Shadow Clone automation active. Provision supply jutsu fires at 18:00:00 IST.",
        "paused_title": "STATUS: ON MEDICAL LEAVE",
        "paused_desc": "Shinobi is resting. Supply squad will bypass this ninja registration.",
        "not_found": "No Shinobi registry located. Switch to Shinobi Archive to inscribe your ninja pact.",
        "success_msg": "JUTSU BOUND: Shinobi pact encrypted and logged in the Hokage Archives.",
        "particle_color": "249, 115, 22",
        "banner_tag": "WILL OF FIRE",
        "banner_sub": "[ KONOHAGAKURE • RATION JUTSU CONSOLE ]"
    },
    "One Piece": {
        "primary": "#eab308",
        "secondary": "#0284c7",
        "accent": "#ef4444",
        "bg_radial": "rgba(234, 179, 8, 0.22)",
        "bg_base": "#040914",
        "font_family": "'Impact', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "LOG POSE: MESS RAID",
        "badge": "☠️ [ GRAND LINE LOG POSE LOCKED ]",
        "subtitle": "Galleon Galley Infiltration Time: 18:00:00 IST Sharp",
        "role_title": "PIRATE",
        "identity_label": "BOUNTY POSTER ALIAS (EMAIL)",
        "identity_placeholder": "monkey_d_luffy@strawhatpirates.com",
        "name_label": "CAPTAIN / CREW CODENAME",
        "name_placeholder": "Monkey D. Luffy",
        "pass_label": "TREASURE CHEST CIPHER (PASSWORD)",
        "tenant_label": "PIRATE FLEET CODE (TENANT)",
        "tab1_title": "[ ⚓ FLEET LOG & DOCKING MODE ]",
        "tab2_title": "[ 🍖 CREW REGISTRATION & BANQUET RULES ]",
        "tab1_header": "📍 GRAND LINE RADAR & BOUNTY LOG",
        "tab1_caption": "Check Galley raid status or anchor your ship at port during shore leave.",
        "tab2_header": "⚙️ PIRATE ARTICLES OF AGREEMENT",
        "tab2_caption": "Your treasure cipher is sealed tight in iron chests with AES-128 encryption.",
        "ration_section": "🍖 SANJI'S GALLEY MENU PRIORITY",
        "lunch_label": "HIGH SEAS NOON FEAST",
        "dinner_label": "NIGHTFALL BANQUET RATION",
        "skip_section": "🏝️ ISLAND EXPLORATION DAYS (SKIP GALLEY)",
        "skip_caption": "Mark days when the crew hunts on islands and skips galley rations:",
        "meal_dawn": "Skip Sea Rations (Breakfast)",
        "meal_midday": "Skip Galley Roast (Lunch)",
        "meal_dusk": "Skip Midnight Feast (Dinner)",
        "submit_btn": "🍖 SET SAIL & HOIST FLAG",
        "pause_btn": "🏝️ DROP ANCHOR (PAUSE EXPEDITION)",
        "resume_btn": "⚓ RAISE ANCHOR (RESUME EXPEDITION)",
        "active_title": "STATUS: FULL SAIL AHEAD",
        "active_desc": "Galley raid autopilot armed. Sanji reserves your meal at 18:00:00 IST.",
        "paused_title": "STATUS: ANCHORED AT PORT",
        "paused_desc": "Crew is ashore. The automated Galley raid will bypass your ship.",
        "not_found": "No Pirate bounty found under this alias. Join the crew in the registration tab.",
        "success_msg": "CREW ARTICLES SIGNED: You are now an active pirate on the Grand Line fleet.",
        "particle_color": "234, 179, 8",
        "banner_tag": "STRAW HAT FLEET",
        "banner_sub": "[ THOUSAND SUNNY • GALLEY AUTOMATION ]"
    },
    "Demon Slayer": {
        "primary": "#ef4444",
        "secondary": "#10b981",
        "accent": "#fbbf24",
        "bg_radial": "rgba(239, 68, 68, 0.25)",
        "bg_base": "#080506",
        "font_family": "'Cinzel', serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "BREATHING STYLE: MEAL CLAIM",
        "badge": "⚔️ [ DEMON SLAYER CORPS DISPATCH ]",
        "subtitle": "Nichirin Blade Strike Target: 18:00:00 IST Sharp",
        "role_title": "SLAYER",
        "identity_label": "KASUGAI CROW ADDRESS (EMAIL)",
        "identity_placeholder": "tanjiro.kamado@slayercorps.jp",
        "name_label": "SLAYER RANK CODENAME",
        "name_placeholder": "Tanjiro Kamado",
        "pass_label": "BREATHING TECHNIQUE CIPHER (PASSWORD)",
        "tenant_label": "WISTERIA ESTATE CODE (TENANT)",
        "tab1_title": "[ 🏮 SLAYER TELEMETRY & REHABILITATION ]",
        "tab2_title": "[ 🗡️ CORPS CONTRACT & RATION FORM ]",
        "tab1_header": "📍 CORPS HEADQUARTERS DISPATCH",
        "tab1_caption": "Track daily ration acquisition or enter Butterfly Mansion for recovery.",
        "tab2_header": "⚙️ NICHIRIN OATH & CORPS ALLOCATION",
        "tab2_caption": "Breathing ciphers are forged under unbreakable AES-128 ward seals.",
        "ration_section": "🍱 WISTERIA HOUSE RATION PRIORITY",
        "lunch_label": "MIDDAY CONCENTRATION MEAL",
        "dinner_label": "DUSK PATROL NUTRITION",
        "skip_section": "🌸 BUTTERFLY REHABILITATION DAYS (SKIP)",
        "skip_caption": "Mark days spent resting where automated mess claims are bypassed:",
        "meal_dawn": "Skip Morning Onigiri (Breakfast)",
        "meal_midday": "Skip Midday Bento (Lunch)",
        "meal_dusk": "Skip Night Patrol Meal (Dinner)",
        "submit_btn": "🔥 FORGE NICHIRIN CONTRACT",
        "pause_btn": "🌸 ENTER BUTTERFLY MANSION (REST)",
        "resume_btn": "⚔️ DRAW NICHIRIN BLADE (RESUME)",
        "active_title": "STATUS: TOTAL CONCENTRATION ACTIVE",
        "active_desc": "Corps ration technique primed. Automatic acquisition triggers at 18:00:00 IST.",
        "paused_title": "STATUS: RESTING IN BUTTERFLY MANSION",
        "paused_desc": "Slayer is in rehabilitation. Kasugai Crow will bypass this account.",
        "not_found": "No Slayer record found on the Kasugai network. Inscribe your oath in tab 2.",
        "success_msg": "NICHIRIN OATH FORGED: Your slayer profile is synchronized with Corps Headquarters.",
        "particle_color": "239, 68, 68",
        "banner_tag": "TOTAL CONCENTRATION",
        "banner_sub": "[ DEMON SLAYER CORPS • RATION BREATHING ]"
    },
    "Jujutsu Kaisen": {
        "primary": "#a855f7",
        "secondary": "#4338ca",
        "accent": "#06b6d4",
        "bg_radial": "rgba(168, 85, 247, 0.28)",
        "bg_base": "#05040a",
        "font_family": "'Space Grotesk', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "DOMAIN EXPANSION: MESS REIGN",
        "badge": "👁️ [ SPECIAL GRADE CURSED SEAL ]",
        "subtitle": "Sure-Hit Booking Activation: 18:00:00 IST Sharp",
        "role_title": "SORCERER",
        "identity_label": "CURSED ENERGY SIGNATURE (EMAIL)",
        "identity_placeholder": "satoru.gojo@jujutsutech.edu",
        "name_label": "JUJUTSU SORCERER IDENTIFIER",
        "name_placeholder": "Satoru Gojo",
        "pass_label": "INHERITED CURSED PASSKEY (PASSWORD)",
        "tenant_label": "BARRIER SECTOR ID (TENANT)",
        "tab1_title": "[ 👁️ DOMAIN STATUS & SEALED BARRIER ]",
        "tab2_title": "[ 🗝️ CURSED CONTRACT & MEAL TECHNIQUE ]",
        "tab1_header": "📍 JUJUTSU HIGH TELEMETRY DESK",
        "tab1_caption": "Inspect domain booking deployment or apply sealing talisman during off-campus leave.",
        "tab2_header": "⚙️ BINDING VOW & SORCERER ALLOCATION",
        "tab2_caption": "All inherited passkeys are shrouded with AES-128 Special Grade barrier seals.",
        "ration_section": "🍙 CURSED RATION CONSUMPTION ORDER",
        "lunch_label": "MIDDAY ENERGY INFUSION",
        "dinner_label": "NIGHTFALL SORCERY FEAST",
        "skip_section": "⛩️ BARRIER SEAL DAYS (SKIP DOMAIN MEALS)",
        "skip_caption": "Select days when you are off-campus and domain claims are skipped:",
        "meal_dawn": "Skip Dawn Nourishment (Breakfast)",
        "meal_midday": "Skip Midday Bento (Lunch)",
        "meal_dusk": "Skip Nightfall Meal (Dinner)",
        "submit_btn": "🤞 EXPAND DOMAIN & BIND VOW",
        "pause_btn": "⛩️ APPLY SEALED BARRIER (PAUSE)",
        "resume_btn": "👁️ UNLEASH INFINITY (RESUME)",
        "active_title": "STATUS: DOMAIN EXPANDED",
        "active_desc": "Sure-Hit auto-booking active. Automatic ration reservation triggers at 18:00:00 IST.",
        "paused_title": "STATUS: ENCLOSED IN SEALED BARRIER",
        "paused_desc": "Sorcerer is in sealed meditation. The automated script will bypass this barrier.",
        "not_found": "No Cursed Energy signature detected. Expand your domain in tab 2.",
        "success_msg": "BINDING VOW IN EFFECT: Your cursed technique is armed for 18:00:00 IST execution.",
        "particle_color": "168, 85, 247",
        "banner_tag": "LIMITLESS VOID",
        "banner_sub": "[ SPECIAL GRADE AUTOMATION DOMAIN ]"
    },
    "I don't watch anime": {
        "primary": "#6366f1",
        "secondary": "#4f46e5",
        "accent": "#10b981",
        "bg_radial": "rgba(99, 102, 241, 0.18)",
        "bg_base": "#090d16",
        "font_family": "'Plus Jakarta Sans', sans-serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "title": "MESS CONQUERS AUTOPILOT",
        "badge": "⚡ [ AUTOMATED CLOUD DISPATCH ACTIVE ]",
        "subtitle": "Daily Execution Scheduled: 18:00:00 IST Sharp",
        "role_title": "STUDENT",
        "identity_label": "REGISTERED SPACEBASIC EMAIL",
        "identity_placeholder": "student@example.com",
        "name_label": "STUDENT FULL NAME",
        "name_placeholder": "Alex Kumar",
        "pass_label": "SPACEBASIC PASSWORD",
        "tenant_label": "CAMPUS TENANT ID",
        "tab1_title": "[ ⚡ SERVICE STATUS & VACATION MODE ]",
        "tab2_title": "[ 🛠️ ACCOUNT SETUP & PREFERENCES ]",
        "tab1_header": "📍 BOOKING STATUS & SERVICE OVERVIEW",
        "tab1_caption": "Check your automated booking status or pause the service during holidays.",
        "tab2_header": "⚙️ STUDENT CREDENTIALS & MEAL PREFERENCES",
        "tab2_caption": "Passwords are encrypted using AES-128 before syncing to Supabase.",
        "ration_section": "🍱 MEAL TYPE PREFERENCE",
        "lunch_label": "LUNCH PREFERENCE ORDER",
        "dinner_label": "DINNER PREFERENCE ORDER",
        "skip_section": "🚫 RECURRING WEEKLY SKIPS",
        "skip_caption": "Select meals you want the automation script to skip automatically:",
        "meal_dawn": "Skip Breakfast",
        "meal_midday": "Skip Lunch",
        "meal_dusk": "Skip Dinner",
        "submit_btn": "🚀 SAVE PREFERENCES & ACTIVATE",
        "pause_btn": "🏖️ HEADING HOME (PAUSE SERVICE)",
        "resume_btn": "🎒 BACK ON CAMPUS (RESUME SERVICE)",
        "active_title": "STATUS: SERVICE ACTIVE",
        "active_desc": "Autopilot is active. Tomorrow's meals will be booked automatically at 18:00:00 IST.",
        "paused_title": "STATUS: SERVICE PAUSED",
        "paused_desc": "Auto-booking is paused. The daily runner will bypass this account.",
        "not_found": "No account found with this email. Switch to tab 2 to register.",
        "success_msg": "CONFIGURATION SAVED: Your account is synchronized and armed for 18:00:00 IST execution.",
        "particle_color": "99, 102, 241",
        "banner_tag": "AUTOMATION CONSOLE",
        "banner_sub": "[ HIGH-AVAILABILITY MEAL BOOKER ]"
    }
}

# ==========================================
# THEME GATEKEEPER SELECTOR MODAL
# ==========================================
if "theme" not in st.session_state:
    st.markdown("""
    <style>
        .stApp { background-color: #030712; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
        .intro-box {
            text-align: center;
            padding: 2.5rem 1.5rem;
            background: rgba(15, 23, 42, 0.75);
            border-radius: 16px;
            border: 1px solid rgba(56, 189, 248, 0.35);
            margin-top: 2rem;
            box-shadow: 0 0 35px rgba(0,0,0,0.8);
        }
        .intro-title {
            font-size: 2.4rem;
            font-weight: 900;
            background: linear-gradient(90deg, #38bdf8, #c084fc, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: 0.05em;
        }
    </style>
    <div class="intro-box">
        <div class="intro-title">MESS CONQUERS</div>
        <p style="color: #94a3b8; font-size: 1.05rem;">Choose your universe to calibrate UI terminology, artwork, and visual style:</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    choice = st.selectbox(
        "SELECT YOUR INTERFACE REALM",
        list(THEMES.keys()),
        index=0
    )
    
    if st.button("INITIALIZE INTERFACE →", use_container_width=True):
        st.session_state["theme"] = choice
        st.rerun()

    st.stop()

cfg = THEMES[st.session_state["theme"]]

# ==========================================
# FLOATING CANVAS PARTICLES ENGINE
# ==========================================
components.html(f"""
<canvas id="systemParticles" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0;"></canvas>
<script>
    const canvas = document.getElementById('systemParticles');
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {{
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }});

    const particles = [];
    for (let i = 0; i < 42; i++) {{
        particles.push({{
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2 + 0.8,
            speedY: Math.random() * 1.1 + 0.3,
            speedX: (Math.random() - 0.5) * 0.4,
            alpha: Math.random() * 0.6 + 0.2
        }});
    }}

    function animate() {{
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => {{
            p.y -= p.speedY;
            p.x += p.speedX;
            if (p.y < 0) {{
                p.y = height + 10;
                p.x = Math.random() * width;
            }}
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba({cfg["particle_color"]}, ${{p.alpha}})`;
            ctx.shadowBlur = 8;
            ctx.shadowColor = '{cfg["primary"]}';
            ctx.fill();
        }});
        requestAnimationFrame(animate);
    }}
    animate();
</script>
""", height=0)

# ==========================================
# DYNAMIC CSS ENGINE
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Space+Grotesk:wght@600;800&family=Plus+Jakarta+Sans:wght@500;700;800&family=Cinzel:wght@700;900&display=swap');

    * {{
        font-family: {cfg['body_font']};
    }}

    .stApp {{
        background-color: {cfg['bg_base']};
        background-image: 
            radial-gradient(circle at 50% 0%, {cfg['bg_radial']} 0%, transparent 65%),
            linear-gradient(rgba(3, 7, 18, 0.95), rgba(3, 7, 18, 0.95));
        background-size: 100% 100%;
        color: #f8fafc;
    }}

    .system-title {{
        font-family: {cfg['font_family']};
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #ffffff;
        text-shadow: 0 0 16px {cfg['primary']};
        margin-bottom: 0.2rem;
    }}

    .system-badge {{
        font-family: {cfg['font_family']};
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid {cfg['primary']};
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        color: {cfg['primary']};
        letter-spacing: 0.15em;
        box-shadow: 0 0 14px {cfg['primary']};
        margin-bottom: 0.8rem;
    }}

    .animated-banner-box {{
        position: relative;
        overflow: hidden;
        border-radius: 8px;
        border: 1.5px solid {cfg['primary']};
        margin-bottom: 1.4rem;
        box-shadow: 0 0 25px {cfg['primary']};
    }}

    div[data-testid="stForm"], .system-panel {{
        background: rgba(10, 15, 28, 0.82) !important;
        backdrop-filter: blur(16px);
        border: 1.5px solid {cfg['secondary']} !important;
        border-radius: 8px !important;
        padding: 1.8rem !important;
        box-shadow: inset 0 0 25px {cfg['bg_radial']}, 0 0 35px rgba(0, 0, 0, 0.5) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 6px;
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: {cfg['font_family']};
        font-size: 0.78rem;
        color: #94a3b8;
        border-radius: 4px;
        transition: all 0.25s ease !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: {cfg['bg_radial']} !important;
        color: {cfg['primary']} !important;
        border: 1px solid {cfg['primary']} !important;
        box-shadow: 0 0 16px {cfg['primary']} !important;
    }}

    .stButton>button {{
        font-family: {cfg['font_family']} !important;
        background: linear-gradient(180deg, {cfg['primary']} 0%, {cfg['secondary']} 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: 1px solid {cfg['primary']} !important;
        box-shadow: 0 0 16px {cfg['primary']} !important;
        transition: all 0.25s ease !important;
    }}

    .stButton>button:hover {{
        box-shadow: 0 0 28px {cfg['primary']} !important;
        transform: translateY(-2px);
    }}

    .stTextInput input, .stSelectbox select {{
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid {cfg['secondary']} !important;
        color: #f8fafc !important;
        font-size: 1rem !important;
    }}

    .stTextInput input:focus {{
        border-color: {cfg['primary']} !important;
        box-shadow: 0 0 18px {cfg['primary']} !important;
    }}

    .status-card-active {{
        background: rgba(6, 44, 40, 0.65);
        border: 1.5px solid #10b981;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
    }}

    .status-card-paused {{
        background: rgba(45, 20, 10, 0.65);
        border: 1.5px solid #f59e0b;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.35);
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE INITIALIZATION
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SYSTEM CONFIGURATION ERROR: Supabase credentials missing from secrets matrix.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==========================================
# TOP THEME CHANGER BAR
# ==========================================
top_col1, top_col2 = st.columns([3, 1])
top_col1.markdown(f'<div class="system-badge">{cfg["badge"]}</div>', unsafe_allow_html=True)
if top_col2.button("🔄 Swap Universe"):
    del st.session_state["theme"]
    st.rerun()

# ==========================================
# MOTION BANNER
# ==========================================
st.markdown('<div class="animated-banner-box">', unsafe_allow_html=True)
st.markdown(f"""
    <div style="
        width: 100%;
        height: 160px;
        background: radial-gradient(circle at 50% 30%, {cfg['bg_radial']} 0%, {cfg['bg_base']} 80%),
                    repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.03) 0px, rgba(255, 255, 255, 0.03) 1px, transparent 1px, transparent 4px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    ">
        <div style="font-family: {cfg['font_family']}; font-size: 1.5rem; font-weight: 900; letter-spacing: 0.25em; color: #ffffff; text-shadow: 0 0 14px {cfg['primary']};">
            {cfg['banner_tag']}
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; letter-spacing: 0.2em; color: {cfg['primary']}; margin-top: 6px;">
            {cfg['banner_sub']}
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div class="system-title">{cfg["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;">{cfg["subtitle"]}</div>', unsafe_allow_html=True)

tab_status, tab_config = st.tabs([cfg["tab1_title"], cfg["tab2_title"]])

# ==========================================
# TAB 1: STATUS INSPECTION & REST MODE
# ==========================================
with tab_status:
    st.markdown(f"##### {cfg['tab1_header']}")
    st.caption(cfg["tab1_caption"])

    search_email = st.text_input(
        cfg["identity_label"],
        placeholder=cfg["identity_placeholder"],
        key="status_lookup_box"
    ).strip().lower()

    if search_email:
        try:
            res = supabase.table("users").select("*").eq("email", search_email).execute()
            
            if res.data and len(res.data) > 0:
                user_rec = res.data[0]
                user_name = user_rec.get("name", cfg["role_title"]).upper()
                is_active = user_rec.get("is_active", True)

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="status-card-active">
                        <div style="font-family: {cfg['font_family']}; font-size: 1rem; font-weight: 700; color: #6ee7b7; letter-spacing: 0.1em;">
                            {cfg['active_title']} • {cfg['role_title']} {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #a7f3d0; font-size: 0.95rem;">
                            {cfg['active_desc']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(cfg["pause_btn"]):
                        supabase.table("users").update({"is_active": False}).eq("email", search_email).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="status-card-paused">
                        <div style="font-family: {cfg['font_family']}; font-size: 1rem; font-weight: 700; color: #fcd34d; letter-spacing: 0.1em;">
                            {cfg['paused_title']} • {cfg['role_title']} {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #fde68a; font-size: 0.95rem;">
                            {cfg['paused_desc']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(cfg["resume_btn"]):
                        supabase.table("users").update({"is_active": True}).eq("email", search_email).execute()
                        st.rerun()
            else:
                st.info(cfg["not_found"])
        except Exception as e:
            st.error(f"Telemetry query error: {e}")

# ==========================================
# TAB 2: PROFILE REGISTRATION & PREFERENCES
# ==========================================
with tab_config:
    st.markdown(f"##### {cfg['tab2_header']}")
    st.caption(cfg["tab2_caption"])
    
    with st.form("universe_contract_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input(cfg["name_label"], placeholder=cfg["name_placeholder"])
            email_input = st.text_input(cfg["identity_label"], placeholder=cfg["identity_placeholder"])
        with col2:
            tenant_id = st.text_input(cfg["tenant_label"], value="143")
            password_input = st.text_input(
                cfg["pass_label"],
                placeholder="••••••••",
                type="password"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"##### {cfg['ration_section']}")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox(cfg["lunch_label"], ["Non Veg", "Egg", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox(cfg["dinner_label"], ["Non Veg", "Egg", "Veg"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"##### {cfg['skip_section']}")
        st.caption(cfg["skip_caption"])

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            st.write(f"**{day.upper()}**")
            c1, c2, c3 = st.columns(3)
            b_skip = c1.checkbox(cfg["meal_dawn"], key=f"{day}_b")
            l_skip = c2.checkbox(cfg["meal_midday"], key=f"{day}_l")
            d_skip = c3.checkbox(cfg["meal_dusk"], key=f"{day}_d")
            
            day_skips_list = []
            if b_skip: day_skips_list.append("breakfast")
            if l_skip: day_skips_list.append("lunch")
            if d_skip: day_skips_list.append("dinner")
            
            if day_skips_list:
                skip_config[day] = day_skips_list

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button(cfg["submit_btn"])

    if submit:
        if not name_input or not email_input or not password_input:
            st.error("Parameters incomplete: Codename, Soul Signature/Email, and Passkey are strictly required.")
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
                st.success(cfg["success_msg"])
            except Exception as err:
                st.error(f"System synchronization failure: {err}")
