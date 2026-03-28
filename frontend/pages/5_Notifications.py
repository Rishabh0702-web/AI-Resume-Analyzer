"""
frontend/pages/5_Notifications.py — Student notification center.
Shows job postings matching the student's domain.
Students can apply by uploading their resume.
"""

import streamlit as st
import os
import sys
import json
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frontend.styles import inject_styles, render_chip, render_top_nav

st.set_page_config(page_title="ResumeIQ — Notifications", page_icon="🔔", layout="wide")
inject_styles()

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("role") != "student":
    st.switch_page("app.py")

render_top_nav()

# ── File paths ────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
JOBS_PATH = os.path.join(OUTPUT_DIR, "jobs.json")
APPS_PATH = os.path.join(OUTPUT_DIR, "applications.json")
RESUME_DIR = os.path.join(BASE_DIR, "resumes")
os.makedirs(RESUME_DIR, exist_ok=True)


def load_json(path: str) -> list[dict]:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_json(path: str, data: list[dict]) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ── Load data ─────────────────────────────────────────────────────────────────
student_domain = st.session_state.get("student_domain", "")
student_id = st.session_state.get("user_id", "")
student_name = st.session_state.get("user_name", "Student")

all_jobs = load_json(JOBS_PATH)
all_applications = load_json(APPS_PATH)

# Filter jobs matching student's domain
matching_jobs = [j for j in all_jobs if j.get("domain") == student_domain]

# Track which jobs this student already applied to
applied_job_ids = {
    a["job_id"] for a in all_applications
    if a.get("student_id") == student_id
}

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-hero">
  <div class="hero-badge">🔔 Notifications</div>
  <h1>Job Opportunities</h1>
  <p>Jobs matching your domain: <strong>{student_domain}</strong>. Apply directly by uploading your resume.</p>
</div>
""", unsafe_allow_html=True)

# ── Quick stats ───────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
<div class="stat-card">
  <div class="stat-card-label">Available Jobs</div>
  <div class="stat-card-value" style="color:var(--accent)">{len(matching_jobs)}</div>
</div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
<div class="stat-card">
  <div class="stat-card-label">Applied</div>
  <div class="stat-card-value" style="color:var(--ok)">{len(applied_job_ids)}</div>
</div>""", unsafe_allow_html=True)
with c3:
    pending = len(matching_jobs) - len(applied_job_ids.intersection(j["id"] for j in matching_jobs))
    st.markdown(f"""
<div class="stat-card">
  <div class="stat-card-label">Pending</div>
  <div class="stat-card-value" style="color:var(--warn)">{pending}</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# JOB NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Your Notifications</div>', unsafe_allow_html=True)

if not matching_jobs:
    st.markdown(f"""
<div class="card" style="text-align:center;padding:40px;border-style:dashed">
  <div style="font-size:2rem;margin-bottom:12px">🔔</div>
  <div class="card-title">No jobs available right now</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:4px">
    No <strong>{student_domain}</strong> positions have been posted yet. Check back later!
  </div>
</div>""", unsafe_allow_html=True)
else:
    DOMAIN_COLORS = {
        "Machine Learning": ("#4f8ff7", "chip-teal"),
        "Web Development": ("#4ade80", "chip-green"),
        "Data Science": ("#a78bfa", "chip-indigo"),
        "Cloud / DevOps": ("#e5a63e", "chip-warn"),
        "Android Development": ("#f472b6", "chip-pink"),
    }

    for idx, job in enumerate(reversed(matching_jobs)):
        job_id = job["id"]
        already_applied = job_id in applied_job_ids
        accent_color, chip_class = DOMAIN_COLORS.get(job["domain"], ("#4f8ff7", "chip-teal"))

        # Format date
        try:
            dt = datetime.fromisoformat(job["posted_at"])
            date_str = dt.strftime("%d %b %Y, %I:%M %p")
            time_ago = ""
        except Exception:
            date_str = job.get("posted_at", "Unknown")

        # Status badge
        if already_applied:
            status_html = render_chip("✓ Applied", "chip-green")
        else:
            status_html = render_chip("New", "chip-teal")

        st.markdown(f"""
<div class="card" style="border-left:3px solid {accent_color}">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px">
    <div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span style="font-size:1.15rem">📢</span>
        <span style="font-weight:700;font-size:1.05rem;color:var(--text)">{job['title']}</span>
        {status_html}
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--muted);margin-top:2px">
        Posted by {job.get('posted_by_name', 'HR')} · {date_str}
      </div>
    </div>
    <div>
      {render_chip(job['domain'], chip_class)}
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px">
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">💰 Salary</div>
      <div style="font-size:0.85rem;color:var(--text2);font-weight:500">{job['salary']}</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">⏰ Hours</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job['working_hours']}</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">📍 Location</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job.get('location', 'N/A')}</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">📊 Experience</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job.get('experience', 'N/A')}</div>
    </div>
  </div>

  <div style="margin-bottom:10px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px">Description</div>
    <div style="font-size:0.82rem;color:var(--muted2);line-height:1.65">{job['description']}</div>
  </div>

  <div style="margin-bottom:6px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px">Requirements</div>
    <div style="font-size:0.82rem;color:var(--muted2);line-height:1.65">{job['requirements']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Apply section
        if already_applied:
            st.markdown(f"""
<div style="background:var(--ok-muted);border:1px solid rgba(74,222,128,0.2);border-radius:10px;
            padding:12px 18px;margin-bottom:20px;margin-top:-8px;display:flex;align-items:center;gap:10px">
  <span style="font-size:1.2rem">✅</span>
  <div>
    <div style="font-weight:600;color:var(--ok);font-size:0.88rem">Application Submitted</div>
    <div style="font-size:0.75rem;color:var(--muted2)">You have already applied for this position.</div>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            with st.expander(f"🚀 Apply for {job['title']}", expanded=False):
                st.markdown("""
<div style="font-size:0.85rem;color:var(--muted2);margin-bottom:12px">
  Upload your resume to apply. Supported formats: PDF, DOCX, TXT.
</div>
""", unsafe_allow_html=True)

                resume_file = st.file_uploader(
                    f"Upload resume for {job['title']}",
                    type=["pdf", "docx", "txt"],
                    accept_multiple_files=False,
                    key=f"resume_{job_id}",
                    label_visibility="collapsed",
                )

                if st.button("Submit Application", key=f"apply_{job_id}", use_container_width=True):
                    if not resume_file:
                        st.error("Please upload your resume before submitting.")
                    else:
                        # Save resume file
                        resume_filename = f"{student_id}_{job_id}_{resume_file.name}"
                        resume_path = os.path.join(RESUME_DIR, resume_filename)
                        with open(resume_path, "wb") as rf:
                            rf.write(resume_file.getbuffer())

                        # Save application record
                        application = {
                            "job_id": job_id,
                            "job_title": job["title"],
                            "student_id": student_id,
                            "student_name": student_name,
                            "student_domain": student_domain,
                            "resume_name": resume_file.name,
                            "resume_file": resume_filename,
                            "applied_at": datetime.now().isoformat(),
                        }

                        apps = load_json(APPS_PATH)
                        apps.append(application)
                        save_json(APPS_PATH, apps)

                        st.success(f"🎉 Application submitted for **{job['title']}**! Your resume has been uploaded.")
                        st.balloons()
                        # Rerun to update UI
                        st.rerun()
