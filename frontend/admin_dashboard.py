"""
frontend/admin_dashboard.py — HR (Admin) Dashboard.

Multi-section SaaS dashboard with sidebar navigation:
 1. App Overview — pipeline metrics + summary
 2. Resume Analysis — list, score, shortlist/reject
 3. Best Profiles — top candidates ranked
 4. Compare    — side-by-side candidate comparison
"""

from __future__ import annotations

import os
import sys
import json
import re
from datetime import datetime

import streamlit as st
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADERS
# ══════════════════════════════════════════════════════════════════════════════

def _load_results():
  ranking_path  = os.path.join(OUTPUT_DIR, "ranking.csv")
  extracted_path = os.path.join(OUTPUT_DIR, "extracted.json")
  domains_path  = os.path.join(OUTPUT_DIR, "domains.json")

  ranking_df = pd.read_csv(ranking_path) if os.path.exists(ranking_path) else None
  extracted = json.load(open(extracted_path)) if os.path.exists(extracted_path) else None
  domains  = json.load(open(domains_path)) if os.path.exists(domains_path) else None

  return ranking_df, extracted, domains


def _init_hr_state():
  defaults = {
    "hr_shortlisted": [],
    "hr_rejected": [],
    "hr_activity_log": [],
    "hr_selected_resume": None,
    "hr_nav": "App Overview",
    "hr_compare_selection": [],
  }
  for k, v in defaults.items():
    if k not in st.session_state:
      st.session_state[k] = v


def _log_activity(action: str, name: str):
  entry = {"time": datetime.now().strftime("%I:%M %p"), "action": action, "name": name}
  st.session_state.hr_activity_log.insert(0, entry)
  st.session_state.hr_activity_log = st.session_state.hr_activity_log[:20]


def _get_status(name: str) -> str:
  if name in st.session_state.hr_shortlisted:
    return "shortlisted"
  if name in st.session_state.hr_rejected:
    return "rejected"
  return "pending"


def _status_chip(status: str) -> str:
  m = {
    "shortlisted": (" Shortlisted", "rgba(74,222,128,0.10)", "#4ade80"),
    "rejected":  (" Rejected",  "rgba(239,68,68,0.10)", "#ef4444"),
    "pending":   (" Pending",   "rgba(229,166,62,0.10)", "#e5a63e"),
  }
  label, bg, fg = m.get(status, m["pending"])
  return (f'<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;'
      f'border-radius:6px;font-size:0.68rem;font-family:\'JetBrains Mono\',monospace;'
      f'background:{bg};color:{fg}">{label}</span>')


# ══════════════════════════════════════════════════════════════════════════════
# SECTION RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def _render_overview(ranking_df, extracted, domains):
  """App Overview — pipeline metrics + activity log."""

  all_names = ranking_df["Resume"].tolist()
  total = len(all_names)
  shortlisted = len([n for n in all_names if n in st.session_state.hr_shortlisted])
  rejected  = len([n for n in all_names if n in st.session_state.hr_rejected])
  pending   = total - shortlisted - rejected
  avg_score  = round(ranking_df["Score"].mean(), 1) if total else 0
  top_score  = ranking_df["Score"].max() if total else 0

  st.markdown("""
<div class="page-hero">
 <div class="hero-badge">App Overview</div>
 <h1>Hiring Pipeline</h1>
 <p>Real-time overview of your recruitment pipeline — track candidates, monitor scores, and review activity.</p>
</div>""", unsafe_allow_html=True)

  # ── Metric cards ──────────────────────────────────────────────────────────
  st.markdown('<div class="section-label">Key Metrics</div>', unsafe_allow_html=True)

  m1, m2, m3, m4, m5 = st.columns(5)
  metrics = [
    (m1, "", "Total Resumes", str(total),    "#4f8ff7"),
    (m2, "", "Shortlisted",  str(shortlisted), "#4ade80"),
    (m3, "", "Rejected",    str(rejected),   "#ef4444"),
    (m4, "", "Pending",    str(pending),   "#e5a63e"),
    (m5, "", "Avg Score",   str(avg_score),  "#a78bfa"),
  ]
  for col, icon, label, val, color in metrics:
    with col:
      st.markdown(f"""
<div class="stat-card" style="border-left:3px solid {color}">
 <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
  <span style="font-size:1.15rem">{icon}</span>
  <div class="stat-card-label" style="margin-bottom:0">{label}</div>
 </div>
 <div class="stat-card-value" style="color:{color}">{val}</div>
</div>""", unsafe_allow_html=True)

  # ── Summary cards row ─────────────────────────────────────────────────────
  st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)

  s1, s2, s3 = st.columns(3)

  with s1:
    st.markdown(f"""
<div class="card" style="padding:22px 26px">
 <div class="card-title">Top Score</div>
 <div class="card-sub" style="margin-bottom:12px">Highest scoring candidate</div>
 <div style="font-size:2.2rem;font-weight:800;color:#4ade80;letter-spacing:-0.03em">{top_score}<span style="font-size:0.8rem;color:var(--muted);font-weight:400"> /65</span></div>
</div>""", unsafe_allow_html=True)

  with s2:
    domain_count = sum(1 for v in (domains or {}).values() if v)
    st.markdown(f"""
<div class="card" style="padding:22px 26px">
 <div class="card-title">Domains Active</div>
 <div class="card-sub" style="margin-bottom:12px">Domains with matched candidates</div>
 <div style="font-size:2.2rem;font-weight:800;color:#4f8ff7;letter-spacing:-0.03em">{domain_count}<span style="font-size:0.8rem;color:var(--muted);font-weight:400"> / {len(domains or {})}</span></div>
</div>""", unsafe_allow_html=True)

  with s3:
    accept_rate = round(shortlisted / total * 100, 1) if total else 0
    st.markdown(f"""
<div class="card" style="padding:22px 26px">
 <div class="card-title">Accept Rate</div>
 <div class="card-sub" style="margin-bottom:12px">Shortlisted vs total</div>
 <div style="font-size:2.2rem;font-weight:800;color:#a78bfa;letter-spacing:-0.03em">{accept_rate}<span style="font-size:0.8rem;color:var(--muted);font-weight:400">%</span></div>
</div>""", unsafe_allow_html=True)

  # ── Activity Log ──────────────────────────────────────────────────────────
  st.markdown('<div class="section-label">Recent Activity</div>', unsafe_allow_html=True)

  log = st.session_state.hr_activity_log
  if not log:
    st.markdown("""
<div class="card" style="text-align:center;padding:32px;border-style:dashed">
 <div style="font-size:1.4rem;margin-bottom:8px"></div>
 <div style="color:var(--muted2);font-size:0.85rem">No actions yet. Use <strong>Resume Analysis</strong> to shortlist or reject candidates.</div>
</div>""", unsafe_allow_html=True)
  else:
    st.markdown('<div class="card" style="padding:0;overflow:hidden">', unsafe_allow_html=True)
    for i, entry in enumerate(log[:8]):
      icon = "" if entry["action"] == "Shortlisted" else ""
      a_color = "#4ade80" if entry["action"] == "Shortlisted" else "#ef4444"
      name_d = os.path.splitext(entry["name"])[0].replace("_", " ")
      border = "border-bottom:1px solid var(--border);" if i < min(len(log), 8) - 1 else ""
      st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:12px 20px;{border}">
 <span>{icon}</span>
 <div style="flex:1"><span style="font-weight:600;font-size:0.85rem;color:var(--text)">{name_d}</span>
  <span style="color:{a_color};font-size:0.8rem;margin-left:6px">{entry['action'].lower()}</span></div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--muted)">{entry['time']}</div>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_resume_analysis(ranking_df, extracted, domains):
  """Resume Analysis — list, score, shortlist/reject with filters."""

  from frontend.styles import score_color, render_chip

  st.markdown("""
<div class="page-hero">
 <div class="hero-badge">Resume Analysis</div>
 <h1>Review Candidates</h1>
 <p>Score, filter, and manage candidates. Shortlist the best fits and reject mismatches.</p>
</div>""", unsafe_allow_html=True)

  all_names = ranking_df["Resume"].tolist()
  total = len(all_names)

  # ── Filters ───────────────────────────────────────────────────────────────
  st.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)

  f1, f2, f3 = st.columns([2, 2, 1])
  with f1:
    score_range = st.slider("Score Range", 0, 65, (0, 65), key="hr_score_slider")
  with f2:
    domain_opts = ["All"] + list((domains or {}).keys())
    domain_filter = st.selectbox("Domain", domain_opts, key="hr_domain_filter")
  with f3:
    status_filter = st.selectbox("Status", ["All", "Pending", "Shortlisted", "Rejected"], key="hr_status_filter")

  filtered = ranking_df[
    (ranking_df["Score"] >= score_range[0]) &
    (ranking_df["Score"] <= score_range[1])
  ].copy()

  if domain_filter != "All" and domains:
    filtered = filtered[filtered["Resume"].isin(set(domains.get(domain_filter, [])))]
  if status_filter != "All":
    filtered = filtered[filtered["Resume"].apply(lambda n: _get_status(n) == status_filter.lower())]

  # ── Candidate list ────────────────────────────────────────────────────────
  st.markdown(f'<div class="section-label">Candidates ({len(filtered)} of {total})</div>', unsafe_allow_html=True)

  # Header
  st.markdown("""
<div style="display:grid;grid-template-columns:40px 1fr 110px 100px 200px;gap:12px;
      padding:10px 20px;background:var(--surface2);border-radius:12px 12px 0 0;border:1px solid var(--border)">
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">#</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Candidate</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Score</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Status</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;text-align:right">Actions</div>
</div>""", unsafe_allow_html=True)

  for rank, (_, row) in enumerate(filtered.iterrows(), start=1):
    name = row["Resume"]
    score = row["Score"]
    status = _get_status(name)
    pct = min(100, round(score / 65 * 100))
    s_color = score_color(score)

    st.markdown(f"""
<div style="display:grid;grid-template-columns:40px 1fr 110px 100px 200px;gap:12px;
      padding:12px 20px;border-bottom:1px solid var(--border);border-left:1px solid var(--border);
      border-right:1px solid var(--border);align-items:center;transition:background 0.15s ease"
   onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background='transparent'">
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:var(--muted)">{rank}</div>
 <div>
  <div style="font-weight:600;font-size:0.88rem;color:var(--text)">{os.path.splitext(name)[0].replace('_',' ')}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--muted);margin-top:2px">{name}</div>
 </div>
 <div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:{s_color};font-weight:600">{score}<span style="font-size:0.6rem;color:var(--muted);font-weight:400"> /65</span></div>
  <div style="height:4px;background:var(--surface3);border-radius:4px;overflow:hidden;margin-top:4px;width:75px">
   <div style="width:{pct}%;height:100%;background:{s_color};border-radius:4px"></div>
  </div>
 </div>
 <div>{_status_chip(status)}</div>
 <div></div>
</div>""", unsafe_allow_html=True)

    # Action buttons
    _, _, _, _, act = st.columns([0.3, 1, 0.75, 0.7, 1.4])
    with act:
      b1, b2, b3 = st.columns(3)
      with b1:
        if st.button("View", key=f"v_{name}", use_container_width=True):
          st.session_state.hr_selected_resume = name
      with b2:
        if status != "shortlisted":
          if st.button("", key=f"s_{name}", use_container_width=True):
            if name in st.session_state.hr_rejected:
              st.session_state.hr_rejected.remove(name)
            if name not in st.session_state.hr_shortlisted:
              st.session_state.hr_shortlisted.append(name)
            _log_activity("Shortlisted", name)
            st.rerun()
      with b3:
        if status != "rejected":
          if st.button("", key=f"r_{name}", use_container_width=True):
            if name in st.session_state.hr_shortlisted:
              st.session_state.hr_shortlisted.remove(name)
            if name not in st.session_state.hr_rejected:
              st.session_state.hr_rejected.append(name)
            _log_activity("Rejected", name)
            st.rerun()

  # Bottom border
  st.markdown('<div style="height:3px;border-radius:0 0 12px 12px;background:var(--surface);border:1px solid var(--border);border-top:none"></div>', unsafe_allow_html=True)

  # ── Detail panel for selected resume ──────────────────────────────────────
  sel = st.session_state.hr_selected_resume
  if sel and extracted and sel in extracted:
    sections = extracted[sel]
    score_row = ranking_df.loc[ranking_df["Resume"] == sel, "Score"]
    sel_score = float(score_row.values[0]) if not score_row.empty else 0
    sel_color = score_color(sel_score)
    sel_pct = min(100, round(sel_score / 65 * 100))
    status = _get_status(sel)

    st.markdown('<div class="section-label">Candidate Deep Dive</div>', unsafe_allow_html=True)

    d_left, d_right = st.columns([3, 1])
    with d_left:
      st.markdown(f"""
<div class="card" style="border-top:3px solid {sel_color};padding:24px 28px">
 <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
  <div style="width:42px;height:42px;border-radius:12px;background:var(--surface3);display:flex;align-items:center;justify-content:center;font-size:1.1rem"></div>
  <div>
   <div style="font-size:1.05rem;font-weight:700;color:var(--text)">{os.path.splitext(sel)[0].replace('_',' ')}</div>
   <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--muted);margin-top:2px">{sel}</div>
  </div>
  <div style="margin-left:auto">{_status_chip(status)}</div>
 </div>
 <div style="display:flex;align-items:center;gap:16px">
  <div>
   <div style="font-family:'JetBrains Mono',monospace;font-size:0.52rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Score</div>
   <div style="font-size:1.6rem;font-weight:800;color:{sel_color};margin-top:3px">{sel_score}<span style="font-size:0.7rem;color:var(--muted);font-weight:400"> /65</span></div>
  </div>
  <div style="flex:1;max-width:280px">
   <div style="height:6px;background:var(--surface3);border-radius:4px;overflow:hidden">
    <div style="width:{sel_pct}%;height:100%;background:{sel_color};border-radius:4px"></div>
   </div>
  </div>
 </div>
</div>""", unsafe_allow_html=True)

    with d_right:
      st.markdown(f"""
<div class="stat-card" style="text-align:center;border-top:3px solid {sel_color}">
 <div style="font-size:2.6rem;font-weight:800;color:{sel_color};line-height:1">{sel_score}</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.12em;margin-top:6px">Score / 65</div>
</div>""", unsafe_allow_html=True)

    # Skills + Experience
    sk_col, ex_col = st.columns(2)

    with sk_col:
      st.markdown('<div class="card" style="padding:20px 24px">', unsafe_allow_html=True)
      st.markdown('<div class="card-title">Skills</div>', unsafe_allow_html=True)
      raw = sections.get("skills", "")
      skills = [s.strip() for s in re.split(r'[,\n|•/]', raw) if s.strip() and len(s.strip()) > 1]
      if skills:
        chip_cls = ["chip-teal", "chip-indigo", "chip-pink", "chip-green", "chip-warn"]
        chips = " ".join(render_chip(s, chip_cls[i % len(chip_cls)]) for i, s in enumerate(skills))
        st.markdown(f'<div style="line-height:2.1;margin-top:10px">{chips}</div>', unsafe_allow_html=True)
        match_pct = min(100, round(len(skills) / 15 * 100))
        st.markdown(f"""
<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border)">
 <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:4px">
  <span style="color:var(--muted2)">Coverage</span>
  <span style="font-family:'JetBrains Mono',monospace;color:var(--accent)">{len(skills)} skills · {match_pct}%</span>
 </div>
 <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden">
  <div style="width:{match_pct}%;height:100%;background:var(--accent);border-radius:4px"></div>
 </div>
</div>""", unsafe_allow_html=True)
      else:
        st.caption("No skills detected")
      st.markdown('</div>', unsafe_allow_html=True)

    with ex_col:
      st.markdown('<div class="card" style="padding:20px 24px">', unsafe_allow_html=True)
      st.markdown('<div class="card-title">Experience</div>', unsafe_allow_html=True)
      for key, icon, title in [("experience", "", "Work"), ("education", "", "Education"), ("projects", "", "Projects")]:
        content = sections.get(key, "").strip()
        if content:
          lines = [l.strip() for l in content.split("\n") if l.strip()][:3]
          st.markdown(f'<div style="margin-bottom:14px"><div style="display:flex;align-items:center;gap:5px;margin-bottom:6px"><span style="font-size:0.85rem">{icon}</span><span style="font-weight:600;font-size:0.8rem;color:var(--text)">{title}</span></div>', unsafe_allow_html=True)
          for line in lines:
            st.markdown(f'<div style="padding:4px 0;color:var(--muted2);font-size:0.78rem;border-bottom:1px solid var(--border)">› {line}</div>', unsafe_allow_html=True)
          st.markdown('</div>', unsafe_allow_html=True)
      st.markdown('</div>', unsafe_allow_html=True)


def _render_best_profiles(ranking_df, extracted):
  """Best Profiles — top candidates by score."""

  from frontend.styles import score_color, render_chip

  st.markdown("""
<div class="page-hero">
 <div class="hero-badge">Best Profiles</div>
 <h1>Top Candidates</h1>
 <p>Your highest-scoring candidates, ranked and ready for review.</p>
</div>""", unsafe_allow_html=True)

  total_resumes = len(ranking_df)
  if total_resumes > 1:
    max_v = min(20, total_resumes)
    def_v = min(10, total_resumes)
    top_n = st.slider("Show top", 1, max_v, def_v, key="hr_top_n")
  else:
    top_n = total_resumes
  top_df = ranking_df.nlargest(top_n, "Score")

  for rank, (_, row) in enumerate(top_df.iterrows(), start=1):
    name = row["Resume"]
    score = row["Score"]
    pct = min(100, round(score / 65 * 100))
    s_color = score_color(score)
    medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"#{rank}")
    status = _get_status(name)

    # Skills from extracted data
    skills_text = ""
    if extracted and name in extracted:
      raw = extracted[name].get("skills", "")
      skills = [s.strip() for s in re.split(r'[,\n|•/]', raw) if s.strip() and len(s.strip()) > 1][:8]
      if skills:
        chip_cls = ["chip-teal", "chip-indigo", "chip-pink", "chip-green", "chip-warn"]
        skills_text = " ".join(render_chip(s, chip_cls[i % len(chip_cls)]) for i, s in enumerate(skills))

    left, right = st.columns([4, 1])
    with left:
      st.markdown(f"""
<div class="card" style="padding:20px 26px;border-left:3px solid {s_color}">
 <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
  <span style="font-size:1.2rem">{medal}</span>
  <div>
   <div style="font-weight:700;font-size:0.95rem;color:var(--text)">{os.path.splitext(name)[0].replace('_',' ')}</div>
   <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--muted)">{name}</div>
  </div>
  <div style="margin-left:auto">{_status_chip(status)}</div>
 </div>
 <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden;max-width:320px;margin-bottom:8px">
  <div style="width:{pct}%;height:100%;background:{s_color};border-radius:4px"></div>
 </div>
 <div style="line-height:2;margin-top:6px">{skills_text}</div>
</div>""", unsafe_allow_html=True)

    with right:
      st.markdown(f"""
<div class="stat-card" style="text-align:center;border-top:3px solid {s_color}">
 <div style="font-size:2.2rem;font-weight:800;color:{s_color};line-height:1">{score}</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-top:5px">Score / 65</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:var(--muted2);margin-top:6px">{pct}%</div>
</div>""", unsafe_allow_html=True)


def _render_compare(ranking_df, extracted):
  """Compare — side-by-side candidate comparison."""

  from frontend.styles import score_color, render_chip

  st.markdown("""
<div class="page-hero">
 <div class="hero-badge">Compare</div>
 <h1>Compare Candidates</h1>
 <p>Select two or more candidates to see a side-by-side comparison of scores, skills, and sections.</p>
</div>""", unsafe_allow_html=True)

  all_names = ranking_df["Resume"].tolist()

  selected = st.multiselect(
    "Select candidates to compare",
    options=all_names,
    default=st.session_state.hr_compare_selection[:4] if st.session_state.hr_compare_selection else [],
    max_selections=4,
    key="hr_compare_picker",
  )
  st.session_state.hr_compare_selection = selected

  if len(selected) < 2:
    st.markdown("""
<div class="card" style="text-align:center;padding:40px;border-style:dashed">
 <div style="font-size:2rem;margin-bottom:10px"></div>
 <div style="color:var(--muted2);font-size:0.88rem">Select at least <strong>2 candidates</strong> above to begin comparison.</div>
</div>""", unsafe_allow_html=True)
    return

  # Comparison columns
  cols = st.columns(len(selected))

  for col, name in zip(cols, selected):
    with col:
      score_row = ranking_df.loc[ranking_df["Resume"] == name, "Score"]
      score = float(score_row.values[0]) if not score_row.empty else 0
      pct = min(100, round(score / 65 * 100))
      s_color = score_color(score)
      status = _get_status(name)

      # Score card
      st.markdown(f"""
<div class="card" style="border-top:3px solid {s_color};padding:20px 22px">
 <div style="font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:4px">{os.path.splitext(name)[0].replace('_',' ')}</div>
 <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);margin-bottom:12px">{name}</div>
 <div style="text-align:center;margin-bottom:12px">
  <div style="font-size:2.4rem;font-weight:800;color:{s_color};line-height:1">{score}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;color:var(--muted);text-transform:uppercase;margin-top:4px">Score / 65 · {pct}%</div>
 </div>
 <div style="height:5px;background:var(--surface3);border-radius:4px;overflow:hidden;margin-bottom:12px">
  <div style="width:{pct}%;height:100%;background:{s_color};border-radius:4px"></div>
 </div>
 <div style="text-align:center">{_status_chip(status)}</div>
</div>""", unsafe_allow_html=True)

      # Skills
      if extracted and name in extracted:
        sections = extracted[name]
        raw = sections.get("skills", "")
        skills = [s.strip() for s in re.split(r'[,\n|•/]', raw) if s.strip() and len(s.strip()) > 1][:10]

        st.markdown('<div class="card" style="padding:16px 20px">', unsafe_allow_html=True)
        st.markdown('<div class="card-title" style="font-size:0.78rem">Skills</div>', unsafe_allow_html=True)
        if skills:
          chip_cls = ["chip-teal", "chip-indigo", "chip-pink", "chip-green", "chip-warn"]
          for i, s in enumerate(skills):
            st.markdown(render_chip(s, chip_cls[i % len(chip_cls)]), unsafe_allow_html=True)
        else:
          st.caption("None detected")
        st.markdown('</div>', unsafe_allow_html=True)

        # Experience summary
        st.markdown('<div class="card" style="padding:16px 20px">', unsafe_allow_html=True)
        st.markdown('<div class="card-title" style="font-size:0.78rem">Experience</div>', unsafe_allow_html=True)
        exp = sections.get("experience", "").strip()
        if exp:
          for line in [l.strip() for l in exp.split("\n") if l.strip()][:3]:
            st.markdown(f'<div style="font-size:0.75rem;color:var(--muted2);padding:3px 0;border-bottom:1px solid var(--border)">› {line}</div>', unsafe_allow_html=True)
        else:
          st.caption("Not listed")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

# removed show_admin_dashboard to rely on Streamlit multipage routing
