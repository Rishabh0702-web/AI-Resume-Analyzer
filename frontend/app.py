"""
frontend/app.py — Entry point: role-based routing to HR or Customer dashboard.

Only two dashboards exist:
 • HR (Admin)  — Native Streamlit multipage nav (Overview, Analysis, Best Profiles, Compare)
 • Customer   — minimal single-page (upload + analysis only)

Sidebar page links are hidden from the customer view via CSS.
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
  initial_sidebar_state="expanded",
)

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

from backend.semantic_search import ResumeSemanticSearch, DOMAIN_QUERIES, get_model
from backend.extractor import extract_text
from backend.section_splitter import split_sections
from backend.scorer import score_resume
from backend.utils import sanitize_filename
from backend.database import save_result, get_database_status
from frontend.styles import inject_styles
from frontend.admin_dashboard import _init_hr_state, _load_results, _render_overview
from frontend.customer_dashboard import show_customer_dashboard

RESUME_DIR = os.path.join(BASE_DIR, "resumes")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ranking_path  = os.path.join(OUTPUT_DIR, "ranking.csv")
extracted_path = os.path.join(OUTPUT_DIR, "extracted.json")
domains_path  = os.path.join(OUTPUT_DIR, "domains.json")
results_exist = os.path.exists(ranking_path) and os.path.exists(extracted_path)

for key, val in [("analysis_running", False), ("analysis_done", False), ("overwrite_confirmed", False)]:
  if key not in st.session_state:
    st.session_state[key] = val

# ── Cache model ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
  return get_model()

load_model()
inject_styles()

# ── Authentication State ──────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "role" not in st.session_state:
  st.session_state["role"] = None

# ── Login Page (Dummy UI mapping screenshot) ──────────────────────────────────
if not st.session_state["logged_in"]:
  # Hide sidebar
  st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
  
  col1, col2, col3 = st.columns([1, 1.2, 1])
  with col2:
    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-weight: 900; letter-spacing: 0.05em; margin-bottom: 24px;'>DASHBOARD</h1>", unsafe_allow_html=True)
    
    # Segmented / Radio selector mimicking the screenshot
    role_col1, role_col2, role_col3 = st.columns([1, 2, 1])
    with role_col2:
      role = st.selectbox(
        "Role",
        ["HR", "Student"],
        label_visibility="collapsed",
        key="login_role"
      )
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    # User ID Input
    u_col1, u_col2 = st.columns([1, 2.5])
    with u_col1:
      st.markdown("<div style='margin-top:8px;font-weight:700;font-size:1.05rem;'>User id</div>", unsafe_allow_html=True)
    with u_col2:
      user_id = st.text_input("User id", label_visibility="collapsed", key="login_uid")
    
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    
    # Password Input
    p_col1, p_col2 = st.columns([1, 2.5])
    with p_col1:
      st.markdown("<div style='margin-top:8px;font-weight:700;font-size:1.05rem;'>Password</div>", unsafe_allow_html=True)
    with p_col2:
      password = st.text_input("Password", type="password", label_visibility="collapsed", key="login_pwd")
      
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns([1, 1, 1])
    with b2:
      if st.button("Login", use_container_width=True, type="primary"):
        if user_id and password:
          st.session_state["logged_in"] = True
          st.session_state["role"] = "admin" if role == "HR" else "customer"
          st.session_state["_dashboard_view"] = "HR (Admin)" if role == "HR" else "Customer"
          st.rerun()
        else:
          st.error("Please enter any dummy credentials.")
          
  st.stop()

# ── Dashboard active view string mapping ──
_view = "HR (Admin)" if st.session_state["role"] == "admin" else "Customer"

# If logged in, add logout button to sidebar
with st.sidebar:
  st.markdown("---")
  if st.session_state.get("role") == "customer":
    st.markdown("""
<div style="display:flex; flex-direction:column; align-items:center; margin-bottom:20px;">
 <div style="width:72px; height:72px; border-radius:50%; background:var(--surface2); border:2px solid var(--primary); display:flex; justify-content:center; align-items:center; margin-bottom:12px;">
  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width:36px; height:36px; color:var(--text);">
   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
 </div>
 <div style="font-weight:700; font-size:1.05rem; color:var(--text);">Student Profile</div>
 <div style="font-size:0.8rem; color:var(--muted); margin-top:4px;">View / Edit</div>
</div>
""", unsafe_allow_html=True)

  st.markdown(f"**Current Role:** {'HR (Admin)' if st.session_state['role'] == 'admin' else 'Student (Customer)'}")
  if st.button("Log Out", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["_dashboard_view"] = None
    st.rerun()

# ── Customer dashboard ────────────────────────────────────────────────────────
if _view == "Customer":
  st.session_state["role"] = "customer"
  # Hide the multipage nav items so customer sees nothing extra
  st.markdown("""<style>[data-testid="stSidebarNav"] { display: none !important; }</style>""", unsafe_allow_html=True)
  show_customer_dashboard()
  st.stop()

# ── HR Admin Dashboard (App Overview & Upload) ────────────────────────────────
st.session_state["role"] = "admin"
_init_hr_state()

# 1. Bulk Upload Section
st.markdown('<div class="section-label">Upload Candidates</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card">
 <div class="card-title">Bulk Resume Upload</div>
 <div class="card-sub">PDF · DOCX · TXT &nbsp;·&nbsp; Process multiple candidates simultaneously</div>
</div>""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
  "Drag & drop resumes here, or click to browse",
  type=["pdf", "docx", "txt"],
  accept_multiple_files=True,
  help="Supported: PDF, DOCX, TXT. Max 10 MB per file.",
)

db_status = get_database_status()
if db_status["connected"]:
  st.caption(f" Connected to database: {db_status['db_name']}.{db_status['collection_name']}")
else:
  st.warning(f"MongoDB not connected. Saving disabled. Reason: {db_status['error'] or 'unknown error'}")

btn_col, info_col = st.columns([1, 4])
with btn_col:
  analyze = st.button("Analyse Batch", use_container_width=True, type="primary")

if analyze and results_exist and not st.session_state.overwrite_confirmed:
  with info_col:
    st.warning("⚠ Prev results exist. Click **Analyse Batch** again to overwrite and start a new pipeline.")
  st.session_state.overwrite_confirmed = True
  st.stop()

if analyze:
  st.session_state.overwrite_confirmed = False

# ─ Run Analysis Logic
if analyze and not st.session_state.analysis_running:
  if not uploaded_files:
    st.warning("Please upload at least one resume.")
    st.stop()

  st.session_state.analysis_running = True
  st.session_state.analysis_done  = False
  st.markdown('<div class="section-label">Processing</div>', unsafe_allow_html=True)
  progress = st.progress(0, text="Starting analysis…")
  status  = st.empty()

  results: list[dict] = []
  extracted_data: dict = {}
  saved_paths: list[str] = []
  total = len(uploaded_files)

  for idx, file in enumerate(uploaded_files, start=1):
    pct = int((idx / total) * 100)
    safe_name = sanitize_filename(file.name)
    progress.progress(pct, text=f"Analysing {safe_name} ({idx}/{total})…")
    status.caption(f"Processing {safe_name}…")

    path = os.path.join(RESUME_DIR, safe_name)
    with open(path, "wb") as f:
      f.write(file.getbuffer())
    saved_paths.append(path)

    text   = extract_text(path)
    sections = split_sections(text)
    score  = score_resume(sections)

    results.append({"resume": safe_name, "score": score, "sections": sections})
    extracted_data[safe_name] = sections
    save_result({"resume_name": safe_name, "score": score, "sections": sections})

  # Save to outputs dir
  ranking_df = pd.DataFrame([{"Resume": r["resume"], "Score": r["score"]} for r in results]).sort_values("Score", ascending=False)
  ranking_df.to_csv(ranking_path, index=False)

  with open(extracted_path, "w") as f:
    json.dump(extracted_data, f, indent=2)

  search_engine = ResumeSemanticSearch()
  search_engine.index_resumes(results)
  domain_groups = search_engine.classify_by_domain(DOMAIN_QUERIES)

  with open(domains_path, "w") as f:
    json.dump(domain_groups, f, indent=2)

  for p in saved_paths:
    try: os.remove(p)
    except OSError: pass

  st.session_state.analysis_running = False
  st.session_state.analysis_done  = True
  
  # reset HR state pipeline tracking
  for k in ["hr_shortlisted", "hr_rejected", "hr_activity_log", "hr_selected_resume", "hr_compare_selection"]:
    st.session_state[k] = [] if isinstance(st.session_state.get(k), list) else None

  progress.progress(100, text="Analysis complete. Renderings updated.")
  status.empty()
  st.rerun()

# 2. Pipeline Overview (App Overview)
st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
ranking_df, extracted, domains = _load_results()

if ranking_df is None or ranking_df.empty:
  st.markdown("""
<div class="card" style="text-align:center;padding:50px;border-style:dashed;background:var(--surface2)">
 <div style="font-size:2.4rem;margin-bottom:14px"></div>
 <div class="card-title" style="font-size:1.1rem">Empty Pipeline</div>
 <div style="color:var(--muted2);font-size:0.88rem;margin-top:8px;max-width:440px;margin-left:auto;margin-right:auto">
  Upload resumes in the batch processor above to populate your HR pipeline and begin tracking candidates.
 </div>
</div>""", unsafe_allow_html=True)
else:
  _render_overview(ranking_df, extracted, domains)
