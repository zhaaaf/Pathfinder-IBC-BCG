"""
PATHFINDER — AI-powered career guidance for Indonesian students
Production-ready single-file app (Streamlit + SQLAlchemy + google-genai + pypdf)
"""

import streamlit as st
import os, io, json, re, uuid, datetime, math
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

from google import genai
from google.genai import types as genai_types

# ══════════════════════════════════════════════════════════════════════════════
# MODELS
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
    ("Python for Everybody Specialization", "Coursera",
     "https://www.coursera.org/specializations/python", "15-1252.00", 40),
    ("The Web Developer Bootcamp 2024", "Udemy",
     "https://www.udemy.com/course/the-web-developer-bootcamp/", "15-1252.00", 60),
    ("Algorithms, Part I", "Coursera (Princeton)",
     "https://www.coursera.org/learn/algorithms-part1", "15-1252.00", 30),
    ("DevOps Foundations", "LinkedIn Learning",
     "https://www.linkedin.com/learning/devops-foundations", "15-1252.00", 25),
    ("Machine Learning Specialization", "Coursera (DeepLearning.AI)",
     "https://www.coursera.org/specializations/machine-learning-introduction", "15-2051.00", 80),
    ("Data Analysis with Python", "Coursera (IBM)",
     "https://www.coursera.org/learn/data-analysis-with-python", "15-2051.00", 35),
    ("Practical Deep Learning for Coders", "fast.ai",
     "https://course.fast.ai/", "15-2051.00", 50),
    ("SQL for Data Science", "Coursera (UC Davis)",
     "https://www.coursera.org/learn/sql-for-data-science", "15-2051.00", 20),
    ("DeepLearning.AI TensorFlow Developer Certificate", "Coursera",
     "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "15-1299.00", 60),
    ("Machine Learning Engineering for Production (MLOps)", "Coursera",
     "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops", "15-1299.00", 45),
    ("Hugging Face NLP Course", "Hugging Face",
     "https://huggingface.co/learn/nlp-course/chapter1/1", "15-1299.00", 30),
    ("Cybersecurity Fundamentals", "edX (Rochester Institute of Technology)",
     "https://www.edx.org/learn/cybersecurity/rochester-institute-of-technology-cybersecurity-fundamentals", "15-1212.00", 40),
    ("Learn Ethical Hacking From Scratch", "Udemy",
     "https://www.udemy.com/course/learn-ethical-hacking-from-scratch/", "15-1212.00", 35),
    ("CompTIA Security+ Certification Prep", "CompTIA",
     "https://www.comptia.org/certifications/security", "15-1212.00", 50),
    ("Financial Modeling & Valuation Analyst (FMVA)", "Corporate Finance Institute",
     "https://corporatefinanceinstitute.com/certifications/financial-modeling-valuation-analyst-fmva-certification/", "13-2051.00", 45),
    ("Investment Management Specialization", "Coursera (University of Geneva)",
     "https://www.coursera.org/specializations/investment-management", "13-2051.00", 30),
    ("Excel Skills for Business Specialization", "Coursera (Macquarie University)",
     "https://www.coursera.org/specializations/excel", "13-2051.00", 20),
    ("Google Digital Marketing & E-commerce Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce", "11-2021.00", 25),
    ("Social Media Marketing Certification Course", "HubSpot Academy",
     "https://academy.hubspot.com/courses/social-media", "11-2021.00", 20),
    ("Content Marketing Certification", "HubSpot Academy",
     "https://academy.hubspot.com/courses/content-marketing", "11-2021.00", 15),
    ("Business Analysis & Process Management", "Coursera",
     "https://www.coursera.org/learn/business-analysis-process-management", "13-1111.00", 30),
    ("Google Project Management Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-project-management", "13-1111.00", 60),
    ("Lean Six Sigma Fundamentals", "Coursera (University System of Georgia)",
     "https://www.coursera.org/specializations/six-sigma-fundamentals", "13-1111.00", 40),
    ("Cisco CCNA 200-301 Complete Course", "Udemy",
     "https://www.udemy.com/course/ccna-complete/", "15-1244.00", 80),
    ("CompTIA Network+ Certification Prep", "CompTIA",
     "https://www.comptia.org/certifications/network", "15-1244.00", 50),
    ("Strategic Communication & Public Relations", "edX (UC Berkeley)",
     "https://www.edx.org/certificates/professional-certificate/berkeleyx-strategic-communication-and-public-relations", "27-3031.00", 20),
    ("Introduction to Public Relations", "Coursera",
     "https://www.coursera.org/learn/introduction-to-public-relations", "27-3031.00", 15),
    ("Google UX Design Professional Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-ux-design", "27-1024.00", 40),
    ("Graphic Design Specialization", "Coursera (California Institute of the Arts)",
     "https://www.coursera.org/specializations/graphic-design", "27-1024.00", 35),
    ("Figma UI UX Design Essentials", "Udemy",
     "https://www.udemy.com/course/figma-ux-ui-design-user-experience-tutorial-course/", "27-1024.00", 20),
    ("Financial Management Specialization", "Coursera (University of Illinois)",
     "https://www.coursera.org/specializations/financial-management", "11-3031.00", 50),
    ("Corporate Finance Fundamentals", "Corporate Finance Institute",
     "https://corporatefinanceinstitute.com/course/corporate-finance-fundamentals/", "11-3031.00", 35),
    ("Intuit Academy Bookkeeping Certificate", "Coursera (Intuit)",
     "https://www.coursera.org/professional-certificates/intuit-bookkeeping", "13-2011.00", 40),
    ("Financial Accounting Fundamentals", "Coursera (University of Virginia)",
     "https://www.coursera.org/learn/uva-darden-financial-accounting", "13-2011.00", 30),
    ("Accounting Analytics", "Coursera (University of Pennsylvania)",
     "https://www.coursera.org/learn/accounting-analytics", "13-2011.00", 20),
]

_ONET_TYPICAL_SKILLS = {
    "15-1252.00": ["JavaScript", "React", "Node.js", "SQL", "Git", "REST APIs", "Docker", "Agile", "Unit Testing", "Python"],
    "15-2051.00": ["Python", "Machine Learning", "SQL", "Statistics", "R", "TensorFlow", "Data Visualization", "Pandas", "NumPy", "Deep Learning"],
    "15-1299.00": ["Python", "TensorFlow", "PyTorch", "MLOps", "Docker", "Kubernetes", "NLP", "Computer Vision", "AWS/GCP", "ML Pipelines"],
    "15-1244.00": ["Cisco IOS", "TCP/IP", "Firewalls", "VPN", "Linux", "Active Directory", "VLAN", "BGP", "Network Security", "Troubleshooting"],
    "15-1212.00": ["Network Security", "SIEM", "Penetration Testing", "Linux", "Incident Response", "Cryptography", "Firewall Management", "Risk Assessment"],
    "13-2011.00": ["GAAP", "Financial Reporting", "Excel", "Auditing", "Tax Compliance", "QuickBooks", "Financial Analysis", "Budgeting"],
    "13-1111.00": ["Business Analysis", "Process Mapping", "Project Management", "Six Sigma", "Stakeholder Management", "Data Analysis", "Change Management"],
    "11-2021.00": ["Digital Marketing", "SEO/SEM", "Google Analytics", "Social Media Strategy", "Content Marketing", "Marketing Automation", "A/B Testing"],
    "41-3099.00": ["CRM Software", "Negotiation", "Lead Generation", "Salesforce", "Cold Calling", "Proposal Writing", "Pipeline Management"],
    "13-1151.00": ["Instructional Design", "LMS Administration", "Needs Assessment", "Training Delivery", "E-learning Tools", "Performance Evaluation"],
    "27-3031.00": ["Media Relations", "Press Release Writing", "Crisis Communication", "Brand Storytelling", "Social Media", "Event Management"],
    "11-3031.00": ["Financial Modeling", "Budgeting", "Cash Flow Management", "Risk Management", "Financial Reporting", "Investor Relations"],
    "15-1231.00": ["Network Architecture", "Cloud Computing", "SD-WAN", "Network Security", "Capacity Planning", "Cisco/Juniper"],
    "11-1021.00": ["Operations Management", "Leadership", "Strategic Planning", "P&L Management", "Team Building", "Process Improvement"],
    "13-2051.00": ["Financial Modeling", "Excel", "Bloomberg Terminal", "Equity Research", "Valuation", "Financial Statements", "Portfolio Analysis"],
    "27-1024.00": ["Adobe Photoshop", "Illustrator", "InDesign", "Figma", "Typography", "Brand Identity", "UI/UX Principles", "Color Theory"],
    "25-1099.00": ["Curriculum Development", "Accreditation", "Budget Management", "Faculty Management", "Assessment Design", "Educational Policy"],
    "29-1141.00": ["Patient Care", "Clinical Assessment", "Electronic Health Records", "Medical Procedures", "HIPAA Compliance", "IV Therapy"],
    "15-1211.00": ["Systems Analysis", "Requirements Gathering", "SQL", "Business Intelligence", "SDLC", "ERP Systems", "Documentation"],
    "15-1221.00": ["Research Methods", "Algorithm Design", "Programming Languages", "Technical Writing", "Academic Publishing", "ML Research"],
}

def _compute_skill_gaps(soc_code: str, user_skills: list) -> list:
    typical   = _ONET_TYPICAL_SKILLS.get(soc_code, [])
    user_low  = {s.lower() for s in user_skills}
    return [s for s in typical if s.lower() not in user_low]

def _init_db() -> None:
    Base.metadata.create_all(_engine)
    with _Session() as s:
        if s.query(IndonesianMajorCatalog).count() == 0:
            s.add_all([IndonesianMajorCatalog(major_name=m) for m in _MAJORS])
        if s.query(OnetOccupation).count() == 0:
            s.add_all([OnetOccupation(soc_code=c, title=t, description=d) for c, t, d in _OCCUPATIONS])
        first = s.query(CourseCatalog).first()
        needs_reseed = (first is None) or ("www." not in (first.url or ""))
        if needs_reseed:
            s.query(CourseCatalog).delete()
            s.add_all([
                CourseCatalog(title=t, provider=p, url=u, mapped_onet_code=o, total_hours=h)
                for t, p, u, o, h in _COURSES
            ])
        s.commit()

@st.cache_resource
def get_db_engine():
    _init_db()
    return _engine

def _db():
    get_db_engine()
    return _Session()

def get_all_majors() -> list:
    with _db() as s:
        return [r.major_name for r in
                s.query(IndonesianMajorCatalog).order_by(IndonesianMajorCatalog.major_name).all()]

def get_all_onet_titles() -> list:
    with _db() as s:
        return [r.title for r in
                s.query(OnetOccupation).order_by(OnetOccupation.title).all()]

def get_courses_for_onet(soc_code: str) -> list:
    with _db() as s:
        return [{"title": r.title, "provider": r.provider, "url": r.url,
                 "hours": r.total_hours, "course_id": r.course_id}
                for r in s.query(CourseCatalog).filter_by(mapped_onet_code=soc_code).all()]

def get_total_hours(soc_code: str) -> float:
    with _db() as s:
        return sum(r.total_hours for r in
                   s.query(CourseCatalog).filter_by(mapped_onet_code=soc_code).all())

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

def verify_user_skill(session_id: str, skill_name: str, url: str) -> None:
    with _db() as s:
        row = s.query(UserSkill).filter_by(session_id=session_id, skill_name=skill_name).first()
        if row:
            row.verified = 1
            row.verify_url = url
            s.commit()

def generate_verified_roadmap(onet_codes: list, duration_tier: str = "balanced") -> list:
    if not onet_codes:
        return []
    with _db() as s:
        rows = (s.query(CourseCatalog)
                .filter(CourseCatalog.mapped_onet_code.in_(onet_codes))
                .all())
        return [{"course_id": r.course_id, "title": r.title, "provider": r.provider,
                 "url": r.url, "hours": r.total_hours, "onet_code": r.mapped_onet_code}
                for r in rows]

# ══════════════════════════════════════════════════════════════════════════════
# GEMINI BACKEND
# ══════════════════════════════════════════════════════════════════════════════

ANALYZE_MODEL = "gemini-2.0-flash"

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
    client   = genai.Client(api_key=api_key)
    prompt   = ANALYZE_SYSTEM_PROMPT + "\n\n--- BEGIN CV ---\n" + cv_text + "\n--- END CV ---"
    response = client.models.generate_content(
        model=ANALYZE_MODEL, contents=prompt,
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0.1),
    )
    raw  = re.sub(r"^```(?:json)?\s*", "", response.text.strip())
    raw  = re.sub(r"\s*```$", "", raw)
    data = json.loads(raw)
    for m in data.get("top_matches", []):
        soc = m.get("soc_code", "")
        m["total_course_hours"] = get_total_hours(soc)
        m["courses"]            = get_courses_for_onet(soc)
    return data

def _run_with_loading(fn, *args, **kwargs):
    import time
    steps = [
        ("🔍", "Parsing profile data..."),
        ("📡", "Scanning O*NET & SKKNI databases..."),
        ("🗺️",  "Mapping career trajectories..."),
        ("📊", "Calculating skill gap metrics..."),
    ]
    ph = st.empty()
    for i, (icon, step) in enumerate(steps):
        pct = int((i + 1) / (len(steps) + 1) * 100)
        with ph.container():
            st.markdown(f"""
            <div style="text-align:center;padding:3.5rem 1rem;background:#F5F4F0;border-radius:16px;">
              <div style="font-size:3rem;margin-bottom:1rem;">{icon}</div>
              <div style="font-size:1.05rem;font-weight:600;color:#2563eb;margin-bottom:1.2rem;">{step}</div>
              <div style="background:#DDD9D0;border-radius:9999px;height:6px;
                          overflow:hidden;max-width:360px;margin:0 auto;">
                <div style="background:linear-gradient(90deg,#B48E4B,#D4AF6E);
                            height:100%;width:{pct}%;border-radius:9999px;
                            transition:width .4s ease;"></div>
              </div>
              <div style="font-size:0.78rem;color:#9ca3af;margin-top:.6rem;">{pct}%</div>
            </div>""", unsafe_allow_html=True)
        time.sleep(0.45)
    result = fn(*args, **kwargs)
    ph.empty()
    return result

def extract_pdf_text(file_bytes: bytes) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf not installed.")
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(p.extract_text() or "" for p in reader.pages)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — GLOBAL CSS THEME  apply_global_css()
# ══════════════════════════════════════════════════════════════════════════════

def apply_global_css():
    st.markdown("""
    <style>
    /* ── Google Font ──────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Root variables ───────────────────────────────────────────────────── */
    :root {
        --cream:      #F5F4F0;
        --white:      #FFFFFF;
        --gold:       #B48E4B;
        --gold-light: #F3E8C8;
        --gold-dark:  #8C6D36;
        --slate:      #374151;
        --muted:      #6B7280;
        --border:     #E5E7EB;
        --chip-bg:    #E2E8F0;
        --dash-border: #CBD5E1;
        --card-shadow: 0 2px 8px rgba(0,0,0,.07);
    }

    /* ── Global reset ─────────────────────────────────────────────────────── */
    html, body, [class*="css"], .stApp, .main, section[data-testid="stSidebar"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ── App background (cream) ───────────────────────────────────────────── */
    .stApp {
        background-color: var(--cream) !important;
    }
    [data-testid="stHeader"] {
        background-color: var(--cream) !important;
    }
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        background-color: var(--cream) !important;
        padding-top: 1rem !important;
        max-width: 1400px;
    }

    /* ── Hide Streamlit chrome ────────────────────────────────────────────── */
    #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], .stDeployButton { display: none !important; }

    /* ── Topbar ───────────────────────────────────────────────────────────── */
    .pf-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: .75rem 1.5rem;
        background: var(--white);
        border-bottom: 1px solid var(--border);
        border-radius: 0 0 14px 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,.04);
    }
    .pf-logo { font-size: 1.4rem; font-weight: 800; color: #2563EB; letter-spacing: -.5px; }
    .pf-logo span { color: var(--gold); }
    .pf-steps { display: flex; gap: .4rem; align-items: center; flex-wrap: wrap; }
    .pf-step {
        font-size: .72rem; padding: .28rem .75rem; border-radius: 9999px;
        font-weight: 500; background: #F3F4F6; color: var(--muted);
        border: 1px solid transparent;
    }
    .pf-step.active { background: #2563EB; color: var(--white); }
    .pf-step.done   { background: #DCFCE7; color: #15803D; }

    /* ── custom-card ──────────────────────────────────────────────────────── */
    .custom-card {
        background: var(--white);
        border-radius: 12px;
        padding: 20px;
        box-shadow: var(--card-shadow);
        border: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    /* ── best-match-card ──────────────────────────────────────────────────── */
    .best-match-card {
        background: var(--white);
        border-radius: 12px;
        padding: 20px;
        border: 3px solid var(--gold) !important;
        box-shadow: 0 4px 16px rgba(180,142,75,.18);
        margin-bottom: 1rem;
    }

    /* ── dashed-box ───────────────────────────────────────────────────────── */
    .dashed-box {
        border: 2px dashed var(--dash-border);
        border-radius: 12px;
        background: rgba(203,213,225,.08);
        padding: 20px;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* ── skill-chip ───────────────────────────────────────────────────────── */
    .skill-chip {
        display: inline-block;
        background: var(--chip-bg);
        color: var(--slate);
        font-size: .72rem;
        font-weight: 500;
        padding: .25rem .7rem;
        border-radius: 9999px;
        margin: 3px 5px 3px 0;
        white-space: nowrap;
    }
    .skill-chip.has { background: #DCFCE7; color: #15803D; }
    .skill-chip.gap { background: #FEE2E2; color: #DC2626; }

    /* ── btn-gold ─────────────────────────────────────────────────────────── */
    .btn-gold {
        display: inline-block;
        background: var(--gold);
        color: var(--white) !important;
        font-weight: 600;
        font-size: .88rem;
        padding: .6rem 1.4rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        text-align: center;
        width: 100%;
        transition: background .2s;
    }
    .btn-gold:hover { background: var(--gold-dark); }

    /* ── section label above inputs ───────────────────────────────────────── */
    .section-label {
        font-size: .68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .09em;
        color: var(--muted);
        margin-bottom: .6rem;
        padding-bottom: .35rem;
        border-bottom: 2px solid var(--border);
    }

    /* ── card number watermark ────────────────────────────────────────────── */
    .card-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #F3F4F6;
        line-height: 1;
        margin-bottom: -.4rem;
    }

    /* ── Work entry container ─────────────────────────────────────────────── */
    .work-entry-shell {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: .75rem;
    }

    /* ── Result card profession title ─────────────────────────────────────── */
    .prof-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--slate);
        margin: .35rem 0 .2rem;
        line-height: 1.25;
    }
    .soc-code {
        font-size: .7rem;
        color: var(--muted);
        font-weight: 500;
        letter-spacing: .04em;
        margin-bottom: .75rem;
    }

    /* ── Gold badge ───────────────────────────────────────────────────────── */
    .gold-badge {
        display: inline-block;
        background: var(--gold-light);
        color: var(--gold-dark);
        font-size: .62rem;
        font-weight: 700;
        padding: .2rem .55rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: .06em;
        float: right;
        margin-top: -.2rem;
    }

    /* ── Metric row in result card ────────────────────────────────────────── */
    .card-metrics {
        display: flex;
        gap: 1rem;
        margin-top: .6rem;
        font-size: .78rem;
        color: var(--muted);
    }
    .card-metrics strong { color: var(--slate); }

    /* ── Outlined button (non-best cards) ─────────────────────────────────── */
    .btn-outline {
        display: inline-block;
        background: transparent;
        color: var(--slate) !important;
        font-weight: 600;
        font-size: .85rem;
        padding: .55rem 1.2rem;
        border-radius: 8px;
        border: 1.5px solid var(--dash-border);
        cursor: pointer;
        text-align: center;
        width: 100%;
        transition: border-color .2s, color .2s;
    }
    .btn-outline:hover { border-color: var(--gold); color: var(--gold) !important; }

    /* ── Hero ─────────────────────────────────────────────────────────────── */
    .pf-hero {
        text-align: center;
        padding: 4rem 1rem 3rem;
        background: linear-gradient(135deg, #EFF6FF 0%, #FEF9EE 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid #E9E4D8;
    }
    .pf-hero h1 { font-size: 2.8rem; font-weight: 800; color: #111827;
                   margin: 0 0 .5rem; line-height: 1.1; }
    .pf-hero h1 span { color: var(--gold); }
    .pf-hero p  { font-size: 1.1rem; color: var(--muted); max-width: 500px;
                   margin: 0 auto 2rem; }

    /* ── Timeline ─────────────────────────────────────────────────────────── */
    .pf-timeline-item { display: flex; gap: 1rem; align-items: flex-start;
                         padding: .75rem 0; border-bottom: 1px solid #F3F4F6; }
    .pf-timeline-dot  { width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
                         display: flex; align-items: center; justify-content: center;
                         font-size: .8rem; font-weight: 700; }

    /* ── Dashboard stat ───────────────────────────────────────────────────── */
    .pf-stat { text-align: center; padding: 1.25rem; background: var(--white);
               border: 1px solid var(--border); border-radius: 14px; }
    .pf-stat-num   { font-size: 2rem; font-weight: 800; color: var(--gold); }
    .pf-stat-label { font-size: .78rem; color: var(--muted); margin-top: .2rem; }

    /* ── Streamlit native element tweaks ──────────────────────────────────── */
    .stTextInput > label, .stSelectbox > label,
    .stTextArea > label, .stFileUploader > label {
        font-size: .75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: .07em !important;
        color: var(--muted) !important;
    }
    .stTextInput input, .stSelectbox select,
    [data-baseweb="input"] input,
    [data-baseweb="select"] div[data-id="content"] {
        border-radius: 8px !important;
        border: 1.5px solid var(--border) !important;
        background: var(--white) !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--gold), #D4AF6E) !important;
        border-radius: 9999px !important;
    }
    div[data-testid="stProgress"] {
        background: #E9E4D8 !important;
        border-radius: 9999px !important;
        height: 6px !important;
    }
    /* Buttons */
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all .2s !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--gold) !important;
        border-color: var(--gold) !important;
        color: var(--white) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--gold-dark) !important;
        border-color: var(--gold-dark) !important;
    }
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
    current     = st.session_state.get("pf_step", "landing")
    idx_current = _STEPS_ORDER.index(current) if current in _STEPS_ORDER else 0
    steps_html  = ""
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
        "pf_days_per_week": 5,
        "pf_roadmap_courses": [],
        "pf_completed_courses": set(),
        "pf_cert_verify": {},
        "pf_work_entries": [{"id": 0}],
        "pf_work_counter": 1,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — MANUAL INPUT FORM  render_manual_input_form()
# ══════════════════════════════════════════════════════════════════════════════

def render_manual_input_form(majors_list: list, job_titles_list: list) -> dict:
    """
    Pure UI form: accepts DB-backed option lists as arguments.
    Returns dict of collected form values.
    """
    major_opts = ["— Select or type below —"] + majors_list + ["Other / Not listed"]
    title_opts = ["— Select or type below —"] + job_titles_list + ["Other / Not listed"]

    col1, col2, col3 = st.columns([1, 1.2, 1], gap="large")

    # ── COL 1 · Identity & Education ─────────────────────────────────────────
    with col1:
        st.markdown('<div class="section-label">🎓 Education</div>', unsafe_allow_html=True)
        full_name = st.text_input("FULL NAME", placeholder="e.g. Budi Santoso",
                                  key="pf_fn")
        edu_level = st.selectbox(
            "EDUCATION LEVEL",
            ["High School Diploma", "Associate Degree (D3)",
             "Bachelor's Degree (S1)", "Master's Degree (S2)",
             "Doctorate (S3)", "Other"],
            key="pf_edu"
        )
        major_sel = st.selectbox("MAJOR / FIELD OF STUDY", major_opts, key="pf_major_sel")
        if major_sel in ("— Select or type below —", "Other / Not listed"):
            major = st.text_input("Specify major", placeholder="e.g. Teknik Informatika",
                                  key="pf_major_txt")
        else:
            major = major_sel
        institution = st.text_input("INSTITUTION NAME",
                                    placeholder="e.g. Universitas Padjadjaran",
                                    key="pf_inst")

    # ── COL 2 · Work Experience ───────────────────────────────────────────────
    with col2:
        hdr_l, hdr_r = st.columns([3, 1])
        with hdr_l:
            st.markdown('<div class="section-label">💼 Work Experience</div>',
                        unsafe_allow_html=True)
        with hdr_r:
            st.markdown(
                '<div style="text-align:right;padding-top:.15rem;">'
                '<span style="font-size:.75rem;color:#9CA3AF;cursor:pointer;">+ Add</span>'
                '</div>', unsafe_allow_html=True)

        entries = st.session_state["pf_work_entries"]
        for idx, entry in enumerate(entries):
            eid = entry["id"]
            st.markdown('<div class="work-entry-shell">', unsafe_allow_html=True)
            job_sel = st.selectbox(f"JOB TITLE #{idx+1}", title_opts,
                                   key=f"pf_job_sel_{eid}")
            if job_sel in ("— Select or type below —", "Other / Not listed"):
                st.text_input("Specify title", placeholder="e.g. Data Analyst",
                              key=f"pf_job_txt_{eid}")
            st.text_input("COMPANY NAME", placeholder="e.g. PT Tokopedia",
                          key=f"pf_co_{eid}")
            st.selectbox("DURATION",
                         ["Less than 1 year", "1–3 years", "3–5 years", "5+ years"],
                         key=f"pf_dur_{eid}")
            st.text_area("KEY RESPONSIBILITIES",
                         placeholder="Briefly describe your main responsibilities...",
                         height=72, key=f"pf_resp_{eid}")
            st.markdown('</div>', unsafe_allow_html=True)

            if len(entries) > 1:
                if st.button("✕ Remove this entry", key=f"pf_rm_{eid}",
                             use_container_width=True):
                    st.session_state["pf_work_entries"] = [
                        e for e in entries if e["id"] != eid
                    ]
                    st.rerun()

        if st.button("＋ Add Another Experience", use_container_width=True,
                     key="pf_add_exp"):
            new_id = st.session_state["pf_work_counter"]
            st.session_state["pf_work_entries"].append({"id": new_id})
            st.session_state["pf_work_counter"] += 1
            st.rerun()

    # ── COL 3 · Skills & Upload ───────────────────────────────────────────────
    with col3:
        st.markdown('<div class="section-label">🛠 Skills You Have</div>',
                    unsafe_allow_html=True)
        raw_skills = st.text_input(
            "SKILLS",
            placeholder="Type a skill and press Enter, e.g. Python, SQL, Figma",
            key="pf_skills_raw"
        )
        # Live chip preview
        if raw_skills.strip():
            chips = [s.strip() for s in raw_skills.split(",") if s.strip()]
            chips_html = "".join(f'<span class="skill-chip">{c}</span>' for c in chips)
            st.markdown(f'<div style="margin:.4rem 0 .8rem;">{chips_html}</div>',
                        unsafe_allow_html=True)
            st.caption(f"{len(chips)} skill(s) detected")

        st.markdown('<div class="section-label" style="margin-top:1rem;">'
                    '📎 Upload Certificates (Optional)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="dashed-box" style="padding:1.25rem .75rem;">
          <div style="font-size:1.8rem;margin-bottom:.35rem;">⬆️</div>
          <div style="font-size:.8rem;color:#9CA3AF;margin-bottom:.5rem;">
            Drop PDF, PNG or JPG files here
          </div>
        </div>
        """, unsafe_allow_html=True)
        cert_files = st.file_uploader(
            "Drop certificate files here", type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True, label_visibility="collapsed",
            key="pf_cert_files"
        )
        if cert_files:
            for cf in cert_files:
                st.markdown(
                    f'<span class="skill-chip has">✓ {cf.name}</span>',
                    unsafe_allow_html=True
                )
        cert_text = st.text_area(
            "Or list certifications manually",
            placeholder="AWS Certified Developer (2023)\nGoogle UX Certificate",
            height=72, key="pf_cert_text"
        )

    # ── Analyze button (gold, below columns) ──────────────────────────────────
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([0, 1, 3])
    with btn_col:
        analyze_clicked = st.button(
            "🔍  Analyze Now", type="primary",
            use_container_width=True, key="pf_analyze_manual"
        )

    return {
        "full_name":     full_name,
        "edu_level":     edu_level,
        "major":         major,
        "institution":   institution,
        "raw_skills":    raw_skills,
        "cert_text":     cert_text,
        "analyze_clicked": analyze_clicked,
    }

def _build_cv_text(form_data: dict) -> str:
    entries = st.session_state.get("pf_work_entries", [])
    lines = [
        f"Name: {form_data['full_name']}",
        f"Education: {form_data['edu_level']} in {form_data['major']} at {form_data['institution']}",
        "", "Work Experience:",
    ]
    for entry in entries:
        eid = entry["id"]
        sel = st.session_state.get(f"pf_job_sel_{eid}", "")
        if sel in ("— Select or type below —", "Other / Not listed"):
            title = st.session_state.get(f"pf_job_txt_{eid}", "")
        else:
            title = sel
        company = st.session_state.get(f"pf_co_{eid}", "")
        dur     = st.session_state.get(f"pf_dur_{eid}", "")
        resp    = st.session_state.get(f"pf_resp_{eid}", "")
        if title:
            lines.append(f"  - {title} at {company} ({dur}): {resp}")
    lines += ["", "Skills:"]
    for sk in form_data.get("raw_skills", "").split(","):
        if sk.strip():
            lines.append(f"  - {sk.strip()}")
    lines += ["", "Certifications:"]
    for line in form_data.get("cert_text", "").splitlines():
        if line.strip():
            lines.append(f"  - {line.strip()}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — RESULTS GRID  render_results_grid()
# ══════════════════════════════════════════════════════════════════════════════

def render_results_grid(matches: list, detected_skills: list) -> str | None:
    """
    Pure UI — renders 4-column career match grid.
    Returns the soc_code of the profession the user selected, or None.
    """
    # ── Skill chips bar ───────────────────────────────────────────────────────
    st.markdown('<h2 style="font-size:1.6rem;font-weight:800;color:#111827;margin-bottom:.3rem;">'
                'Professions most suited for you</h2>', unsafe_allow_html=True)
    if detected_skills:
        chips_html = "".join(
            f'<span class="skill-chip has">✔ {s}</span>'
            for s in detected_skills[:12]
        )
        st.markdown(f'<div style="margin-bottom:1.25rem;line-height:2.2;">{chips_html}</div>',
                    unsafe_allow_html=True)

    selected_soc = None
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    cols = [col1, col2, col3, col4]

    card_defs = []
    for i, match in enumerate(matches[:3]):
        soc       = match.get("soc_code", "")
        total_hrs = match.get("total_course_hours") or get_total_hours(soc)
        score     = match.get("match_score", 0)
        gap_count = len(match.get("skill_gaps", []))
        card_defs.append({
            "match": match, "soc": soc, "total_hrs": total_hrs,
            "score": score, "gap_count": gap_count,
        })

    ordinals = ["01", "02", "03"]

    for i, cd in enumerate(card_defs):
        match     = cd["match"]
        soc       = cd["soc"]
        total_hrs = cd["total_hrs"]
        score     = cd["score"]
        gap_count = cd["gap_count"]
        is_best   = (i == 0)

        with cols[i]:
            # Card shell via HTML
            card_cls   = "best-match-card" if is_best else "custom-card"
            badge_html = ('<span class="gold-badge">⭐ Best Match</span>'
                          if is_best else "")
            title_color = "#B48E4B" if is_best else "#374151"
            st.markdown(f"""
            <div class="{card_cls}">
              {badge_html}
              <div class="card-number">{ordinals[i]}</div>
              <div class="prof-title" style="color:{title_color};">
                {match.get('title','')}
              </div>
              <div class="soc-code">SOC {soc}</div>
            </div>
            """, unsafe_allow_html=True)

            # Native progress bar (Streamlit renders it between HTML blocks)
            st.progress(score / 100)

            st.markdown(f"""
            <div class="card-metrics">
              <span>Gap: <strong>{gap_count} skills</strong></span>
              <span>Roadmap: <strong>~{int(total_hrs)} hrs</strong></span>
            </div>
            """, unsafe_allow_html=True)

            # Skill gap pills
            gaps = match.get("skill_gaps", [])
            if gaps:
                pills = "".join(f'<span class="skill-chip gap">{g}</span>'
                                for g in gaps[:4])
                st.markdown(f'<div style="margin:.6rem 0;">{pills}</div>',
                            unsafe_allow_html=True)

            st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

            # Select button — primary for best, secondary for others
            btn_type = "primary" if is_best else "secondary"
            if st.button("Select", key=f"pf_sel_{i}",
                         use_container_width=True, type=btn_type):
                st.session_state["pf_selected_match"] = {
                    **match,
                    "total_course_hours": total_hrs,
                    "courses": match.get("courses") or get_courses_for_onet(soc),
                    "match_ratio": score / 100,
                }
                st.session_state["pf_roadmap_courses"] = (
                    match.get("courses") or get_courses_for_onet(soc)
                )
                selected_soc = soc

    # ── Col 4 · Manual add ────────────────────────────────────────────────────
    with col4:
        all_onet = get_all_onet_titles()
        st.markdown("""
        <div class="dashed-box">
          <div style="font-size:2rem;margin-bottom:.4rem;color:#CBD5E1;">＋</div>
          <div style="font-weight:600;color:#374151;margin-bottom:.25rem;font-size:.9rem;">
            Add a profession you're interested in
          </div>
          <div style="font-size:.78rem;color:#9CA3AF;">
            Browse O*NET roles to add a custom target
          </div>
        </div>
        """, unsafe_allow_html=True)

        custom_t = st.selectbox("Search profession", ["—"] + all_onet,
                                placeholder="e.g. UX Designer",
                                key="pf_custom_onet")
        if custom_t and custom_t != "—":
            soc = get_soc_for_title(custom_t)
            if soc:
                hrs = get_total_hours(soc)
                st.caption(f"📚 ~{int(hrs)} study hours")

        if st.button("＋ Add Profession", key="pf_add_custom",
                     use_container_width=True):
            if custom_t and custom_t != "—":
                soc = get_soc_for_title(custom_t)
                if soc:
                    hrs     = get_total_hours(soc)
                    courses = get_courses_for_onet(soc)
                    detected = (st.session_state.get("pf_analysis") or {}).get("detected_skills", [])
                    gaps     = _compute_skill_gaps(soc, detected)
                    st.session_state["pf_selected_match"] = {
                        "soc_code": soc, "title": custom_t,
                        "description": "Manually selected profession from O*NET catalog.",
                        "matched_skills": [], "skill_gaps": gaps,
                        "match_score": 50,
                        "total_course_hours": hrs, "courses": courses,
                        "match_ratio": 0.5,
                    }
                    st.session_state["pf_roadmap_courses"] = courses
                    selected_soc = soc

    return selected_soc

# ══════════════════════════════════════════════════════════════════════════════
# PAGE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _render_upload():
    st.markdown("""
    <div style="margin-bottom:1.25rem;">
      <h2 style="font-size:1.6rem;font-weight:800;color:#111827;margin:0 0 .2rem;">
        Analyze Your Profile
      </h2>
      <p style="color:#6B7280;font-size:.9rem;margin:0;">
        Upload your CV or fill in the form below — analyzed by Gemini AI
        against O*NET &amp; SKKNI.
      </p>
    </div>
    """, unsafe_allow_html=True)

    tab_pdf, tab_manual = st.tabs(["📄  Upload PDF", "✏️  Enter Manually"])

    with tab_pdf:
        uploaded = st.file_uploader("Upload your CV (PDF)", type=["pdf"],
                                    key="pf_pdf_upload", label_visibility="collapsed")
        if uploaded:
            st.success(f"✓ {uploaded.name} loaded")
            if st.button("Analyze CV", type="primary",
                         use_container_width=True, key="pf_analyze_pdf"):
                try:
                    cv_text = extract_pdf_text(uploaded.read())
                    if not cv_text.strip():
                        st.error("Could not extract text. Try the manual form.")
                    else:
                        result = _run_with_loading(_call_gemini, cv_text)
                        st.session_state["pf_analysis"] = result
                        upsert_user_profile(st.session_state["pf_session_id"],
                                            cv_text=cv_text)
                        st.session_state["pf_step"] = "results"
                        st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    with tab_manual:
        form = render_manual_input_form(get_all_majors(), get_all_onet_titles())
        if form["analyze_clicked"]:
            if not form["full_name"].strip():
                st.warning("Please enter your full name.")
            elif not form["raw_skills"].strip():
                st.warning("Please enter at least one skill.")
            else:
                cv_text = _build_cv_text(form)
                try:
                    result     = _run_with_loading(_call_gemini, cv_text)
                    session_id = st.session_state["pf_session_id"]
                    skills_list = [s.strip() for s in form["raw_skills"].split(",") if s.strip()]
                    st.session_state["pf_analysis"] = result
                    upsert_user_profile(session_id, full_name=form["full_name"],
                                        education=form["edu_level"], major=form["major"],
                                        institution=form["institution"], cv_text=cv_text)
                    upsert_user_skills(session_id, skills_list)
                    st.session_state["pf_step"] = "results"
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    st.markdown("---")
    if st.button("← Back to Home"):
        st.session_state["pf_step"] = "landing"
        st.rerun()


def _render_results():
    analysis = st.session_state.get("pf_analysis")
    if not analysis:
        st.session_state["pf_step"] = "upload"
        st.rerun()

    matches         = analysis.get("top_matches", [])
    detected_skills = analysis.get("detected_skills", [])
    candidate       = analysis.get("candidate_name", "Candidate")

    st.markdown(f'<p style="color:#6B7280;font-size:.85rem;margin-bottom:.5rem;">'
                f'Results for <strong>{candidate}</strong></p>',
                unsafe_allow_html=True)

    selected_soc = render_results_grid(matches, detected_skills)

    if selected_soc:
        st.session_state["pf_step"] = "skill_gap"
        st.rerun()

    st.markdown("---")
    if st.button("← Retake Analysis"):
        st.session_state["pf_step"] = "upload"
        st.session_state["pf_analysis"] = None
        st.rerun()


def _render_skill_gap():
    match    = st.session_state.get("pf_selected_match", {})
    analysis = st.session_state.get("pf_analysis", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    detected = (analysis or {}).get("detected_skills", [])
    gaps     = match.get("skill_gaps", [])
    score    = match.get("match_score", 50)

    st.markdown(f"""
    <h2 style="font-size:1.6rem;font-weight:800;color:#111827;margin:0 0 .2rem;">
      Skill Gap Analysis
    </h2>
    <p style="color:#6B7280;font-size:.9rem;margin:0 0 1.25rem;">
      Target role: <strong>{match.get('title','')}</strong>
      &nbsp;·&nbsp; Match score: <strong>{score}%</strong>
    </p>
    """, unsafe_allow_html=True)

    col_have, col_gap = st.columns(2, gap="large")
    with col_have:
        st.markdown('<div class="section-label">✅ Skills You Have</div>',
                    unsafe_allow_html=True)
        if detected:
            chips = "".join(f'<span class="skill-chip has">{s}</span>' for s in detected)
            st.markdown(f'<div style="line-height:2.2;">{chips}</div>',
                        unsafe_allow_html=True)
        else:
            st.info("No skills detected from your profile.")
    with col_gap:
        st.markdown('<div class="section-label">🔴 Skills to Acquire</div>',
                    unsafe_allow_html=True)
        if gaps:
            chips = "".join(f'<span class="skill-chip gap">{g}</span>' for g in gaps)
            st.markdown(f'<div style="line-height:2.2;">{chips}</div>',
                        unsafe_allow_html=True)
        else:
            st.success("No significant skill gaps detected!")

    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
    st.progress(score / 100)
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Matches", use_container_width=True):
            st.session_state["pf_step"] = "results"
            st.rerun()
    with c2:
        if st.button("Create Study Plan →", type="primary", use_container_width=True):
            st.session_state["pf_step"] = "choose_plan"
            st.rerun()


def _render_choose_plan():
    match = st.session_state.get("pf_selected_match", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    soc       = match.get("soc_code", "")
    total_hrs = match.get("total_course_hours") or get_total_hours(soc) or \
                sum(c.get("hours", 0) for c in match.get("courses", []))

    st.markdown("""
    <h2 style="font-size:1.6rem;font-weight:800;color:#111827;margin:0 0 .2rem;">
      Choose Your Study Plan
    </h2>
    <p style="color:#6B7280;font-size:.9rem;margin:0 0 1.25rem;">
      Set your daily commitment and pick a study cadence.
    </p>
    """, unsafe_allow_html=True)

    hours_pd = st.slider("⏱ Hours per day", 1, 8,
                         st.session_state.get("pf_study_hours_per_day", 2),
                         key="pf_hrs_slider")
    st.session_state["pf_study_hours_per_day"] = hours_pd
    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

    plans = [
        {"id": "intensive", "name": "Fast Track",  "days": 7, "icon": "🔥",
         "desc": "Every day — maximum speed"},
        {"id": "balanced",  "name": "Regular",     "days": 5, "icon": "⚖️",
         "desc": "Weekdays only — recommended"},
        {"id": "casual",    "name": "Flexible",    "days": 3, "icon": "🌱",
         "desc": "3 days/week — relaxed pace"},
    ]
    pcols = st.columns(3, gap="large")
    for plan, pcol in zip(plans, pcols):
        weekly  = hours_pd * plan["days"]
        weeks   = math.ceil(total_hrs / weekly) if (total_hrs and weekly) else 0
        end_d   = (datetime.date.today() + datetime.timedelta(weeks=weeks)).strftime("%b %Y")
        sel     = st.session_state.get("pf_selected_plan") == plan["id"]
        bdr     = "border:2px solid #B48E4B;" if sel else "border:1px solid #E5E7EB;"

        with pcol:
            st.markdown(f"""
            <div class="custom-card" style="{bdr}text-align:center;padding:1.5rem;">
              <div style="font-size:2.2rem;">{plan['icon']}</div>
              <div style="font-weight:700;font-size:1rem;margin:.5rem 0 .2rem;">{plan['name']}</div>
              <div style="font-size:.82rem;color:#6B7280;margin-bottom:.9rem;">{plan['desc']}</div>
              <div style="font-size:1.7rem;font-weight:800;color:#B48E4B;">{weeks} wks</div>
              <div style="font-size:.75rem;color:#9CA3AF;">
                {plan['days']} days/wk · {hours_pd}h/day · done {end_d}
              </div>
            </div>
            """, unsafe_allow_html=True)
            btype = "primary" if sel else "secondary"
            if st.button(f"{'✓ ' if sel else ''}Choose {plan['name']}",
                         key=f"pf_plan_{plan['id']}",
                         use_container_width=True, type=btype):
                st.session_state["pf_selected_plan"]       = plan["id"]
                st.session_state["pf_days_per_week"]       = plan["days"]
                st.session_state["pf_study_hours_per_day"] = hours_pd
                st.session_state["pf_roadmap_courses"] = generate_verified_roadmap(
                    [soc], plan["id"])
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


@st.dialog("Submit Verification", width="small")
def _verify_dialog(course: dict):
    cid   = str(course.get("course_id", course.get("title", "")))
    title = course.get("title", "")
    st.markdown(f"**{title}**")
    st.caption(f"Provider: {course.get('provider','')}")
    url_val = st.text_input(
        "Paste your certificate URL (Coursera / edX / LinkedIn / other)",
        placeholder="https://coursera.org/verify/XXXXXXXXX",
        key=f"pf_vinput_{cid}"
    )
    col_ok, col_cancel = st.columns(2)
    with col_ok:
        if st.button("Submit", type="primary", use_container_width=True, key=f"pf_vsub_{cid}"):
            if url_val.strip().startswith("http"):
                cv = st.session_state.setdefault("pf_cert_verify", {})
                cv[cid] = {"url": url_val.strip(), "verified": True}
                st.session_state["pf_cert_verify"] = cv
                try:
                    verify_user_skill(st.session_state.get("pf_session_id",""),
                                      title, url_val.strip())
                except Exception:
                    pass
                st.rerun()
            else:
                st.error("Enter a valid URL starting with http.")
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key=f"pf_vcan_{cid}"):
            st.rerun()


def _render_roadmap():
    match    = st.session_state.get("pf_selected_match", {})
    hours_pd = st.session_state.get("pf_study_hours_per_day", 2)
    done_set = st.session_state.get("pf_completed_courses", set())
    cv_map   = st.session_state.get("pf_cert_verify", {})

    if not match:
        st.session_state["pf_step"] = "choose_plan"
        st.rerun()

    soc     = match.get("soc_code", "")
    courses = st.session_state.get("pf_roadmap_courses") or generate_verified_roadmap([soc])
    if not courses:
        courses = get_courses_for_onet(soc)
    st.session_state["pf_roadmap_courses"] = courses

    st.markdown(f"""
    <h2 style="font-size:1.6rem;font-weight:800;color:#111827;margin:0 0 .2rem;">
      Your Custom Learning Roadmap
    </h2>
    <p style="color:#6B7280;font-size:.88rem;margin:0 0 1rem;">
      {match.get('title','')} &nbsp;·&nbsp;
      All course links are from our verified database.
    </p>
    """, unsafe_allow_html=True)

    if courses:
        total_hrs = sum(c.get("hours", 0) for c in courses)
        done_hrs  = sum(c.get("hours", 0) for c in courses
                        if str(c.get("course_id", c.get("title",""))) in done_set
                        or c.get("title","") in done_set)
        pct = int(done_hrs / total_hrs * 100) if total_hrs else 0
        st.markdown(f"**{pct}% complete** — {int(done_hrs)}/{int(total_hrs)} hours")
        st.progress(pct / 100)
        st.markdown("---")

        cumday = 0
        for i, course in enumerate(courses):
            cid      = str(course.get("course_id", course.get("title", i)))
            title    = course.get("title", "")
            hrs      = course.get("hours", 0)
            days_n   = math.ceil(hrs / max(hours_pd, 1))
            verified = cv_map.get(cid, {}).get("verified", False)
            done     = cid in done_set or title in done_set

            dot_bg    = "#DCFCE7" if (done or verified) else "#DBEAFE"
            dot_color = "#15803D" if (done or verified) else "#1D4ED8"

            st.markdown(f"""
            <div class="pf-timeline-item">
              <div class="pf-timeline-dot" style="background:{dot_bg};color:{dot_color};">
                {'✓' if (done or verified) else i+1}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;color:#111827;">{title}</div>
                <div style="font-size:.78rem;color:#6B7280;">
                  {course.get('provider','')} &nbsp;·&nbsp; {int(hrs)}h
                  &nbsp;·&nbsp; ~{days_n} days (starts day {cumday+1})
                </div>
                {('<div style="font-size:.72rem;color:#15803D;margin-top:.2rem;">✓ Certificate submitted</div>' if verified else '')}
              </div>
            </div>
            """, unsafe_allow_html=True)

            ca, cb, cc = st.columns([3, 1, 1])
            with cb:
                if course.get("url") and not verified:
                    st.link_button("Go to Course →", course["url"], use_container_width=True)
            with cc:
                if verified:
                    st.markdown('<span class="skill-chip has">✅ Verified</span>',
                                unsafe_allow_html=True)
                elif done:
                    if st.button("Verify Cert", key=f"pf_vbtn_{i}", use_container_width=True):
                        _verify_dialog(course)
                else:
                    if st.button("Mark Done", key=f"pf_done_{i}", use_container_width=True):
                        done_set.add(cid)
                        done_set.add(title)
                        st.session_state["pf_completed_courses"] = done_set
                        st.rerun()
            cumday += days_n
    else:
        st.info("No courses found. Choose a plan first.")

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


@st.dialog("Study Planner", width="large")
def _study_planner_dialog():
    match     = st.session_state.get("pf_selected_match", {})
    courses   = st.session_state.get("pf_roadmap_courses", [])
    soc       = match.get("soc_code", "")
    total_hrs = (match.get("total_course_hours") or
                 sum(c.get("hours", 0) for c in courses) or
                 get_total_hours(soc))

    st.markdown(f"### {match.get('title','')} — Personalized Schedule")

    hours_pd = st.slider("Study hours per day", 1, 8,
                         st.session_state.get("pf_study_hours_per_day", 2),
                         key="pf_dlg_hrs")
    dpw_map   = {"Every day (7)": 7, "Weekdays (5)": 5, "3 days/week": 3}
    dpw_label = st.selectbox("Days per week", list(dpw_map.keys()), key="pf_dlg_dpw")
    dpw       = dpw_map[dpw_label]
    st.session_state["pf_study_hours_per_day"] = hours_pd
    st.session_state["pf_days_per_week"]       = dpw

    weekly_hrs  = hours_pd * dpw
    total_weeks = math.ceil(total_hrs / weekly_hrs) if (total_hrs and weekly_hrs) else 0
    end_date    = datetime.date.today() + datetime.timedelta(weeks=total_weeks)

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total Hours",  f"{int(total_hrs)}h")
    mc2.metric("Duration",     f"{total_weeks} weeks")
    mc3.metric("Finish By",    end_date.strftime("%b %d, %Y"))

    st.markdown("---")
    st.markdown("#### Certificate Verification")
    cv_map = st.session_state.setdefault("pf_cert_verify", {})

    for course in courses:
        cid     = str(course.get("course_id", course.get("title", "")))
        title   = course.get("title", "")
        v_state = cv_map.get(cid, {"url": "", "verified": False})

        col_t, col_icon = st.columns([4, 1])
        with col_t:
            st.markdown(f"**{title}**  \n_{course.get('provider','')}_")
        with col_icon:
            icon = "✅" if v_state["verified"] else "✗"
            color = "#15803D" if v_state["verified"] else "#DC2626"
            st.markdown(f'<div style="font-size:1.35rem;color:{color};text-align:center;'
                        f'padding-top:.4rem;">{icon}</div>', unsafe_allow_html=True)

        new_url = st.text_input("Certificate URL", value=v_state["url"],
                                key=f"pf_dlg_url_{cid}",
                                placeholder="https://coursera.org/verify/...")
        v_state["url"] = new_url
        if st.button("Verify", key=f"pf_dlg_v_{cid}"):
            if new_url.strip().startswith("http"):
                v_state["verified"] = True
                cv_map[cid] = v_state
                st.session_state["pf_cert_verify"] = cv_map
                try:
                    verify_user_skill(st.session_state.get("pf_session_id",""),
                                      title, new_url.strip())
                except Exception:
                    pass
                st.success("✓ Verified!")
                st.rerun()
            else:
                st.error("Enter a valid URL.")
        else:
            cv_map[cid] = v_state
            st.session_state["pf_cert_verify"] = cv_map
        st.markdown("---")

    if st.button("Close Planner", use_container_width=True):
        st.rerun()


def _render_dashboard():
    match    = st.session_state.get("pf_selected_match", {})
    courses  = st.session_state.get("pf_roadmap_courses", [])
    done_set = st.session_state.get("pf_completed_courses", set())
    hours_pd = st.session_state.get("pf_study_hours_per_day", 2)
    dpw      = st.session_state.get("pf_days_per_week", 5)
    cv_map   = st.session_state.get("pf_cert_verify", {})

    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    soc       = match.get("soc_code", "")
    total_hrs = (match.get("total_course_hours") or
                 sum(c.get("hours", 0) for c in courses) or
                 get_total_hours(soc))
    done_hrs  = sum(c.get("hours", 0) for c in courses
                    if str(c.get("course_id", c.get("title",""))) in done_set
                    or c.get("title","") in done_set)
    remain    = max(0, total_hrs - done_hrs)
    pct       = int(done_hrs / total_hrs * 100) if total_hrs else 0
    weekly_h  = hours_pd * dpw
    wks_left  = math.ceil(remain / weekly_h) if (remain and weekly_h) else 0
    verified_n = sum(1 for v in cv_map.values() if v.get("verified"))

    st.markdown(f"""
    <h2 style="font-size:1.6rem;font-weight:800;color:#111827;margin:0 0 1rem;">
      Dashboard — {match.get('title','')}
    </h2>
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, f"{pct}%",           "Overall Progress"),
        (s2, f"{int(done_hrs)}h", "Hours Completed"),
        (s3, f"{wks_left}w",      "Weeks Remaining"),
        (s4, str(verified_n),     "Certs Verified"),
    ]:
        with col:
            st.markdown(f"""
            <div class="pf-stat">
              <div class="pf-stat-num">{num}</div>
              <div class="pf-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
    st.progress(pct / 100)
    st.caption(f"{pct}% — {int(done_hrs)}/{int(total_hrs)} hours completed")
    st.markdown("---")
    st.markdown("#### Course Status")

    for course in courses:
        cid      = str(course.get("course_id", course.get("title","")))
        done     = cid in done_set or course.get("title","") in done_set
        verified = cv_map.get(cid, {}).get("verified", False)
        if verified:
            badge = '<span class="skill-chip has">✅ Verified</span>'
        elif done:
            badge = '<span class="skill-chip" style="background:#DBEAFE;color:#1D4ED8;">✓ Completed</span>'
        else:
            badge = '<span class="skill-chip">Pending</span>'
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:.6rem 0;border-bottom:1px solid #F3F4F6;">
          <div>
            <span style="font-weight:500;color:#111827;">{course.get('title','')}</span>
            <span style="font-size:.73rem;color:#9CA3AF;margin-left:.5rem;">
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
        if st.button("📅 Open Study Planner", type="primary", use_container_width=True):
            _study_planner_dialog()
    with c3:
        if st.button("🔄 Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("pf_"):
                    del st.session_state[k]
            st.rerun()


def _render_landing():
    st.markdown("""
    <div class="pf-hero">
      <h1>Find Your <span>Career Path</span></h1>
      <p>AI-powered career guidance for Indonesian students — mapped to O*NET and SKKNI standards.</p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="large")
    features = [
        ("🤖", "AI Analysis",
         "Gemini AI analyzes your profile against O*NET taxonomy and Indonesian SKKNI frameworks."),
        ("🎯", "Career Matching",
         "Get 3 personalized career matches ranked by compatibility score."),
        ("📚", "Verified Roadmap",
         "Course links come exclusively from our verified database — no hallucinated URLs."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="custom-card" style="text-align:center;padding:1.5rem;">
              <div style="font-size:2rem;margin-bottom:.5rem;">{icon}</div>
              <div style="font-weight:700;font-size:.95rem;margin-bottom:.4rem;color:#374151;">
                {title}
              </div>
              <div style="font-size:.83rem;color:#6B7280;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Get Started →", type="primary",
                     use_container_width=True, key="pf_start"):
            st.session_state["pf_step"] = "upload"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Pathfinder — Career Guidance",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

get_db_engine()
_init_session()
apply_global_css()
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
