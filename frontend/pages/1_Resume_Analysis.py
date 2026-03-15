"""
frontend/pages/resume_analysis.py — Single resume deep-dive.
Full UI/UX redesign on top of all previous bug fixes.
"""

import re
import streamlit as st
import os
import sys
import plotly.graph_objects as go

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.extractor import extract_text
from backend.section_splitter import split_sections
from backend.scorer import score_resume
from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES, get_model
from backend.utils import sanitize_filename
from frontend.styles import inject_styles, score_color, render_score_bar, render_chip

st.set_page_config(page_title="ResumeIQ — Analysis", page_icon="📊", layout="wide")
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
  <div class="hero-badge">📊 Single Resume Analysis</div>
  <h1 class="gradient-text">Deep Dive</h1>
  <p>Upload one resume to see a full breakdown of scores, domain fit, and extracted content.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Upload</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop a resume (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=False,
    help="Single file only. Supported formats: PDF, DOCX, TXT.",
)

if not uploaded_file:
    st.markdown("""
<div class="card" style="text-align:center;padding:40px;border-style:dashed">
  <div style="font-size:2.5rem;margin-bottom:12px">📄</div>
  <div class="card-title">No resume uploaded yet</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:4px">Upload a PDF, DOCX, or TXT file to begin analysis.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PROCESS
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Extracting and scoring…"):
    safe_name = sanitize_filename(uploaded_file.name)
    temp_dir  = os.path.join(BASE_DIR, "resumes")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, safe_name)

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    text     = extract_text(temp_path)
    sections = split_sections(text)
    total_score, score_breakdown = score_resume(sections, return_breakdown=True)

    try:
        os.remove(temp_path)
    except OSError:
        pass

# Domain analysis
search_engine = ResumeSemanticSearch()
search_engine.index_resumes([{"resume": safe_name, "score": total_score, "sections": sections}])

domain_scores: dict[str, float] = {}
for domain, query in DOMAIN_QUERIES.items():
    matches = search_engine.search(query, top_k=1)
    domain_scores[domain] = round(float(matches[0][1]), 3) if matches and matches[0][0] == safe_name else 0.0

primary_domain    = max(domain_scores, key=domain_scores.get)
primary_conf      = domain_scores[primary_domain]
score_col         = score_color(total_score)

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY HERO CARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)

pct_overall = min(100, round(total_score / 65 * 100))
st.markdown(f"""
<div class="card" style="background:linear-gradient(135deg,var(--surface) 0%,var(--surface2) 100%);
     border-color:var(--border2);padding:28px 32px">
  <div style="display:grid;grid-template-columns:1fr auto;gap:24px;align-items:center">
    <div>
      <div class="card-sub" style="margin-bottom:8px">📄 {safe_name}</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                  color:var(--text);margin-bottom:6px">
        Overall Score: <span style="color:{score_col}">{total_score}</span>
        <span style="font-size:1rem;color:var(--muted)"> / 65</span>
      </div>
      <div style="color:var(--muted2);font-size:0.85rem;margin-bottom:16px">
        Primary domain: <b style="color:var(--text)">{primary_domain}</b>
        &nbsp;·&nbsp;
        Confidence: <b style="color:var(--text)">{round(primary_conf * 100, 1)}%</b>
      </div>
      <div style="height:8px;background:var(--surface3);border-radius:99px;overflow:hidden;max-width:400px">
        <div style="width:{pct_overall}%;height:100%;background:{score_col};border-radius:99px;
                    transition:width 1s ease"></div>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:var(--muted);margin-top:6px">
        {pct_overall}th percentile</div>
    </div>
    <div style="text-align:center;padding:20px 28px;background:var(--surface3);
                border-radius:14px;border:1px solid var(--border2)">
      <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
                  color:{score_col};line-height:1">{total_score}</div>
      <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);
                  text-transform:uppercase;letter-spacing:0.1em;margin-top:4px">Score</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHARTS ROW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Breakdown</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# ── Score breakdown bars ──────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="card" style="padding:22px 26px">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub" style="margin-bottom:18px">Per-section contribution</div>', unsafe_allow_html=True)

    MAX_PER_SECTION = {
        "Skills": 20, "Projects": 15, "Internships": 20,
        "Achievements": 10, "Experience": 5, "Extras": 5, "CGPA": 10,
    }
    COLORS = ["var(--accent)", "var(--accent2)", "var(--accent3)",
              "var(--ok)", "var(--warn)", "#c084fc", "#22d3ee"]

    for i, (label, val) in enumerate(score_breakdown.items()):
        max_v = MAX_PER_SECTION.get(label, 20)
        color = COLORS[i % len(COLORS)]
        st.markdown(render_score_bar(label, val, max_v, color), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Domain radar chart ────────────────────────────────────────────────────────
with col_right:
    st.markdown('<div class="card" style="padding:22px 26px">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Domain Confidence</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub" style="margin-bottom:8px">Semantic similarity per domain</div>', unsafe_allow_html=True)

    categories = list(domain_scores.keys())
    values     = list(domain_scores.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(129,140,248,0.12)',
        line=dict(color='#818cf8', width=2),
        marker=dict(color='#818cf8', size=6),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(color='#64748b', size=9, family='DM Mono'),
                gridcolor='rgba(255,255,255,0.05)',
                linecolor='rgba(255,255,255,0.05)',
            ),
            angularaxis=dict(
                tickfont=dict(color='#94a3b8', size=10, family='DM Sans'),
                gridcolor='rgba(255,255,255,0.05)',
                linecolor='rgba(255,255,255,0.05)',
            ),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e8edf5', family='DM Sans'),
        margin=dict(l=40, r=40, t=20, b=20),
        height=280,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXTRACTED SECTIONS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Extracted Content</div>', unsafe_allow_html=True)

SECTION_ICONS = {
    "skills": "⚡", "experience": "💼", "education": "🎓",
    "projects": "🚀", "achievements": "🏆", "extras": "✨", "summary": "👤",
}

for section, content in sections.items():
    if not content.strip():
        continue

    icon = SECTION_ICONS.get(section, "📋")
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-title">{icon} {section.title()}</div>',
        unsafe_allow_html=True,
    )

    if section == "skills":
        tokens = [t.strip() for t in re.split(r'[,\n|•/]', content) if t.strip() and len(t.strip()) > 1]
        chip_colors = ["chip-indigo", "chip-teal", "chip-pink", "chip-green", "chip-warn"]
        chips = " ".join(
            render_chip(t, chip_colors[i % len(chip_colors)])
            for i, t in enumerate(tokens)
        )
        st.markdown(f'<div style="margin-top:10px">{chips}</div>', unsafe_allow_html=True)

    elif section == "education":
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        for line in lines:
            st.markdown(
                f'<div style="padding:6px 0;color:var(--muted2);font-size:0.85rem;'
                f'border-bottom:1px solid var(--border)">{line}</div>',
                unsafe_allow_html=True,
            )

    elif section == "achievements":
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        for line in lines:
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:8px;padding:5px 0;'
                f'color:var(--muted2);font-size:0.85rem;">'
                f'<span style="color:var(--warn);flex-shrink:0">▸</span>{line}</div>',
                unsafe_allow_html=True,
            )

    else:
        st.markdown(
            f'<p style="white-space:pre-wrap;color:var(--muted2);font-size:0.85rem;'
            f'line-height:1.75;margin-top:10px">{content}</p>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
