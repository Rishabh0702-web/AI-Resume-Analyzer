"""
frontend/pages/1_Resume_Analysis.py — HR Candidate Management

Thin wrapper that renders the Resume Analysis section of the HR dashboard
using the logic from admin_dashboard.py.
"""
import streamlit as st
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

from frontend.styles import inject_styles
from frontend.admin_dashboard import _init_hr_state, _load_results, _render_resume_analysis

st.set_page_config(page_title="ResumeIQ — Candidates", page_icon="", layout="wide")
inject_styles()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
  st.switch_page("app.py")

_init_hr_state()
ranking_df, extracted, domains = _load_results()

if ranking_df is None or ranking_df.empty:
  st.markdown("""
<div class="card" style="text-align:center;padding:50px;border-style:dashed">
 <div style="font-size:2.4rem;margin-bottom:14px"></div>
 <div class="card-title" style="font-size:1.1rem">No Resumes Analysed</div>
 <div style="color:var(--muted2);font-size:0.88rem;margin-top:8px;max-width:440px;margin-left:auto;margin-right:auto">
  Upload resumes to begin analysis.
 </div>
</div>""", unsafe_allow_html=True)
else:
  _render_resume_analysis(ranking_df, extracted, domains)
