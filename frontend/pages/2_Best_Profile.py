"""
frontend/pages/2_Best_Profile.py — Semantic job-role matching.
Premium SaaS UI — clean, no neon or glassmorphism.
"""

import streamlit as st
import os
import sys
import json
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.semantic_search import ResumeSemanticSearch, get_model
from frontend.styles import inject_styles, score_color, render_chip

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

st.set_page_config(page_title="ResumeIQ — Best Fit", page_icon="🎯", layout="wide")
inject_styles()

@st.cache_resource
def load_model():
    return get_model()

load_model()

# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hero">
  <div class="hero-badge">Best Profile Fit</div>
  <h1>Find Your Best Match</h1>
  <p>Describe a role and our semantic engine will rank candidates by fit — combining resume score with AI similarity.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GUARD: ANALYSIS MUST HAVE RUN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("analysis_running", False):
    st.markdown("""
<div class="card" style="border-left:3px solid var(--warn)">
  <div class="card-title">Analysis In Progress</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:4px">
    The bulk analysis is still running on the Dashboard. Please wait for it to finish.
  </div>
</div>""", unsafe_allow_html=True)
    st.stop()

ranking_path   = os.path.join(OUTPUT_DIR, "ranking.csv")
extracted_path = os.path.join(OUTPUT_DIR, "extracted.json")

if not os.path.exists(ranking_path) or not os.path.exists(extracted_path):
    st.markdown("""
<div class="card" style="text-align:center;padding:40px;border-style:dashed">
  <div style="font-size:2rem;margin-bottom:12px">🔍</div>
  <div class="card-title">No analysis results yet</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:4px;margin-bottom:16px">
    Upload and analyse a batch of resumes on the Dashboard first.
  </div>
</div>""", unsafe_allow_html=True)
    st.page_link("app.py", label="Go to Dashboard →")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
ranking_df = pd.read_csv(ranking_path)
ranking_df.rename(columns={"Resume": "resume", "Score": "score"}, inplace=True)

with open(extracted_path) as f:
    extracted_data: dict = json.load(f)

num_candidates = len(ranking_df)

# ══════════════════════════════════════════════════════════════════════════════
# INPUT PANEL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Search</div>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <div class="card-title">Describe the Role</div>
  <div class="card-sub" style="margin-bottom:14px">The more specific, the better the matches</div>
  <div style="background:var(--surface2);border:1px solid var(--border);
              border-radius:10px;padding:12px 16px;font-size:0.82rem;color:var(--muted2)">
    <strong style="color:var(--text)">Tip:</strong> Include skills, tools, experience level, and role type.
    E.g. <em>"Senior ML engineer with PyTorch, BERT fine-tuning, and 3+ years NLP experience"</em>
  </div>
</div>
""", unsafe_allow_html=True)

# Example query chips
EXAMPLES = [
    ("Machine Learning",  "ML intern with Python, NLP, and deep learning projects"),
    ("Web Dev",           "Senior web developer with React, Node.js, and REST API experience"),
    ("Data Science",      "Data analyst with SQL, Tableau, and statistics background"),
    ("Cloud / DevOps",    "DevOps engineer with AWS, Docker, Kubernetes, and CI/CD pipelines"),
]

st.markdown('<div class="section-label">Quick Examples</div>', unsafe_allow_html=True)
ex_cols = st.columns(len(EXAMPLES))
for col, (label, query) in zip(ex_cols, EXAMPLES):
    with col:
        if st.button(label, key=f"ex_{label}", use_container_width=True):
            st.session_state["prefill_query"] = query

job_query = st.text_area(
    "Role description",
    value=st.session_state.get("prefill_query", ""),
    placeholder="e.g. Machine learning intern with Python, NLP, and deep learning projects",
    height=110,
    label_visibility="collapsed",
)

col_slider, col_btn = st.columns([3, 1])
with col_slider:
  max_k = min(10, num_candidates)
  if max_k <= 1:
    top_k = 1
    st.caption("Only one analysed resume is available right now.")
  else:
    top_k = st.slider(
      "Candidates to return",
      min_value=1,
      max_value=max_k,
      value=min(5, max_k),
      help="How many top-matching candidates to show",
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    find = st.button("Find Best Fit", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MATCHING + RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if find:

    if not job_query.strip():
        st.warning("Please describe the role before searching.")
        st.stop()

    with st.spinner("Running semantic search across candidates…"):
        search_engine = ResumeSemanticSearch()
        results = []
        for resume_name, secs in extracted_data.items():
            score_rows = ranking_df.loc[ranking_df["resume"] == resume_name, "score"]
            base_score = float(score_rows.values[0]) if not score_rows.empty else 0.0
            results.append({"resume": resume_name, "score": base_score, "sections": secs})

        search_engine.index_resumes(results)
        matches = search_engine.search(job_query, top_k=top_k)

    if not matches:
        st.info("No matching candidates found. Try broadening your query.")
        st.stop()

    st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
  <div style="font-weight:700;font-size:1.05rem">Top {len(matches)} Matches</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--muted)">
    Sorted by Overall Fit Score
  </div>
</div>""", unsafe_allow_html=True)

    for rank, (resume_name, similarity) in enumerate(matches, start=1):
        score_rows = ranking_df.loc[ranking_df["resume"] == resume_name, "score"]
        base_score = float(score_rows.values[0]) if not score_rows.empty else 0.0

        fit_score  = round((similarity * 100 + base_score) / 2, 1)
        sem_pct    = round(similarity * 100, 1)
        res_pct    = min(100, round(base_score / 65 * 100))
        fit_col    = score_color(fit_score, max_score=100)
        medal      = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

        # Status chip
        if fit_score >= 65:
            status_chip = render_chip("Strong Match", "chip-green")
        elif fit_score >= 45:
            status_chip = render_chip("Good Match", "chip-teal")
        elif fit_score >= 30:
            status_chip = render_chip("Partial Match", "chip-warn")
        else:
            status_chip = render_chip("Low Match", "chip-danger")

        # --- Candidate card: use columns to avoid deep HTML nesting ---
        left_col, right_col = st.columns([4, 1])

        with left_col:
            st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
  <span style="font-size:1.1rem">{medal}</span>
  <div class="candidate-card-name">{resume_name}</div>
  {status_chip}
</div>
<div class="candidate-card-meta" style="margin-bottom:12px">
  Semantic similarity · Resume score · Combined fit
</div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;font-size:0.74rem;margin-bottom:4px">
    <span style="color:var(--muted2)">Semantic Match</span>
    <span style="font-family:'JetBrains Mono',monospace;color:var(--purple)">{sem_pct}%</span>
  </div>
  <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden">
    <div style="width:{sem_pct}%;height:100%;background:var(--purple);border-radius:4px"></div>
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown(f"""<div>
  <div style="display:flex;justify-content:space-between;font-size:0.74rem;margin-bottom:4px">
    <span style="color:var(--muted2)">Resume Score</span>
    <span style="font-family:'JetBrains Mono',monospace;color:var(--accent)">{base_score} / 65</span>
  </div>
  <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden">
    <div style="width:{res_pct}%;height:100%;background:var(--accent);border-radius:4px"></div>
  </div>
</div>""", unsafe_allow_html=True)

        with right_col:
            st.markdown(f"""<div style="text-align:center;padding:18px 22px;background:var(--surface2);border-radius:12px;border:1px solid var(--border);min-width:90px">
  <div class="fit-score-badge" style="color:{fit_col}">{fit_score}</div>
  <div class="fit-score-label">Fit Score</div>
</div>""", unsafe_allow_html=True)
