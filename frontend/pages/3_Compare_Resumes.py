"""
frontend/pages/3_Compare_Resumes.py — Side-by-side resume comparison.

Feature: Select 2–5 resumes from previously analysed results and compare them
across every dimension: total score, per-section breakdown, skill overlap/gap,
domain confidence, and a grouped radar chart.

Requires the bulk analysis on the Dashboard to have been run first.
"""

import re
import json
import os
import sys

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.scorer import score_resume
from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES, get_model
from frontend.styles import inject_styles, score_color, render_chip

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

st.set_page_config(
    page_title="ResumeIQ — Compare",
    page_icon="⚖️",
    layout="wide",
)
inject_styles()

# Extra CSS just for this page
st.markdown("""
<style>
.compare-header {
    display: grid;
    gap: 12px;
    margin-bottom: 4px;
}
.compare-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
}
.compare-score-big {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    line-height: 1;
}
.compare-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-top: 3px;
}
.row-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    padding: 13px 0;
    border-bottom: 1px solid var(--border);
}
.cell {
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
}
.winner-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(74,222,128,0.12);
    border: 1px solid rgba(74,222,128,0.25);
    border-radius: 99px;
    padding: 2px 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--ok);
    letter-spacing: 0.06em;
}
.skill-chip-match {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    margin: 2px;
    background: rgba(110,231,183,0.1);
    border: 1px solid rgba(110,231,183,0.2);
    color: var(--accent);
}
.skill-chip-unique {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    margin: 2px;
    background: rgba(129,140,248,0.1);
    border: 1px solid rgba(129,140,248,0.2);
    color: var(--accent2);
}
.skill-chip-missing {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    margin: 2px;
    background: rgba(248,113,113,0.08);
    border: 1px solid rgba(248,113,113,0.18);
    color: var(--danger);
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return get_model()

load_model()

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hero">
  <div class="hero-badge">⚖️ Compare Resumes</div>
  <h1 class="gradient-text">Side-by-Side Comparison</h1>
  <p>Select 2 to 5 resumes from your analysed batch and compare them across every scoring dimension, skills overlap, and domain fit.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GUARD
# ══════════════════════════════════════════════════════════════════════════════
ranking_path   = os.path.join(OUTPUT_DIR, "ranking.csv")
extracted_path = os.path.join(OUTPUT_DIR, "extracted.json")

if not os.path.exists(ranking_path) or not os.path.exists(extracted_path):
    st.markdown("""
<div class="card" style="text-align:center;padding:40px;border-style:dashed">
  <div style="font-size:2.5rem;margin-bottom:12px">⚖️</div>
  <div class="card-title">No resumes analysed yet</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:6px;margin-bottom:20px">
    Run a bulk analysis on the Dashboard first, then come back here to compare.
  </div>
</div>""", unsafe_allow_html=True)
    st.page_link("app.py", label="Go to Dashboard ->")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
ranking_df = pd.read_csv(ranking_path)
ranking_df.rename(columns={"Resume": "resume", "Score": "score"}, inplace=True)

with open(extracted_path) as f:
    extracted_data: dict = json.load(f)

all_resumes = ranking_df["resume"].tolist()
score_lookup = {
    str(row["resume"]): float(row["score"])
    for _, row in ranking_df.iterrows()
}

if len(all_resumes) < 2:
    st.warning("You need at least 2 analysed resumes to use the compare feature. Upload more on the Dashboard.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# RESUME SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Select Resumes to Compare</div>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <div class="card-title">⚖️ Choose Candidates</div>
  <div class="card-sub" style="margin-bottom:14px">Pick 2 to 5 resumes · Ranked by score by default</div>
</div>
""", unsafe_allow_html=True)

selected = st.multiselect(
    "Select resumes to compare",
    options=all_resumes,
    default=all_resumes[:min(3, len(all_resumes))],
    max_selections=5,
    help="Pick 2–5 resumes. They are ordered by overall score.",
    label_visibility="collapsed",
)

if len(selected) < 2:
    st.info("Please select at least 2 resumes to compare.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# BUILD COMPARISON DATA
# ══════════════════════════════════════════════════════════════════════════════
MAX_PER_SECTION = {
    "Skills": 20, "Projects": 15, "Internships": 20,
    "Achievements": 10, "Experience": 5, "Extras": 5, "CGPA": 10,
}
CARD_COLORS = ["#6ee7b7", "#818cf8", "#f472b6", "#fb923c", "#4ade80"]


def hex_to_rgba(hex_color: str, alpha: float) -> str:
  """Convert '#RRGGBB' to Plotly-friendly 'rgba(r,g,b,a)' string."""
  hex_color = hex_color.lstrip("#")
  if len(hex_color) != 6:
    return f"rgba(255,255,255,{alpha})"
  r = int(hex_color[0:2], 16)
  g = int(hex_color[2:4], 16)
  b = int(hex_color[4:6], 16)
  return f"rgba({r},{g},{b},{alpha})"


def display_name(filename: str) -> str:
    """Make uploaded filename easier to read in UI."""
    stem = os.path.splitext(filename)[0]
    return stem.replace("_", " ").strip() or filename

candidates = []
for name in selected:
    sections   = extracted_data.get(name, {})
    score_result = score_resume(sections, return_breakdown=True)
    if isinstance(score_result, tuple):
        total, breakdown = score_result
    else:
        total = float(score_result)
        breakdown = {}
    stored_score = score_lookup.get(name, total)

    # Extract skills list
    raw_skills = sections.get("skills", "")
    skills_list = sorted({
        s.strip().lower()
        for s in re.split(r'[,\n|•/]', raw_skills)
        if len(s.strip()) > 1
    })

    candidates.append({
        "name":      name,
        "score":     stored_score,
        "breakdown": breakdown,
        "sections":  sections,
        "skills":    skills_list,
    })

# Domain scores
search_engine = ResumeSemanticSearch()
search_engine.index_resumes([
    {"resume": c["name"], "score": c["score"], "sections": c["sections"]}
    for c in candidates
])
for c in candidates:
    c["domains"] = {}
    for domain, query in DOMAIN_QUERIES.items():
        matches = search_engine.search(query, top_k=len(candidates))
        score_map = {m[0]: m[1] for m in matches}
        c["domains"][domain] = round(float(score_map.get(c["name"], 0.0)), 3)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SCORE OVERVIEW CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Overall Scores</div>', unsafe_allow_html=True)

top_score = max(c["score"] for c in candidates)
cols = st.columns(len(candidates))

for i, (col, c) in enumerate(zip(cols, candidates)):
    color  = CARD_COLORS[i % len(CARD_COLORS)]
    s_col  = score_color(c["score"])
    is_top = c["score"] == top_score
    pct    = min(100, round(c["score"] / 65 * 100))

    with col:
        st.markdown(f"""
<div class="card" style="border-top:3px solid {color};text-align:center;padding:22px 18px">
  {'<div class="winner-badge" style="margin:0 auto 10px">🏆 Top Score</div>' if is_top else '<div style="height:22px;margin-bottom:10px"></div>'}
    <div class="compare-name" style="text-align:center;margin-bottom:14px">{display_name(c['name'])}</div>
  <div class="compare-score-big" style="color:{s_col}">{c['score']}</div>
  <div class="compare-label">/ 65 points</div>
  <div style="height:5px;background:var(--surface3);border-radius:99px;overflow:hidden;margin-top:14px">
    <div style="width:{pct}%;height:100%;background:{color};border-radius:99px"></div>
  </div>
  <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:var(--muted);margin-top:5px">{pct}th pct</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — RADAR CHART (all candidates overlaid)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Score Breakdown · Radar</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown('<div class="card" style="padding:22px">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Breakdown Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub" style="margin-bottom:12px">Each axis = one scoring dimension</div>', unsafe_allow_html=True)

    sections_order = list(MAX_PER_SECTION.keys())
    fig = go.Figure()

    for i, c in enumerate(candidates):
        color_hex = CARD_COLORS[i % len(CARD_COLORS)]
        vals = [c["breakdown"].get(s, 0) for s in sections_order]
        # normalise each dimension to 0–1 for fair radar display
        vals_norm = [v / MAX_PER_SECTION[s] for v, s in zip(vals, sections_order)]

        fig.add_trace(go.Scatterpolar(
            r=vals_norm + [vals_norm[0]],
            theta=sections_order + [sections_order[0]],
            fill="toself",
          fillcolor=hex_to_rgba(color_hex, 0.15),
            line=dict(color=color_hex, width=2),
            marker=dict(size=5, color=color_hex),
            name=c["name"],
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 1],
                tickvals=[0.25, 0.5, 0.75, 1.0],
                ticktext=["25%", "50%", "75%", "100%"],
                tickfont=dict(size=8, color="#64748b", family="DM Mono"),
                gridcolor="rgba(255,255,255,0.05)",
                linecolor="rgba(255,255,255,0.05)",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#94a3b8", family="DM Sans"),
                gridcolor="rgba(255,255,255,0.06)",
                linecolor="rgba(255,255,255,0.06)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5", family="DM Sans"),
        legend=dict(
            bgcolor="rgba(14,20,32,0.8)",
            bordercolor="rgba(255,255,255,0.08)",
            borderwidth=1,
            font=dict(size=10, color="#94a3b8", family="DM Mono"),
        ),
        margin=dict(l=40, r=40, t=20, b=20),
        height=360,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Per-section table ─────────────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="card" style="padding:22px">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Section Scores</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub" style="margin-bottom:14px">Raw points per dimension</div>', unsafe_allow_html=True)

    for section, max_v in MAX_PER_SECTION.items():
        vals = [c["breakdown"].get(section, 0) for c in candidates]
        best = max(vals)

        st.markdown(f'<div class="row-label">{section} <span style="color:var(--surface3)">/ {max_v}</span></div>', unsafe_allow_html=True)

        bar_cols = st.columns(len(candidates))
        for i, (bc, v) in enumerate(zip(bar_cols, vals)):
            color  = CARD_COLORS[i % len(CARD_COLORS)]
            pct    = min(100, round(v / max_v * 100))
            is_win = v == best and best > 0
            with bc:
                st.markdown(f"""
<div class="cell">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
    <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:{color if is_win else 'var(--muted2)'};font-weight:{'600' if is_win else '400'}">{v}</span>
    {"<span style='font-size:0.6rem;color:var(--ok)'>▲</span>" if is_win else ""}
  </div>
  <div style="height:4px;background:var(--surface3);border-radius:99px;overflow:hidden">
    <div style="width:{pct}%;height:100%;background:{color if is_win else 'var(--surface3)'};border-radius:99px;opacity:{'1' if is_win else '0.4'}"></div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SKILLS COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Skills Analysis</div>', unsafe_allow_html=True)

all_skill_sets = [set(c["skills"]) for c in candidates]
shared_skills  = set.intersection(*all_skill_sets) if all_skill_sets else set()

st.markdown(f"""
<div class="card" style="padding:22px 26px">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div>
      <div class="card-title">Skill Overlap & Gaps</div>
      <div class="card-sub">Shared across all · Unique per candidate · Missing</div>
    </div>
    <div style="text-align:right">
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.6rem;color:var(--accent)">{len(shared_skills)}</div>
      <div class="compare-label">shared skills</div>
    </div>
  </div>

  {'<div style="margin-bottom:16px"><div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">✅ Shared by all candidates</div>' + " ".join(f'<span class="skill-chip-match">{s}</span>' for s in sorted(shared_skills)) + '</div>' if shared_skills else '<div style="color:var(--muted2);font-size:0.82rem;margin-bottom:16px;font-style:italic">No skills are shared across all selected candidates.</div>'}
</div>
""", unsafe_allow_html=True)

# Per-candidate skill breakdown
skill_cols = st.columns(len(candidates))
for i, (col, c) in enumerate(zip(skill_cols, candidates)):
    color  = CARD_COLORS[i % len(CARD_COLORS)]
    unique = set(c["skills"]) - shared_skills
    # "missing" = skills all OTHER candidates have but this one doesn't
    others_union = set.union(*(all_skill_sets[j] for j in range(len(candidates)) if j != i)) if len(candidates) > 1 else set()
    missing = others_union - set(c["skills"]) - shared_skills

    unique_html  = " ".join(f'<span class="skill-chip-unique">{s}</span>' for s in sorted(unique)[:12])
    missing_html = " ".join(f'<span class="skill-chip-missing">{s}</span>' for s in sorted(missing)[:8])

    with col:
        st.markdown(f"""
<div class="card" style="border-top:3px solid {color};padding:18px 20px">
    <div class="compare-name" style="margin-bottom:12px">{display_name(c['name'])}</div>

  <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);
              text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px">
    Unique skills ({len(unique)})
  </div>
  <div style="margin-bottom:14px">
    {unique_html or '<span style="color:var(--muted);font-size:0.78rem;font-style:italic">None unique</span>'}
  </div>

  <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--danger);
              text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px">
    Missing vs others ({min(len(missing), 8)}{'+'if len(missing)>8 else ''})
  </div>
  <div>
    {missing_html or '<span style="color:var(--muted);font-size:0.78rem;font-style:italic">Nothing missing</span>'}
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DOMAIN CONFIDENCE BAR CHART
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Domain Confidence</div>', unsafe_allow_html=True)

st.markdown('<div class="card" style="padding:22px">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Domain Fit Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="card-sub" style="margin-bottom:12px">Semantic similarity to each domain — higher is stronger fit</div>', unsafe_allow_html=True)

domains = list(DOMAIN_QUERIES.keys())
fig2    = go.Figure()

for i, c in enumerate(candidates):
    fig2.add_trace(go.Bar(
        name=c["name"],
        x=domains,
        y=[c["domains"].get(d, 0) for d in domains],
        marker=dict(color=CARD_COLORS[i % len(CARD_COLORS)], opacity=0.85),
        text=[f"{c['domains'].get(d, 0):.2f}" for d in domains],
        textposition="outside",
        textfont=dict(size=9, color="#94a3b8", family="DM Mono"),
    ))

fig2.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8edf5", family="DM Sans"),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(size=10, color="#94a3b8", family="DM Sans"),
        linecolor="rgba(255,255,255,0.05)",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.04)",
        range=[0, 1.1],
        tickfont=dict(size=9, color="#64748b", family="DM Mono"),
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(14,20,32,0.8)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(size=10, color="#94a3b8", family="DM Mono"),
    ),
    margin=dict(l=10, r=10, t=20, b=10),
    height=300,
    bargap=0.2,
    bargroupgap=0.05,
)
st.plotly_chart(fig2, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — VERDICT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Verdict</div>', unsafe_allow_html=True)

# Sort by score for ranking
ranked_candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

rank_index = st.slider(
    "Slide through compared resumes",
    min_value=1,
    max_value=len(ranked_candidates),
    value=1,
)

rank = rank_index - 1
c = ranked_candidates[rank]
medal = medals[rank]
dom_top = max(c["domains"], key=c["domains"].get)
dom_conf = round(c["domains"][dom_top] * 100, 1)
n_skills = len(c["skills"])
n_unique = len(set(c["skills"]) - shared_skills)

with st.container(border=True):
    left, right = st.columns([5, 1])
    with left:
        title = f"{medal} {display_name(c['name'])}"
        if rank == 0:
            title += "  ·  Top Pick"
        st.markdown(f"**{title}**")
        st.caption(f"🎯 {dom_top} ({dom_conf}%)   |   ⚡ {n_skills} ({n_unique} unique)")

        # Visual slider bars for quick comparison without verbose text labels.
        st.progress(min(1.0, c["score"] / 65), text=f"{c['score']} / 65")
        st.progress(min(1.0, dom_conf / 100), text=f"{dom_conf}%")
    with right:
        st.markdown(f"**{c['score']} / 65**")
