"""
frontend/styles.py — Shared design system for all pages.

UI/UX overhaul:
  - Rich dark theme with layered depth (not flat black)  [DEFAULT]
  - LIGHT MODE: Comic-style red & white theme — bold outlines, Bangers font, halftone bg
  - Theme toggle button rendered top-left (in sidebar) via inject_styles()
  - Custom sidebar with branded nav items
  - Redesigned upload zone, stat cards, table, domain cards
  - Score bar components, skill chips, candidate cards
  - Smooth fade-in animations on key elements
  - Google Fonts: Syne + Bangers (display) + DM Sans (body) + DM Mono (data)
  - Streamlit native element overrides (file uploader, buttons,
    dataframe, progress, spinner, alerts)
"""

import streamlit as st


def inject_styles() -> None:
    # Initialise theme in session state (default: dark)
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    # Toggle button — sits at the very top of the sidebar
    with st.sidebar:
        is_dark = st.session_state["theme"] == "dark"
        label = "☀️  Light Mode" if is_dark else "🌙  Dark Mode"
        if st.button(label, key="theme_toggle", use_container_width=True):
            st.session_state["theme"] = "light" if is_dark else "dark"
            st.rerun()

    theme = st.session_state["theme"]
    is_light = theme == "light"

    # ── TOKEN SETS ──────────────────────────────────────────────────────────
    dark_vars = """
    --bg:        #080c14;
    --surface:   #0e1420;
    --surface2:  #151d2e;
    --surface3:  #1c2640;
    --border:    rgba(255,255,255,0.07);
    --border2:   rgba(255,255,255,0.12);
    --accent:    #6ee7b7;
    --accent2:   #818cf8;
    --accent3:   #f472b6;
    --text:      #e8edf5;
    --muted:     #64748b;
    --muted2:    #94a3b8;
    --ok:        #4ade80;
    --warn:      #fb923c;
    --danger:    #f87171;
    --r:         14px;
    --r-lg:      20px;
    --shadow:    0 4px 24px rgba(0,0,0,0.5);
    --shadow-lg: 0 12px 48px rgba(0,0,0,0.6);
    --font-display: 'Syne', sans-serif;
    --font-body:    'DM Sans', sans-serif;
    --font-mono:    'DM Mono', monospace;
    """

    light_vars = """
    --bg:        #f2f5fc;
    --surface:   #ffffff;
    --surface2:  #f8faff;
    --surface3:  #eef1f9;
    --border:    rgba(0,0,0,0.06);
    --border2:   rgba(0,0,0,0.11);
    --accent:    #2563eb;
    --accent2:   #7c3aed;
    --accent3:   #0ea5e9;
    --text:      #0f172a;
    --muted:     #94a3b8;
    --muted2:    #64748b;
    --ok:        #16a34a;
    --warn:      #d97706;
    --danger:    #dc2626;
    --r:         14px;
    --r-lg:      22px;
    --shadow:    0 4px 16px rgba(0,0,0,0.08),0 1px 4px rgba(0,0,0,0.04);
    --shadow-lg: 0 16px 48px rgba(0,0,0,0.12),0 4px 16px rgba(0,0,0,0.06);
    --font-display: 'Inter', sans-serif;
    --font-body:    'Plus Jakarta Sans', sans-serif;
    --font-mono:    'DM Mono', monospace;
    """

    css_vars = light_vars if is_light else dark_vars

    # ── LIGHT-ONLY OVERRIDES (ChronoTask style) ─────────────────────────────
    light_extra = """
    /* ── ChronoTask dot-grid background ── */
    .stApp::before {
        background-image: radial-gradient(circle, rgba(37,99,235,0.13) 1px, transparent 1px) !important;
        background-size: 26px 26px !important;
    }

    /* ── Typography: Inter heavy headings ── */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 900 !important;
        color: #0f172a !important;
        letter-spacing: -0.03em !important;
        text-shadow: none !important;
    }
    .gradient-text {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 60%, #0ea5e9 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.03em !important;
    }

    /* ── Hero panel ── */
    .page-hero {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 24px !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.09), 0 4px 16px rgba(0,0,0,0.05) !important;
        position: relative;
        overflow: visible !important;
    }
    .page-hero::before {
        background: radial-gradient(circle, rgba(37,99,235,0.06) 0%, transparent 70%) !important;
        top: -60px !important; right: -60px !important;
        width: 280px !important; height: 280px !important;
    }
    .page-hero p { color: #64748b !important; }

    /* Hero badge pill */
    .hero-badge {
        background: #dbeafe !important;
        border: 1px solid rgba(37,99,235,0.2) !important;
        color: #2563eb !important;
        font-family: 'DM Mono', monospace !important;
        border-radius: 99px !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.06em !important;
        padding: 5px 14px !important;
    }

    /* Two-tone hero headings */
    .hero-title-primary {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: #0f172a;
        letter-spacing: -0.04em;
        line-height: 1.05;
        margin: 0;
    }
    .hero-title-secondary {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: #94a3b8;
        letter-spacing: -0.04em;
        line-height: 1.05;
        margin: 0 0 16px 0;
    }

    /* Floating decorative mini-cards */
    .hero-float-card {
        position: absolute;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 16px;
        padding: 14px 18px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.06);
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        color: #1e293b;
        animation: floatCard 4s ease-in-out infinite;
        pointer-events: none;
        z-index: 10;
    }
    .hero-float-left  { top: 16px; left: 12px; animation-delay: 0s; }
    .hero-float-right { top: 12px; right: 12px; animation-delay: 1.5s; }

    @keyframes floatCard {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33%  { transform: translateY(-7px) rotate(0.5deg); }
        66%  { transform: translateY(-3px) rotate(-0.5deg); }
    }

    /* ── Cards: white + soft shadow (no bold comic border) ── */
    .card, .stat-card, .domain-card, .candidate-card {
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04) !important;
        border-radius: 16px !important;
    }
    .card:hover, .stat-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 36px rgba(0,0,0,0.11), 0 4px 12px rgba(0,0,0,0.06) !important;
    }
    .domain-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 16px 44px rgba(0,0,0,0.12) !important;
    }
    .candidate-card:hover {
        transform: translateX(4px) !important;
        border-color: #2563eb !important;
        box-shadow: 0 8px 24px rgba(37,99,235,0.12) !important;
    }

    /* ── Buttons: solid blue (ChronoTask CTA style) ── */
    .stButton > button {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.35) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(37,99,235,0.45) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
    }

    /* Download buttons */
    [data-testid="stDownloadButton"] > button {
        background: #ffffff !important;
        border: 1.5px solid rgba(0,0,0,0.12) !important;
        color: #2563eb !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: #dbeafe !important;
        border-color: #2563eb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.15) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 2px 0 12px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stSidebar"] * { color: #1e293b !important; }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #dbeafe !important;
        color: #2563eb !important;
        font-weight: 700 !important;
        border-left: none !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #f8faff !important;
        color: #0f172a !important;
    }

    /* ── Progress bar ── */
    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #0ea5e9, #2563eb) !important;
    }

    /* ── Chips: colorful pastel ── */
    .chip-teal   { background: #f0fdf4 !important; color: #15803d !important; border-color: #bbf7d0 !important; }
    .chip-indigo { background: #eef2ff !important; color: #4338ca !important; border-color: #c7d2fe !important; }
    .chip-pink   { background: #fdf4ff !important; color: #a21caf !important; border-color: #f5d0fe !important; }
    .chip-green  { background: #f0fdf4 !important; color: #16a34a !important; border-color: #bbf7d0 !important; }
    .chip-warn   { background: #fffbeb !important; color: #d97706 !important; border-color: #fde68a !important; }
    .chip-danger { background: #fef2f2 !important; color: #dc2626 !important; border-color: #fecaca !important; }

    /* ── Score bar track ── */
    .score-bar-track { background: #f1f5f9 !important; }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #f8faff !important;
        border: 2px dashed rgba(37,99,235,0.28) !important;
        border-radius: 14px !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(37,99,235,0.55) !important;
        background: rgba(37,99,235,0.03) !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p { color: #64748b !important; }

    /* ── Text area ── */
    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        border: 1.5px solid rgba(0,0,0,0.12) !important;
        border-radius: 12px !important;
        color: #0f172a !important;
    }
    [data-testid="stTextArea"] textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.1) !important;
    }

    /* ── Alert ── */
    [data-testid="stAlert"] {
        background: #f8faff !important;
        border: 1px solid rgba(0,0,0,0.09) !important;
        border-radius: 12px !important;
        color: #0f172a !important;
    }

    /* ── Page header ── */
    header[data-testid="stHeader"] {
        background: rgba(242,245,252,0.85) !important;
        border-bottom: 1px solid rgba(0,0,0,0.07) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* ── Section label ── */
    .section-label { color: #94a3b8 !important; }
    .section-label::after { background: rgba(0,0,0,0.1) !important; }
    hr { border-color: rgba(0,0,0,0.08) !important; border-style: solid !important; }

    /* ── Domain titles ── */
    .domain-title { color: #0f172a !important; font-family: 'Inter', sans-serif !important; letter-spacing: -0.01em !important; font-size: 0.9rem !important; }
    .domain-item  { color: #475569 !important; border-bottom-color: rgba(0,0,0,0.06) !important; }

    /* ── Fit score badge ── */
    .fit-score-badge { font-family: 'Inter', sans-serif !important; letter-spacing: -0.03em !important; }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] th { background: #f8faff !important; color: #94a3b8 !important; border-bottom: 1px solid rgba(0,0,0,0.08) !important; }
    [data-testid="stDataFrame"] td { color: #0f172a !important; border-bottom-color: rgba(0,0,0,0.05) !important; }

    /* ── Caption ── */
    [data-testid="stCaptionContainer"] { color: #94a3b8 !important; }

    /* ── Multiselect tags ── */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    """ if is_light else ""

    # ── DARK-ONLY EXTRAS ────────────────────────────────────────────────────
    dark_extra = """
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }
    """ if not is_light else ""

    st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Syne:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Bangers&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">

<style>

/* ── ROOT TOKENS ─────────────────────────────────────────────────── */
:root {{
    {css_vars}
}}

/* ── HIDE STREAMLIT DEPLOY BUTTON ─────────────────────────────────── */
[data-testid="stAppDeployButton"],
.stDeployButton,
[data-testid="stToolbar"] button[kind="header"] {{
    display: none !important;
    visibility: hidden !important;
}}

/* ── BASE ────────────────────────────────────────────────────────── */
html, body, .stApp {{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}}

/* ── SIDEBAR ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{ font-family: var(--font-body) !important; }}
[data-testid="stSidebarHeader"],
[data-testid="stSidebar"] [data-testid="stLogo"],
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] + div,
[data-testid="stSidebar"] header,
[data-testid="stSidebarUserContent"] > div:first-child > [data-testid="stMarkdownContainer"]:empty {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}}
[data-testid="stSidebarNav"] a {{
    border-radius: 10px !important;
    margin: 2px 8px !important;
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
    color: var(--muted2) !important;
    transition: all 0.18s !important;
}}
[data-testid="stSidebarNav"] a:hover {{
    background: var(--surface2) !important;
    color: var(--text) !important;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background: rgba(110, 231, 183, 0.1) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}}

/* ── TYPOGRAPHY ──────────────────────────────────────────────────── */
h1 {{ font-family: var(--font-display) !important; font-weight: 800 !important; font-size: 2rem !important; letter-spacing: -0.02em !important; }}
h2 {{ font-family: var(--font-display) !important; font-weight: 700 !important; }}
h3, h4 {{ font-family: var(--font-display) !important; font-weight: 700 !important; }}

/* ── PAGE HEADER HERO ────────────────────────────────────────────── */
.page-hero {{
    background: linear-gradient(135deg, var(--surface2) 0%, var(--surface3) 100%);
    border: 1px solid var(--border2);
    border-radius: var(--r-lg);
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.4s ease both;
}}
.page-hero::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(110,231,183,0.08), transparent 70%);
}}
.page-hero h1 {{ color: var(--text) !important; margin-bottom: 6px !important; }}
.page-hero p {{ color: var(--muted2) !important; font-size: 0.9rem !important; margin: 0 !important; }}
.page-hero .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(110,231,183,0.1);
    border: 1px solid rgba(110,231,183,0.2);
    border-radius: 99px;
    padding: 4px 12px;
    font-size: 0.72rem;
    font-family: var(--font-mono);
    color: var(--accent);
    letter-spacing: 0.06em;
    margin-bottom: 14px;
}}

/* ── STAT CARDS ──────────────────────────────────────────────────── */
.stat-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    animation: fadeUp 0.4s ease both;
}}
.stat-card:hover {{ transform: translateY(-3px); border-color: var(--border2); }}
.stat-card-label {{
    font-family: var(--font-mono);
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 10px;
}}
.stat-card-value {{
    font-family: var(--font-display);
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 6px;
}}
.stat-card-delta {{
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--muted2);
}}

/* ── CARDS ───────────────────────────────────────────────────────── */
.card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 22px 26px;
    margin-bottom: 16px;
    animation: fadeUp 0.35s ease both;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.card-title {{
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 4px;
    color: var(--text);
}}
.card-sub {{
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

/* ── UPLOAD ZONE ─────────────────────────────────────────────────── */
.upload-zone {{
    border: 1.5px dashed rgba(110,231,183,0.25);
    border-radius: var(--r);
    padding: 36px;
    text-align: center;
    background: rgba(110,231,183,0.02);
    transition: all 0.2s;
    margin: 8px 0 16px;
}}
.upload-zone:hover {{
    border-color: rgba(110,231,183,0.45);
    background: rgba(110,231,183,0.04);
}}
.upload-icon {{ font-size: 2.4rem; margin-bottom: 10px; display: block; }}
.upload-text {{ color: var(--muted2); font-size: 0.88rem; line-height: 1.5; }}
.upload-text b {{ color: var(--accent); }}

/* Override Streamlit file uploader */
[data-testid="stFileUploader"] {{
    background: var(--surface2) !important;
    border: 1.5px dashed rgba(110,231,183,0.2) !important;
    border-radius: var(--r) !important;
    padding: 20px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: rgba(110,231,183,0.4) !important;
}}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p {{
    color: var(--muted2) !important;
    font-family: var(--font-body) !important;
}}

/* ── BUTTONS ─────────────────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
    letter-spacing: 0.01em !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}

/* Download buttons */
[data-testid="stDownloadButton"] > button {{
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--accent) !important;
    box-shadow: none !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: var(--surface3) !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(110,231,183,0.15) !important;
}}

/* ── PROGRESS BAR ────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {{
    background: var(--surface2) !important;
    border-radius: 99px !important;
    height: 6px !important;
}}
[data-testid="stProgressBar"] > div > div {{
    background: linear-gradient(90deg, var(--accent2), var(--accent)) !important;
    border-radius: 99px !important;
}}

/* ── SCORE BAR COMPONENT ─────────────────────────────────────────── */
.score-bar-wrap {{ margin: 6px 0; }}
.score-bar-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
    font-size: 0.8rem;
}}
.score-bar-label {{ color: var(--text); }}
.score-bar-value {{
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 500;
}}
.score-bar-track {{
    height: 6px;
    background: var(--surface3);
    border-radius: 99px;
    overflow: hidden;
}}
.score-bar-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* ── CHIPS ───────────────────────────────────────────────────────── */
.chip {{
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-family: var(--font-mono);
    font-weight: 500;
    margin: 3px;
    border: 1px solid transparent;
    transition: all 0.15s;
}}
.chip-teal   {{ background: rgba(110,231,183,0.1); color: var(--accent);  border-color: rgba(110,231,183,0.2); }}
.chip-indigo {{ background: rgba(129,140,248,0.1); color: var(--accent2); border-color: rgba(129,140,248,0.2); }}
.chip-pink   {{ background: rgba(244,114,182,0.1); color: var(--accent3); border-color: rgba(244,114,182,0.2); }}
.chip-green  {{ background: rgba(74,222,128,0.1);  color: var(--ok);      border-color: rgba(74,222,128,0.2); }}
.chip-warn   {{ background: rgba(251,146,60,0.1);  color: var(--warn);    border-color: rgba(251,146,60,0.2); }}
.chip-danger {{ background: rgba(248,113,113,0.1); color: var(--danger);  border-color: rgba(248,113,113,0.2); }}

/* ── CANDIDATE RESULT CARD ───────────────────────────────────────── */
.candidate-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 20px 24px;
    margin-bottom: 12px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 16px;
    align-items: center;
    transition: all 0.2s;
    animation: fadeUp 0.35s ease both;
}}
.candidate-card:hover {{
    border-color: var(--border2);
    background: var(--surface2);
    transform: translateX(3px);
}}
.candidate-card-name {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text);
    margin-bottom: 4px;
}}
.candidate-card-meta {{
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--muted);
}}
.fit-score-badge {{
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 1.6rem;
    text-align: right;
    line-height: 1;
}}
.fit-score-label {{
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    text-align: right;
    margin-top: 2px;
}}

/* ── DOMAIN GRID ─────────────────────────────────────────────────── */
.domain-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin: 20px 0;
}}
@media (min-width: 1100px) {{ .domain-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (min-width: 1400px) {{ .domain-grid {{ grid-template-columns: repeat(5, 1fr); }} }}
.domain-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 18px 20px;
    transition: all 0.25s;
    animation: fadeUp 0.35s ease both;
}}
.domain-card:hover {{
    transform: translateY(-4px);
    border-color: var(--border2);
    box-shadow: var(--shadow);
}}
.domain-title {{
    font-family: var(--font-display);
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 10px;
}}
.domain-item {{
    font-size: 0.78rem;
    color: var(--muted2);
    padding: 4px 0;
    border-bottom: 1px solid var(--border);
    font-family: var(--font-mono);
    display: flex;
    align-items: center;
    gap: 6px;
}}
.domain-item:last-child {{ border-bottom: none; }}
.domain-empty {{
    font-size: 0.75rem;
    color: var(--muted);
    font-style: italic;
    font-family: var(--font-mono);
}}

/* ── DATAFRAME OVERRIDE ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
}}
[data-testid="stDataFrame"] table {{ background: var(--surface) !important; }}
[data-testid="stDataFrame"] th {{
    background: var(--surface2) !important;
    color: var(--muted2) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
}}
[data-testid="stDataFrame"] td {{
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid var(--border) !important;
}}

/* ── ALERTS ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
    background: var(--surface2) !important;
    border-radius: var(--r) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
}}

/* ── SPINNER ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div > div {{ border-top-color: var(--accent) !important; }}

/* ── SLIDER ──────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {{ background: var(--accent2) !important; }}

/* ── TEXT AREA ───────────────────────────────────────────────────── */
[data-testid="stTextArea"] textarea {{
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 0.88rem !important;
}}
[data-testid="stTextArea"] textarea:focus {{
    border-color: var(--accent2) !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.15) !important;
}}

/* ── CAPTION ─────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] {{
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
}}

/* ── DIVIDER ─────────────────────────────────────────────────────── */
hr {{ border-color: var(--border) !important; }}

/* ── SECTION LABEL ───────────────────────────────────────────────── */
.section-label {{
    font-family: var(--font-mono);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--muted);
    margin: 24px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}}

/* ── ANIMATIONS ──────────────────────────────────────────────────── */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes pulse-glow {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(110,231,183,0.15); }}
    50%       {{ box-shadow: 0 0 0 8px rgba(110,231,183,0); }}
}}

/* ── GRADIENT TEXT (dark default) ────────────────────────────────── */
.gradient-text {{
    background: linear-gradient(135deg, #6ee7b7 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* ── STREAMLIT CHROME ─────────────────────────────────────────────── */
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"][aria-expanded="true"],
[data-testid="stSidebar"][aria-expanded="false"] {{
    min-width: 220px !important;
}}
[data-testid="collapsedControl"] {{ color: var(--muted2) !important; }}
.block-container {{ padding-top: 2rem !important; padding-bottom: 3rem !important; }}

{dark_extra}
{light_extra}

</style>
""", unsafe_allow_html=True)


def score_color(score: float, max_score: float = 65) -> str:
    """Return a CSS color string based on score percentage."""
    pct = score / max_score
    if pct >= 0.75:
        return "var(--ok)"
    if pct >= 0.5:
        return "var(--accent)"
    if pct >= 0.3:
        return "var(--warn)"
    return "var(--danger)"


def render_score_bar(label: str, value: float, max_val: float, color: str = "var(--accent2)") -> str:
    """Return HTML for a labelled score bar."""
    pct = min(100, round(value / max_val * 100))
    return f"""
<div class="score-bar-wrap">
  <div class="score-bar-header">
    <span class="score-bar-label">{label}</span>
    <span class="score-bar-value" style="color:{color}">{value}</span>
  </div>
  <div class="score-bar-track">
    <div class="score-bar-fill" style="width:{pct}%;background:{color}"></div>
  </div>
</div>"""


def render_chip(text: str, style: str = "chip-indigo") -> str:
    return f'<span class="chip {style}">{text}</span>'
