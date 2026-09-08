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
    page_title="MESS CONQUERS • MULTI-VERSE HUB",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# THEME & VOCABULARY DICTIONARY (ALL 10 REALMS)
# ==========================================
THEMES = {
    "Solo Leveling": {
        "primary": "#38bdf8",
        "secondary": "#0284c7",
        "accent": "#0ea5e9",
        "bg_base": "#030712",
        "panel_bg": "#091428",
        "input_bg": "#0c1f3d",
        "border_color": "#0284c7",
        "text_primary": "#ffffff",
        "text_secondary": "#cbd5e1",
        "font_family": "'Orbitron', monospace",
        "body_font": "'Rajdhani', sans-serif",
        "title": "QUEST: MESS CONQUER",
        "badge": "[ SYSTEM ALERT: MONARCH CORE ARMED ]",
        "subtitle": "Dungeon Gate Infiltration Window: 07:00 AM – 09:30 PM IST",
        "role_title": "HUNTER",
        "tab1_title": "[ ⚡ HUNTER STATUS & REST GATE ]",
        "tab2_title": "[ 🛠️ HUNTER REGISTRATION & CONTRACT ]",
        "tab1_header": "📍 GUILD TELEMETRY & STATUS RADAR",
        "tab1_caption": "Inspect active automated quest extraction or enter rest mode during campus leave.",
        "tab2_header": "⚙️ HUNTER GUILD CONTRACT SETUP",
        "tab2_caption": "All credentials and session tokens are encrypted using AES-128 before storage.",
        "particle_color": "56, 189, 248",
        "banner_tag": "SUNG JIN-WOO",
        "banner_sub": "[ SHADOW MONARCH • SYSTEM INTERFACE ]"
    },
    "Naruto": {
        "primary": "#f97316",
        "secondary": "#c2410c",
        "accent": "#ea580c",
        "bg_base": "#0d0907",
        "panel_bg": "#1c120c",
        "input_bg": "#2a1b12",
        "border_color": "#ea580c",
        "text_primary": "#ffffff",
        "text_secondary": "#fed7aa",
        "font_family": "'Impact', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "SCROLL: MESS CONQUEST",
        "badge": "🍥 [ HIDDEN LEAF MISSION PROTOCOL ]",
        "subtitle": "Chakra Infiltration Window: 07:00 AM – 09:30 PM IST",
        "role_title": "SHINOBI",
        "tab1_title": "[ 🍥 MISSION STATUS & RECOVERY ]",
        "tab2_title": "[ 📜 SHINOBI PACT & RATION JUTSU ]",
        "tab1_header": "📍 HOKAGE DESK TELEMETRY",
        "tab1_caption": "Check active ration supply missions or request medical recovery leave.",
        "tab2_header": "⚙️ BINDING CHAKRA PACT SETUP",
        "tab2_caption": "Secret Jutsu Ciphers are locked with AES-128 Sealing Jutsu before storage.",
        "particle_color": "249, 115, 22",
        "banner_tag": "WILL OF FIRE",
        "banner_sub": "[ KONOHAGAKURE • RATION JUTSU CONSOLE ]"
    },
    "One Piece": {
        "primary": "#fbbf24",
        "secondary": "#b45309",
        "accent": "#0284c7",
        "bg_base": "#040914",
        "panel_bg": "#0c192e",
        "input_bg": "#122544",
        "border_color": "#0284c7",
        "text_primary": "#ffffff",
        "text_secondary": "#fde68a",
        "font_family": "'Impact', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "LOG POSE: MESS RAID",
        "badge": "☠️ [ GRAND LINE LOG POSE LOCKED ]",
        "subtitle": "Galleon Galley Infiltration Time: 07:00 AM – 09:30 PM IST",
        "role_title": "PIRATE",
        "tab1_title": "[ ⚓ FLEET LOG & DOCKING MODE ]",
        "tab2_title": "[ 🍖 CREW REGISTRATION & BANQUET RULES ]",
        "tab1_header": "📍 GRAND LINE RADAR & BOUNTY LOG",
        "tab1_caption": "Check Galley raid status or anchor your ship at port during shore leave.",
        "tab2_header": "⚙️ PIRATE ARTICLES OF AGREEMENT",
        "tab2_caption": "Your treasure cipher is sealed tight in iron chests with AES-128 encryption.",
        "particle_color": "251, 191, 36",
        "banner_tag": "STRAW HAT FLEET",
        "banner_sub": "[ THOUSAND SUNNY • GALLEY AUTOMATION ]"
    },
    "Demon Slayer": {
        "primary": "#ef4444",
        "secondary": "#991b1b",
        "accent": "#10b981",
        "bg_base": "#080506",
        "panel_bg": "#1a0f12",
        "input_bg": "#28171b",
        "border_color": "#dc2626",
        "text_primary": "#ffffff",
        "text_secondary": "#fecaca",
        "font_family": "'Cinzel', serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "BREATHING STYLE: MEAL CLAIM",
        "badge": "⚔️ [ DEMON SLAYER CORPS DISPATCH ]",
        "subtitle": "Nichirin Blade Strike Target: 07:00 AM – 09:30 PM IST",
        "role_title": "SLAYER",
        "tab1_title": "[ 🏮 SLAYER TELEMETRY & REHAB ]",
        "tab2_title": "[ 🗡️ CORPS OATH & RATION FORMS ]",
        "tab1_header": "📍 CORPS HEADQUARTERS DISPATCH",
        "tab1_caption": "Track daily ration acquisition or enter Butterfly Mansion for recovery.",
        "tab2_header": "⚙️ NICHIRIN OATH & CORPS ALLOCATION",
        "tab2_caption": "Breathing ciphers are forged under unbreakable AES-128 ward seals.",
        "particle_color": "239, 68, 68",
        "banner_tag": "TOTAL CONCENTRATION",
        "banner_sub": "[ DEMON SLAYER CORPS • RATION BREATHING ]"
    },
    "Jujutsu Kaisen": {
        "primary": "#c084fc",
        "secondary": "#7e22ce",
        "accent": "#06b6d4",
        "bg_base": "#06040a",
        "panel_bg": "#150d22",
        "input_bg": "#201435",
        "border_color": "#9333ea",
        "text_primary": "#ffffff",
        "text_secondary": "#e9d5ff",
        "font_family": "'Space Grotesk', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "DOMAIN EXPANSION: MESS REIGN",
        "badge": "👁️ [ SPECIAL GRADE CURSED SEAL ]",
        "subtitle": "Sure-Hit Booking Activation: 07:00 AM – 09:30 PM IST",
        "role_title": "SORCERER",
        "tab1_title": "[ 👁️ DOMAIN STATUS & SEALED BARRIER ]",
        "tab2_title": "[ 🗝️ CURSED CONTRACT & MEAL TECHNIQUE ]",
        "tab1_header": "📍 JUJUTSU HIGH TELEMETRY DESK",
        "tab1_caption": "Inspect domain booking deployment or apply sealing talisman during off-campus leave.",
        "tab2_header": "⚙️ BINDING VOW & SORCERER ALLOCATION",
        "tab2_caption": "All inherited passkeys are shrouded with AES-128 Special Grade barrier seals.",
        "particle_color": "192, 132, 252",
        "banner_tag": "LIMITLESS VOID",
        "banner_sub": "[ SPECIAL GRADE AUTOMATION DOMAIN ]"
    },
    "Attack on Titan": {
        "primary": "#a3e635",
        "secondary": "#4d7c0f",
        "accent": "#eab308",
        "bg_base": "#060a04",
        "panel_bg": "#121a0c",
        "input_bg": "#1c2a13",
        "border_color": "#65a30d",
        "text_primary": "#ffffff",
        "text_secondary": "#d9f99d",
        "font_family": "'Cinzel', serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "EXPEDITION: WALL ROSE RATION",
        "badge": "🛡️ [ SCOUT REGIMENT DEPLOYMENT ]",
        "subtitle": "Wall Reconnaissance Strike Time: 07:00 AM – 09:30 PM IST",
        "role_title": "SOLDIER",
        "tab1_title": "[ 🛡️ SCOUT TELEMETRY & INTERIOR RETREAT ]",
        "tab2_title": "[ ⚔️ CADET CONTRACT & RATION ALLOCATION ]",
        "tab1_header": "📍 SCOUT REGIMENT RECON COMMAND",
        "tab1_caption": "Track daily mess expedition claims or pull back inside Wall Sina during leave.",
        "tab2_header": "⚙️ WINGS OF FREEDOM CADET OATH",
        "tab2_caption": "Military Ciphers are locked within high-security AES-128 reinforced barricades.",
        "particle_color": "163, 230, 53",
        "banner_tag": "WINGS OF FREEDOM",
        "banner_sub": "[ SCOUT REGIMENT • RECONNAISSANCE CONSOLE ]"
    },
    "Bleach": {
        "primary": "#38bdf8",
        "secondary": "#0284c7",
        "accent": "#f43f5e",
        "bg_base": "#05060a",
        "panel_bg": "#0c1322",
        "input_bg": "#131e36",
        "border_color": "#0284c7",
        "text_primary": "#ffffff",
        "text_secondary": "#bae6fd",
        "font_family": "'Impact', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "BANKAI: SEIREITEI MESS ORDER",
        "badge": "⚡ [ GOTEI 13 REISHI DISPATCH ]",
        "subtitle": "Senkaimon Infiltration Window: 07:00 AM – 09:30 PM IST",
        "role_title": "REAPER",
        "tab1_title": "[ ⚡ REISHI STATUS & WORLD OF LIVING ]",
        "tab2_title": "[ 🗡️ SQUAD CONTRACT & PROVISION KIDO ]",
        "tab1_header": "📍 SOUKYOKU HILL TELEMETRY",
        "tab1_caption": "Check automated Soul Society rations or take patrol leave in the World of the Living.",
        "tab2_header": "⚙️ GOTEI 13 ENROLLMENT & RATION PREFERENCES",
        "tab2_caption": "Release passwords are protected using Bakudo AES-128 sealing spells.",
        "particle_color": "56, 189, 248",
        "banner_tag": "TENSA ZANGETSU",
        "banner_sub": "[ GOTEI 13 • REISHI RATION ARCHIVE ]"
    },
    "Dragon Ball Z": {
        "primary": "#fbbf24",
        "secondary": "#d97706",
        "accent": "#f97316",
        "bg_base": "#0a0703",
        "panel_bg": "#1c1409",
        "input_bg": "#2b1f0e",
        "border_color": "#f59e0b",
        "text_primary": "#ffffff",
        "text_secondary": "#fef3c7",
        "font_family": "'Impact', sans-serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "SUPER SAIYAN: SENZU CLAIM",
        "badge": "🐉 [ CAPSULE CORP RADAR ARMED ]",
        "subtitle": "Kame House Delivery Target: 07:00 AM – 09:30 PM IST",
        "role_title": "WARRIOR",
        "tab1_title": "[ 🐉 SCOUTER RADAR & GRAVITY ROOM ]",
        "tab2_title": "[ 🥩 SAIYAN FEAST & RATION STATS ]",
        "tab1_header": "📍 SCOUTER POWER LEVEL TELEMETRY",
        "tab1_caption": "Monitor automated feast delivery or enter Hyperbolic Time Chamber to pause.",
        "tab2_header": "⚙️ Z-WARRIOR ALLIANCE & FEAST RULES",
        "tab2_caption": "Scouter Passkeys are shielded inside Capsule Corp AES-128 reinforced technology.",
        "particle_color": "251, 191, 36",
        "banner_tag": "KAMEHAMEHA",
        "banner_sub": "[ CAPSULE CORP • SAIYAN RATION RADAR ]"
    },
    "Death Note": {
        "primary": "#fb7185",
        "secondary": "#e11d48",
        "accent": "#cbd5e1",
        "bg_base": "#080305",
        "panel_bg": "#180a0e",
        "input_bg": "#261017",
        "border_color": "#be123c",
        "text_primary": "#ffffff",
        "text_secondary": "#fecdd3",
        "font_family": "'Cinzel', serif",
        "body_font": "'Rajdhani', sans-serif",
        "title": "DEATH NOTE: MEAL JUDGMENT",
        "badge": "📓 [ SHINIGAMI EYE CONTRACT ACTIVE ]",
        "subtitle": "Notebook Inscription Deadline: 07:00 AM – 09:30 PM IST",
        "role_title": "INVESTIGATOR",
        "tab1_title": "[ 📓 NOTEBOOK SURVEILLANCE & REST ]",
        "tab2_title": "[ 🖋️ DEATH NOTE CONTRACT & RULES ]",
        "tab1_header": "📍 TASK FORCE WIRE MONITOR",
        "tab1_caption": "Inspect automated meal judgments or go into surveillance darkness during holidays.",
        "tab2_header": "⚙️ HOW TO USE: MEAL AUTOMATION RULES",
        "tab2_caption": "All investigator aliases are wiped and encrypted with Watari's AES-128 cryptographic algorithms.",
        "particle_color": "251, 113, 133",
        "banner_tag": "JUSTICE PREVAILS",
        "banner_sub": "[ KIRA TASK FORCE • SHINIGAMI APPRENTICE ]"
    },
    "My Hero Academia": {
        "primary": "#34d399",
        "secondary": "#059669",
        "accent": "#38bdf8",
        "bg_base": "#020906",
        "panel_bg": "#091c13",
        "input_bg": "#0f2c1e",
        "border_color": "#10b981",
        "text_primary": "#ffffff",
        "text_secondary": "#a7f3d0",
        "font_family": "'Orbitron', monospace",
        "body_font": "'Rajdhani', sans-serif",
        "title": "PLUS ULTRA: U.A. CAFETERIA",
        "badge": "💥 [ HERO ALLIANCE REGISTRY ENGAGED ]",
        "subtitle": "Lunch Rush Speed Claim Window: 07:00 AM – 09:30 PM IST",
        "role_title": "HERO",
        "tab1_title": "[ 💥 QUIRK MONITOR & DORM REST ]",
        "tab2_title": "[ 🦸 HERO REGISTRATION & DIET PLAN ]",
        "tab1_header": "📍 U.A. HIGH MONITORING SYSTEM",
        "tab1_caption": "Check your automated Lunch Rush reservation or pause service during work study leave.",
        "tab2_header": "⚙️ HERO ALLIANCE CONTRACT & QUIRK STATS",
        "tab2_caption": "Your hero credentials are protected by U.A. High AES-128 firewall defenses.",
        "particle_color": "52, 211, 153",
        "banner_tag": "PLUS ULTRA",
        "banner_sub": "[ U.A. HIGH SCHOOL • HERO CAFETERIA CONSOLE ]"
    },
    "I don't watch anime": {
        "primary": "#818cf8",
        "secondary": "#4f46e5",
        "accent": "#38bdf8",
        "bg_base": "#090d16",
        "panel_bg": "#111827",
        "input_bg": "#1f2937",
        "border_color": "#4f46e5",
        "text_primary": "#ffffff",
        "text_secondary": "#e2e8f0",
        "font_family": "'Plus Jakarta Sans', sans-serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "title": "MESS CONQUERS AUTOPILOT",
        "badge": "⚡ [ AUTOMATED CLOUD DISPATCH ACTIVE ]",
        "subtitle": "Daily Execution Window: 07:00 AM – 09:30 PM IST",
        "role_title": "STUDENT",
        "tab1_title": "[ ⚡ SERVICE STATUS & VACATION MODE ]",
        "tab2_title": "[ 🛠️ ACCOUNT SETUP & PREFERENCES ]",
        "tab1_header": "📍 BOOKING STATUS & SERVICE OVERVIEW",
        "tab1_caption": "Check your automated booking status or pause the service during holidays.",
        "tab2_header": "⚙️ STUDENT CREDENTIALS & MEAL PREFERENCES",
        "tab2_caption": "Passwords and session tokens are encrypted using AES-128 before syncing to Supabase.",
        "particle_color": "129, 140, 248",
        "banner_tag": "AUTOMATION CONSOLE",
        "banner_sub": "[ HIGH-AVAILABILITY MEAL BOOKER ]"
    }
}

# ==========================================
# THEME GATEKEEPER SELECTOR
# ==========================================
if "theme" not in st.session_state:
    st.markdown("""
    <style>
        .stApp { background-color: #030712; color: #ffffff; font-family: 'Plus Jakarta Sans', sans-serif; }
        .intro-box {
            text-align: center;
            padding: 2.5rem 1.5rem;
            background: #0f172a;
            border-radius: 12px;
            border: 1.5px solid #0284c7;
            margin-top: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }
        .intro-title {
            font-size: 2.4rem;
            font-weight: 900;
            color: #38bdf8;
            margin-bottom: 0.5rem;
            letter-spacing: 0.05em;
        }
    </style>
    <div class="intro-box">
        <div class="intro-title">MESS CONQUERS</div>
        <p style="color: #cbd5e1; font-size: 1.05rem;">Choose from the Top 10 Anime Realms or Standard Mode:</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    choice = st.selectbox("SELECT YOUR INTERFACE REALM", list(THEMES.keys()), index=0)

    if st.button("INITIALIZE INTERFACE →", use_container_width=True):
        st.session_state["theme"] = choice
        st.rerun()

    st.stop()

cfg = THEMES[st.session_state["theme"]]

# ==========================================
# FLOATING PARTICLES CANVAS
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
    for (let i = 0; i < 48; i++) {{
        particles.push({{
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2.2 + 0.8,
            speedY: Math.random() * 1.3 + 0.4,
            speedX: (Math.random() - 0.5) * 0.45,
            alpha: Math.random() * 0.65 + 0.25
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
# MOTION ANIMATION & HIGH-CONTRAST CSS
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Rajdhani:wght@600;700&family=Space+Grotesk:wght@600;700&family=Plus+Jakarta+Sans:wght@600;700;800&family=Cinzel:wght@700;900&display=swap');

    * {{
        font-family: {cfg['body_font']};
    }}

    @keyframes ambientPulse {{
        0%, 100% {{
            background-color: {cfg['bg_base']};
            background-image: radial-gradient(circle at 50% 0%, {cfg['primary']}22 0%, transparent 70%);
        }}
        50% {{
            background-color: {cfg['bg_base']};
            background-image: radial-gradient(circle at 50% 12%, {cfg['primary']}38 0%, transparent 80%);
        }}
    }}

    .stApp {{
        animation: ambientPulse 8s infinite alternate ease-in-out;
        color: {cfg['text_primary']};
    }}

    @keyframes titleGlow {{
        0%, 100% {{
            text-shadow: 0 0 10px {cfg['primary']}aa, 0 0 20px {cfg['secondary']}66;
            letter-spacing: 0.05em;
        }}
        50% {{
            text-shadow: 0 0 20px {cfg['primary']}, 0 0 35px {cfg['secondary']};
            letter-spacing: 0.07em;
        }}
    }}

    .system-title {{
        font-family: {cfg['font_family']};
        font-size: 2.2rem;
        font-weight: 900;
        text-transform: uppercase;
        color: #ffffff;
        animation: titleGlow 3.5s infinite ease-in-out;
        margin-bottom: 0.2rem;
    }}

    @keyframes badgePing {{
        0%, 100% {{
            transform: scale(1);
            box-shadow: 0 0 10px {cfg['primary']}44;
        }}
        50% {{
            transform: scale(1.02);
            box-shadow: 0 0 22px {cfg['primary']}99;
        }}
    }}

    .system-badge {{
        font-family: {cfg['font_family']};
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: #0f172a;
        border: 1.5px solid {cfg['primary']};
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 800;
        color: {cfg['primary']};
        letter-spacing: 0.12em;
        animation: badgePing 2.5s infinite ease-in-out;
        margin-bottom: 0.8rem;
    }}

    @keyframes bannerGlow {{
        0%, 100% {{
            border-color: {cfg['border_color']};
            box-shadow: 0 0 15px {cfg['primary']}33;
        }}
        50% {{
            border-color: {cfg['primary']};
            box-shadow: 0 0 30px {cfg['primary']}77, inset 0 0 15px {cfg['primary']}33;
        }}
    }}

    @keyframes scanLineMotion {{
        0% {{ transform: translateY(-100%); }}
        100% {{ transform: translateY(900%); }}
    }}

    .motion-banner-box {{
        position: relative;
        overflow: hidden;
        background: {cfg['panel_bg']};
        border: 1.5px solid {cfg['border_color']};
        border-radius: 8px;
        padding: 2.4rem 1rem;
        text-align: center;
        margin-bottom: 1.4rem;
        animation: bannerGlow 4s infinite ease-in-out;
    }}

    .motion-banner-box::after {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 25px;
        background: linear-gradient(180deg, transparent, {cfg['primary']}55, transparent);
        animation: scanLineMotion 3.2s linear infinite;
        pointer-events: none;
    }}

    @keyframes formEntrance {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    div[data-testid="stForm"], .system-panel {{
        background-color: {cfg['panel_bg']} !important;
        border: 1.5px solid {cfg['border_color']} !important;
        border-radius: 8px !important;
        padding: 1.8rem !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.7) !important;
        animation: formEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        background-color: {cfg['input_bg']} !important;
        border: 1.5px solid {cfg['border_color']} !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    .stTextInput input:hover, .stTextArea textarea:hover, .stSelectbox select:hover {{
        border-color: {cfg['primary']} !important;
        box-shadow: 0 0 10px {cfg['primary']}44 !important;
        transform: translateY(-1px);
    }}

    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {cfg['primary']} !important;
        box-shadow: 0 0 16px {cfg['primary']}88 !important;
        transform: translateY(-2px);
    }}

    .stButton>button {{
        font-family: {cfg['font_family']} !important;
        background: linear-gradient(180deg, {cfg['primary']} 0%, {cfg['secondary']} 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border: 1.5px solid {cfg['primary']} !important;
        border-radius: 6px !important;
        padding: 0.75rem 1.4rem !important;
        box-shadow: 0 0 16px {cfg['primary']}55 !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100%;
    }}

    .stButton>button:hover {{
        box-shadow: 0 0 28px {cfg['primary']}, inset 0 0 10px rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-3px) scale(1.02);
    }}

    .stButton>button:active {{
        transform: translateY(1px) scale(0.98) !important;
    }}

    div[data-testid="stCheckbox"] {{
        padding: 4px 6px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }}

    div[data-testid="stCheckbox"]:hover {{
        background: {cfg['primary']}15;
        transform: translateX(4px);
    }}

    div[data-testid="stWidgetLabel"] label p {{
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: {cfg['text_primary']} !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background: {cfg['panel_bg']};
        border: 1px solid {cfg['border_color']};
        border-radius: 6px;
        padding: 6px;
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: {cfg['font_family']};
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 700;
        border-radius: 4px;
        transition: all 0.25s ease !important;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: {cfg['primary']} !important;
        transform: translateY(-2px);
    }}

    .stTabs [aria-selected="true"] {{
        background: {cfg['input_bg']} !important;
        color: {cfg['primary']} !important;
        border: 1px solid {cfg['primary']} !important;
        box-shadow: 0 0 14px {cfg['primary']}44 !important;
    }}

    .guide-box {{
        background-color: {cfg['input_bg']};
        border-left: 4px solid {cfg['primary']};
        padding: 14px 18px;
        border-radius: 4px;
        margin-top: 8px;
        margin-bottom: 16px;
        color: {cfg['text_secondary']};
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: inset 0 0 15px {cfg['primary']}15;
    }}

    @keyframes greenGlow {{
        0%, 100% {{ box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }}
        50% {{ box-shadow: 0 0 28px rgba(16, 185, 129, 0.65); }}
    }}

    @keyframes amberGlow {{
        0%, 100% {{ box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }}
        50% {{ box-shadow: 0 0 28px rgba(245, 158, 11, 0.65); }}
    }}

    .status-card-active {{
        background: #064e3b;
        border: 1.5px solid #10b981;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        animation: greenGlow 3s infinite ease-in-out;
        transition: transform 0.25s ease;
    }}

    .status-card-active:hover {{
        transform: scale(1.01);
    }}

    .status-card-paused {{
        background: #451a03;
        border: 1.5px solid #f59e0b;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        animation: amberGlow 3s infinite ease-in-out;
        transition: transform 0.25s ease;
    }}

    .status-card-paused:hover {{
        transform: scale(1.01);
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
# REALM SELECTOR
# ==========================================
top_col1, top_col2 = st.columns([3, 1])
top_col1.markdown(f'<div class="system-badge">{cfg["badge"]}</div>', unsafe_allow_html=True)
if top_col2.button("🔄 Swap Realm"):
    del st.session_state["theme"]
    st.rerun()

# ==========================================
# HEADER BANNER
# ==========================================
st.markdown(f"""
<div class="motion-banner-box">
    <div style="font-family: {cfg['font_family']}; font-size: 1.7rem; font-weight: 900; letter-spacing: 0.2em; color: #ffffff;">
        {cfg['banner_tag']}
    </div>
    <div style="font-size: 0.9rem; font-weight: 700; letter-spacing: 0.15em; color: {cfg['primary']}; margin-top: 6px;">
        {cfg['banner_sub']}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="system-title">{cfg["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="color: {cfg["text_secondary"]}; font-size: 1rem; margin-bottom: 1.5rem; font-weight: 600;">{cfg["subtitle"]}</div>', unsafe_allow_html=True)

tab_status, tab_config = st.tabs([cfg["tab1_title"], cfg["tab2_title"]])

# ==========================================
# TAB 1: TELEMETRY & STATUS INSPECTION
# ==========================================
with tab_status:
    st.markdown(f"##### {cfg['tab1_header']}")
    st.caption(cfg["tab1_caption"])

    lookup_choice = st.radio(
        "IDENTIFY YOUR ACCOUNT PROTOCOL",
        [
            "🔑 SpaceBasic User ID (Token / Magic Link Users)",
            "✉️ Registered Login Email (Direct Credentials Users)"
        ],
        horizontal=True,
        key="status_lookup_radio"
    )

    if "User ID" in lookup_choice:
        search_val = st.text_input("SPACEBASIC USER ID", placeholder="e.g. 123456", key="status_lookup_uid").strip()
        field_to_query = "spacebasic_id"
    else:
        search_val = st.text_input("SPACEBASIC LOGIN EMAIL", placeholder="e.g. student@example.com", key="status_lookup_email").strip().lower()
        field_to_query = "email"

    if search_val:
        try:
            res = supabase.table("users").select("*").eq(field_to_query, search_val).execute()
            if res.data and len(res.data) > 0:
                user_rec = res.data[0]
                user_name = user_rec.get("name", cfg["role_title"]).upper()
                is_active = user_rec.get("is_active", True)
                auth_type_stored = user_rec.get("auth_type", "password").upper()
                notif_email = user_rec.get("notification_email") or user_rec.get("email") or "Not configured"
                row_id = user_rec.get("id")

                st.write("")
                if is_active:
                    st.markdown(f"""
                    <div class="status-card-active">
                        <div style="font-family: {cfg['font_family']}; font-size: 1.1rem; font-weight: 800; color: #6ee7b7; letter-spacing: 0.05em;">
                            STATUS: ACTIVE • {cfg['role_title']} {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #a7f3d0; font-size: 1rem;">
                            Autopilot routine engaged. Daily meal booking triggers automatically.<br>
                            <span style="font-size: 0.85rem; opacity: 0.9;">AUTHENTICATION PROTOCOL: {auth_type_stored}</span><br>
                            <span style="font-size: 0.85rem; opacity: 0.9;">EXPIRATION ALERTS: {notif_email}</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🏖️ ENTER REST MODE (PAUSE AUTOPILOT)"):
                        supabase.table("users").update({"is_active": False}).eq("id", row_id).execute()
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div class="status-card-paused">
                        <div style="font-family: {cfg['font_family']}; font-size: 1.1rem; font-weight: 800; color: #fcd34d; letter-spacing: 0.05em;">
                            STATUS: PAUSED / EXPIRED • {cfg['role_title']} {user_name}
                        </div>
                        <p style="margin: 8px 0 0 0; color: #fde68a; font-size: 1rem;">
                            Account is paused or your session link expired. Daily runners bypass this profile until resumed or updated.<br>
                            <span style="font-size: 0.85rem; opacity: 0.9;">NOTIFICATIONS DISPATCHED TO: {notif_email}</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("⚔️ RESUME AUTOPILOT"):
                        supabase.table("users").update({"is_active": True}).eq("id", row_id).execute()
                        st.rerun()
            else:
                st.info(f"No contract found for [{search_val}]. Inscribe your details in Tab 2.")
        except Exception as e:
            st.error(f"Telemetry query error: {e}")

# ==========================================
# TAB 2: PROFILE REGISTRATION & CONTRACT
# ==========================================
with tab_config:
    st.markdown(f"##### {cfg['tab2_header']}")
    st.caption(cfg["tab2_caption"])

    login_method = st.radio(
        "SELECT YOUR LOGIN METHOD",
        [
            "Option A: SpaceBasic Direct Email & Password",
            "Option B: SpaceBasic Auth Link / Bearer Token"
        ],
        index=0,
        key="login_method_selector"
    )

    st.markdown("<hr style='border: 0.5px solid #334155; margin: 1.2rem 0;'>", unsafe_allow_html=True)

    with st.form("universe_contract_form"):
        # ===============================================
        # OPTION A: DIRECT EMAIL & PASSWORD USERS
        # ===============================================
        if "Option A" in login_method:
            st.markdown("#### 1. CREDENTIALS & IDENTIFIER")
            st.markdown(f"""
            <div class="guide-box">
                <b style="color: {cfg['primary']};">DIRECT LOGIN PROTOCOL:</b><br>
                Enter your SpaceBasic login email and password. Your credentials authenticate dynamically via the API. No session links or user IDs required.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input(f"{cfg['role_title']} FULL NAME", placeholder="Your Full Name").strip()
            with col2:
                tenant_id = st.text_input("SPACEBASIC TENANT ID", value="143").strip()

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                email_input = st.text_input("SPACEBASIC LOGIN EMAIL", placeholder="student@example.com").strip().lower()
            with col_a2:
                secret_input = st.text_input("SPACEBASIC PASSWORD", type="password", placeholder="••••••••").strip()

            spacebasic_id = None
            notification_email = None

        # ===============================================
        # OPTION B: AUTH LINK / TOKEN USERS
        # ===============================================
        else:
            st.markdown("#### 1. USER ID & ALERT EMAIL")
            st.markdown(f"""
            <div class="guide-box">
                <b>Easy Steps to Get User ID & Token:</b><br>
                1. Open SpaceBasic and go to <b>Mess -> Booking</b>.<br>
                2. Right-click anywhere and select <b>Inspect</b> (or press F12) -> go to the <b>Network</b> tab.<br>
                3. Click on <b>Tomorrow</b> (on the left side).<br>
                4. Look for <code>mealsmenu?userId=123456...</code> in the list and click it.<br>
                5. Under the <b>Headers</b> tab, scroll down to <code>Authorization</code> and copy the full value starting with <b>Bearer ...</b><br>
                6. Your <b>SpaceBasic User ID</b> is the number after <code>userId=</code> (e.g. <code>123456</code>).
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                name_input = st.text_input(f"{cfg['role_title']} FULL NAME", placeholder="Your Full Name").strip()
            with col2:
                tenant_id = st.text_input("SPACEBASIC TENANT ID", value="143").strip()

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                spacebasic_id = st.text_input(
                    "SPACEBASIC USER ID",
                    placeholder="123456",
                    help="The number seen after userId= in the mealsmenu network request."
                ).strip()
            with col_b2:
                notification_email = st.text_input(
                    "ALERT EMAIL ADDRESS",
                    placeholder="student@gmail.com",
                    help="We will email you here when your token expires so you can refresh it."
                ).strip().lower()

            secret_input = st.text_area(
                "SPACEBASIC AUTHENTICATION LINK OR BEARER TOKEN",
                placeholder="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                help="Paste the full Authorization Bearer token copied from the headers."
            ).strip()
            email_input = None

        st.markdown("<hr style='border: 0.5px solid #334155; margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 2. MEAL PREFERENCES & RECURRING SKIPS")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            lunch_pref = st.selectbox("LUNCH PREFERENCE", ["Non Veg", "Eggetarian", "Veg"], index=0)
        with col_p2:
            dinner_pref = st.selectbox("DINNER PREFERENCE", ["Non Veg", "Eggetarian", "Veg"], index=0)

        st.caption("Select any meals you want the automation script to skip claiming automatically:")

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        skip_config = {}

        for day in days:
            skips = st.multiselect(f"Skip on {day.capitalize()}", ["Breakfast", "Lunch", "Dinner"], key=f"skip_{day}")
            if skips:
                skip_config[day] = [s.lower() for s in skips]

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button(f"⚔️ LOCK {cfg['role_title']} CONTRACT & ACTIVATE")

    if submit:
        is_direct_email = "Option A" in login_method

        if is_direct_email:
            if not email_input or not secret_input:
                st.error("SpaceBasic Login Email and Password are required.")
                st.stop()
        else:
            if not spacebasic_id or not secret_input or not notification_email:
                st.error("SpaceBasic User ID, Auth Link/Token, and Alert Email are strictly required.")
                st.stop()
            if "@" not in notification_email:
                st.error("Please provide a valid Alert Email.")
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
                "name": name_input or "Hunter",
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

            success_target = email_input if is_direct_email else f"SpaceBasic ID {spacebasic_id}"
            st.success(f"CONTRACT ARMED for {success_target}! Autopilot registered successfully.")
        except Exception as err:
            st.error(f"System synchronization failure: {err}")
