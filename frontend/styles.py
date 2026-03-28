"""
frontend/styles.py — Shared design system for all pages.

Premium SaaS redesign:
  - Deep navy dark theme with solid surfaces (no glass/blur)
  - Muted blue accent palette (no neon)
  - Clean typography: Inter (body) + JetBrains Mono (data)
  - Custom smooth-follow cursor with hover scaling
  - Subtle mount/hover animations only
  - Full Streamlit native element overrides
"""

import streamlit as st


def inject_styles() -> None:
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">

<style>

/* ── ROOT TOKENS ─────────────────────────────────────────────────── */
:root {
    --bg:        #0f1117;
    --surface:   #161b26;
    --surface2:  #1c2333;
    --surface3:  #232c3d;
    --border:    #1e2536;
    --border2:   #2a3448;
    --border3:   #364258;

    --accent:    #4f8ff7;
    --accent-hover: #3d7ce8;
    --accent-muted: rgba(79, 143, 247, 0.10);
    --accent-soft: rgba(79, 143, 247, 0.06);

    --text:      #e2e8f0;
    --text2:     #c1c9d6;
    --muted:     #64748b;
    --muted2:    #8896ab;

    --ok:        #4ade80;
    --ok-muted:  rgba(74, 222, 128, 0.10);
    --warn:      #e5a63e;
    --warn-muted: rgba(229, 166, 62, 0.10);
    --danger:    #ef4444;
    --danger-muted: rgba(239, 68, 68, 0.10);
    --purple:    #a78bfa;
    --purple-muted: rgba(167, 139, 250, 0.10);
    --pink:      #f472b6;
    --pink-muted: rgba(244, 114, 182, 0.10);

    --r:         12px;
    --r-lg:      16px;
    --shadow:    0 1px 3px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.2);
    --shadow-lg: 0 4px 16px rgba(0,0,0,0.35);
}

/* ── BASE ────────────────────────────────────────────────────────── */
html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── SIDEBAR ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #111620 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    margin: 2px 8px !important;
    padding: 10px 14px !important;
    font-size: 0.86rem !important;
    color: var(--muted2) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: var(--accent-soft) !important;
    color: var(--text) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: var(--accent-muted) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}

/* ── TYPOGRAPHY ──────────────────────────────────────────────────── */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    letter-spacing: -0.03em !important;
    color: var(--text) !important;
}
h2 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
h3, h4 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}

/* ── HERO ────────────────────────────────────────────────────────── */
.page-hero {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 36px 40px;
    margin-bottom: 28px;
    animation: fadeIn 0.4s ease both;
}
.page-hero h1 {
    margin-bottom: 8px !important;
}
.page-hero p {
    color: var(--muted2) !important;
    font-size: 0.92rem !important;
    margin: 0 !important;
    line-height: 1.65 !important;
    max-width: 600px;
}
.hero-badge {
    display: inline-block;
    background: var(--accent-muted);
    color: var(--accent);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.04em;
    margin-bottom: 14px;
}

/* ── STAT CARDS ──────────────────────────────────────────────────── */
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 22px 24px;
    transition: border-color 0.2s ease, transform 0.2s ease;
    animation: fadeSlide 0.35s ease both;
}
.stat-card:hover {
    border-color: var(--border2);
    transform: translateY(-2px);
}
.stat-card-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 10px;
}
.stat-card-value {
    font-family: 'Inter', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
}

/* ── CARDS ───────────────────────────────────────────────────────── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 22px 26px;
    margin-bottom: 14px;
    animation: fadeSlide 0.3s ease both;
    transition: border-color 0.2s ease;
}
.card:hover {
    border-color: var(--border2);
}
.card-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 3px;
}
.card-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── UPLOAD ZONE ─────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: var(--r) !important;
    padding: 20px !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p {
    color: var(--muted2) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── BUTTONS ─────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(79,143,247,0.2) !important;
}
.stButton > button:hover {
    background: var(--accent-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(79,143,247,0.28) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Download buttons — secondary style */
[data-testid="stDownloadButton"] > button {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--accent) !important;
    box-shadow: none !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: var(--surface3) !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
}

/* ── PROGRESS BAR ────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: var(--surface3) !important;
    border-radius: 4px !important;
    height: 6px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: var(--accent) !important;
    border-radius: 4px !important;
}

/* ── SCORE BAR ───────────────────────────────────────────────────── */
.score-bar-wrap { margin: 7px 0; }
.score-bar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
    font-size: 0.82rem;
}
.score-bar-label { color: var(--text2); font-weight: 500; }
.score-bar-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    font-weight: 500;
}
.score-bar-track {
    height: 6px;
    background: var(--surface3);
    border-radius: 4px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── CHIPS ───────────────────────────────────────────────────────── */
.chip {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    margin: 2px;
    transition: background 0.15s ease;
}
.chip-teal   { background: var(--accent-muted); color: var(--accent); }
.chip-indigo { background: var(--purple-muted); color: var(--purple); }
.chip-pink   { background: var(--pink-muted);   color: var(--pink); }
.chip-green  { background: var(--ok-muted);     color: var(--ok); }
.chip-warn   { background: var(--warn-muted);   color: var(--warn); }
.chip-danger { background: var(--danger-muted); color: var(--danger); }

/* ── CANDIDATE CARD ──────────────────────────────────────────────── */
.candidate-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 22px 26px;
    margin-bottom: 12px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 20px;
    align-items: center;
    transition: border-color 0.2s ease, transform 0.2s ease;
    animation: fadeSlide 0.3s ease both;
}
.candidate-card:hover {
    border-color: var(--border2);
    transform: translateY(-2px);
}
.candidate-card-name {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text);
    margin-bottom: 3px;
}
.candidate-card-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
}
.fit-score-badge {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 1.7rem;
    text-align: right;
    line-height: 1;
    letter-spacing: -0.02em;
}
.fit-score-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    text-align: right;
    margin-top: 3px;
}

/* ── DOMAIN GRID ─────────────────────────────────────────────────── */
.domain-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin: 18px 0;
}
@media (min-width: 1100px) {
    .domain-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 1400px) {
    .domain-grid { grid-template-columns: repeat(5, 1fr); }
}
.domain-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 18px 20px;
    transition: border-color 0.2s ease, transform 0.2s ease;
    animation: fadeSlide 0.3s ease both;
}
.domain-card:hover {
    border-color: var(--border2);
    transform: translateY(-2px);
}
.domain-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 10px;
}
.domain-item {
    font-size: 0.78rem;
    color: var(--muted2);
    padding: 4px 0;
    border-bottom: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 7px;
}
.domain-item:last-child { border-bottom: none; }
.domain-empty {
    font-size: 0.75rem;
    color: var(--muted);
    font-style: italic;
}

/* ── DATAFRAME OVERRIDE ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table { background: var(--surface) !important; }
[data-testid="stDataFrame"] th {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── ALERTS ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: var(--surface2) !important;
    border-radius: var(--r) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
}

/* ── SPINNER ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div > div {
    border-top-color: var(--accent) !important;
}

/* ── SLIDER ──────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
}

/* ── TEXT AREA ───────────────────────────────────────────────────── */
[data-testid="stTextArea"] textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-muted) !important;
}

/* ── MULTISELECT ─────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
}

/* ── CAPTION ─────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
}

/* ── DIVIDER ─────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── SECTION LABEL ───────────────────────────────────────────────── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--muted);
    margin: 26px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── ANIMATIONS ──────────────────────────────────────────────────── */
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── SCROLLBAR ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--border3); }

/* ── PURE CSS CUSTOM SVG CURSOR ─────────────────────────────────── */
/* Default ring cursor */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    cursor: url('data:image/svg+xml;utf8,<svg width="28" height="28" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="14" r="12" fill="none" stroke="%234f8ff7" stroke-width="2"/></svg>') 14 14, auto !important;
}

/* Expanded ring on hover for interactive elements */
button, a, a *, button *, [role="slider"], [role="button"], [data-testid="stFileUploader"] *, [data-testid="stDownloadButton"] *, input, textarea, select, .stButton * {
    cursor: url('data:image/svg+xml;utf8,<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="18" fill="rgba(79,143,247,0.15)" stroke="%234f8ff7" stroke-width="2"/></svg>') 20 20, pointer !important;
}

/* Hide Streamlit branding & sidebar collapse button ("keyboard_double" text) */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] { display: none !important; }
.block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; }

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


def render_score_bar(label: str, value: float, max_val: float, color: str = "var(--accent)") -> str:
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


def render_chip(text: str, style: str = "chip-teal") -> str:
    return f'<span class="chip {style}">{text}</span>'

def render_top_nav() -> None:
    """Renders a horizontal top navigation bar replacing the default sidebar."""
    st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNavItems"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
.notif-bell {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.88rem;
    color: var(--text);
    text-decoration: none;
    font-weight: 600;
}
.notif-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--danger);
    color: #fff;
    border-radius: 50%;
    min-width: 20px;
    height: 20px;
    font-size: 0.65rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)
    
    if not st.session_state.get("logged_in"):
        return

    role = st.session_state.get("role", "hr")
    user_name = st.session_state.get("user_name", "User")
    
    # Layout with logout button on the right
    n_cols = st.columns([10, 2])
    
    with n_cols[0]:
        if role == "student":
            # Count unread notifications for this student
            import json, os
            _base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            _jobs_path = os.path.join(_base, "outputs", "jobs.json")
            _student_domain = st.session_state.get("student_domain", "")
            _notif_count = 0
            if os.path.exists(_jobs_path):
                try:
                    with open(_jobs_path) as _f:
                        _all_jobs = json.load(_f)
                    _notif_count = sum(1 for j in _all_jobs if j.get("domain") == _student_domain)
                except Exception:
                    pass

            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            with c1:
                st.page_link("pages/1_Resume_Analysis.py", label="Resume Analysis")
            with c2:
                st.page_link("pages/6_Resume_Builder.py", label="📝 Resume Builder")
            with c3:
                _bell_label = f"🔔 Notifications ({_notif_count})" if _notif_count > 0 else "🔔 Notifications"
                st.page_link("pages/5_Notifications.py", label=_bell_label)
            with c4:
                st.markdown(f"<div style='font-size:0.8rem;color:var(--muted2);padding-top:8px;text-align:right'>👤 {user_name}</div>", unsafe_allow_html=True)
        else:
            c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 1, 1])
            with c1: st.page_link("app.py", label="App Overview")
            with c2: st.page_link("pages/1_Resume_Analysis.py", label="Resume Analysis")
            with c3: st.page_link("pages/2_Best_Profile.py", label="Best Profiles")
            with c4: st.page_link("pages/3_Compare_Resumes.py", label="Compare Resumes")
            with c5: st.page_link("pages/4_Post_Job.py", label="📋 Post Job")
            with c6:
                st.markdown(f"<div style='font-size:0.8rem;color:var(--muted2);padding-top:8px;text-align:right'>👤 {user_name}</div>", unsafe_allow_html=True)
            
    with n_cols[1]:
        if st.button("Log Out", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.session_state["user_id"] = None
            st.session_state["user_name"] = None
            st.session_state["student_domain"] = None
            st.switch_page("app.py")
            
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px;'/>", unsafe_allow_html=True)

