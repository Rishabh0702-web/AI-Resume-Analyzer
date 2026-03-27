"""
frontend/pages/4_Resume_Builder.py
"""

import sys
import os
import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frontend.styles import inject_styles, render_top_nav

st.set_page_config(page_title="ResumeIQ — Builder", page_icon="📝", layout="wide")
inject_styles()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

render_top_nav()

st.markdown("<h1 style='text-align:center;'>Resume Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:var(--text-muted);'>Dynamically construct your ATS-friendly resume by filling in the details below.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1. Personal Information")
    full_name = st.text_input("Full Name", placeholder="John Doe")
    email = st.text_input("Email Address", placeholder="john@example.com")
    phone = st.text_input("Phone Number", placeholder="+1 234 567 8900")
    linkedin = st.text_input("LinkedIn / Portfolio URL", placeholder="linkedin.com/in/johndoe")
    
    st.markdown("<br>### 2. Professional Summary", unsafe_allow_html=True)
    summary = st.text_area("Objective/Summary", placeholder="Driven software engineer with 3+ years of experience...", height=100)

with col2:
    st.markdown("### 3. Experience & Education")
    experience = st.text_area("Work Experience", placeholder="""Company Name — Job Title
Jan 2020 - Present
- Developed scalable web applications using Python and React.
- Improved database query performance by 40%.
""", height=180)

    education = st.text_area("Education", placeholder="""University Name — Degree
2016 - 2020
- Graduated with First Class Honors.
""", height=120)

    skills = st.text_input("Core Skills (comma separated)", placeholder="Python, JavaScript, Machine Learning, UI/UX")

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
generate_clicked = btn_col.button("Generate Preview", type="primary", use_container_width=True)

if generate_clicked or "resume_markdown" in st.session_state:
    st.markdown("---")
    st.markdown("<h2 style='text-align:center;'>Resume Preview</h2>", unsafe_allow_html=True)
    
    # Construct Markdown Resume
    md_content = f"""
# {full_name.upper() if full_name else 'YOUR NAME'}
**Email:** {email} | **Phone:** {phone}  
**Links:** {linkedin}  

---

### PROFESSIONAL SUMMARY
{summary}

---

### SKILLS
{skills}

---

### WORK EXPERIENCE
{experience}

---

### EDUCATION
{education}
    """
    
    st.session_state["resume_markdown"] = md_content
    
    # Show preview inside a container
    preview_container = st.container()
    with preview_container:
        st.markdown(f"<div style='background:var(--surface2); border:1px solid var(--border); padding:40px; border-radius:12px; margin-top:20px; color:var(--text);'>\n{md_content}\n</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download Button
    st.download_button(
        label="📄 Download as Markdown (.md)",
        data=md_content,
        file_name=f"{full_name.replace(' ', '_') if full_name else 'resume'}.md",
        mime="text/markdown",
        use_container_width=True
    )
