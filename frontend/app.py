"""
frontend/app.py — Main page: bulk upload, analysis, ranking, domain classification.
Full UI/UX redesign applied on top of all previous bug fixes.
"""

import streamlit as st
import os
import sys
import json
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — Dashboard",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.extractor import extract_text
from backend.section_splitter import split_sections
from backend.scorer import score_resume
from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES, get_model
from backend.utils import sanitize_filename
from frontend.styles import inject_styles, score_color, render_score_bar, render_chip

RESUME_DIR = os.path.join(BASE_DIR, "resumes")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

DOMAIN_COLORS = {
    "Machine Learning":    ("#818cf8", "chip-indigo"),
    "Data Science":        ("#22d3ee", "chip-teal"),
    "Web Development":     ("#4ade80", "chip-green"),
    "Cloud / DevOps":      ("#fb923c", "chip-warn"),
    "Android Development": ("#f87171", "chip-danger"),
}

# ── Cache model ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return get_model()

load_model()

# ── Styles ────────────────────────────────────────────────────────────────────
inject_styles()

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in [("analysis_running", False), ("analysis_done", False),
                 ("confirmed_overwrite", False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── File paths ────────────────────────────────────────────────────────────────
ranking_path   = os.path.join(OUTPUT_DIR, "ranking.csv")
extracted_path = os.path.join(OUTPUT_DIR, "extracted.json")
domains_path   = os.path.join(OUTPUT_DIR, "domains.json")
results_exist  = os.path.exists(ranking_path) and os.path.exists(extracted_path)

# Only auto-show old results if user hasn't started a new overwrite flow
if results_exist and not st.session_state.analysis_done and not st.session_state.confirmed_overwrite:
    st.session_state.analysis_done = True

# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
_is_light = st.session_state.get("theme", "dark") == "light"

if _is_light:
    # ChronoTask-style: two-tone heading + floating mini-cards
    st.markdown("""
<div class="page-hero">
  <!-- Floating mini-card: left -->
  <div class="hero-float-card hero-float-left" style="max-width:200px">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
      <span style="font-size:1.2rem">📄</span>
      <span style="font-weight:700;font-size:0.82rem;color:#0f172a">AI Resume Scoring</span>
    </div>
    <div style="font-size:0.72rem;color:#64748b;line-height:1.5">Semantic analysis &amp; instant ranking of all candidates</div>
    <div style="margin-top:10px;height:4px;background:#e2e8f0;border-radius:99px;overflow:hidden">
      <div style="width:78%;height:100%;background:#2563eb;border-radius:99px"></div>
    </div>
  </div>

  <!-- Floating mini-card: right -->
  <div class="hero-float-card hero-float-right" style="max-width:180px">
    <div style="font-size:0.65rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px">Top Domains</div>
    <div style="display:flex;flex-direction:column;gap:5px">
      <div style="display:flex;align-items:center;gap:7px;font-size:0.75rem;color:#0f172a;font-weight:500">
        <span style="width:8px;height:8px;border-radius:50%;background:#2563eb;flex-shrink:0"></span>Machine Learning
      </div>
      <div style="display:flex;align-items:center;gap:7px;font-size:0.75rem;color:#0f172a;font-weight:500">
        <span style="width:8px;height:8px;border-radius:50%;background:#7c3aed;flex-shrink:0"></span>Web Development
      </div>
      <div style="display:flex;align-items:center;gap:7px;font-size:0.75rem;color:#0f172a;font-weight:500">
        <span style="width:8px;height:8px;border-radius:50%;background:#0ea5e9;flex-shrink:0"></span>Data Science
      </div>
    </div>
  </div>

  <!-- Main hero content (centered) -->
  <div style="position:relative;z-index:2;text-align:center;padding:28px 60px 20px">
    <div class="hero-badge">⬡ ResumeIQ · Dashboard</div>
    <div class="hero-title-primary">Analyse, rank, and</div>
    <div class="hero-title-secondary">hire smarter with AI</div>
    <p style="margin:0 auto;max-width:460px;font-size:0.95rem">Upload a batch of resumes and get instant scoring, ranking, and domain classification powered by semantic AI.</p>
  </div>
</div>
""", unsafe_allow_html=True)
else:
    # Dark theme: original gradient heading
    st.markdown("""
<div class="page-hero">
  <div class="hero-badge">⬡ ResumeIQ · Dashboard</div>
  <h1 class="gradient-text">Resume Intelligence</h1>
  <p>Upload a batch of resumes and get instant scoring, ranking, and domain classification powered by semantic AI.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Upload</div>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <div class="card-title">📤 Upload Resumes</div>
  <div class="card-sub">PDF · DOCX · TXT &nbsp;·&nbsp; Multiple files supported</div>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drag & drop resumes here, or click to browse",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Supported: PDF, DOCX, TXT. Max 10 MB per file.",
)

# ── Analyse button + re-run guard ─────────────────────────────────────────────
btn_col, info_col = st.columns([1, 4])
with btn_col:
    analyze = st.button("🚀 Analyse Resumes", use_container_width=True)

if analyze and results_exist and st.session_state.analysis_done and not st.session_state.confirmed_overwrite:
    with info_col:
        st.warning("⚠️ Previous results exist. Click **Analyse** again to overwrite them.")
    st.session_state.analysis_done = False
    st.session_state.confirmed_overwrite = True
    st.stop()

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
        status.markdown(
            f'<p style="color:var(--muted2);font-family:\'DM Mono\',monospace;font-size:0.8rem;">'
            f'🔍 {safe_name}</p>',
            unsafe_allow_html=True,
        )

        path = os.path.join(RESUME_DIR, safe_name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        saved_paths.append(path)

        text     = extract_text(path)
        sections = split_sections(text)
        score    = score_resume(sections)

        results.append({"resume": safe_name, "score": score, "sections": sections})
        extracted_data[safe_name] = sections

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

    # Cleanup temp files
    for p in saved_paths:
        try:
            os.remove(p)
        except OSError:
            pass

    st.session_state.analysis_running    = False
    st.session_state.analysis_done       = True
    st.session_state.confirmed_overwrite = False
    progress.progress(100, text="✅ Analysis complete!")
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
        (c2, "Avg. Score",       f"{avg_score}",     "var(--accent2)", "/ 65"),
        (c3, "Top Score",        f"{top_score}",     "var(--ok)",      "/ 65"),
        (c4, "Domains Detected", str(domain_hits),   "var(--warn)",    f"/ {len(domain_groups)}"),
    ]
    for col, label, val, color, suffix in cards:
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-card-label">{label}</div>
  <div class="stat-card-value" style="color:{color}">{val}<span style="font-size:1rem;color:var(--muted)">{suffix}</span></div>
</div>""", unsafe_allow_html=True)

    # ── Ranked table ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Rankings</div>', unsafe_allow_html=True)

    # Build a rich HTML table instead of plain st.dataframe
    rows_html = ""
    for rank, (_, row) in enumerate(ranking_df.iterrows(), start=1):
        name  = row["Resume"]
        score = row["Score"]
        color = score_color(score)
        pct   = min(100, round(score / 65 * 100))
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        rows_html += f"""
<div style="display:grid;grid-template-columns:40px 1fr 200px 80px;align-items:center;
            gap:16px;padding:12px 20px;border-bottom:1px solid var(--border);
            transition:background 0.15s;font-size:0.85rem;"
     onmouseover="this.style.background='var(--surface2)'"
     onmouseout="this.style.background='transparent'">
  <div style="font-family:'DM Mono',monospace;font-size:0.8rem;color:var(--muted)">{medal}</div>
  <div style="font-weight:500;color:var(--text);font-family:'DM Sans',sans-serif">{name}</div>
  <div>
    <div style="height:4px;background:var(--surface3);border-radius:99px;overflow:hidden">
      <div style="width:{pct}%;height:100%;background:{color};border-radius:99px"></div>
    </div>
  </div>
  <div style="font-family:'DM Mono',monospace;font-size:0.82rem;color:{color};text-align:right;font-weight:500">{score}</div>
</div>"""

    st.markdown(f"""
<div class="card" style="padding:0;overflow:hidden">
  <div style="display:grid;grid-template-columns:40px 1fr 200px 80px;gap:16px;
              padding:10px 20px;border-bottom:1px solid var(--border2)">
    <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">#</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Resume</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Score Bar</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;text-align:right">Score</div>
  </div>
  {rows_html}
</div>""", unsafe_allow_html=True)

    # Download row
    dl1, dl2, _ = st.columns([1, 1, 3])
    with dl1:
        st.download_button(
            "⬇️ Download CSV",
            data=open(ranking_path, "rb").read(),
            file_name="ranking.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        if os.path.exists(domains_path):
            st.download_button(
                "⬇️ Download JSON",
                data=open(domains_path, "rb").read(),
                file_name="domains.json",
                mime="application/json",
                use_container_width=True,
            )

    # ── Domain classification ──────────────────────────────────────────────────
    st.markdown('<div class="section-label">Domain Classification</div>', unsafe_allow_html=True)

    st.markdown('<div class="domain-grid">', unsafe_allow_html=True)
    for domain, resumes in domain_groups.items():
        accent_color, chip_cls = DOMAIN_COLORS.get(domain, ("#818cf8", "chip-indigo"))

        if resumes:
            items_html = "".join(
                f'<div class="domain-item">'
                f'<span style="width:6px;height:6px;border-radius:50%;background:{accent_color};display:inline-block;flex-shrink:0"></span>'
                f'{r}</div>'
                for r in resumes
            )
        else:
            items_html = '<div class="domain-empty">No matches found</div>'

        st.markdown(f"""
<div class="domain-card" style="border-top:3px solid {accent_color}">
  <div class="domain-title">{domain}</div>
  {items_html}
  <div style="margin-top:10px">
    {render_chip(f"{len(resumes)} resume{'s' if len(resumes) != 1 else ''}", chip_cls)}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
