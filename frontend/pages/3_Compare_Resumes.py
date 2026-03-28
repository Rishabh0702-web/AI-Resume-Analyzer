"""
frontend/pages/3_Compare_Resumes.py — Side-by-side resume comparison.

Feature: Select 2–5 resumes from previously analysed results and compare them
across every dimension: total score, per-section breakdown, skill overlap/gap,
domain confidence, and a grouped radar chart.

Premium SaaS UI — clean, no neon or glassmorphism.
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
from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES
from frontend.styles import inject_styles, score_color, render_chip, render_top_nav

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

st.set_page_config(
    page_title="ResumeIQ — Compare",
    page_icon="⚖️",
    layout="wide",
)
inject_styles()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("role") == "student":
    st.switch_page("pages/1_Resume_Analysis.py")

render_top_nav()

# Extra CSS for this page
st.markdown("""
<style>
.compare-name {
    font-weight: 700;
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
}
.compare-score-big {
    font-weight: 800;
    font-size: 2.6rem;
    line-height: 1;
    letter-spacing: -0.03em;
}
.compare-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-top: 3px;
}
.row-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    padding: 12px 0;
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
    background: var(--ok-muted);
    border-radius: 6px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: var(--ok);
    letter-spacing: 0.04em;
}
.skill-chip-match {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px;
    background: var(--accent-muted);
    color: var(--accent);
}
.skill-chip-unique {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px;
    background: var(--purple-muted);
    color: var(--purple);
}
.skill-chip-missing {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px;
    background: var(--danger-muted);
    color: var(--danger);
}
</style>
""", unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hero">
  <div class="hero-badge">Compare</div>
  <h1>Side-by-Side Comparison</h1>
  <p>Select 2 to 5 resumes and compare them across scoring dimensions, skills overlap, and domain fit.</p>
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
  <div style="font-size:2rem;margin-bottom:12px">⚖️</div>
  <div class="card-title">No resumes analysed yet</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:6px;margin-bottom:16px">
    Run a bulk analysis on the Dashboard first, then come back here to compare.
  </div>
</div>""", unsafe_allow_html=True)
    st.page_link("app.py", label="Go to Dashboard →")
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
    st.warning("You need at least 2 analysed resumes to use the compare feature.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# RESUME SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Select Resumes</div>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
  <div class="card-title">Choose Candidates</div>
  <div class="card-sub" style="margin-bottom:14px">Pick 2 to 5 resumes · Ranked by score</div>
</div>
""", unsafe_allow_html=True)

selected = st.multiselect(
    "Select resumes to compare",
    options=all_resumes,
    default=all_resumes[:min(3, len(all_resumes))],
    max_selections=5,
    help="Pick 2–5 resumes.",
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
CARD_COLORS = ["#4f8ff7", "#a78bfa", "#f472b6", "#e5a63e", "#4ade80"]


def hex_to_rgba(hex_color: str, alpha: float) -> str:
  hex_color = hex_color.lstrip("#")
  if len(hex_color) != 6:
    return f"rgba(255,255,255,{alpha})"
  r = int(hex_color[0:2], 16)
  g = int(hex_color[2:4], 16)
  b = int(hex_color[4:6], 16)
  return f"rgba({r},{g},{b},{alpha})"


def display_name(filename: str) -> str:
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
<div class="card" style="border-top:2px solid {color};text-align:center;padding:22px 18px">
  {'<div class="winner-badge" style="margin:0 auto 10px">🏆 Top Score</div>' if is_top else '<div style="height:20px;margin-bottom:10px"></div>'}
  <div class="compare-name" style="text-align:center;margin-bottom:14px">{display_name(c['name'])}</div>
  <div class="compare-score-big" style="color:{s_col}">{c['score']}</div>
  <div class="compare-label">/ 65 points</div>
  <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden;margin-top:14px">
    <div style="width:{pct}%;height:100%;background:{color};border-radius:4px"></div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--muted);margin-top:4px">{pct}th pct</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — RADAR CHART
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
        vals_norm = [v / MAX_PER_SECTION[s] for v, s in zip(vals, sections_order)]

        fig.add_trace(go.Scatterpolar(
            r=vals_norm + [vals_norm[0]],
            theta=sections_order + [sections_order[0]],
            fill="toself",
            fillcolor=hex_to_rgba(color_hex, 0.08),
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
                tickfont=dict(size=8, color="#64748b", family="JetBrains Mono"),
                gridcolor="rgba(255,255,255,0.04)",
                linecolor="rgba(255,255,255,0.04)",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#8896ab", family="Inter"),
                gridcolor="rgba(255,255,255,0.04)",
                linecolor="rgba(255,255,255,0.04)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter"),
        legend=dict(
            bgcolor="rgba(17,22,32,0.9)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
            font=dict(size=10, color="#8896ab", family="JetBrains Mono"),
        ),
        margin=dict(l=40, r=40, t=20, b=20),
        height=360,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:{color if is_win else 'var(--muted2)'};font-weight:{'600' if is_win else '400'}">{v}</span>
    {"<span style='font-size:0.55rem;color:var(--ok)'>▲</span>" if is_win else ""}
  </div>
  <div style="height:4px;background:var(--surface3);border-radius:4px;overflow:hidden">
    <div style="width:{pct}%;height:100%;background:{color if is_win else 'var(--surface3)'};border-radius:4px;opacity:{'1' if is_win else '0.35'}"></div>
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
      <div class="card-sub">Shared · Unique · Missing</div>
    </div>
    <div style="text-align:right">
      <div style="font-size:1.6rem;font-weight:800;color:var(--accent);letter-spacing:-0.02em">{len(shared_skills)}</div>
      <div class="compare-label">shared</div>
    </div>
  </div>

  {'<div style="margin-bottom:16px"><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.58rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">Shared by all</div>' + " ".join(f'<span class="skill-chip-match">{s}</span>' for s in sorted(shared_skills)) + '</div>' if shared_skills else '<div style="color:var(--muted2);font-size:0.82rem;margin-bottom:16px;font-style:italic">No skills shared across all candidates.</div>'}
</div>
""", unsafe_allow_html=True)

skill_cols = st.columns(len(candidates))
for i, (col, c) in enumerate(zip(skill_cols, candidates)):
    color  = CARD_COLORS[i % len(CARD_COLORS)]
    unique = set(c["skills"]) - shared_skills
    others_union = set.union(*(all_skill_sets[j] for j in range(len(candidates)) if j != i)) if len(candidates) > 1 else set()
    missing = others_union - set(c["skills"]) - shared_skills

    unique_html  = " ".join(f'<span class="skill-chip-unique">{s}</span>' for s in sorted(unique)[:12])
    missing_html = " ".join(f'<span class="skill-chip-missing">{s}</span>' for s in sorted(missing)[:8])

    with col:
        st.markdown(f"""
<div class="card" style="border-top:2px solid {color};padding:18px 20px">
  <div class="compare-name" style="margin-bottom:12px">{display_name(c['name'])}</div>

  <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">
    Unique ({len(unique)})
  </div>
  <div style="margin-bottom:14px">
    {unique_html or '<span style="color:var(--muted);font-size:0.78rem;font-style:italic">None</span>'}
  </div>

  <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--danger);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">
    Missing ({min(len(missing), 8)}{'+'if len(missing)>8 else ''})
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
st.markdown('<div class="card-sub" style="margin-bottom:12px">Semantic similarity — higher is stronger fit</div>', unsafe_allow_html=True)

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
        textfont=dict(size=9, color="#8896ab", family="JetBrains Mono"),
    ))

fig2.update_layout(
    barmode="group",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="Inter"),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(size=10, color="#8896ab", family="Inter"),
        linecolor="rgba(255,255,255,0.04)",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.03)",
        range=[0, 1.1],
        tickfont=dict(size=9, color="#64748b", family="JetBrains Mono"),
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(17,22,32,0.9)",
        bordercolor="rgba(255,255,255,0.06)",
        borderwidth=1,
        font=dict(size=10, color="#8896ab", family="JetBrains Mono"),
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
v_color = CARD_COLORS[rank % len(CARD_COLORS)]

left_v, right_v = st.columns([4, 1])

with left_v:
    st.markdown(f"""<div style="font-weight:700;font-size:1.1rem;margin-bottom:8px">
  {medal} {display_name(c['name'])}{'  ·  <span style="color:var(--ok)">Top Pick</span>' if rank == 0 else ''}
</div>
<div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap">
  <span class="chip chip-teal">🎯 {dom_top} ({dom_conf}%)</span>
  <span class="chip chip-indigo">⚡ {n_skills} skills ({n_unique} unique)</span>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="margin-bottom:6px">
  <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:3px">
    <span style="color:var(--muted2)">Overall Score</span>
    <span style="font-family:'JetBrains Mono',monospace;color:{v_color}">{c['score']} / 65</span>
  </div>
  <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden">
    <div style="width:{min(100, round(c['score']/65*100))}%;height:100%;background:{v_color};border-radius:4px"></div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""<div>
  <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:3px">
    <span style="color:var(--muted2)">Domain Confidence</span>
    <span style="font-family:'JetBrains Mono',monospace;color:var(--accent)">{dom_conf}%</span>
  </div>
  <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden">
    <div style="width:{dom_conf}%;height:100%;background:var(--accent);border-radius:4px"></div>
  </div>
</div>""", unsafe_allow_html=True)

with right_v:
    st.markdown(f"""<div style="text-align:center;padding:20px 24px;background:var(--surface2);border-radius:12px;border:1px solid var(--border);min-width:90px">
  <div style="font-size:2.4rem;font-weight:800;color:{v_color};line-height:1;letter-spacing:-0.03em">{c['score']}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.52rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-top:4px">Score</div>
</div>""", unsafe_allow_html=True)
