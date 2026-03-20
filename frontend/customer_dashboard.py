"""
frontend/customer_dashboard.py — Customer (Job-Seeker) Dashboard.

Strictly limited view: resume upload + analysis results only.
NO sidebar navigation. NO admin features. NO access to Best Profiles or Compare.
"""

from __future__ import annotations

import os
import sys
import re
from datetime import datetime

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

from backend.extractor import extract_text
from backend.section_splitter import split_sections
from backend.scorer import score_resume
from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES, get_model
from backend.utils import sanitize_filename
from frontend.styles import score_color, render_score_bar, render_chip


@st.cache_resource
def _load_model():
  return get_model()


def _generate_suggestions(breakdown: dict) -> list[str]:
  """Generate improvement tips based on weak score sections."""
  MAX = {
    "Skills": 20, "Projects": 15, "Internships": 20,
    "Achievements": 10, "Experience": 5, "Extras": 5, "CGPA": 10,
  }
  tips = []
  for section, max_v in MAX.items():
    val = breakdown.get(section, 0)
    pct = val / max_v if max_v else 0
    if pct < 0.3:
      if section == "Skills":
        tips.append("**Add more technical skills** — list languages, frameworks, tools, and certs. Aim for 10+.")
      elif section == "Projects":
        tips.append("**Include more projects** — 3-5 with tech stack, role, and measurable outcomes.")
      elif section == "Internships":
        tips.append("**Strengthen experience** — add internships or roles with responsibilities and impact.")
      elif section == "Achievements":
        tips.append("**Highlight achievements** — hackathons, certifications, publications, or awards.")
      elif section == "Experience":
        tips.append("**Expand experience** — include duration, company, and key contributions.")
      elif section == "CGPA":
        tips.append(" **Add academic details** — CGPA, relevant coursework, or honours.")
    elif pct < 0.5:
      if section == "Skills":
        tips.append("**Diversify skills** — mix technical (Python, SQL) and soft skills (leadership).")
      elif section == "Projects":
        tips.append("**Enhance projects** — add quantifiable results like \"improved speed by 40%\".")
  if not tips:
    tips.append("**Great resume!** All key sections are well-covered. Keep it updated.")
  return tips[:5]


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

def show_customer_dashboard():
  """Customer dashboard — upload + analysis only. No sidebar, no admin features."""

  # ── ROLE GUARD ────────────────────────────────────────────────────────────
  if st.session_state.get("role") == "admin":
    st.error("This is the customer dashboard. Switch to HR Dashboard for admin features.")
    st.stop()

  _load_model()

  # Init state
  if "cust_analysis_result" not in st.session_state:
    st.session_state.cust_analysis_result = None

  # Get user info for greeting
  user = st.session_state.get("user", {})
  email = user.get("email", "User") if isinstance(user, dict) else "User"
  display_name = email.split("@")[0].replace(".", " ").replace("_", " ").title() if "@" in email else email

  hour = datetime.now().hour
  greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

  # ══════════════════════════════════════════════════════════════════════════
  # NOTIFICATIONS
  # ══════════════════════════════════════════════════════════════════════════
  n_col1, n_col2 = st.columns([9, 2])
  with n_col2:
    with st.popover("Notifications", use_container_width=True):
      st.markdown("""
<div style="font-size: 0.9rem; color: var(--text); padding: 4px;">
  <div style="padding: 8px 0; border-bottom: 1px solid var(--border);">notification 1</div>
  <div style="padding: 8px 0; border-bottom: 1px solid var(--border);">notification 2</div>
  <div style="padding: 8px 0; border-bottom: 1px solid var(--border);">notification 3</div>
  <div style="padding: 8px 0; border-bottom: 1px solid var(--border);">notification 4</div>
  <div style="padding: 8px 0; border-bottom: 1px solid var(--border);">notification 5</div>
  <div style="padding: 8px 0;">notification 6</div>
</div>
""", unsafe_allow_html=True)

  # ══════════════════════════════════════════════════════════════════════════
  # HERO — personalised, simple
  # ══════════════════════════════════════════════════════════════════════════
  st.markdown(f"""
<div class="page-hero" style="margin-top:-20px;">
 <div class="hero-badge">Resume Analysis</div>
 <h1>{greeting}, {display_name}</h1>
 <p>Upload your resume for an instant AI-powered score, skills analysis, and personalised improvement tips.</p>
</div>
""", unsafe_allow_html=True)

  # ══════════════════════════════════════════════════════════════════════════
  # UPLOAD
  # ══════════════════════════════════════════════════════════════════════════
  st.markdown('<div class="section-label">Upload Resume</div>', unsafe_allow_html=True)

  st.markdown("""
<div class="card">
 <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
  <span style="font-size:1.2rem"></span>
  <div class="card-title">Upload Your Resume</div>
 </div>
 <div class="card-sub">PDF · DOCX · TXT &nbsp;·&nbsp; Single file</div>
</div>""", unsafe_allow_html=True)

  uploaded_file = st.file_uploader(
    "Drop your resume here",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=False,
    help="Supported: PDF, DOCX, TXT.",
    key="cust_uploader",
  )

  if uploaded_file:
    if st.button("Analyse My Resume", use_container_width=True, key="cust_analyse"):
      with st.spinner("Analysing your resume…"):
        safe_name = sanitize_filename(uploaded_file.name)
        temp_dir = os.path.join(BASE_DIR, "resumes")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, safe_name)

        with open(temp_path, "wb") as f:
          f.write(uploaded_file.getbuffer())

        text = extract_text(temp_path)
        sections = split_sections(text)
        total_score, breakdown = score_resume(sections, return_breakdown=True)

        # Domain analysis
        engine = ResumeSemanticSearch()
        engine.index_resumes([{"resume": safe_name, "score": total_score, "sections": sections}])
        domain_scores = {}
        for domain, query in DOMAIN_QUERIES.items():
          matches = engine.search(query, top_k=1)
          domain_scores[domain] = round(float(matches[0][1]), 3) if matches and matches[0][0] == safe_name else 0.0

        try:
          os.remove(temp_path)
        except OSError:
          pass

        st.session_state.cust_analysis_result = {
          "name": safe_name,
          "score": total_score,
          "breakdown": breakdown,
          "sections": sections,
          "domains": domain_scores,
        }
      st.rerun()

  # ══════════════════════════════════════════════════════════════════════════
  # ANALYSIS RESULTS
  # ══════════════════════════════════════════════════════════════════════════
  result = st.session_state.cust_analysis_result

  if result:
    score = result["score"]
    breakdown = result["breakdown"]
    sections = result["sections"]
    domains = result["domains"]
    s_color = score_color(score)
    s_pct = min(100, round(score / 65 * 100))
    primary_domain = max(domains, key=domains.get) if domains else "N/A"
    primary_conf = round(domains.get(primary_domain, 0) * 100, 1)

    # ── Score overview ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Your Results</div>', unsafe_allow_html=True)

    ov1, ov2, ov3 = st.columns([2.5, 1, 1])

    with ov1:
      st.markdown(f"""
<div class="card" style="border-left:4px solid {s_color};padding:24px 28px">
 <div class="card-sub" style="margin-bottom:8px">{result['name']}</div>
 <div style="font-size:1.3rem;font-weight:800;color:var(--text);margin-bottom:10px;letter-spacing:-0.02em">
  Overall Score: <span style="color:{s_color}">{score}</span>
  <span style="font-size:0.85rem;color:var(--muted);font-weight:400"> / 65</span>
 </div>
 <div style="height:8px;background:var(--surface3);border-radius:4px;overflow:hidden;max-width:360px">
  <div style="width:{s_pct}%;height:100%;background:{s_color};border-radius:4px;transition:width 0.8s ease"></div>
 </div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:var(--muted);margin-top:5px">{s_pct}% match score</div>
</div>""", unsafe_allow_html=True)

    with ov2:
      st.markdown(f"""
<div class="stat-card" style="text-align:center;border-top:3px solid {s_color}">
 <div class="stat-card-label">Match</div>
 <div class="stat-card-value" style="color:{s_color}">{s_pct}%</div>
</div>""", unsafe_allow_html=True)

    with ov3:
      st.markdown(f"""
<div class="stat-card" style="text-align:center;border-top:3px solid var(--accent)">
 <div class="stat-card-label">Best Domain</div>
 <div style="font-size:0.88rem;font-weight:700;color:var(--accent);margin-top:6px">{primary_domain}</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--muted);margin-top:2px">{primary_conf}%</div>
</div>""", unsafe_allow_html=True)

    # ── Score breakdown + Skills ──────────────────────────────────────────
    bd_left, bd_right = st.columns(2)

    MAX_SECTIONS = {
      "Skills": 20, "Projects": 15, "Internships": 20,
      "Achievements": 10, "Experience": 5, "Extras": 5, "CGPA": 10,
    }
    COLORS = ["var(--accent)", "var(--purple)", "var(--pink)",
          "var(--ok)", "var(--warn)", "#94a3b8", "var(--accent)"]

    with bd_left:
      st.markdown('<div class="card" style="padding:22px 26px">', unsafe_allow_html=True)
      st.markdown('<div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
      st.markdown('<div class="card-sub" style="margin-bottom:16px">Per-section analysis</div>', unsafe_allow_html=True)
      for i, (label, val) in enumerate(breakdown.items()):
        max_v = MAX_SECTIONS.get(label, 20)
        color = COLORS[i % len(COLORS)]
        st.markdown(render_score_bar(label, val, max_v, color), unsafe_allow_html=True)
      st.markdown('</div>', unsafe_allow_html=True)

    with bd_right:
      st.markdown('<div class="card" style="padding:22px 26px">', unsafe_allow_html=True)
      st.markdown('<div class="card-title">Skills Detected</div>', unsafe_allow_html=True)
      st.markdown('<div class="card-sub" style="margin-bottom:14px">Extracted from your resume</div>', unsafe_allow_html=True)
      raw_skills = sections.get("skills", "")
      skills = [s.strip() for s in re.split(r'[,\n|•/]', raw_skills) if s.strip() and len(s.strip()) > 1]
      if skills:
        chip_cls = ["chip-teal", "chip-indigo", "chip-pink", "chip-green", "chip-warn"]
        chips = " ".join(render_chip(s, chip_cls[i % len(chip_cls)]) for i, s in enumerate(skills))
        st.markdown(f'<div style="line-height:2.2">{chips}</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border)">
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em">{len(skills)} skills identified</div>
</div>""", unsafe_allow_html=True)
      else:
        st.markdown('<div style="color:var(--muted);font-style:italic;font-size:0.85rem;padding:20px 0">No skills detected — make sure your resume has a clear skills section.</div>', unsafe_allow_html=True)
      st.markdown('</div>', unsafe_allow_html=True)

    # ── Improvement Suggestions ───────────────────────────────────────────
    st.markdown('<div class="section-label">Improvement Suggestions</div>', unsafe_allow_html=True)

    suggestions = _generate_suggestions(breakdown)

    st.markdown("""
<div class="card" style="padding:22px 26px">
 <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
  <span style="font-size:1.1rem"></span>
  <div class="card-title">AI-Powered Tips</div>
 </div>""", unsafe_allow_html=True)

    for sug in suggestions:
      st.markdown(f"""
<div style="padding:12px 16px;background:var(--surface2);border:1px solid var(--border);
      border-radius:10px;margin-bottom:8px;font-size:0.85rem;color:var(--text2);
      line-height:1.6;transition:border-color 0.2s ease"
   onmouseover="this.style.borderColor='var(--accent)'"
   onmouseout="this.style.borderColor='var(--border)'">
 {sug}
</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

  elif not uploaded_file:
    # Empty state
    st.markdown("""
<div class="card" style="text-align:center;padding:50px;border-style:dashed">
 <div style="font-size:2.4rem;margin-bottom:14px"></div>
 <div class="card-title" style="font-size:1.05rem">No Analysis Yet</div>
 <div style="color:var(--muted2);font-size:0.88rem;margin-top:8px;max-width:400px;margin-left:auto;margin-right:auto">
  Upload your resume above to get an instant AI-powered score, domain classification, and improvement suggestions.
 </div>
</div>""", unsafe_allow_html=True)
