"""
frontend/app.py — Main page: bulk upload, analysis, ranking, domain classification.
Premium SaaS UI redesign — clean, intentional, human-designed.
"""

import streamlit as st
import os
import sys
import json
import pandas as pd


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import save_result, get_database_status
from backend.extractor import extract_text
from backend.section_splitter import split_sections
from backend.scorer import score_resume
from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES, get_model
from backend.utils import sanitize_filename
from frontend.styles import inject_styles, score_color, render_score_bar, render_chip, render_top_nav

RESUME_DIR = os.path.join(BASE_DIR, "resumes")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

DOMAIN_COLORS = {
    "Machine Learning":    ("#4f8ff7", "chip-teal"),
    "Data Science":        ("#a78bfa", "chip-indigo"),
    "Web Development":     ("#4ade80", "chip-green"),
    "Cloud / DevOps":      ("#e5a63e", "chip-warn"),
    "Android Development": ("#f472b6", "chip-pink"),
}

# ── Cache model ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return get_model()


# ── Styles ────────────────────────────────────────────────────────────────────
inject_styles()

# ── User credentials database ─────────────────────────────────────────────────
USERS = {
    "hr001":  {"password": "hr123",  "name": "Priya Sharma",  "role": "hr",      "domain": None},
    "hr002":  {"password": "hr456",  "name": "Rahul Verma",   "role": "hr",      "domain": None},
    "stu001": {"password": "stu123", "name": "Rishabh Gupta", "role": "student", "domain": "Machine Learning"},
    "stu002": {"password": "stu456", "name": "Ananya Singh",  "role": "student", "domain": "Machine Learning"},
    "stu003": {"password": "stu789", "name": "Arjun Mehta",   "role": "student", "domain": "Machine Learning"},
    "stu004": {"password": "stu321", "name": "Sneha Patel",   "role": "student", "domain": "Web Development"},
    "stu005": {"password": "stu654", "name": "Vikram Reddy",  "role": "student", "domain": "Web Development"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.student_domain = None

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h2 style='text-align:center; margin-top: 100px; font-weight:800; letter-spacing: 1px;'>DASHBOARD</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        _, sel_col, _ = st.columns([1, 2, 1])
        with sel_col:
            role_selection = st.selectbox("Role", ["Select", "HR", "Student"], label_visibility="collapsed")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        user_col1, user_col2 = st.columns([1, 3])
        with user_col1:
            st.markdown("<div style='margin-top: 8px; font-weight: 600; font-size: 1.1rem;'>User id</div>", unsafe_allow_html=True)
        with user_col2:
            user_id = st.text_input("User id", label_visibility="collapsed")
            
        pass_col1, pass_col2 = st.columns([1, 3])
        with pass_col1:
            st.markdown("<div style='margin-top: 8px; font-weight: 600; font-size: 1.1rem;'>Password</div>", unsafe_allow_html=True)
        with pass_col2:
            password = st.text_input("Password", type="password", label_visibility="collapsed")
            
        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([1, 1.5, 1])
        with btn_col:
            if st.button("Login", use_container_width=True):
                if role_selection == "Select":
                    st.error("Please select a specific role.")
                elif not user_id or not password:
                    st.error("Please enter credentials.")
                elif user_id not in USERS:
                    st.error("Invalid user ID.")
                elif USERS[user_id]["password"] != password:
                    st.error("Incorrect password.")
                elif USERS[user_id]["role"] != role_selection.lower().strip():
                    st.error(f"User '{user_id}' is not registered as {role_selection}.")
                else:
                    user = USERS[user_id]
                    st.session_state.logged_in = True
                    st.session_state.role = user["role"]
                    st.session_state.user_id = user_id
                    st.session_state.user_name = user["name"]
                    st.session_state.student_domain = user.get("domain")
                    if st.session_state.role == "student":
                        st.switch_page("pages/1_Resume_Analysis.py")
                    else:
                        st.rerun()
                    
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.stop()

if st.session_state.role == "student":
    st.switch_page("pages/1_Resume_Analysis.py")

render_top_nav()

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in [
    ("analysis_running", False),
    ("analysis_done", False),
    ("overwrite_confirmed", False),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── File paths ────────────────────────────────────────────────────────────────
ranking_path   = os.path.join(OUTPUT_DIR, "ranking.csv")
extracted_path = os.path.join(OUTPUT_DIR, "extracted.json")
domains_path   = os.path.join(OUTPUT_DIR, "domains.json")
results_exist  = os.path.exists(ranking_path) and os.path.exists(extracted_path)

if results_exist and not st.session_state.analysis_done:
    st.session_state.analysis_done = True

# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hero">
  <div class="hero-badge">ResumeIQ</div>
  <h1>Resume Intelligence</h1>
  <p>Upload resumes for instant scoring, ranking, and domain classification powered by semantic AI.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Upload</div>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <div class="card-title">Upload Resumes</div>
  <div class="card-sub">PDF · DOCX · TXT &nbsp;·&nbsp; Multiple files supported</div>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drag & drop resumes here, or click to browse",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Supported: PDF, DOCX, TXT. Max 10 MB per file.",
)

# Show database status
db_status = get_database_status()
if db_status["connected"]:
    st.caption(
        f"✓ Connected: {db_status['db_name']}.{db_status['collection_name']}"
    )
else:
    st.warning(
        "MongoDB not connected. Saving to Atlas is disabled. "
        f"Reason: {db_status['error'] or 'unknown error'}"
    )

# ── Analyse button + re-run guard ─────────────────────────────────────────────
btn_col, info_col = st.columns([1, 4])
with btn_col:
    analyze = st.button("Analyse Resumes", use_container_width=True)

if analyze and results_exist and not st.session_state.overwrite_confirmed:
    with info_col:
        st.warning("Previous results exist. Click **Analyse** again to overwrite them.")
    st.session_state.overwrite_confirmed = True
    st.stop()

if analyze:
    st.session_state.overwrite_confirmed = False

# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS LOGIC
# ══════════════════════════════════════════════════════════════════════════════
saved_paths: list[str] = []

if analyze and not st.session_state.analysis_running:

    if not uploaded_files:
        st.warning("Please upload at least one resume before running analysis.")
        st.stop()

    st.session_state.analysis_running = True
    st.session_state.analysis_done    = False

    st.markdown('<div class="section-label">Processing</div>', unsafe_allow_html=True)
    progress = st.progress(0, text="Starting analysis…")
    status   = st.empty()

    results: list[dict]   = []
    extracted_data: dict  = {}
    total = len(uploaded_files)

    for idx, file in enumerate(uploaded_files, start=1):
        pct  = int((idx / total) * 100)
        safe_name = sanitize_filename(file.name)
        progress.progress(pct, text=f"Analysing {safe_name} ({idx}/{total})…")
        status.caption(f"Processing {safe_name}…")

        path = os.path.join(RESUME_DIR, safe_name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        saved_paths.append(path)

        text     = extract_text(path)
        sections = split_sections(text)
        score    = score_resume(sections)

        results.append({"resume": safe_name, "score": score, "sections": sections})
        extracted_data[safe_name] = sections

        data = {
            "resume_name": safe_name,
            "score": score,
            "sections": sections,
        }
        save_result(data)

    # Save outputs
    ranking_df = pd.DataFrame(
        [{"Resume": r["resume"], "Score": r["score"]} for r in results]
    ).sort_values("Score", ascending=False)
    ranking_df.to_csv(ranking_path, index=False)

    with open(extracted_path, "w") as f:
        json.dump(extracted_data, f, indent=2)

    search_engine = ResumeSemanticSearch()
    search_engine.index_resumes(results)
    domain_groups = search_engine.classify_by_domain(DOMAIN_QUERIES)

    with open(domains_path, "w") as f:
        json.dump(domain_groups, f, indent=2)

    for p in saved_paths:
        try:
            os.remove(p)
        except OSError:
            pass

    st.session_state.analysis_running = False
    st.session_state.analysis_done    = True
    progress.progress(100, text="Analysis complete.")
    status.empty()

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.analysis_done:

    ranking_df = pd.read_csv(ranking_path)

    with open(domains_path) as f:
        domain_groups = json.load(f)

    total_resumes  = len(ranking_df)
    avg_score      = round(ranking_df["Score"].mean(), 1) if total_resumes else 0
    top_score      = ranking_df["Score"].max() if total_resumes else 0
    domain_hits    = sum(1 for v in domain_groups.values() if v)

    # ── Stat cards ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Resumes Analysed", str(total_resumes), "var(--accent)",  ""),
        (c2, "Avg. Score",       f"{avg_score}",     "var(--purple)",  "/ 65"),
        (c3, "Top Score",        f"{top_score}",     "var(--ok)",      "/ 65"),
        (c4, "Domains Detected", str(domain_hits),   "var(--warn)",    f"/ {len(domain_groups)}"),
    ]
    for col, label, val, color, suffix in cards:
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-card-label">{label}</div>
  <div class="stat-card-value" style="color:{color}">{val}<span style="font-size:0.85rem;color:var(--muted);margin-left:4px;font-weight:400">{suffix}</span></div>
</div>""", unsafe_allow_html=True)

    # ── Ranked table ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Rankings</div>', unsafe_allow_html=True)

    rows_html = ""
    for rank, (_, row) in enumerate(ranking_df.iterrows(), start=1):
        name  = row["Resume"]
        score = row["Score"]
        color = score_color(score)
        pct   = min(100, round(score / 65 * 100))
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

        rows_html += f"""
<div style="display:grid;grid-template-columns:44px 1fr 200px 72px;align-items:center;
            gap:14px;padding:12px 20px;
            border-bottom:1px solid var(--border);
            transition:background 0.15s ease;font-size:0.85rem;"
     onmouseover="this.style.background='var(--surface2)'"
     onmouseout="this.style.background='transparent'">
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:var(--muted)">{medal}</div>
  <div style="font-weight:600;color:var(--text)">{name}</div>
  <div>
    <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden">
      <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;transition:width 0.6s ease"></div>
    </div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:{color};text-align:right;font-weight:600">{score}</div>
</div>"""

    st.markdown(f"""
<div class="card" style="padding:0;overflow:hidden">
  <div style="display:grid;grid-template-columns:44px 1fr 200px 72px;gap:14px;
              padding:10px 20px;border-bottom:1px solid var(--border2);background:var(--surface2)">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">#</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Resume</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Score</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;text-align:right">Value</div>
  </div>
  {rows_html}
</div>""", unsafe_allow_html=True)

    # Download row
    dl1, dl2, _ = st.columns([1, 1, 3])
    with dl1:
        st.download_button(
            "Download CSV",
            data=open(ranking_path, "rb").read(),
            file_name="ranking.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        if os.path.exists(domains_path):
            st.download_button(
                "Download JSON",
                data=open(domains_path, "rb").read(),
                file_name="domains.json",
                mime="application/json",
                use_container_width=True,
            )

    # ── Domain classification ──────────────────────────────────────────────────
    st.markdown('<div class="section-label">Domain Classification</div>', unsafe_allow_html=True)

    st.markdown('<div class="domain-grid">', unsafe_allow_html=True)
    for domain, resumes in domain_groups.items():
        accent_color, chip_cls = DOMAIN_COLORS.get(domain, ("#4f8ff7", "chip-teal"))

        if resumes:
            items_html = "".join(
                f'<div class="domain-item">'
                f'<span style="width:5px;height:5px;border-radius:50%;background:{accent_color};'
                f'display:inline-block;flex-shrink:0"></span>'
                f'{r}</div>'
                for r in resumes
            )
        else:
            items_html = '<div class="domain-empty">No matches found</div>'

        st.markdown(f"""
<div class="domain-card" style="border-top:2px solid {accent_color}">
  <div class="domain-title">{domain}</div>
  {items_html}
  <div style="margin-top:10px">
    {render_chip(f"{len(resumes)} resume{'s' if len(resumes) != 1 else ''}", chip_cls)}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
