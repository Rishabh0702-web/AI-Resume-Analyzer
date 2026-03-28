"""
frontend/pages/4_Post_Job.py — HR job posting page.
HR can create job requisitions with domain, salary, hours, etc.
Jobs are saved to outputs/jobs.json and matched to students by domain.
"""

import streamlit as st
import os
import sys
import json
import uuid
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frontend.styles import inject_styles, render_chip, render_top_nav

st.set_page_config(page_title="ResumeIQ — Post Job", page_icon="📋", layout="wide")
inject_styles()

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("role") == "student":
    st.switch_page("pages/1_Resume_Analysis.py")

render_top_nav()

# ── File setup ────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
JOBS_PATH = os.path.join(OUTPUT_DIR, "jobs.json")


def load_jobs() -> list[dict]:
    if os.path.exists(JOBS_PATH):
        try:
            with open(JOBS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_jobs(jobs: list[dict]) -> None:
    with open(JOBS_PATH, "w") as f:
        json.dump(jobs, f, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hero">
  <div class="hero-badge">Job Requisition</div>
  <h1>Post a Job</h1>
  <p>Create a new job posting. Matching students will be notified automatically based on the domain you select.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# JOB POSTING FORM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">New Job Posting</div>', unsafe_allow_html=True)

DOMAINS = [
    "Machine Learning",
    "Web Development",
    "Data Science",
    "Cloud / DevOps",
    "Android Development",
]

with st.form("job_form", clear_on_submit=True):
    st.markdown("""
<div class="card">
  <div class="card-title">Job Details</div>
  <div class="card-sub" style="margin-bottom:16px">Fill all fields to create a job requisition</div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title *", placeholder="e.g. ML Engineer Intern")
    with col2:
        domain = st.selectbox("Domain *", options=DOMAINS)

    col3, col4 = st.columns(2)
    with col3:
        salary = st.text_input("Salary Range *", placeholder="e.g. ₹5L - ₹8L per annum")
    with col4:
        working_hours = st.text_input("Working Hours *", placeholder="e.g. 9:00 AM - 6:00 PM (Mon-Fri)")

    col5, col6 = st.columns(2)
    with col5:
        location = st.text_input("Location", placeholder="e.g. Bangalore, Remote")
    with col6:
        experience = st.text_input("Experience Required", placeholder="e.g. 0-2 years, Fresher")

    description = st.text_area(
        "Job Description *",
        placeholder="Describe the role, responsibilities, and what the employee will work on...",
        height=120,
    )

    requirements = st.text_area(
        "Requirements *",
        placeholder="List required skills, qualifications, and technologies...",
        height=100,
    )

    submitted = st.form_submit_button("📋 Post Job", use_container_width=True)

if submitted:
    # Validation
    if not job_title.strip():
        st.error("Job title is required.")
    elif not salary.strip():
        st.error("Salary range is required.")
    elif not working_hours.strip():
        st.error("Working hours is required.")
    elif not description.strip():
        st.error("Job description is required.")
    elif not requirements.strip():
        st.error("Requirements are required.")
    else:
        job = {
            "id": str(uuid.uuid4())[:8],
            "title": job_title.strip(),
            "domain": domain,
            "salary": salary.strip(),
            "working_hours": working_hours.strip(),
            "location": location.strip() or "Not specified",
            "experience": experience.strip() or "Not specified",
            "description": description.strip(),
            "requirements": requirements.strip(),
            "posted_by": st.session_state.get("user_id", "unknown"),
            "posted_by_name": st.session_state.get("user_name", "Unknown"),
            "posted_at": datetime.now().isoformat(),
        }

        jobs = load_jobs()
        jobs.append(job)
        save_jobs(jobs)

        st.success(f"✅ Job **{job_title}** posted successfully! Students in **{domain}** will be notified.")
        st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# POSTED JOBS TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Posted Jobs</div>', unsafe_allow_html=True)

jobs = load_jobs()

if not jobs:
    st.markdown("""
<div class="card" style="text-align:center;padding:40px;border-style:dashed">
  <div style="font-size:2rem;margin-bottom:12px">📋</div>
  <div class="card-title">No jobs posted yet</div>
  <div style="color:var(--muted2);font-size:0.85rem;margin-top:4px">Use the form above to create your first job posting.</div>
</div>""", unsafe_allow_html=True)
else:
    # Load applications to show counts
    apps_path = os.path.join(OUTPUT_DIR, "applications.json")
    applications = []
    if os.path.exists(apps_path):
        try:
            with open(apps_path) as f:
                applications = json.load(f)
        except Exception:
            pass

    DOMAIN_CHIP = {
        "Machine Learning": "chip-teal",
        "Web Development": "chip-green",
        "Data Science": "chip-indigo",
        "Cloud / DevOps": "chip-warn",
        "Android Development": "chip-pink",
    }

    for job in reversed(jobs):
        chip_class = DOMAIN_CHIP.get(job["domain"], "chip-teal")
        app_count = sum(1 for a in applications if a.get("job_id") == job["id"])

        # Format date
        try:
            dt = datetime.fromisoformat(job["posted_at"])
            date_str = dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            date_str = job.get("posted_at", "Unknown")

        st.markdown(f"""
<div class="card" style="border-left:3px solid {'var(--accent)'}">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
    <div>
      <div style="font-weight:700;font-size:1.05rem;color:var(--text)">{job['title']}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--muted);margin-top:3px">
        ID: {job['id']} · Posted by {job.get('posted_by_name', 'HR')} · {date_str}
      </div>
    </div>
    <div style="display:flex;gap:6px;align-items:center">
      {render_chip(job['domain'], chip_class)}
      {render_chip(f"{app_count} application{'s' if app_count != 1 else ''}", "chip-indigo")}
    </div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px">
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">Salary</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job['salary']}</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">Hours</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job['working_hours']}</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">Location</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job.get('location', 'N/A')}</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">Experience</div>
      <div style="font-size:0.85rem;color:var(--text2)">{job.get('experience', 'N/A')}</div>
    </div>
  </div>
  <div style="font-size:0.82rem;color:var(--muted2);line-height:1.6">{job['description'][:200]}{'...' if len(job['description']) > 200 else ''}</div>
</div>
""", unsafe_allow_html=True)
