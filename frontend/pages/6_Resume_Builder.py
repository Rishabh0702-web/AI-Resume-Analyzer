"""
frontend/pages/6_Resume_Builder.py
Resume Builder for Student section with 3 sub-tabs:
  ✏️ Build Resume  — 7-step form wizard
  👁 Preview       — Classic / Modern / Minimal templates
  🌐 Portfolio     — Personal portfolio-style view
"""

import streamlit as st
import os, sys, json, copy

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frontend.styles import inject_styles, render_top_nav

st.set_page_config(page_title="ResumeIQ — Resume Builder", page_icon="📝", layout="wide")
inject_styles()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("role") != "student":
    st.switch_page("app.py")

render_top_nav()

# ══════════════════════════════════════════════════════════════════════════════
# DATA DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_DATA = {
    "personal": {"fullName":"","title":"","email":"","phone":"","location":"","website":"","linkedin":"","github":"","summary":""},
    "education": [{"institution":"","degree":"","field":"","startDate":"","endDate":"","gpa":"","description":""}],
    "skills": [{"category":"Technical Skills","items":""},{"category":"Soft Skills","items":""}],
    "projects": [{"name":"","description":"","technologies":"","link":"","highlights":""}],
    "experience": [{"company":"","position":"","startDate":"","endDate":"","current":False,"description":"","highlights":""}],
    "certifications": [{"name":"","issuer":"","date":"","link":""}],
    "achievements": [{"title":"","description":"","date":""}],
}

SAMPLE_DATA = {
    "personal": {"fullName":"Rishabh Gupta","title":"Full Stack Developer","email":"rishabh09454@gmail.com","phone":"+91 7905028145","location":"Ghaziabad, UP","website":"","linkedin":"linkedin.com/in/rishabh","github":"github.com/Rishabh0702-web","summary":"B.Tech CSE student at ABES Engineering College with expertise in full-stack development, ML fine-tuning, and UI/UX design. Built multiple production-grade projects."},
    "education": [{"institution":"ABES Engineering College","degree":"B.Tech","field":"Computer Science","startDate":"2024","endDate":"2028","gpa":"8.5","description":"Relevant coursework: DSA, Machine Learning, Web Dev"}],
    "skills": [{"category":"Languages & Frameworks","items":"Python, JavaScript, TypeScript, React, Next.js, Node.js, Tailwind CSS"},{"category":"Tools & Platforms","items":"GitHub, VS Code, Figma, MongoDB, Firebase, Docker"}],
    "projects": [{"name":"E-Learning Platform (SIH)","description":"Full-stack gamified learning platform with 3D UI for rural accessibility.","technologies":"Next.js, React, MongoDB, Firebase, Three.js","link":"","highlights":"Low-bandwidth optimization, offline support"},{"name":"LLM Fine-Tuning (IIITD)","description":"Fine-tuned 7B LLM on MedQuAD dataset using LoRA with 4-bit quantization.","technologies":"Python, PyTorch, HuggingFace, PEFT","link":"","highlights":"Top 5 at HackLLM Hackathon IIITD"}],
    "experience": [{"company":"CodeChef ABES","position":"Graphic Designer / UI-UX Designer","startDate":"2024","endDate":"","current":True,"description":"Designed posters, banners, and UI screens for technical events.","highlights":"Figma prototypes, Brand identity"}],
    "certifications": [{"name":"AWS Solutions Architect","issuer":"Amazon Web Services","date":"2024","link":""}],
    "achievements": [{"title":"HackLLM IIITD — Top 5","description":"Fine-tuned medical LLM at IIIT Delhi hackathon","date":"2024"},{"title":"Startup Pitching — Top 3","description":"E-Cell ABESEC startup ideation challenge","date":"2024"}],
}

SECTION_TEMPLATES = {
    "education":{"institution":"","degree":"","field":"","startDate":"","endDate":"","gpa":"","description":""},
    "skills":{"category":"","items":""},
    "projects":{"name":"","description":"","technologies":"","link":"","highlights":""},
    "experience":{"company":"","position":"","startDate":"","endDate":"","current":False,"description":"","highlights":""},
    "certifications":{"name":"","issuer":"","date":"","link":""},
    "achievements":{"title":"","description":"","date":""},
}

STEPS = [
    {"label":"Personal","icon":"👤","desc":"Your name, contact, and professional summary."},
    {"label":"Education","icon":"🎓","desc":"Your educational background and academic details."},
    {"label":"Skills","icon":"⚡","desc":"Technical and soft skills grouped by category."},
    {"label":"Projects","icon":"🚀","desc":"Projects you built — include links and highlights."},
    {"label":"Experience","icon":"💼","desc":"Work experience, internships, and roles."},
    {"label":"Certifications","icon":"📜","desc":"Certifications and licenses you hold."},
    {"label":"Achievements","icon":"🏆","desc":"Awards, competitions, and accomplishments."},
]

if "resume_data" not in st.session_state:
    st.session_state.resume_data = copy.deepcopy(DEFAULT_DATA)
if "builder_step" not in st.session_state:
    st.session_state.builder_step = 0
if "selected_template" not in st.session_state:
    st.session_state.selected_template = "classic"

rd = st.session_state.resume_data

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CSS — everything in one block for our dark UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
/* stepper */
.builder-stepper{display:flex;gap:4px;margin-bottom:20px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:8px 12px;overflow-x:auto}
.step-pill{display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;font-size:.78rem;font-weight:500;white-space:nowrap;color:var(--muted);border:1px solid transparent}
.step-pill.active{background:var(--accent-muted);color:var(--accent);border-color:rgba(79,143,247,.2);font-weight:600}
.step-pill.done{color:var(--ok)}
.step-num{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;font-size:.65rem;font-family:'JetBrains Mono',monospace;font-weight:600;background:var(--surface3);color:var(--muted)}
.step-pill.active .step-num{background:var(--accent);color:#fff}
.step-pill.done .step-num{background:var(--ok-muted);color:var(--ok)}
/* resume sheet */
.resume-sheet{background:#fff;color:#1a1a2e;padding:40px 50px;border-radius:var(--r);box-shadow:var(--shadow-lg);font-family:'Inter',sans-serif;max-width:800px;margin:0 auto;line-height:1.5}
/* classic */
.ct-header{text-align:center;border-bottom:2px solid #2d3748;padding-bottom:16px;margin-bottom:20px}
.ct-name{font-size:1.8rem;font-weight:800;color:#1a1a2e;margin:0;letter-spacing:-.02em}
.ct-title{font-size:.95rem;color:#4a5568;margin:4px 0 10px}
.ct-contact{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;font-size:.78rem;color:#4a5568}
.ct-contact span::before{content:'·';margin-right:12px;color:#cbd5e0}.ct-contact span:first-child::before{content:'';margin-right:0}
.ct-section{margin-bottom:18px}.ct-sh{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#2d3748;border-bottom:1px solid #e2e8f0;padding-bottom:4px;margin-bottom:10px}
.ct-item{margin-bottom:12px}.ct-item-head{display:flex;justify-content:space-between;align-items:flex-start}
.ct-item-title{font-weight:600;color:#1a1a2e;font-size:.88rem}.ct-item-sub{color:#4a5568;font-size:.82rem}
.ct-item-date{font-size:.75rem;color:#718096;white-space:nowrap}.ct-text{font-size:.82rem;color:#4a5568;margin-top:4px;line-height:1.6}
.ct-list{margin:4px 0 0 18px;font-size:.82rem;color:#4a5568}.ct-list li{margin-bottom:2px}.ct-tech{font-size:.75rem;color:#667eea;margin-top:2px}
/* modern */
.mod-wrap{display:grid;grid-template-columns:240px 1fr;min-height:600px}
.mod-sidebar{background:#1a1a2e;color:#e2e8f0;padding:30px 24px;border-radius:10px 0 0 10px}
.mod-main{padding:30px 28px}
.mod-avatar{width:60px;height:60px;border-radius:50%;background:#4f8ff7;color:#fff;display:flex;align-items:center;justify-content:center;font-size:1.3rem;font-weight:800;margin-bottom:14px}
.mod-name{font-size:1.2rem;font-weight:800;color:#fff;margin-bottom:2px}
.mod-role{font-size:.8rem;color:#a0aec0;margin-bottom:18px}
.mod-sh{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#a0aec0;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,.1);padding-bottom:4px}
.mod-contact-item{font-size:.75rem;color:#cbd5e0;margin-bottom:4px;word-break:break-all}
.mod-skill-cat{font-size:.7rem;color:#a0aec0;font-weight:600;margin-bottom:4px;margin-top:10px}
.mod-skill-tags{display:flex;flex-wrap:wrap;gap:4px}
.mod-skill-tag{background:rgba(79,143,247,.2);color:#90cdf4;padding:2px 8px;border-radius:4px;font-size:.65rem}
.mod-main-sh{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#2d3748;border-bottom:1px solid #e2e8f0;padding-bottom:4px;margin-bottom:10px;margin-top:18px}
.mod-item{margin-bottom:12px;padding-left:14px;border-left:2px solid #e2e8f0}
.mod-item-head{display:flex;justify-content:space-between;align-items:flex-start}
.mod-item-title{font-weight:600;font-size:.86rem;color:#1a1a2e}.mod-item-sub{font-size:.78rem;color:#4a5568}
.mod-item-date{font-size:.72rem;color:#718096}.mod-text{font-size:.8rem;color:#4a5568;margin-top:3px;line-height:1.55}
.mod-list{margin:4px 0 0 16px;font-size:.8rem;color:#4a5568}.mod-list li{margin-bottom:2px}
.mod-tech{font-size:.72rem;color:#667eea;margin-top:2px}
.mod-cert-name{font-size:.78rem;color:#cbd5e0;font-weight:500}.mod-cert-issuer{font-size:.68rem;color:#718096}
/* minimal */
.min-header{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #1a1a2e;padding-bottom:14px;margin-bottom:20px}
.min-name{font-size:1.6rem;font-weight:800;color:#1a1a2e;letter-spacing:-.02em}.min-role{font-size:.88rem;color:#4a5568}
.min-contact{text-align:right;font-size:.75rem;color:#4a5568;line-height:1.7}
.min-summary{font-size:.82rem;color:#4a5568;line-height:1.65;margin-bottom:18px;font-style:italic;border-left:3px solid #e2e8f0;padding-left:14px}
.min-sh{font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#1a1a2e;margin-bottom:10px;margin-top:18px}
.min-entry{display:grid;grid-template-columns:130px 1fr;gap:16px;margin-bottom:12px}
.min-date{font-size:.72rem;color:#718096;padding-top:2px}.min-entry-title{font-weight:600;font-size:.86rem;color:#1a1a2e}
.min-entry-sub{font-size:.78rem;color:#4a5568}.min-text{font-size:.8rem;color:#4a5568;margin-top:3px;line-height:1.55}
.min-list{margin:4px 0 0 16px;font-size:.8rem;color:#4a5568}.min-list li{margin-bottom:2px}
.min-skills-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.min-skill-cat{font-weight:600;font-size:.78rem;color:#2d3748}
/* portfolio */
.pf-hero{background:linear-gradient(135deg,#0f1117 0%,#1c2333 50%,#161b26 100%);border:1px solid var(--border);border-radius:var(--r-lg);padding:50px 40px;text-align:center;margin-bottom:24px}
.pf-greeting{font-size:.9rem;color:var(--accent);font-weight:500;margin-bottom:6px}
.pf-name{font-size:2.2rem;font-weight:800;color:var(--text);letter-spacing:-.03em;margin-bottom:4px}
.pf-role{font-size:1rem;color:var(--muted2);margin-bottom:14px}
.pf-bio{font-size:.88rem;color:var(--muted2);line-height:1.7;max-width:600px;margin:0 auto 20px}
.pf-links{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.pf-link-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;border-radius:8px;font-size:.8rem;font-weight:600;text-decoration:none;transition:all .2s}
.pf-link-primary{background:var(--accent);color:#fff}.pf-link-secondary{background:var(--surface2);color:var(--text);border:1px solid var(--border)}
.pf-section-title{font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border)}
.pf-skill-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:18px}
.pf-skill-cat{font-weight:700;font-size:.82rem;color:var(--text);margin-bottom:8px}
.pf-skill-tag{display:inline-block;background:var(--accent-muted);color:var(--accent);padding:3px 10px;border-radius:6px;font-size:.72rem;margin:2px 4px 2px 0}
.pf-project-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:20px;transition:border-color .2s}
.pf-project-card:hover{border-color:var(--accent)}
.pf-project-name{font-weight:700;font-size:.95rem;color:var(--text);margin-bottom:4px}
.pf-project-desc{font-size:.82rem;color:var(--muted2);line-height:1.6;margin-bottom:8px}
.pf-project-tech-tag{display:inline-block;background:var(--surface3);color:var(--muted2);padding:2px 8px;border-radius:4px;font-size:.65rem;margin:2px 4px 2px 0}
.pf-project-hl{font-size:.75rem;color:var(--ok);margin-top:8px}
.pf-timeline-item{display:flex;gap:16px;margin-bottom:18px}
.pf-timeline-dot{width:10px;height:10px;border-radius:50%;background:var(--accent);margin-top:6px;flex-shrink:0}
.pf-timeline-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:16px;flex:1}
.pf-timeline-pos{font-weight:700;font-size:.88rem;color:var(--text)}.pf-timeline-co{font-size:.8rem;color:var(--muted2)}
.pf-timeline-date{font-size:.72rem;color:var(--muted);font-family:'JetBrains Mono',monospace}
.pf-timeline-desc{font-size:.82rem;color:var(--muted2);margin-top:6px;line-height:1.6}
.pf-edu-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:18px}
.pf-edu-deg{font-weight:700;font-size:.88rem;color:var(--text)}.pf-edu-school{font-size:.82rem;color:var(--muted2)}
.pf-edu-date{font-size:.72rem;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:4px}
.pf-ach-item{display:flex;align-items:flex-start;gap:12px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:14px 18px;margin-bottom:10px}
.pf-ach-icon{font-size:1.2rem;margin-top:2px}.pf-ach-title{font-weight:700;font-size:.85rem;color:var(--text)}
.pf-ach-desc{font-size:.78rem;color:var(--muted2);margin-top:2px}
.pf-ach-date{font-size:.68rem;color:var(--muted);margin-left:auto;white-space:nowrap}
.pf-contact-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:24px;text-align:center}
.pf-contact-intro{font-size:.88rem;color:var(--muted2);margin-bottom:16px}
.pf-contact-link{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:8px;background:var(--surface3);color:var(--text2);font-size:.78rem;margin:4px;text-decoration:none}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO + SUB-TABS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hero">
  <div class="hero-badge">📝 Resume Builder</div>
  <h1>Build · Preview · Showcase</h1>
  <p>Create your professional resume, preview it in different templates, and generate a portfolio page.</p>
</div>
""", unsafe_allow_html=True)

tab_build, tab_preview, tab_portfolio = st.tabs(["✏️ Build Resume", "👁 Preview", "🌐 Portfolio"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: BUILD RESUME
# ══════════════════════════════════════════════════════════════════════════════
with tab_build:
    # Quick actions row
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        if st.button("📋 Load Sample Data", use_container_width=True, key="load_sample"):
            st.session_state.resume_data = copy.deepcopy(SAMPLE_DATA)
            st.rerun()
    with ac2:
        if st.button("🗑️ Clear All Fields", use_container_width=True, key="clear_all"):
            st.session_state.resume_data = copy.deepcopy(DEFAULT_DATA)
            st.session_state.builder_step = 0
            st.rerun()
    with ac3:
        # Completion score
        p = rd["personal"]
        score = 0
        if p["fullName"]: score += 15
        if p["email"]: score += 10
        if p["summary"]: score += 15
        if any(e["institution"] for e in rd["education"]): score += 15
        if any(s["items"] for s in rd["skills"]): score += 15
        if any(pr["name"] for pr in rd["projects"]): score += 15
        if any(e["company"] for e in rd["experience"]): score += 15
        score = min(score, 100)
        st.markdown(f"""
<div class="stat-card">
  <div class="stat-card-label">Completion</div>
  <div class="stat-card-value" style="color:{'var(--ok)' if score >= 70 else 'var(--warn)' if score >= 40 else 'var(--muted)'}">{score}%</div>
</div>""", unsafe_allow_html=True)

    step = st.session_state.builder_step

    # Stepper
    pills = ""
    for i, s in enumerate(STEPS):
        cls = "active" if i == step else ("done" if i < step else "")
        num = "✓" if i < step else str(i + 1)
        pills += f'<div class="step-pill {cls}"><span class="step-num">{num}</span>{s["label"]}</div>'
    st.markdown(f'<div class="builder-stepper">{pills}</div>', unsafe_allow_html=True)

    # Step header
    st.markdown(f"""<div class="card" style="padding:16px 20px;margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:12px">
    <span style="font-size:1.5rem">{STEPS[step]["icon"]}</span>
    <div><div class="card-title" style="margin-bottom:2px">{STEPS[step]["label"]}</div>
    <div class="card-sub">{STEPS[step]["desc"]}</div></div>
  </div></div>""", unsafe_allow_html=True)

    # ── Step 0: Personal ──
    if step == 0:
        p = rd["personal"]
        c1, c2 = st.columns(2)
        with c1: p["fullName"] = st.text_input("Full Name *", value=p["fullName"], placeholder="e.g. Rishabh Gupta", key="p_name")
        with c2: p["title"] = st.text_input("Professional Title", value=p["title"], placeholder="e.g. Full Stack Developer", key="p_title")
        c3, c4 = st.columns(2)
        with c3: p["email"] = st.text_input("Email *", value=p["email"], placeholder="e.g. you@email.com", key="p_email")
        with c4: p["phone"] = st.text_input("Phone", value=p["phone"], placeholder="e.g. +91 9876543210", key="p_phone")
        c5, c6 = st.columns(2)
        with c5: p["location"] = st.text_input("Location", value=p["location"], placeholder="e.g. Bangalore", key="p_loc")
        with c6: p["website"] = st.text_input("Website", value=p["website"], placeholder="e.g. https://yoursite.com", key="p_web")
        c7, c8 = st.columns(2)
        with c7: p["linkedin"] = st.text_input("LinkedIn", value=p["linkedin"], placeholder="e.g. linkedin.com/in/you", key="p_li")
        with c8: p["github"] = st.text_input("GitHub", value=p["github"], placeholder="e.g. github.com/you", key="p_gh")
        p["summary"] = st.text_area("Professional Summary *", value=p["summary"], placeholder="Briefly describe who you are, your key strengths, and what you're looking for.", height=120, key="p_sum")

    # ── Steps 1-6: List sections ──
    else:
        FIELD_MAP = {
            1: ("education", [("institution","Institution","e.g. ABES Engineering College"),("degree","Degree","e.g. B.Tech"),("field","Field","e.g. Computer Science"),("startDate","Start Year","e.g. 2024"),("endDate","End Year","e.g. 2028"),("gpa","GPA / CGPA","e.g. 8.5"),("description","Description","Honors, clubs, coursework","textarea")]),
            2: ("skills", [("category","Category","e.g. Programming Languages"),("items","Skills (comma separated)","e.g. Python, React, Node.js","textarea")]),
            3: ("projects", [("name","Project Name","e.g. E-Learning Platform"),("description","Description","What it does and why","textarea"),("technologies","Tech Stack","e.g. React, Node.js, MongoDB"),("link","Project Link","e.g. https://github.com/..."),("highlights","Key Highlights","e.g. 10K users, Top 5","textarea")]),
            4: ("experience", [("company","Company / Organisation","e.g. Google"),("position","Role / Position","e.g. Software Intern"),("startDate","Start Date","e.g. Jan 2024"),("endDate","End Date","e.g. May 2024"),("description","Description","What did you do?","textarea"),("highlights","Key Achievements","e.g. Built feature X","textarea")]),
            5: ("certifications", [("name","Certification Name","e.g. AWS Solutions Architect"),("issuer","Issuing Body","e.g. Amazon Web Services"),("date","Date","e.g. 2024"),("link","Credential Link","e.g. https://...")]),
            6: ("achievements", [("title","Achievement","e.g. Hackathon Winner"),("description","Description","Briefly describe","textarea"),("date","Date","e.g. 2024")]),
        }
        section, fields = FIELD_MAP[step]
        items = rd[section]

        for idx, item in enumerate(items):
            with st.container():
                hc1, hc2 = st.columns([8, 1])
                with hc1:
                    st.markdown(f"<div style='font-family:\"JetBrains Mono\",monospace;font-size:.72rem;font-weight:600;color:var(--accent);background:var(--accent-muted);display:inline-block;padding:2px 10px;border-radius:6px;margin-bottom:8px'>#{idx+1}</div>", unsafe_allow_html=True)
                with hc2:
                    if len(items) > 1:
                        if st.button("🗑️", key=f"rm_{section}_{idx}"):
                            rd[section].pop(idx)
                            st.rerun()

                for fd in fields:
                    k, label, placeholder = fd[0], fd[1], fd[2]
                    ftype = fd[3] if len(fd) > 3 else "text"
                    wk = f"{section}_{idx}_{k}"
                    if ftype == "textarea":
                        item[k] = st.text_area(label, value=item.get(k, ""), placeholder=placeholder, key=wk, height=80)
                    else:
                        item[k] = st.text_input(label, value=item.get(k, ""), placeholder=placeholder, key=wk)

                if section == "experience":
                    item["current"] = st.checkbox("I currently work here", value=item.get("current", False), key=f"exp_{idx}_cur")

                st.markdown("---")

        if st.button(f"+ Add Another", use_container_width=True, key=f"add_{section}"):
            rd[section].append(copy.deepcopy(SECTION_TEMPLATES[section]))
            st.rerun()

    # Navigation
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("← Back", disabled=(step == 0), use_container_width=True, key="nav_back"):
            st.session_state.builder_step = step - 1
            st.rerun()
    with n2:
        st.markdown(f"<div style='text-align:center;padding-top:8px;font-family:\"JetBrains Mono\",monospace;font-size:.7rem;color:var(--muted)'>Step {step+1} of {len(STEPS)}</div>", unsafe_allow_html=True)
    with n3:
        label = "Preview Resume →" if step == 6 else "Next →"
        if st.button(label, use_container_width=True, key="nav_next"):
            if step < 6:
                st.session_state.builder_step = step + 1
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: PREVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_preview:
    p = rd["personal"]
    edu = rd["education"]
    skl = rd["skills"]
    proj = rd["projects"]
    exp = rd["experience"]
    certs = rd["certifications"]
    ach = rd["achievements"]

    def has(lst, key):
        return any(item.get(key, "").strip() for item in lst)

    def hl_html(text, cls="ct-list"):
        if not text: return ""
        return f'<ul class="{cls}">{"".join(f"<li>{h.strip()}</li>" for h in text.split(",") if h.strip())}</ul>'

    # Template picker
    st.markdown('<div class="section-label">Choose Template</div>', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    for col, (tid, tname, tdesc) in zip([tc1, tc2, tc3], [("classic","Classic","Traditional & Formal"),("modern","Modern","Two-Column & Bold"),("minimal","Minimal","Clean & Elegant")]):
        with col:
            active = st.session_state.selected_template == tid
            icon = "✅ " if active else ""
            if st.button(f"{icon}{tname}\n{tdesc}", key=f"tpl_{tid}", use_container_width=True):
                st.session_state.selected_template = tid
                st.rerun()

    st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)
    tpl = st.session_state.selected_template
    contact_parts = [p["email"], p["phone"], p["location"], p["website"], p["linkedin"], p["github"]]

    # ── CLASSIC ──
    if tpl == "classic":
        contact_html = " ".join(f"<span>{c}</span>" for c in contact_parts if c)
        html = f'<div class="ct-header"><h1 class="ct-name">{p["fullName"] or "Your Name"}</h1>'
        if p["title"]: html += f'<p class="ct-title">{p["title"]}</p>'
        html += f'<div class="ct-contact">{contact_html}</div></div>'
        if p["summary"]: html += f'<div class="ct-section"><h2 class="ct-sh">Professional Summary</h2><p class="ct-text">{p["summary"]}</p></div>'
        if has(exp,"company"):
            html += '<div class="ct-section"><h2 class="ct-sh">Work Experience</h2>'
            for e in exp:
                if not e.get("company"): continue
                end = "Present" if e.get("current") else e.get("endDate","")
                html += f'<div class="ct-item"><div class="ct-item-head"><div><strong class="ct-item-title">{e["position"]}</strong><p class="ct-item-sub">{e["company"]}</p></div><span class="ct-item-date">{e.get("startDate","")} — {end}</span></div>'
                if e.get("description"): html += f'<p class="ct-text">{e["description"]}</p>'
                html += hl_html(e.get("highlights","")) + '</div>'
            html += '</div>'
        if has(edu,"institution"):
            html += '<div class="ct-section"><h2 class="ct-sh">Education</h2>'
            for e in edu:
                if not e.get("institution"): continue
                deg = e["degree"] + (f' in {e["field"]}' if e.get("field") else "")
                gpa = f' | GPA: {e["gpa"]}' if e.get("gpa") else ""
                html += f'<div class="ct-item"><div class="ct-item-head"><div><strong class="ct-item-title">{deg}</strong><p class="ct-item-sub">{e["institution"]}</p></div><span class="ct-item-date">{e.get("startDate","")} — {e.get("endDate","")}{gpa}</span></div></div>'
            html += '</div>'
        if has(skl,"items"):
            html += '<div class="ct-section"><h2 class="ct-sh">Skills</h2>'
            for s in skl:
                if s.get("items"): html += f'<p class="ct-text"><strong>{s["category"]}:</strong> {s["items"]}</p>'
            html += '</div>'
        if has(proj,"name"):
            html += '<div class="ct-section"><h2 class="ct-sh">Projects</h2>'
            for pr in proj:
                if not pr.get("name"): continue
                html += f'<div class="ct-item"><strong class="ct-item-title">{pr["name"]}</strong>'
                if pr.get("technologies"): html += f'<p class="ct-tech">{pr["technologies"]}</p>'
                if pr.get("description"): html += f'<p class="ct-text">{pr["description"]}</p>'
                html += hl_html(pr.get("highlights","")) + '</div>'
            html += '</div>'
        if has(certs,"name"):
            html += '<div class="ct-section"><h2 class="ct-sh">Certifications</h2>'
            for c in certs:
                if c.get("name"): html += f'<p class="ct-text"><strong>{c["name"]}</strong> — {c.get("issuer","")} ({c.get("date","")})</p>'
            html += '</div>'
        if has(ach,"title"):
            html += '<div class="ct-section"><h2 class="ct-sh">Achievements</h2>'
            for a in ach:
                if a.get("title"):
                    desc = f' — {a["description"]}' if a.get("description") else ""
                    date = f' ({a["date"]})' if a.get("date") else ""
                    html += f'<p class="ct-text"><strong>{a["title"]}</strong>{desc}{date}</p>'
            html += '</div>'
        st.markdown(f'<div class="resume-sheet">{html}</div>', unsafe_allow_html=True)

    # ── MODERN ──
    elif tpl == "modern":
        initials = "".join(w[0] for w in (p["fullName"] or "YN").split()[:2]).upper()
        sb = f'<div class="mod-avatar">{initials}</div><div class="mod-name">{p["fullName"] or "Your Name"}</div><p class="mod-role">{p["title"] or "Professional Title"}</p><h3 class="mod-sh">Contact</h3>'
        for f in ["email","phone","location","website","linkedin","github"]:
            if p.get(f): sb += f'<p class="mod-contact-item">{p[f]}</p>'
        if has(skl,"items"):
            sb += '<h3 class="mod-sh" style="margin-top:18px">Skills</h3>'
            for s in skl:
                if s.get("items"):
                    tags = "".join(f'<span class="mod-skill-tag">{t.strip()}</span>' for t in s["items"].split(",") if t.strip())
                    sb += f'<p class="mod-skill-cat">{s["category"]}</p><div class="mod-skill-tags">{tags}</div>'
        if has(certs,"name"):
            sb += '<h3 class="mod-sh" style="margin-top:18px">Certifications</h3>'
            for c in certs:
                if c.get("name"): sb += f'<p class="mod-cert-name">{c["name"]}</p><p class="mod-cert-issuer">{c.get("issuer","")} · {c.get("date","")}</p>'
        mn = ""
        if p["summary"]: mn += f'<h2 class="mod-main-sh">About Me</h2><p class="mod-text">{p["summary"]}</p>'
        if has(exp,"company"):
            mn += '<h2 class="mod-main-sh">Experience</h2>'
            for e in exp:
                if not e.get("company"): continue
                end = "Present" if e.get("current") else e.get("endDate","")
                mn += f'<div class="mod-item"><div class="mod-item-head"><strong class="mod-item-title">{e["position"]}</strong><span class="mod-item-date">{e.get("startDate","")} — {end}</span></div><p class="mod-item-sub">{e["company"]}</p>'
                if e.get("description"): mn += f'<p class="mod-text">{e["description"]}</p>'
                mn += hl_html(e.get("highlights",""),"mod-list") + '</div>'
        if has(edu,"institution"):
            mn += '<h2 class="mod-main-sh">Education</h2>'
            for e in edu:
                if not e.get("institution"): continue
                deg = e["degree"] + (f' in {e["field"]}' if e.get("field") else "")
                gpa = f' · GPA: {e["gpa"]}' if e.get("gpa") else ""
                mn += f'<div class="mod-item"><div class="mod-item-head"><strong class="mod-item-title">{deg}</strong><span class="mod-item-date">{e.get("startDate","")} — {e.get("endDate","")}</span></div><p class="mod-item-sub">{e["institution"]}{gpa}</p></div>'
        if has(proj,"name"):
            mn += '<h2 class="mod-main-sh">Projects</h2>'
            for pr in proj:
                if not pr.get("name"): continue
                mn += f'<div class="mod-item"><strong class="mod-item-title">{pr["name"]}</strong>'
                if pr.get("technologies"): mn += f'<p class="mod-tech">{pr["technologies"]}</p>'
                if pr.get("description"): mn += f'<p class="mod-text">{pr["description"]}</p>'
                mn += hl_html(pr.get("highlights",""),"mod-list") + '</div>'
        if has(ach,"title"):
            mn += '<h2 class="mod-main-sh">Achievements</h2>'
            for a in ach:
                if a.get("title"):
                    mn += f'<div class="mod-item"><strong class="mod-item-title">{a["title"]}</strong>'
                    if a.get("description"): mn += f'<p class="mod-text">{a["description"]}</p>'
                    mn += '</div>'
        st.markdown(f'<div class="resume-sheet" style="padding:0;overflow:hidden"><div class="mod-wrap"><div class="mod-sidebar">{sb}</div><div class="mod-main">{mn}</div></div></div>', unsafe_allow_html=True)

    # ── MINIMAL ──
    elif tpl == "minimal":
        cl = ""
        for f in ["email","phone","location","linkedin","github"]:
            if p.get(f): cl += f"<p>{p[f]}</p>"
        sec = ""
        if p["summary"]: sec += f'<p class="min-summary">{p["summary"]}</p>'
        if has(exp,"company"):
            sec += '<h2 class="min-sh">Experience</h2>'
            for e in exp:
                if not e.get("company"): continue
                end = "Present" if e.get("current") else e.get("endDate","")
                sec += f'<div class="min-entry"><div class="min-date">{e.get("startDate","")} — {end}</div><div><strong class="min-entry-title">{e["position"]}</strong><p class="min-entry-sub">{e["company"]}</p>'
                if e.get("description"): sec += f'<p class="min-text">{e["description"]}</p>'
                sec += hl_html(e.get("highlights",""),"min-list") + '</div></div>'
        if has(edu,"institution"):
            sec += '<h2 class="min-sh">Education</h2>'
            for e in edu:
                if not e.get("institution"): continue
                deg = e["degree"] + (f' in {e["field"]}' if e.get("field") else "")
                gpa = f' — GPA: {e["gpa"]}' if e.get("gpa") else ""
                sec += f'<div class="min-entry"><div class="min-date">{e.get("startDate","")} — {e.get("endDate","")}</div><div><strong class="min-entry-title">{deg}</strong><p class="min-entry-sub">{e["institution"]}{gpa}</p></div></div>'
        if has(skl,"items"):
            sec += '<h2 class="min-sh">Skills</h2><div class="min-skills-grid">'
            for s in skl:
                if s.get("items"): sec += f'<div><p class="min-skill-cat">{s["category"]}</p><p class="min-text">{s["items"]}</p></div>'
            sec += '</div>'
        if has(proj,"name"):
            sec += '<h2 class="min-sh">Projects</h2>'
            for pr in proj:
                if not pr.get("name"): continue
                sec += f'<div class="min-entry"><div class="min-date">{pr.get("technologies","")}</div><div><strong class="min-entry-title">{pr["name"]}</strong>'
                if pr.get("description"): sec += f'<p class="min-text">{pr["description"]}</p>'
                sec += hl_html(pr.get("highlights",""),"min-list") + '</div></div>'
        st.markdown(f'<div class="resume-sheet"><div class="min-header"><div><h1 class="min-name">{p["fullName"] or "Your Name"}</h1><p class="min-role">{p["title"] or "Professional Title"}</p></div><div class="min-contact">{cl}</div></div>{sec}</div>', unsafe_allow_html=True)

    # Download
    st.markdown("")
    dl_html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>Resume - {p.get("fullName","Resume")}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Inter',sans-serif;background:#f7f8fa;padding:20px}}
.resume-sheet{{background:#fff;color:#1a1a2e;padding:40px 50px;max-width:800px;margin:0 auto;line-height:1.5;box-shadow:0 2px 20px rgba(0,0,0,.08)}}
.ct-header{{text-align:center;border-bottom:2px solid #2d3748;padding-bottom:16px;margin-bottom:20px}}.ct-name{{font-size:1.8rem;font-weight:800;letter-spacing:-.02em}}
.ct-title{{font-size:.95rem;color:#4a5568;margin:4px 0 10px}}.ct-contact{{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;font-size:.78rem;color:#4a5568}}
.ct-section{{margin-bottom:18px}}.ct-sh{{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#2d3748;border-bottom:1px solid #e2e8f0;padding-bottom:4px;margin-bottom:10px}}
.ct-item{{margin-bottom:12px}}.ct-item-head{{display:flex;justify-content:space-between}}.ct-item-title{{font-weight:600;font-size:.88rem}}.ct-item-sub{{color:#4a5568;font-size:.82rem}}
.ct-item-date{{font-size:.75rem;color:#718096}}.ct-text{{font-size:.82rem;color:#4a5568;margin-top:4px;line-height:1.6}}.ct-list{{margin:4px 0 0 18px;font-size:.82rem;color:#4a5568}}.ct-tech{{font-size:.75rem;color:#667eea;margin-top:2px}}
@media print{{body{{padding:0;background:#fff}}.resume-sheet{{box-shadow:none;padding:30px 40px}}}}</style></head><body><div class="resume-sheet">'''
    # reuse classic html for download
    contact_dl = " ".join(f"<span>{c}</span>" for c in contact_parts if c)
    dl_html += f'<div class="ct-header"><h1 class="ct-name">{p["fullName"] or "Your Name"}</h1>'
    if p["title"]: dl_html += f'<p class="ct-title">{p["title"]}</p>'
    dl_html += f'<div class="ct-contact">{contact_dl}</div></div>'
    if p["summary"]: dl_html += f'<div class="ct-section"><h2 class="ct-sh">Professional Summary</h2><p class="ct-text">{p["summary"]}</p></div>'
    dl_html += '</div></body></html>'

    fname = f"{p.get('fullName','resume').replace(' ','_')}_Resume.html"
    st.download_button("⬇ Download Resume as HTML", data=dl_html, file_name=fname, mime="text/html", use_container_width=True, key="dl_resume")
    st.markdown("""<div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:12px 18px;margin-top:10px">
  <div style="font-size:.82rem;color:var(--muted2)">💡 <strong style="color:var(--text)">Tip:</strong> Open the HTML file in your browser, then press <strong>Ctrl+P</strong> and select <strong>"Save as PDF"</strong>.</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
with tab_portfolio:
    p = rd["personal"]
    edu = rd["education"]
    skl = rd["skills"]
    proj = rd["projects"]
    exp = rd["experience"]
    certs = rd["certifications"]
    ach = rd["achievements"]

    def has(lst, key):
        return any(item.get(key, "").strip() for item in lst)

    # Hero
    links_html = ""
    if p["email"]: links_html += f'<a class="pf-link-btn pf-link-primary" href="mailto:{p["email"]}">✉ Contact Me</a>'
    if p["github"]:
        gh = p["github"] if p["github"].startswith("http") else f'https://{p["github"]}'
        links_html += f'<a class="pf-link-btn pf-link-secondary" href="{gh}" target="_blank">GitHub ↗</a>'
    if p["linkedin"]:
        li = p["linkedin"] if p["linkedin"].startswith("http") else f'https://{p["linkedin"]}'
        links_html += f'<a class="pf-link-btn pf-link-secondary" href="{li}" target="_blank">LinkedIn ↗</a>'

    st.markdown(f"""
<div class="pf-hero">
  <p class="pf-greeting">Hello, I'm</p>
  <h1 class="pf-name">{p["fullName"] or "Your Name"}</h1>
  <p class="pf-role">{p["title"] or "Professional Title"}</p>
  <p class="pf-bio">{p["summary"] or "Your professional summary will appear here. Fill in the Build tab to get started."}</p>
  <div class="pf-links">{links_html}</div>
</div>
""", unsafe_allow_html=True)

    # Skills
    if has(skl, "items"):
        st.markdown('<div class="pf-section-title">Skills & Expertise</div>', unsafe_allow_html=True)
        skill_cols = st.columns(min(len([s for s in skl if s.get("items")]), 3))
        for i, s in enumerate([s for s in skl if s.get("items")]):
            with skill_cols[i % len(skill_cols)]:
                tags = "".join(f'<span class="pf-skill-tag">{t.strip()}</span>' for t in s["items"].split(",") if t.strip())
                st.markdown(f'<div class="pf-skill-card"><div class="pf-skill-cat">{s["category"]}</div>{tags}</div>', unsafe_allow_html=True)

    # Projects
    if has(proj, "name"):
        st.markdown('<div class="pf-section-title">Featured Projects</div>', unsafe_allow_html=True)
        pcols = st.columns(2)
        for i, pr in enumerate([pr for pr in proj if pr.get("name")]):
            with pcols[i % 2]:
                tech_tags = ""
                if pr.get("technologies"):
                    tech_tags = "".join(f'<span class="pf-project-tech-tag">{t.strip()}</span>' for t in pr["technologies"].split(",") if t.strip())
                hl = f'<p class="pf-project-hl">✦ {pr["highlights"]}</p>' if pr.get("highlights") else ""
                st.markdown(f"""<div class="pf-project-card">
  <div class="pf-project-name">{pr["name"]}</div>
  <p class="pf-project-desc">{pr.get("description","")}</p>
  <div>{tech_tags}</div>
  {hl}
</div>""", unsafe_allow_html=True)

    # Experience Timeline
    if has(exp, "company"):
        st.markdown('<div class="pf-section-title">Experience</div>', unsafe_allow_html=True)
        for e in exp:
            if not e.get("company"): continue
            end = "Present" if e.get("current") else e.get("endDate", "")
            hl_tags = ""
            if e.get("highlights"):
                hl_tags = "".join(f'<span class="pf-skill-tag">{h.strip()}</span>' for h in e["highlights"].split(",") if h.strip())
            st.markdown(f"""<div class="pf-timeline-item">
  <div class="pf-timeline-dot"></div>
  <div class="pf-timeline-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start">
      <div><div class="pf-timeline-pos">{e["position"]}</div><p class="pf-timeline-co">{e["company"]}</p></div>
      <span class="pf-timeline-date">{e.get("startDate","")} — {end}</span>
    </div>
    {f'<p class="pf-timeline-desc">{e["description"]}</p>' if e.get("description") else ""}
    <div style="margin-top:8px">{hl_tags}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Education
    if has(edu, "institution"):
        st.markdown('<div class="pf-section-title">Education</div>', unsafe_allow_html=True)
        ecols = st.columns(min(len([e for e in edu if e.get("institution")]), 3))
        for i, e in enumerate([e for e in edu if e.get("institution")]):
            with ecols[i % len(ecols)]:
                deg = e["degree"] + (f' in {e["field"]}' if e.get("field") else "")
                gpa = f' · GPA: {e["gpa"]}' if e.get("gpa") else ""
                st.markdown(f"""<div class="pf-edu-card">
  <div class="pf-edu-deg">{deg}</div>
  <p class="pf-edu-school">{e["institution"]}</p>
  <p class="pf-edu-date">{e.get("startDate","")} — {e.get("endDate","")}{gpa}</p>
</div>""", unsafe_allow_html=True)

    # Achievements
    if has(ach, "title"):
        st.markdown('<div class="pf-section-title">Achievements</div>', unsafe_allow_html=True)
        for a in ach:
            if not a.get("title"): continue
            date_chip = f'<span class="pf-ach-date">{a["date"]}</span>' if a.get("date") else ""
            st.markdown(f"""<div class="pf-ach-item">
  <span class="pf-ach-icon">🏆</span>
  <div><div class="pf-ach-title">{a["title"]}</div>
  {f'<p class="pf-ach-desc">{a["description"]}</p>' if a.get("description") else ""}</div>
  {date_chip}
</div>""", unsafe_allow_html=True)

    # Contact
    st.markdown('<div class="pf-section-title">Get In Touch</div>', unsafe_allow_html=True)
    contact_links = ""
    if p["email"]: contact_links += f'<a class="pf-contact-link" href="mailto:{p["email"]}">✉ {p["email"]}</a>'
    if p["phone"]: contact_links += f'<span class="pf-contact-link">📞 {p["phone"]}</span>'
    if p["location"]: contact_links += f'<span class="pf-contact-link">📍 {p["location"]}</span>'
    if p["website"]:
        ws = p["website"] if p["website"].startswith("http") else f'https://{p["website"]}'
        contact_links += f'<a class="pf-contact-link" href="{ws}" target="_blank">🌐 Website</a>'
    st.markdown(f"""<div class="pf-contact-card">
  <p class="pf-contact-intro">Open to opportunities, collaborations, and interesting projects.</p>
  <div>{contact_links}</div>
</div>""", unsafe_allow_html=True)

    if not p["fullName"]:
        st.markdown("""<div class="card" style="text-align:center;padding:30px;margin-top:20px;border-style:dashed">
  <div style="font-size:2rem;margin-bottom:8px">📝</div>
  <div class="card-title">No data yet</div>
  <div style="color:var(--muted2);font-size:.85rem;margin-top:4px">Fill in the <strong>✏️ Build Resume</strong> tab first, then come back here to see your portfolio.</div>
</div>""", unsafe_allow_html=True)
