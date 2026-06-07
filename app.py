"""
PATHFINDER — AI-powered career guidance for Indonesian students
Production-ready single-file app (Streamlit + SQLAlchemy + google-genai + pypdf)
"""

import streamlit as st
import os, io, json, re, uuid, datetime, math
from pathlib import Path

# ── PDF ────────────────────────────────────────────────────────────────────────
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# ── Database (SQLAlchemy) ──────────────────────────────────────────────────────
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ── Gemini ─────────────────────────────────────────────────────────────────────
from google import genai
from google.genai import types as genai_types

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — SQLAlchemy Models & Seed Data
# ══════════════════════════════════════════════════════════════════════════════

Base = declarative_base()

class IndonesianMajorCatalog(Base):
    __tablename__ = "indonesian_major_catalog"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    major_name = Column(String(200), nullable=False, unique=True)

class OnetOccupation(Base):
    __tablename__ = "onet_occupations"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    soc_code    = Column(String(20), nullable=False, unique=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text)

class CourseCatalog(Base):
    __tablename__ = "course_catalog"
    course_id        = Column(Integer, primary_key=True, autoincrement=True)
    title            = Column(String(300), nullable=False)
    provider         = Column(String(100))
    url              = Column(String(500))
    mapped_onet_code = Column(String(20), ForeignKey("onet_occupations.soc_code"))
    total_hours      = Column(Float, default=0)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id  = Column(String(64), unique=True)
    full_name   = Column(String(200))
    education   = Column(String(100))
    major       = Column(String(200))
    institution = Column(String(200))
    cv_text     = Column(Text)
    created_at  = Column(String(30))

class UserSkill(Base):
    __tablename__ = "user_skills"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id  = Column(String(64))
    skill_name  = Column(String(200))
    verified    = Column(Integer, default=0)
    verify_url  = Column(String(500))

DB_PATH = Path(__file__).parent / "pathfinder.db"
_engine  = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
_Session = sessionmaker(bind=_engine)

# ── Seed data ──────────────────────────────────────────────────────────────────
_MAJORS = [
    "Teknik Informatika", "Sistem Informasi", "Ilmu Komputer", "Teknik Elektro",
    "Manajemen", "Akuntansi", "Ekonomi", "Bisnis Internasional",
    "Ilmu Komunikasi", "Hubungan Internasional", "Psikologi", "Sosiologi",
    "Teknik Industri", "Teknik Mesin", "Teknik Sipil", "Arsitektur",
    "Kedokteran", "Keperawatan", "Farmasi", "Kesehatan Masyarakat",
    "Hukum", "Pendidikan", "Matematika", "Statistika", "Fisika", "Kimia",
    "Biologi", "Agribisnis", "Pertanian", "Perikanan", "Kehutanan",
    "Desain Komunikasi Visual", "Desain Interior", "Seni Rupa",
    "Sastra Inggris", "Sastra Indonesia", "Bahasa dan Sastra Asing",
    "Ilmu Politik", "Administrasi Publik", "Administrasi Bisnis",
]

_OCCUPATIONS = [
    ("15-1252.00", "Software Developer", "Design, build, and maintain software systems and applications."),
    ("15-1211.00", "Computer Systems Analyst", "Analyze IT requirements and recommend solutions."),
    ("15-2051.00", "Data Scientist", "Use statistical methods and ML to analyze large data sets."),
    ("15-1244.00", "Network and Computer Systems Administrator", "Install and maintain networking hardware and software."),
    ("15-1221.00", "Computer and Information Research Scientist", "Invent and design new approaches to computing technology."),
    ("13-2011.00", "Accountant", "Examine and prepare financial records and ensure accuracy."),
    ("13-1111.00", "Management Analyst", "Propose ways to improve organizational efficiency."),
    ("11-2021.00", "Marketing Manager", "Plan programs to generate interest in products or services."),
    ("41-3099.00", "Sales Representative", "Sell products and services to businesses or individuals."),
    ("13-1151.00", "Training and Development Specialist", "Help plan, conduct, and administer programs for training."),
    ("27-3031.00", "Public Relations Specialist", "Create and maintain a favorable public image for an organization."),
    ("11-3031.00", "Financial Manager", "Direct financial activities of an organization."),
    ("15-1299.00", "AI/ML Engineer", "Develop machine learning models and AI systems."),
    ("15-1231.00", "Computer Network Architect", "Design and build data communication networks."),
    ("11-1021.00", "General and Operations Manager", "Oversee day-to-day operations and plan organizational goals."),
    ("13-2051.00", "Financial Analyst", "Assess the performance of investments and provide guidance."),
    ("15-1212.00", "Information Security Analyst", "Plan and carry out security measures to protect data."),
    ("27-1024.00", "Graphic Designer", "Create visual concepts to communicate ideas."),
    ("25-1099.00", "Education Administrator", "Direct activities in educational institutions."),
    ("29-1141.00", "Registered Nurse", "Provide care for patients and coordinate with healthcare workers."),
]

_COURSES = [
    # Software Developer
    ("Python for Everybody", "Coursera", "https://coursera.org/learn/python", "15-1252.00", 40),
    ("Full Stack Web Development", "Udemy", "https://udemy.com/full-stack", "15-1252.00", 60),
    ("Data Structures & Algorithms", "edX", "https://edx.org/dsa", "15-1252.00", 30),
    ("DevOps Fundamentals", "Coursera", "https://coursera.org/devops", "15-1252.00", 25),
    # Data Scientist
    ("Machine Learning Specialization", "Coursera", "https://coursera.org/ml", "15-2051.00", 80),
    ("Data Analysis with Python", "edX", "https://edx.org/da-python", "15-2051.00", 35),
    ("Deep Learning", "fast.ai", "https://fast.ai", "15-2051.00", 50),
    ("SQL for Data Science", "Coursera", "https://coursera.org/sql", "15-2051.00", 20),
    # AI/ML Engineer
    ("TensorFlow Developer Certificate", "Coursera", "https://coursera.org/tensorflow", "15-1299.00", 60),
    ("MLOps Specialization", "Coursera", "https://coursera.org/mlops", "15-1299.00", 45),
    ("NLP with HuggingFace", "Hugging Face", "https://huggingface.co/course", "15-1299.00", 30),
    # Information Security Analyst
    ("Cybersecurity Fundamentals", "edX", "https://edx.org/cyber", "15-1212.00", 40),
    ("Ethical Hacking", "Udemy", "https://udemy.com/ethical-hacking", "15-1212.00", 35),
    ("CompTIA Security+ Prep", "CompTIA", "https://comptia.org", "15-1212.00", 50),
    # Financial Analyst
    ("Financial Modeling & Valuation", "CFI", "https://corporatefinanceinstitute.com", "13-2051.00", 45),
    ("Investment Analysis", "Coursera", "https://coursera.org/investment", "13-2051.00", 30),
    ("Excel for Finance", "Udemy", "https://udemy.com/excel-finance", "13-2051.00", 20),
    # Marketing Manager
    ("Digital Marketing Fundamentals", "Google", "https://skillshop.google.com", "11-2021.00", 25),
    ("Social Media Marketing", "HubSpot", "https://academy.hubspot.com", "11-2021.00", 20),
    ("Content Marketing Strategy", "Coursera", "https://coursera.org/content-marketing", "11-2021.00", 15),
    # Management Analyst
    ("Business Analysis Fundamentals", "Udemy", "https://udemy.com/business-analysis", "13-1111.00", 30),
    ("Project Management Professional", "PMI", "https://pmi.org", "13-1111.00", 60),
    ("Lean Six Sigma Green Belt", "ASQ", "https://asq.org", "13-1111.00", 40),
    # Network Admin
    ("Cisco CCNA", "Cisco", "https://cisco.com/ccna", "15-1244.00", 80),
    ("CompTIA Network+", "CompTIA", "https://comptia.org/network", "15-1244.00", 50),
    # Public Relations
    ("Public Relations Fundamentals", "Coursera", "https://coursera.org/pr", "27-3031.00", 20),
    ("Crisis Communications", "edX", "https://edx.org/crisis-comm", "27-3031.00", 15),
    # Graphic Designer
    ("Adobe Creative Suite", "Adobe", "https://adobe.com/learn", "27-1024.00", 40),
    ("UI/UX Design Fundamentals", "Google", "https://grow.google/ux", "27-1024.00", 35),
    ("Figma for Designers", "Figma", "https://figma.com/academy", "27-1024.00", 20),
]

def _init_db() -> None:
    Base.metadata.create_all(_engine)
    with _Session() as s:
        if s.query(IndonesianMajorCatalog).count() == 0:
            s.add_all([IndonesianMajorCatalog(major_name=m) for m in _MAJORS])
        if s.query(OnetOccupation).count() == 0:
            s.add_all([OnetOccupation(soc_code=c, title=t, description=d) for c, t, d in _OCCUPATIONS])
        if s.query(CourseCatalog).count() == 0:
            s.add_all([CourseCatalog(title=t, provider=p, url=u, mapped_onet_code=o, total_hours=h)
                       for t, p, u, o, h in _COURSES])
        s.commit()

@st.cache_resource
def get_db_engine():
    _init_db()
    return _engine

def _db():
    get_db_engine()
    return _Session()

# ── DB helpers ─────────────────────────────────────────────────────────────────
def get_all_majors() -> list:
    with _db() as s:
        rows = s.query(IndonesianMajorCatalog).order_by(IndonesianMajorCatalog.major_name).all()
        return [r.major_name for r in rows]

def get_all_onet_titles() -> list:
    with _db() as s:
        rows = s.query(OnetOccupation).order_by(OnetOccupation.title).all()
        return [r.title for r in rows]

def get_courses_for_onet(soc_code: str) -> list:
    with _db() as s:
        rows = s.query(CourseCatalog).filter_by(mapped_onet_code=soc_code).all()
        return [{"title": r.title, "provider": r.provider, "url": r.url,
                 "hours": r.total_hours} for r in rows]

def get_total_hours(soc_code: str) -> float:
    with _db() as s:
        rows = s.query(CourseCatalog).filter_by(mapped_onet_code=soc_code).all()
        return sum(r.total_hours for r in rows)

def get_soc_for_title(title: str):
    with _db() as s:
        row = s.query(OnetOccupation).filter_by(title=title).first()
        return row.soc_code if row else None

def upsert_user_profile(session_id: str, **kw) -> None:
    with _db() as s:
        row = s.query(UserProfile).filter_by(session_id=session_id).first()
        if row is None:
            row = UserProfile(session_id=session_id)
            s.add(row)
        for k, v in kw.items():
            setattr(row, k, v)
        row.created_at = datetime.datetime.utcnow().isoformat()
        s.commit()

def upsert_user_skills(session_id: str, skills: list) -> None:
    with _db() as s:
        s.query(UserSkill).filter_by(session_id=session_id).delete()
        for sk in skills:
            s.add(UserSkill(session_id=session_id, skill_name=sk))
        s.commit()

def get_user_skills(session_id: str) -> list:
    with _db() as s:
        rows = s.query(UserSkill).filter_by(session_id=session_id).all()
        return [{"skill_name": r.skill_name, "verified": bool(r.verified),
                 "verify_url": r.verify_url} for r in rows]

def verify_user_skill(session_id: str, skill_name: str, url: str) -> None:
    with _db() as s:
        row = s.query(UserSkill).filter_by(session_id=session_id, skill_name=skill_name).first()
        if row:
            row.verified = 1
            row.verify_url = url
            s.commit()

# ══════════════════════════════════════════════════════════════════════════════
# GEMINI BACKEND
# ══════════════════════════════════════════════════════════════════════════════

ANALYZE_MODEL = "gemini-2.0-pro"

ANALYZE_SYSTEM_PROMPT = """
You are an expert career counselor and labor-market analyst specializing in the Indonesian job market and international standards (O*NET SOC codes, SKKNI).

Given a candidate's CV/profile text, return ONLY a valid JSON object (no markdown, no prose) with this exact schema:

{
  "candidate_name": "string",
  "detected_skills": ["skill1", "skill2", ...],
  "education_level": "SMA/SMK | D3 | S1 | S2 | S3 | Other",
  "major": "string",
  "years_experience": number,
  "top_matches": [
    {
      "soc_code": "XX-XXXX.XX",
      "title": "string",
      "description": "string (1-2 sentences, why this role fits)",
      "matched_skills": ["skill1", "skill2"],
      "skill_gaps": ["missing_skill1", "missing_skill2"],
      "match_score": number between 0 and 100
    }
  ]
}

Rules:
- Return exactly 3 items in top_matches, ordered by match_score descending.
- match_score is an integer 0-100.
- detected_skills lists every concrete skill found in the profile (hard + soft, max 20).
- skill_gaps lists skills the role typically requires but the candidate lacks (max 8 per role).
- soc_code must be a valid O*NET code matching one of the common professions.
- Use English for all field values.
- Do NOT wrap in markdown code fences.
"""

def _call_gemini(cv_text: str) -> dict:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None
    if not api_key or str(api_key).strip() in ("", "PASTE_YOUR_KEY_HERE"):
        raise RuntimeError(
            "GEMINI_API_KEY belum dikonfigurasi. "
            "Tambahkan di .streamlit/secrets.toml atau Streamlit Cloud Secrets."
        )
    client = genai.Client(api_key=api_key)
    full_prompt = ANALYZE_SYSTEM_PROMPT + "\n\n--- BEGIN CV ---\n" + cv_text + "\n--- END CV ---"
    response = client.models.generate_content(
        model=ANALYZE_MODEL,
        contents=full_prompt,
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    data = json.loads(raw)
    # Enrich each match with DB course data
    for m in data.get("top_matches", []):
        soc = m.get("soc_code", "")
        m["total_course_hours"] = get_total_hours(soc)
        m["courses"] = get_courses_for_onet(soc)
    return data

def _run_with_loading(fn, *args, **kwargs):
    import time
    steps = [
        ("🔍", "Parsing profile data..."),
        ("📡", "Scanning O*NET & SKKNI databases..."),
        ("🗺️", "Mapping career trajectories..."),
        ("📊", "Calculating skill gap metrics..."),
        ("✨", "Finalizing recommendations..."),
    ]
    placeholder = st.empty()
    for i, (icon, step) in enumerate(steps[:-1]):
        pct = int((i + 1) / len(steps) * 100)
        with placeholder.container():
            st.markdown(f"""
            <div style="text-align:center;padding:3rem 1rem;">
              <div style="font-size:3rem;margin-bottom:1rem;">{icon}</div>
              <div style="font-size:1.1rem;font-weight:600;color:#2563eb;margin-bottom:1rem;">{step}</div>
              <div style="background:#e5e7eb;border-radius:9999px;height:8px;overflow:hidden;max-width:400px;margin:0 auto;">
                <div style="background:linear-gradient(90deg,#2563eb,#7c3aed);height:100%;
                            width:{pct}%;border-radius:9999px;transition:width 0.4s;"></div>
              </div>
              <div style="font-size:0.8rem;color:#9ca3af;margin-top:0.5rem;">{pct}% complete</div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.5)
    result = fn(*args, **kwargs)
    placeholder.empty()
    return result

# ══════════════════════════════════════════════════════════════════════════════
# PDF EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

def extract_pdf_text(file_bytes: bytes) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf not installed. Add pypdf to requirements.txt.")
    reader = PdfReader(io.BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n".join(parts)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════════

def _inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .pf-topbar {
        display:flex; align-items:center; justify-content:space-between;
        padding:0.75rem 1.5rem; background:#fff;
        border-bottom:1px solid #e5e7eb; margin-bottom:1.5rem;
        border-radius:0 0 12px 12px;
    }
    .pf-logo { font-size:1.4rem; font-weight:800; color:#2563eb; letter-spacing:-0.5px; }
    .pf-logo span { color:#7c3aed; }
    .pf-steps { display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap; }
    .pf-step { font-size:0.75rem; padding:0.3rem 0.8rem; border-radius:9999px;
                font-weight:500; background:#f3f4f6; color:#6b7280; }
    .pf-step.active { background:#2563eb; color:#fff; }
    .pf-step.done { background:#d1fae5; color:#059669; }

    .pf-card {
        background:#fff; border:1px solid #e5e7eb; border-radius:16px;
        padding:1.5rem; margin-bottom:1rem;
        box-shadow:0 1px 3px rgba(0,0,0,.06);
    }
    .pf-card-gold { border:2px solid #f59e0b !important; box-shadow:0 4px 14px rgba(245,158,11,.18) !important; }
    .pf-card-dashed { border:2px dashed #d1d5db !important; background:#f9fafb !important; }

    .pf-badge { display:inline-block; font-size:0.65rem; font-weight:700;
                padding:0.2rem 0.55rem; border-radius:9999px;
                text-transform:uppercase; letter-spacing:0.05em; }
    .pf-badge-gold { background:#fef3c7; color:#d97706; }
    .pf-badge-blue { background:#dbeafe; color:#1d4ed8; }
    .pf-badge-green { background:#d1fae5; color:#059669; }
    .pf-badge-red { background:#fee2e2; color:#dc2626; }

    .pf-pill { display:inline-block; font-size:0.7rem; font-weight:500;
               padding:0.15rem 0.55rem; border-radius:9999px;
               background:#ede9fe; color:#7c3aed; margin:0.1rem; }

    .pf-work-card {
        background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px;
        padding:1rem; margin-bottom:0.75rem;
    }
    .pf-section-header {
        font-size:0.7rem; font-weight:700; text-transform:uppercase;
        letter-spacing:0.08em; color:#6b7280; margin-bottom:0.75rem;
        padding-bottom:0.4rem; border-bottom:2px solid #e5e7eb;
    }
    .pf-hero {
        text-align:center; padding:4rem 1rem 3rem;
        background:linear-gradient(135deg,#eff6ff 0%,#f5f3ff 100%);
        border-radius:24px; margin-bottom:2rem;
    }
    .pf-hero h1 { font-size:3rem; font-weight:800; color:#111827;
                   margin:0 0 0.5rem; line-height:1.1; }
    .pf-hero h1 span { color:#2563eb; }
    .pf-hero p { font-size:1.15rem; color:#6b7280; max-width:520px;
                  margin:0 auto 2rem; }
    .pf-cert-zone {
        border:2px dashed #d1d5db; border-radius:12px; padding:1.25rem;
        text-align:center; color:#9ca3af; font-size:0.85rem; margin-bottom:0.5rem;
    }
    .pf-timeline-item {
        display:flex; gap:1rem; align-items:flex-start;
        padding:0.75rem 0; border-bottom:1px solid #f3f4f6;
    }
    .pf-timeline-dot {
        width:32px; height:32px; border-radius:50%; flex-shrink:0;
        display:flex; align-items:center; justify-content:center;
        font-size:0.8rem; font-weight:700;
    }
    .pf-stat { text-align:center; padding:1.25rem; background:#fff;
               border:1px solid #e5e7eb; border-radius:16px; }
    .pf-stat-num { font-size:2.2rem; font-weight:800; color:#2563eb; }
    .pf-stat-label { font-size:0.8rem; color:#6b7280; margin-top:0.25rem; }

    #MainMenu, footer { visibility:hidden; }
    .stDeployButton { display:none; }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════════════════════════════════════════

_STEPS_ORDER = ["landing", "upload", "results", "skill_gap", "choose_plan", "roadmap", "dashboard"]
_STEP_LABELS = {
    "landing": "Home", "upload": "Upload CV", "results": "Matches",
    "skill_gap": "Skill Gap", "choose_plan": "Study Plan",
    "roadmap": "Roadmap", "dashboard": "Dashboard",
}

def _render_topbar():
    current = st.session_state.get("pf_step", "landing")
    idx_current = _STEPS_ORDER.index(current) if current in _STEPS_ORDER else 0
    steps_html = ""
    for i, step in enumerate(_STEPS_ORDER[1:], 1):
        label = _STEP_LABELS[step]
        if i < idx_current:
            cls = "pf-step done"
        elif step == current:
            cls = "pf-step active"
        else:
            cls = "pf-step"
        steps_html += f'<div class="{cls}">{label}</div>'
    st.markdown(f"""
    <div class="pf-topbar">
        <div class="pf-logo">Path<span>finder</span></div>
        <div class="pf-steps">{steps_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def _init_session():
    defaults = {
        "pf_step": "landing",
        "pf_session_id": str(uuid.uuid4()),
        "pf_analysis": None,
        "pf_selected_match": None,
        "pf_selected_plan": None,
        "pf_study_hours_per_day": 2,
        "pf_roadmap_courses": [],
        "pf_completed_courses": set(),
        "pf_work_entries": [{"id": 0}],
        "pf_work_counter": 1,
        "pf_skill_verify_states": {},
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — 3-Column Manual Entry Form
# ══════════════════════════════════════════════════════════════════════════════

def _render_manual_form():
    all_majors = ["(Select or type below)"] + get_all_majors() + ["Other"]
    all_titles = ["(Select or type below)"] + get_all_onet_titles() + ["Other"]

    col_edu, col_work, col_skills = st.columns([1, 1.2, 1], gap="large")

    # ── Col 1: Education ──────────────────────────────────────────────────────
    with col_edu:
        st.markdown('<div class="pf-section-header">🎓 Education</div>', unsafe_allow_html=True)
        full_name = st.text_input("Full Name", placeholder="e.g. Budi Santoso", key="pf_manual_name")
        edu_options = ["SMA/SMK", "D3", "S1 (Bachelor's)", "S2 (Master's)", "S3 (PhD)", "Other"]
        edu_level = st.selectbox("Education Level", edu_options, key="pf_manual_edu")
        major_choice = st.selectbox("Major / Field of Study", all_majors, key="pf_manual_major_sel")
        if major_choice in ("(Select or type below)", "Other"):
            major = st.text_input("Specify Major", placeholder="e.g. Teknik Informatika",
                                  key="pf_manual_major_txt")
        else:
            major = major_choice
        institution = st.text_input("Institution Name", placeholder="e.g. Universitas Padjadjaran",
                                    key="pf_manual_inst")
        grad_year = st.selectbox("Graduation Year",
                                 ["—"] + [str(y) for y in range(2030, 1985, -1)],
                                 key="pf_manual_grad")

    # ── Col 2: Work Experience ────────────────────────────────────────────────
    with col_work:
        st.markdown('<div class="pf-section-header">💼 Work Experience</div>', unsafe_allow_html=True)
        entries = st.session_state["pf_work_entries"]
        for idx, entry in enumerate(entries):
            eid = entry["id"]
            st.markdown('<div class="pf-work-card">', unsafe_allow_html=True)
            job_choice = st.selectbox(f"Job Title #{idx+1}", all_titles,
                                      key=f"pf_job_title_sel_{eid}")
            if job_choice in ("(Select or type below)", "Other"):
                job_title = st.text_input("Specify Title", key=f"pf_job_title_txt_{eid}",
                                          placeholder="e.g. Data Analyst")
            else:
                job_title = job_choice  # noqa: F841
            company = st.text_input("Company / Organization", key=f"pf_company_{eid}",
                                    placeholder="e.g. PT Tokopedia")
            dc1, dc2 = st.columns(2)
            with dc1:
                st.selectbox("Start Year",
                             ["—"] + [str(y) for y in range(2030, 1980, -1)],
                             key=f"pf_start_{eid}")
            with dc2:
                st.selectbox("End Year",
                             ["—", "Present"] + [str(y) for y in range(2030, 1980, -1)],
                             key=f"pf_end_{eid}")
            st.markdown('</div>', unsafe_allow_html=True)
            if len(entries) > 1:
                if st.button("✕ Remove", key=f"pf_remove_{eid}", use_container_width=True):
                    st.session_state["pf_work_entries"] = [e for e in entries if e["id"] != eid]
                    st.rerun()
        if st.button("＋ Add Another Experience", use_container_width=True):
            new_id = st.session_state["pf_work_counter"]
            st.session_state["pf_work_entries"].append({"id": new_id})
            st.session_state["pf_work_counter"] += 1
            st.rerun()

    # ── Col 3: Skills & Certs ─────────────────────────────────────────────────
    with col_skills:
        st.markdown('<div class="pf-section-header">🛠️ Skills & Certifications</div>',
                    unsafe_allow_html=True)
        raw_skills = st.text_area(
            "Technical & Soft Skills",
            placeholder="Python, SQL, Project Management, Communication, ...\n(comma-separated)",
            height=120, key="pf_manual_skills_raw"
        )
        if raw_skills.strip():
            pills = [s.strip() for s in raw_skills.split(",") if s.strip()]
            pills_html = " ".join(f'<span class="pf-pill">{p}</span>' for p in pills)
            st.markdown(pills_html, unsafe_allow_html=True)
            st.caption(f"{len(pills)} skill(s) detected")

        st.markdown("---")
        st.markdown("**Certifications / Licenses**")
        st.markdown('<div class="pf-cert-zone">📎 Drop certificate files here (PDF/PNG/JPG)</div>',
                    unsafe_allow_html=True)
        cert_files = st.file_uploader(
            "Upload Certificates", type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True, label_visibility="collapsed",
            key="pf_cert_files"
        )
        if cert_files:
            for cf in cert_files:
                st.markdown(f'<span class="pf-badge pf-badge-green">✓ {cf.name}</span>',
                            unsafe_allow_html=True)
        cert_text = st.text_area(
            "Or list certifications manually",
            placeholder="AWS Certified Developer (2023)\nGoogle Data Analytics Certificate",
            height=80, key="pf_cert_text"
        )

    return {
        "full_name": full_name,
        "edu_level": edu_level,
        "major": major,
        "institution": institution,
        "grad_year": grad_year,
        "raw_skills": raw_skills,
        "cert_text": cert_text,
    }

def _build_cv_text(form_data: dict) -> str:
    entries = st.session_state.get("pf_work_entries", [])
    lines = [
        f"Name: {form_data['full_name']}",
        f"Education: {form_data['edu_level']} in {form_data['major']} at {form_data['institution']}",
        f"Graduation Year: {form_data['grad_year']}",
        "",
        "Work Experience:",
    ]
    for entry in entries:
        eid = entry["id"]
        job_sel = st.session_state.get(f"pf_job_title_sel_{eid}", "")
        if job_sel in ("(Select or type below)", "Other"):
            job_title = st.session_state.get(f"pf_job_title_txt_{eid}", "")
        else:
            job_title = job_sel
        company = st.session_state.get(f"pf_company_{eid}", "")
        start   = st.session_state.get(f"pf_start_{eid}", "—")
        end     = st.session_state.get(f"pf_end_{eid}", "—")
        if job_title and job_title not in ("(Select or type below)", ""):
            lines.append(f"  - {job_title} at {company} ({start}–{end})")
    lines += ["", "Skills:"]
    raw = form_data.get("raw_skills", "")
    for sk in raw.split(","):
        if sk.strip():
            lines.append(f"  - {sk.strip()}")
    lines += ["", "Certifications:"]
    for line in form_data.get("cert_text", "").splitlines():
        if line.strip():
            lines.append(f"  - {line.strip()}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — Results Grid (4 columns)
# ══════════════════════════════════════════════════════════════════════════════

def _render_results():
    analysis = st.session_state.get("pf_analysis")
    if not analysis:
        st.session_state["pf_step"] = "upload"
        st.rerun()

    matches   = analysis.get("top_matches", [])
    candidate = analysis.get("candidate_name", "Candidate")

    st.markdown(f"### Career Matches for **{candidate}**")
    st.caption("Based on your profile, O*NET taxonomy, and SKKNI competency framework.")

    result_cols = st.columns(4, gap="medium")

    for i, match in enumerate(matches[:3]):
        col = result_cols[i]
        is_best   = (i == 0)
        total_hrs = match.get("total_course_hours", 0)
        score     = match.get("match_score", 0)
        gap_count = len(match.get("skill_gaps", []))
        hours_pd  = st.session_state.get("pf_study_hours_per_day", 2)
        days      = math.ceil(total_hrs / max(hours_pd, 1)) if total_hrs else 0

        with col:
            if is_best:
                st.markdown('<span class="pf-badge pf-badge-gold">⭐ Best Match</span>',
                            unsafe_allow_html=True)
            border = "border:2px solid #f59e0b;" if is_best else ""
            st.markdown(f"""
            <div class="pf-card {'pf-card-gold' if is_best else ''}"
                 style="padding:1rem;{border}">
              <div style="font-size:1.05rem;font-weight:700;color:#111827;margin-bottom:0.25rem;">
                {match.get('title','')}
              </div>
              <div style="font-size:0.75rem;color:#6b7280;">{match.get('soc_code','')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(score / 100)
            st.caption(f"**{score}%** match · {gap_count} gaps")

            with st.expander("Why this role?"):
                st.write(match.get("description", ""))

            with st.expander("Skill Gaps"):
                gaps = match.get("skill_gaps", [])
                if gaps:
                    pills = " ".join(f'<span class="pf-pill">{g}</span>' for g in gaps)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.success("No major gaps!")

            st.metric("Study Hours", f"{int(total_hrs)}h", f"~{days} days")

            if st.button("Select This Career", key=f"pf_sel_{i}",
                         use_container_width=True,
                         type="primary" if is_best else "secondary"):
                st.session_state["pf_selected_match"] = {
                    **match,
                    "match_ratio": score / 100,
                }
                st.session_state["pf_step"] = "skill_gap"
                st.rerun()

    # 4th column — Add Profession
    with result_cols[3]:
        st.markdown("""
        <div class="pf-card pf-card-dashed" style="text-align:center;padding:2rem 1rem;">
          <div style="font-size:2.5rem;">＋</div>
          <div style="font-weight:600;color:#374151;margin-bottom:0.25rem;">Add Profession</div>
          <div style="font-size:0.8rem;color:#9ca3af;">Browse O*NET roles to compare</div>
        </div>
        """, unsafe_allow_html=True)
        all_onet  = get_all_onet_titles()
        custom_t  = st.selectbox("Browse O*NET Roles", ["—"] + all_onet, key="pf_custom_onet")
        if custom_t and custom_t != "—":
            soc = get_soc_for_title(custom_t)
            if soc:
                hrs = get_total_hours(soc)
                st.metric("Study Hours", f"{int(hrs)}h")
                if st.button("Add & Select", key="pf_add_custom", use_container_width=True):
                    st.session_state["pf_selected_match"] = {
                        "soc_code": soc,
                        "title": custom_t,
                        "description": "Manually selected profession.",
                        "matched_skills": [],
                        "skill_gaps": [],
                        "match_score": 50,
                        "total_course_hours": hrs,
                        "courses": get_courses_for_onet(soc),
                        "match_ratio": 0.5,
                    }
                    st.session_state["pf_step"] = "skill_gap"
                    st.rerun()

    st.markdown("---")
    if st.button("← Retake Analysis"):
        st.session_state["pf_step"] = "upload"
        st.session_state["pf_analysis"] = None
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SKILL GAP PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_skill_gap():
    match    = st.session_state.get("pf_selected_match", {})
    analysis = st.session_state.get("pf_analysis", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    st.markdown(f"## Skill Gap Analysis")
    st.markdown(f"**Target Role:** {match.get('title','')}")

    detected = analysis.get("detected_skills", [])
    gaps     = match.get("skill_gaps", [])
    score    = match.get("match_score", 0)

    col_have, col_gap = st.columns(2, gap="large")
    with col_have:
        st.markdown("#### ✅ Skills You Have")
        for sk in detected:
            st.markdown(f'<span class="pf-badge pf-badge-green">{sk}</span>',
                        unsafe_allow_html=True)
    with col_gap:
        st.markdown("#### 🔴 Skills to Acquire")
        for sk in gaps:
            st.markdown(f'<span class="pf-badge pf-badge-red">{sk}</span>',
                        unsafe_allow_html=True)
        if not gaps:
            st.success("No significant skill gaps detected!")

    st.markdown("---")
    st.markdown(f"**Overall Match Score:** `{score}%`")
    st.progress(score / 100)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Matches", use_container_width=True):
            st.session_state["pf_step"] = "results"
            st.rerun()
    with c2:
        if st.button("Create Study Plan →", type="primary", use_container_width=True):
            st.session_state["pf_step"] = "choose_plan"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CHOOSE PLAN PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_choose_plan():
    match = st.session_state.get("pf_selected_match", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    total_hrs = match.get("total_course_hours", 0)
    st.markdown("## Choose Your Study Plan")

    plans = [
        {"id": "intensive", "name": "Intensive", "hours": 4, "icon": "🔥",
         "desc": "4 hrs/day — fastest track"},
        {"id": "balanced",  "name": "Balanced",  "hours": 2, "icon": "⚖️",
         "desc": "2 hrs/day — recommended"},
        {"id": "casual",    "name": "Casual",     "hours": 1, "icon": "🌱",
         "desc": "1 hr/day — at your own pace"},
    ]

    cols = st.columns(3, gap="large")
    for plan, col in zip(plans, cols):
        days  = math.ceil(total_hrs / plan["hours"]) if total_hrs else 0
        weeks = math.ceil(days / 7)
        sel   = st.session_state.get("pf_selected_plan") == plan["id"]
        border = "border:2px solid #2563eb;" if sel else "border:1px solid #e5e7eb;"
        with col:
            st.markdown(f"""
            <div class="pf-card" style="{border}text-align:center;padding:1.5rem;">
              <div style="font-size:2.5rem;">{plan['icon']}</div>
              <div style="font-size:1.1rem;font-weight:700;margin:0.5rem 0;">{plan['name']}</div>
              <div style="font-size:0.85rem;color:#6b7280;margin-bottom:1rem;">{plan['desc']}</div>
              <div style="font-size:1.8rem;font-weight:800;color:#2563eb;">{weeks} wks</div>
              <div style="font-size:0.8rem;color:#9ca3af;">{days} days · {int(total_hrs)}h total</div>
            </div>
            """, unsafe_allow_html=True)
            btn_type = "primary" if sel else "secondary"
            label = f"{'✓ Selected' if sel else 'Choose'} {plan['name']}"
            if st.button(label, key=f"pf_plan_{plan['id']}",
                         use_container_width=True, type=btn_type):
                st.session_state["pf_selected_plan"]       = plan["id"]
                st.session_state["pf_study_hours_per_day"] = plan["hours"]
                soc = match.get("soc_code", "")
                st.session_state["pf_roadmap_courses"] = get_courses_for_onet(soc)
                st.rerun()

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back", use_container_width=True):
            st.session_state["pf_step"] = "skill_gap"
            st.rerun()
    with c2:
        if st.session_state.get("pf_selected_plan"):
            if st.button("View Roadmap →", type="primary", use_container_width=True):
                st.session_state["pf_step"] = "roadmap"
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROADMAP PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_roadmap():
    match    = st.session_state.get("pf_selected_match", {})
    courses  = st.session_state.get("pf_roadmap_courses", [])
    hours_pd = st.session_state.get("pf_study_hours_per_day", 2)
    done_set = st.session_state.get("pf_completed_courses", set())
    if not match:
        st.session_state["pf_step"] = "choose_plan"
        st.rerun()

    st.markdown(f"## Learning Roadmap — {match.get('title','')}")

    if not courses:
        st.info("No courses found for this role. Choose a plan first.")
    else:
        total_hrs = sum(c["hours"] for c in courses)
        done_hrs  = sum(c["hours"] for c in courses if c["title"] in done_set)
        pct = int(done_hrs / total_hrs * 100) if total_hrs else 0
        st.markdown(f"**Progress:** {pct}% complete ({int(done_hrs)}/{int(total_hrs)} hours)")
        st.progress(pct / 100)
        st.markdown("---")

        cumday = 0
        for i, course in enumerate(courses):
            days_needed = math.ceil(course["hours"] / max(hours_pd, 1))
            done = course["title"] in done_set
            dot_bg    = "#d1fae5" if done else "#dbeafe"
            dot_color = "#059669" if done else "#2563eb"

            st.markdown(f"""
            <div class="pf-timeline-item">
              <div class="pf-timeline-dot" style="background:{dot_bg};color:{dot_color};">
                {'✓' if done else i+1}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;color:#111827;">{course['title']}</div>
                <div style="font-size:0.8rem;color:#6b7280;">
                  {course.get('provider','')} · {int(course['hours'])}h ·
                  ~{days_needed} days (starts day {cumday+1})
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            ca, cb, cc = st.columns([3, 1, 1])
            with cb:
                if course.get("url"):
                    st.link_button("Open", course["url"], use_container_width=True)
            with cc:
                label = "✓ Done" if done else "Mark Done"
                if st.button(label, key=f"pf_done_{i}", use_container_width=True):
                    if done:
                        done_set.discard(course["title"])
                    else:
                        done_set.add(course["title"])
                    st.session_state["pf_completed_courses"] = done_set
                    st.rerun()
            cumday += days_needed

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Choose Plan", use_container_width=True):
            st.session_state["pf_step"] = "choose_plan"
            st.rerun()
    with c2:
        if st.button("Dashboard →", type="primary", use_container_width=True):
            st.session_state["pf_step"] = "dashboard"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — @st.dialog Study Planner
# ══════════════════════════════════════════════════════════════════════════════

@st.dialog("Study Planner", width="large")
def _study_planner_dialog():
    import time
    match     = st.session_state.get("pf_selected_match", {})
    courses   = st.session_state.get("pf_roadmap_courses", [])
    total_hrs = match.get("total_course_hours", 0)

    st.markdown(f"### {match.get('title','')} — Personalized Schedule")

    hours_pd = st.slider("Study hours per day", 1, 8,
                         st.session_state.get("pf_study_hours_per_day", 2),
                         key="pf_dialog_hrs")
    st.session_state["pf_study_hours_per_day"] = hours_pd

    total_days  = math.ceil(total_hrs / max(hours_pd, 1)) if total_hrs else 0
    total_weeks = math.ceil(total_days / 7)
    end_date    = datetime.date.today() + datetime.timedelta(days=total_days)

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total Hours", f"{int(total_hrs)}h")
    mc2.metric("Duration", f"{total_weeks} weeks")
    mc3.metric("Finish By", end_date.strftime("%b %d, %Y"))

    st.markdown("---")
    st.markdown("#### Certificate Verification")
    st.caption("Paste a certificate URL to mark course completion as verified.")

    verify_states = st.session_state.setdefault("pf_skill_verify_states", {})

    for course in courses:
        title = course["title"]
        state = verify_states.get(title, {"url": "", "verified": False})

        col_t, col_icon = st.columns([4, 1])
        with col_t:
            st.markdown(f"**{title}** — {course.get('provider','')}")
        with col_icon:
            icon_html = '<span style="font-size:1.4rem;color:#059669;">✅</span>' \
                        if state["verified"] else \
                        '<span style="font-size:1.4rem;color:#dc2626;">✗</span>'
            st.markdown(icon_html, unsafe_allow_html=True)

        new_url = st.text_input(
            "Certificate URL", value=state["url"],
            key=f"pf_cert_url_{hash(title) % 100000}",
            placeholder="https://coursera.org/verify/..."
        )
        state["url"] = new_url

        if st.button("Verify", key=f"pf_verify_{hash(title) % 100000}",
                     use_container_width=False):
            if new_url.strip().startswith("http"):
                state["verified"] = True
                session_id = st.session_state.get("pf_session_id", "")
                try:
                    verify_user_skill(session_id, title, new_url.strip())
                except Exception:
                    pass
                st.success(f"✓ Verified!")
            else:
                st.error("Please enter a valid URL starting with http.")

        verify_states[title] = state
        st.session_state["pf_skill_verify_states"] = verify_states
        st.markdown("---")

    if st.button("Close Planner", use_container_width=True):
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_dashboard():
    match         = st.session_state.get("pf_selected_match", {})
    courses       = st.session_state.get("pf_roadmap_courses", [])
    done_set      = st.session_state.get("pf_completed_courses", set())
    hours_pd      = st.session_state.get("pf_study_hours_per_day", 2)
    verify_states = st.session_state.get("pf_skill_verify_states", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    total_hrs  = match.get("total_course_hours", 0)
    done_hrs   = sum(c["hours"] for c in courses if c["title"] in done_set)
    remain_hrs = max(0, total_hrs - done_hrs)
    pct        = int(done_hrs / total_hrs * 100) if total_hrs else 0
    days_left  = math.ceil(remain_hrs / max(hours_pd, 1))
    verified_n = sum(1 for s in verify_states.values() if s.get("verified"))

    st.markdown(f"## Dashboard — {match.get('title','')}")

    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, f"{pct}%",           "Overall Progress"),
        (s2, f"{int(done_hrs)}h", "Hours Completed"),
        (s3, f"{days_left}d",     "Days Remaining"),
        (s4, str(verified_n),     "Certs Verified"),
    ]:
        with col:
            st.markdown(f"""
            <div class="pf-stat">
              <div class="pf-stat-num">{num}</div>
              <div class="pf-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**Overall Learning Progress**")
    st.progress(pct / 100)
    st.markdown("---")
    st.markdown("#### Course Status")
    for course in courses:
        done     = course["title"] in done_set
        verified = verify_states.get(course["title"], {}).get("verified", False)
        if verified:
            badge = '<span class="pf-badge pf-badge-green">✓ Verified</span>'
        elif done:
            badge = '<span class="pf-badge pf-badge-blue">✓ Completed</span>'
        else:
            badge = '<span class="pf-badge" style="background:#f3f4f6;color:#6b7280;">Pending</span>'
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.6rem 0;border-bottom:1px solid #f3f4f6;">
          <div>
            <span style="font-weight:500;color:#111827;">{course['title']}</span>
            <span style="font-size:0.75rem;color:#9ca3af;margin-left:0.5rem;">
              {course.get('provider','')} · {int(course.get('hours',0))}h
            </span>
          </div>
          {badge}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("← Roadmap", use_container_width=True):
            st.session_state["pf_step"] = "roadmap"
            st.rerun()
    with c2:
        if st.button("📅 Open Study Planner", use_container_width=True, type="primary"):
            _study_planner_dialog()
    with c3:
        if st.button("🔄 Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("pf_"):
                    del st.session_state[k]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_upload():
    st.markdown("## Analyze Your Profile")
    st.caption("Upload your CV or fill in the form — analyzed by Gemini AI against O*NET & SKKNI.")

    tab_pdf, tab_manual = st.tabs(["📄 Upload PDF", "✏️ Enter Manually"])

    with tab_pdf:
        uploaded = st.file_uploader("Upload your CV (PDF)", type=["pdf"],
                                    key="pf_pdf_upload", label_visibility="collapsed")
        if uploaded:
            st.success(f"✓ {uploaded.name} loaded")
            if st.button("Analyze CV", type="primary", use_container_width=True, key="pf_analyze_pdf"):
                try:
                    cv_text = extract_pdf_text(uploaded.read())
                    if not cv_text.strip():
                        st.error("Could not extract text from PDF. Try the manual form.")
                    else:
                        result = _run_with_loading(_call_gemini, cv_text)
                        st.session_state["pf_analysis"] = result
                        upsert_user_profile(st.session_state["pf_session_id"], cv_text=cv_text)
                        st.session_state["pf_step"] = "results"
                        st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    with tab_manual:
        form_data = _render_manual_form()
        st.markdown("")
        if st.button("🔍 Analyze Now", type="primary", use_container_width=True,
                     key="pf_analyze_manual"):
            if not form_data["full_name"].strip():
                st.warning("Please enter your full name.")
            elif not form_data["raw_skills"].strip():
                st.warning("Please enter at least one skill.")
            else:
                cv_text = _build_cv_text(form_data)
                try:
                    result = _run_with_loading(_call_gemini, cv_text)
                    st.session_state["pf_analysis"] = result
                    session_id   = st.session_state["pf_session_id"]
                    skills_list  = [s.strip() for s in form_data["raw_skills"].split(",") if s.strip()]
                    upsert_user_profile(
                        session_id,
                        full_name=form_data["full_name"],
                        education=form_data["edu_level"],
                        major=form_data["major"],
                        institution=form_data["institution"],
                        cv_text=cv_text,
                    )
                    upsert_user_skills(session_id, skills_list)
                    st.session_state["pf_step"] = "results"
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    st.markdown("---")
    if st.button("← Back to Home"):
        st.session_state["pf_step"] = "landing"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_landing():
    st.markdown("""
    <div class="pf-hero">
      <h1>Find Your <span>Career Path</span></h1>
      <p>AI-powered career guidance tailored for Indonesian students — mapped to O*NET and SKKNI competency standards.</p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="large")
    features = [
        ("🤖", "AI Analysis", "Gemini AI analyzes your profile against global O*NET taxonomy and Indonesian SKKNI frameworks."),
        ("🎯", "Career Matching", "Get 3 personalized career matches ranked by compatibility score."),
        ("📚", "Learning Roadmap", "Receive a curated course roadmap with real-time progress tracking and certificate verification."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="pf-card" style="text-align:center;padding:1.5rem;">
              <div style="font-size:2.2rem;margin-bottom:0.5rem;">{icon}</div>
              <div style="font-weight:700;font-size:1rem;margin-bottom:0.4rem;">{title}</div>
              <div style="font-size:0.85rem;color:#6b7280;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Get Started →", type="primary", use_container_width=True, key="pf_start"):
            st.session_state["pf_step"] = "upload"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — App config & router
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Pathfinder — Career Guidance",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

get_db_engine()
_init_session()
_inject_css()
_render_topbar()

step = st.session_state.get("pf_step", "landing")

if step == "landing":
    _render_landing()
elif step == "upload":
    _render_upload()
elif step == "results":
    _render_results()
elif step == "skill_gap":
    _render_skill_gap()
elif step == "choose_plan":
    _render_choose_plan()
elif step == "roadmap":
    _render_roadmap()
elif step == "dashboard":
    _render_dashboard()
else:
    st.session_state["pf_step"] = "landing"
    st.rerun()
