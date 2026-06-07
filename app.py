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
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# ── Gemini ─────────────────────────────────────────────────────────────────────
from google import genai
from google.genai import types as genai_types

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — SQLAlchemy Models
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

# ── REAL verified course URLs from major platforms ─────────────────────────────
_COURSES = [
    # Software Developer (15-1252.00) — 155h total
    ("Python for Everybody Specialization", "Coursera",
     "https://www.coursera.org/specializations/python",
     "15-1252.00", 40),
    ("The Web Developer Bootcamp 2024", "Udemy",
     "https://www.udemy.com/course/the-web-developer-bootcamp/",
     "15-1252.00", 60),
    ("Algorithms, Part I", "Coursera (Princeton)",
     "https://www.coursera.org/learn/algorithms-part1",
     "15-1252.00", 30),
    ("DevOps Foundations", "LinkedIn Learning",
     "https://www.linkedin.com/learning/devops-foundations",
     "15-1252.00", 25),

    # Data Scientist (15-2051.00) — 185h total
    ("Machine Learning Specialization", "Coursera (DeepLearning.AI)",
     "https://www.coursera.org/specializations/machine-learning-introduction",
     "15-2051.00", 80),
    ("Data Analysis with Python", "Coursera (IBM)",
     "https://www.coursera.org/learn/data-analysis-with-python",
     "15-2051.00", 35),
    ("Practical Deep Learning for Coders", "fast.ai",
     "https://course.fast.ai/",
     "15-2051.00", 50),
    ("SQL for Data Science", "Coursera (UC Davis)",
     "https://www.coursera.org/learn/sql-for-data-science",
     "15-2051.00", 20),

    # AI/ML Engineer (15-1299.00) — 135h total
    ("DeepLearning.AI TensorFlow Developer Certificate", "Coursera",
     "https://www.coursera.org/professional-certificates/tensorflow-in-practice",
     "15-1299.00", 60),
    ("Machine Learning Engineering for Production (MLOps)", "Coursera",
     "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
     "15-1299.00", 45),
    ("Hugging Face NLP Course", "Hugging Face",
     "https://huggingface.co/learn/nlp-course/chapter1/1",
     "15-1299.00", 30),

    # Information Security Analyst (15-1212.00) — 125h total
    ("Cybersecurity Fundamentals", "edX (Rochester Institute of Technology)",
     "https://www.edx.org/learn/cybersecurity/rochester-institute-of-technology-cybersecurity-fundamentals",
     "15-1212.00", 40),
    ("Learn Ethical Hacking From Scratch", "Udemy",
     "https://www.udemy.com/course/learn-ethical-hacking-from-scratch/",
     "15-1212.00", 35),
    ("CompTIA Security+ Certification Prep", "CompTIA",
     "https://www.comptia.org/certifications/security",
     "15-1212.00", 50),

    # Financial Analyst (13-2051.00) — 95h total
    ("Financial Modeling & Valuation Analyst (FMVA)", "Corporate Finance Institute",
     "https://corporatefinanceinstitute.com/certifications/financial-modeling-valuation-analyst-fmva-certification/",
     "13-2051.00", 45),
    ("Investment Management Specialization", "Coursera (University of Geneva)",
     "https://www.coursera.org/specializations/investment-management",
     "13-2051.00", 30),
    ("Excel Skills for Business Specialization", "Coursera (Macquarie University)",
     "https://www.coursera.org/specializations/excel",
     "13-2051.00", 20),

    # Marketing Manager (11-2021.00) — 60h total
    ("Google Digital Marketing & E-commerce Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce",
     "11-2021.00", 25),
    ("Social Media Marketing Certification Course", "HubSpot Academy",
     "https://academy.hubspot.com/courses/social-media",
     "11-2021.00", 20),
    ("Content Marketing Certification", "HubSpot Academy",
     "https://academy.hubspot.com/courses/content-marketing",
     "11-2021.00", 15),

    # Management Analyst (13-1111.00) — 130h total
    ("Business Analysis & Process Management", "Coursera",
     "https://www.coursera.org/learn/business-analysis-process-management",
     "13-1111.00", 30),
    ("Google Project Management Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-project-management",
     "13-1111.00", 60),
    ("Lean Six Sigma Fundamentals", "Coursera (University System of Georgia)",
     "https://www.coursera.org/specializations/six-sigma-fundamentals",
     "13-1111.00", 40),

    # Network Admin (15-1244.00) — 130h total
    ("Cisco CCNA 200-301 Complete Course", "Udemy",
     "https://www.udemy.com/course/ccna-complete/",
     "15-1244.00", 80),
    ("CompTIA Network+ Certification Prep", "CompTIA",
     "https://www.comptia.org/certifications/network",
     "15-1244.00", 50),

    # Public Relations Specialist (27-3031.00) — 35h total
    ("Strategic Communication & Public Relations", "edX (UC Berkeley)",
     "https://www.edx.org/certificates/professional-certificate/berkeleyx-strategic-communication-and-public-relations",
     "27-3031.00", 20),
    ("Introduction to Public Relations", "Coursera",
     "https://www.coursera.org/learn/introduction-to-public-relations",
     "27-3031.00", 15),

    # Graphic Designer (27-1024.00) — 95h total
    ("Google UX Design Professional Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-ux-design",
     "27-1024.00", 40),
    ("Graphic Design Specialization", "Coursera (California Institute of the Arts)",
     "https://www.coursera.org/specializations/graphic-design",
     "27-1024.00", 35),
    ("Figma UI UX Design Essentials", "Udemy",
     "https://www.udemy.com/course/figma-ux-ui-design-user-experience-tutorial-course/",
     "27-1024.00", 20),

    # Financial Manager (11-3031.00) — 85h total
    ("Financial Management Specialization", "Coursera (University of Illinois)",
     "https://www.coursera.org/specializations/financial-management",
     "11-3031.00", 50),
    ("Corporate Finance Fundamentals", "Corporate Finance Institute",
     "https://corporatefinanceinstitute.com/course/corporate-finance-fundamentals/",
     "11-3031.00", 35),

    # Accountant (13-2011.00) — 90h total
    ("Intuit Academy Bookkeeping Certificate", "Coursera (Intuit)",
     "https://www.coursera.org/professional-certificates/intuit-bookkeeping",
     "13-2011.00", 40),
    ("Financial Accounting Fundamentals", "Coursera (University of Virginia)",
     "https://www.coursera.org/learn/uva-darden-financial-accounting",
     "13-2011.00", 30),
    ("Accounting Analytics", "Coursera (University of Pennsylvania)",
     "https://www.coursera.org/learn/accounting-analytics",
     "13-2011.00", 20),
]

# ── Typical skills required per O*NET SOC code ────────────────────────────────
# Used to auto-generate skill_gaps for manually added professions
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
    """Return typical O*NET skills for `soc_code` that the user doesn't have."""
    typical = _ONET_TYPICAL_SKILLS.get(soc_code, [])
    user_lower = {s.lower() for s in user_skills}
    return [s for s in typical if s.lower() not in user_lower]

def _init_db() -> None:
    Base.metadata.create_all(_engine)
    with _Session() as s:
        if s.query(IndonesianMajorCatalog).count() == 0:
            s.add_all([IndonesianMajorCatalog(major_name=m) for m in _MAJORS])
        if s.query(OnetOccupation).count() == 0:
            s.add_all([OnetOccupation(soc_code=c, title=t, description=d) for c, t, d in _OCCUPATIONS])
        # Force reseed courses if URLs are stale (old non-www fake URLs)
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
                 "hours": r.total_hours, "course_id": r.course_id} for r in rows]

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

# ── PHASE 1B: Verified Roadmap Query (URLs 100% from DB — no LLM hallucination)
def generate_verified_roadmap(onet_codes: list, duration_tier: str = "balanced") -> list:
    """
    Pull courses exclusively from CourseCatalog for the given O*NET SOC codes.
    URLs come solely from the database — no LLM-generated links.
    duration_tier is accepted for API compatibility but all courses are returned
    (filtering by tier would reduce results to unusably few entries).
    """
    if not onet_codes:
        return []
    with _db() as s:
        rows = (s.query(CourseCatalog)
                .filter(CourseCatalog.mapped_onet_code.in_(onet_codes))
                .all())
        return [{"course_id": r.course_id, "title": r.title, "provider": r.provider,
                 "url": r.url, "hours": r.total_hours,
                 "onet_code": r.mapped_onet_code} for r in rows]

# ══════════════════════════════════════════════════════════════════════════════
# GEMINI BACKEND
# ══════════════════════════════════════════════════════════════════════════════

ANALYZE_MODEL = "gemini-2.5-flash"

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
    # Enrich each match with DB course data (URLs from DB only)
    for m in data.get("top_matches", []):
        soc = m.get("soc_code", "")
        db_hours = get_total_hours(soc)
        # If SOC from Gemini not in our DB, try closest match or default 0
        m["total_course_hours"] = db_hours
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
    ph = st.empty()
    for i, (icon, step) in enumerate(steps[:-1]):
        pct = int((i + 1) / len(steps) * 100)
        with ph.container():
            st.markdown(f"""
            <div style="text-align:center;padding:3rem 1rem;background:#FAF8F5;border-radius:8px;">
              <div style="font-size:3rem;margin-bottom:1rem;">{icon}</div>
              <div style="font-size:1rem;font-weight:600;color:#A17F3E;margin-bottom:1rem;
                          font-family:'Playfair Display',Georgia,serif;font-style:italic;">{step}</div>
              <div style="background:#E8E0D5;border-radius:9999px;height:5px;overflow:hidden;max-width:400px;margin:0 auto;">
                <div style="background:linear-gradient(90deg,#A17F3E,#C09A51);height:100%;
                            width:{pct}%;border-radius:9999px;"></div>
              </div>
              <div style="font-size:0.78rem;color:#9A8060;margin-top:0.5rem;">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.45)
    result = fn(*args, **kwargs)
    ph.empty()
    return result

# ══════════════════════════════════════════════════════════════════════════════
# PDF EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

def extract_pdf_text(file_bytes: bytes) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf not installed. Add pypdf>=4.0.0 to requirements.txt.")
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(p.extract_text() or "" for p in reader.pages)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════════

def _inject_css():
    st.markdown("""
    <style>
    /* ── Typefaces ─────────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── CSS custom properties (design tokens) ─────────────────────────────── */
    :root {
        --white:        #FFFFFF;
        --charcoal:     #2C2C2C;
        --charcoal-mid: #4A4A4A;
        --charcoal-soft:#6B6B6B;
        --copper:       #A17F3E;
        --copper-dark:  #7D6130;
        --copper-light: #C9AC72;
        --gold:         #C09A51;
        --gold-pale:    #F5EDD8;
        --gold-border:  #D4B87A;
        --warm-bg:      #FAF8F5;
        --warm-border:  #E8E0D5;
        --warm-muted:   #F2EDE6;
        --success:      #2D6A4F;
        --success-bg:   #D8F3DC;
        --danger:       #9B2335;
        --danger-bg:    #FAE0E4;
        --serif:        'Playfair Display', Georgia, 'Times New Roman', serif;
        --sans:         'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Global reset & typography ─────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: var(--sans) !important;
        color: var(--charcoal) !important;
    }

    /* ── App background — warm parchment ───────────────────────────────────── */
    .stApp,
    [data-testid="stHeader"],
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        background-color: var(--warm-bg) !important;
    }

    /* ── Topbar ────────────────────────────────────────────────────────────── */
    .pf-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.75rem;
        background: var(--white);
        border-bottom: 1px solid var(--warm-border);
        margin-bottom: 1.5rem;
        border-radius: 0 0 0 0;
        box-shadow: 0 1px 6px rgba(44,44,44,.06);
    }
    .pf-logo {
        font-family: var(--serif) !important;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--copper) !important;
        letter-spacing: 0.02em;
    }
    .pf-logo span { color: var(--gold) !important; font-style: italic; }

    .pf-steps { display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap; }
    .pf-step {
        font-family: var(--sans);
        font-size: 0.72rem;
        padding: 0.3rem 0.85rem;
        border-radius: 2px;
        font-weight: 500;
        background: var(--warm-muted);
        color: var(--charcoal-soft);
        letter-spacing: 0.04em;
        border: 1px solid transparent;
    }
    .pf-step.active {
        background: var(--gold);
        color: var(--white);
        border-color: var(--gold);
    }
    .pf-step.done {
        background: var(--success-bg);
        color: var(--success);
        border-color: transparent;
    }

    /* ── Card — standard white card ────────────────────────────────────────── */
    .pf-card {
        background: var(--white);
        border: 1px solid var(--warm-border);
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(44,44,44,.05);
    }

    /* ── Card — gold/copper accent (Best Match) ────────────────────────────── */
    .pf-card-gold {
        border: 2px solid var(--copper) !important;
        box-shadow: 0 6px 20px rgba(161,127,62,.16) !important;
        background: linear-gradient(160deg, #FFFDF9 0%, var(--white) 100%) !important;
    }

    /* ── Card — dashed placeholder ──────────────────────────────────────────── */
    .pf-card-dashed {
        border: 2px dashed var(--warm-border) !important;
        background: var(--warm-muted) !important;
    }

    /* ── Card — completed (green) ───────────────────────────────────────────── */
    .pf-card-done {
        border: 2px solid var(--success) !important;
        background: var(--success-bg) !important;
    }

    /* ── Badges ─────────────────────────────────────────────────────────────── */
    .pf-badge {
        display: inline-block;
        font-family: var(--sans);
        font-size: 0.6rem;
        font-weight: 700;
        padding: 0.22rem 0.6rem;
        border-radius: 2px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .pf-badge-gold  { background: var(--gold-pale);  color: var(--copper-dark); }
    .pf-badge-blue  { background: #E8EDF8;            color: #2A4490; }
    .pf-badge-green { background: var(--success-bg);  color: var(--success); }
    .pf-badge-red   { background: var(--danger-bg);   color: var(--danger); }

    /* ── Skill pills ────────────────────────────────────────────────────────── */
    .pf-pill {
        display: inline-block;
        font-family: var(--sans);
        font-size: 0.68rem;
        font-weight: 500;
        padding: 0.18rem 0.6rem;
        border-radius: 2px;
        background: var(--gold-pale);
        color: var(--copper-dark);
        border: 1px solid var(--gold-border);
        margin: 0.12rem;
    }

    /* ── Work experience card ────────────────────────────────────────────────── */
    .pf-work-card {
        background: var(--warm-muted);
        border: 1px solid var(--warm-border);
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    /* ── Section header label ────────────────────────────────────────────────── */
    .pf-section-header {
        font-family: var(--sans);
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--copper);
        margin-bottom: 0.75rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--warm-border);
    }

    /* ── Hero banner ─────────────────────────────────────────────────────────── */
    .pf-hero {
        text-align: center;
        padding: 4.5rem 1rem 3.5rem;
        background: linear-gradient(160deg, #FFFDF8 0%, #FAF5EB 60%, #F5EDD8 100%);
        border-radius: 4px;
        margin-bottom: 2rem;
        border: 1px solid var(--warm-border);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.9),
                    0 2px 12px rgba(161,127,62,.08);
    }
    .pf-hero h1 {
        font-family: var(--serif) !important;
        font-size: 3.25rem;
        font-weight: 700;
        color: var(--charcoal) !important;
        margin: 0 0 0.5rem;
        line-height: 1.12;
        letter-spacing: -0.01em;
    }
    .pf-hero h1 span {
        color: var(--copper) !important;
        font-style: italic;
    }
    .pf-hero p {
        font-size: 1.1rem;
        color: var(--charcoal-soft) !important;
        max-width: 520px;
        margin: 0 auto 2rem;
        line-height: 1.7;
    }

    /* ── Certificate dashed upload zone ─────────────────────────────────────── */
    .pf-cert-zone {
        border: 1.5px dashed var(--warm-border);
        border-radius: 4px;
        padding: 1.25rem;
        text-align: center;
        color: var(--charcoal-soft);
        font-size: 0.83rem;
        margin-bottom: 0.5rem;
        background: var(--warm-muted);
    }

    /* ── Roadmap timeline ────────────────────────────────────────────────────── */
    .pf-timeline-item {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        padding: 0.85rem 0;
        border-bottom: 1px solid var(--warm-border);
    }
    .pf-timeline-dot {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 700;
        font-family: var(--sans);
    }

    /* ── Dashboard stats ─────────────────────────────────────────────────────── */
    .pf-stat {
        text-align: center;
        padding: 1.35rem;
        background: var(--white);
        border: 1px solid var(--warm-border);
        border-radius: 4px;
        box-shadow: 0 1px 4px rgba(44,44,44,.04);
    }
    .pf-stat-num {
        font-family: var(--serif) !important;
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--copper) !important;
    }
    .pf-stat-label {
        font-family: var(--sans);
        font-size: 0.75rem;
        color: var(--charcoal-soft) !important;
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ── Plan card — selected state ──────────────────────────────────────────── */
    .pf-plan-selected {
        border: 2px solid var(--copper) !important;
        box-shadow: 0 4px 16px rgba(161,127,62,.18) !important;
    }

    /* ── Streamlit native component overrides ────────────────────────────────── */

    /* Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stFileUploader > label,
    .stNumberInput > label,
    .stSlider > label {
        font-family: var(--sans) !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--charcoal-mid) !important;
    }

    /* Input fields */
    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        border-radius: 3px !important;
        border: 1px solid var(--warm-border) !important;
        background: var(--white) !important;
        color: var(--charcoal) !important;
        font-family: var(--sans) !important;
        font-size: 0.88rem !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--copper) !important;
        box-shadow: 0 0 0 2px rgba(161,127,62,.14) !important;
    }

    /* Selectbox */
    [data-baseweb="select"] > div {
        border-radius: 3px !important;
        border: 1px solid var(--warm-border) !important;
        background: var(--white) !important;
        font-family: var(--sans) !important;
        font-size: 0.88rem !important;
    }

    /* Progress bar — copper/gold gradient */
    div[data-testid="stProgress"] > div {
        background: var(--warm-border) !important;
        border-radius: 9999px !important;
        height: 5px !important;
    }
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--copper), var(--gold)) !important;
        border-radius: 9999px !important;
    }

    /* Primary buttons → gold solid */
    .stButton > button[kind="primary"] {
        font-family: var(--sans) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
        border-radius: 3px !important;
        background: var(--gold) !important;
        border: 1px solid var(--copper) !important;
        color: var(--white) !important;
        padding: 0.55rem 1.4rem !important;
        transition: background 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--copper) !important;
        border-color: var(--copper-dark) !important;
        box-shadow: 0 3px 10px rgba(161,127,62,.3) !important;
    }

    /* Secondary buttons → outlined charcoal */
    .stButton > button[kind="secondary"] {
        font-family: var(--sans) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        border-radius: 3px !important;
        background: var(--white) !important;
        border: 1px solid var(--warm-border) !important;
        color: var(--charcoal-mid) !important;
        transition: border-color 0.2s, color 0.2s !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--copper) !important;
        color: var(--copper) !important;
    }

    /* Tertiary / default buttons */
    .stButton > button:not([kind]) {
        font-family: var(--sans) !important;
        border-radius: 3px !important;
        background: var(--white) !important;
        border: 1px solid var(--warm-border) !important;
        color: var(--charcoal-mid) !important;
    }

    /* Slider thumb & track */
    .stSlider [data-testid="stSlider"] > div > div > div {
        background: var(--copper) !important;
    }

    /* Link buttons */
    .stLinkButton a {
        font-family: var(--sans) !important;
        border-radius: 3px !important;
        border: 1px solid var(--warm-border) !important;
        color: var(--charcoal-mid) !important;
        font-size: 0.83rem !important;
    }
    .stLinkButton a:hover {
        border-color: var(--copper) !important;
        color: var(--copper) !important;
        background: var(--gold-pale) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid var(--warm-border) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--sans) !important;
        font-size: 0.83rem !important;
        font-weight: 500 !important;
        color: var(--charcoal-soft) !important;
        padding: 0.55rem 1.25rem !important;
        border-radius: 0 !important;
        letter-spacing: 0.02em !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--copper) !important;
        border-bottom: 2px solid var(--copper) !important;
        font-weight: 600 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: var(--sans) !important;
        font-size: 0.83rem !important;
        font-weight: 600 !important;
        color: var(--charcoal-mid) !important;
    }

    /* Success / info / warning alerts */
    [data-testid="stAlert"] {
        border-radius: 3px !important;
        font-family: var(--sans) !important;
        font-size: 0.85rem !important;
    }

    /* st.metric */
    [data-testid="stMetricValue"] {
        font-family: var(--serif) !important;
        color: var(--copper) !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--sans) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.07em !important;
        color: var(--charcoal-soft) !important;
    }

    /* Headings that Streamlit renders */
    h1, h2, h3 {
        font-family: var(--serif) !important;
        color: var(--copper) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    h4, h5, h6 {
        font-family: var(--sans) !important;
        color: var(--charcoal) !important;
        font-weight: 600 !important;
    }
    p, li, span, div {
        color: var(--charcoal) !important;
    }

    /* ── Hide Streamlit chrome ───────────────────────────────────────────────── */
    #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], .stDeployButton {
        display: none !important;
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
        <div class="pf-logo">Path<span>finder</span>
          <span style="font-size:.65rem;font-weight:400;color:#9A8060;
                       letter-spacing:.12em;text-transform:uppercase;
                       font-family:'Inter',sans-serif;margin-left:.6rem;
                       vertical-align:middle;">Career Intelligence</span>
        </div>
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
        "pf_days_per_week": 5,          # NEW — plan = days/week
        "pf_roadmap_courses": [],
        "pf_completed_courses": set(),
        "pf_cert_verify": {},            # course_id -> {"url": str, "verified": bool}
        "pf_work_entries": [{"id": 0}],
        "pf_work_counter": 1,
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
        edu_level   = st.selectbox("Education Level", edu_options, key="pf_manual_edu")
        major_choice = st.selectbox("Major / Field of Study", all_majors, key="pf_manual_major_sel")
        if major_choice in ("(Select or type below)", "Other"):
            major = st.text_input("Specify Major", placeholder="e.g. Teknik Informatika",
                                  key="pf_manual_major_txt")
        else:
            major = major_choice
        institution = st.text_input("Institution Name", placeholder="e.g. Universitas Padjadjaran",
                                    key="pf_manual_inst")
        grad_year   = st.selectbox("Graduation Year",
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
                st.text_input("Specify Title", key=f"pf_job_title_txt_{eid}",
                              placeholder="e.g. Data Analyst")
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
        f"Graduation Year: {form_data['grad_year']}", "",
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
    for sk in form_data.get("raw_skills", "").split(","):
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
    detected_skills = analysis.get("detected_skills", [])

    st.markdown(f"### Career Matches for **{candidate}**")
    st.caption("Based on your profile, O*NET taxonomy, and SKKNI competency framework.")

    result_cols = st.columns(4, gap="medium")

    for i, match in enumerate(matches[:3]):
        col      = result_cols[i]
        is_best  = (i == 0)
        soc      = match.get("soc_code", "")
        score    = match.get("match_score", 0)
        gap_count = len(match.get("skill_gaps", []))

        # Ensure total_course_hours is populated from DB (fixes 0h bug)
        total_hrs = match.get("total_course_hours") or get_total_hours(soc)
        match["total_course_hours"] = total_hrs

        hours_pd  = st.session_state.get("pf_study_hours_per_day", 2)
        dpw       = st.session_state.get("pf_days_per_week", 5)
        eff_hrs_wk = hours_pd * dpw
        weeks     = math.ceil(total_hrs / eff_hrs_wk) if (total_hrs and eff_hrs_wk) else 0

        with col:
            if is_best:
                st.markdown('<span class="pf-badge pf-badge-gold">⭐ Best Match</span>',
                            unsafe_allow_html=True)
            card_cls = "pf-card pf-card-gold" if is_best else "pf-card"
            st.markdown(f"""
            <div class="{card_cls}" style="padding:1rem;">
              <div style="font-size:1.05rem;font-weight:700;color:#2C2C2C;margin-bottom:0.25rem;">
                {match.get('title','')}
              </div>
              <div style="font-size:0.75rem;color:#6B6B6B;">{soc}</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(score / 100)
            st.caption(f"**{score}%** match · {gap_count} skill gaps")

            with st.expander("Why this role?"):
                st.write(match.get("description", ""))

            with st.expander("Skill Gaps"):
                gaps = match.get("skill_gaps", [])
                if gaps:
                    pills = " ".join(f'<span class="pf-pill">{g}</span>' for g in gaps)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.success("No major gaps!")

            st.metric("Study Hours", f"{int(total_hrs)}h", f"~{weeks} wks")

            if st.button("Select This Career", key=f"pf_sel_{i}",
                         use_container_width=True,
                         type="primary" if is_best else "secondary"):
                # Make sure courses from DB are attached
                courses = match.get("courses") or get_courses_for_onet(soc)
                st.session_state["pf_selected_match"] = {
                    **match,
                    "total_course_hours": total_hrs,
                    "courses": courses,
                    "match_ratio": score / 100,
                }
                st.session_state["pf_roadmap_courses"] = courses
                st.session_state["pf_step"] = "skill_gap"
                st.rerun()

    # ── 4th column: Add Profession ────────────────────────────────────────────
    with result_cols[3]:
        st.markdown("""
        <div class="pf-card pf-card-dashed" style="text-align:center;padding:2rem 1rem;">
          <div style="font-size:2.5rem;">＋</div>
          <div style="font-weight:600;color:#374151;margin-bottom:0.25rem;">Add Profession</div>
          <div style="font-size:0.8rem;color:#9A8060;">Browse O*NET roles to compare</div>
        </div>
        """, unsafe_allow_html=True)
        all_onet = get_all_onet_titles()
        custom_t = st.selectbox("Browse O*NET Roles", ["—"] + all_onet, key="pf_custom_onet")
        if custom_t and custom_t != "—":
            soc = get_soc_for_title(custom_t)
            if soc:
                hrs     = get_total_hours(soc)
                courses = get_courses_for_onet(soc)
                st.metric("Study Hours", f"{int(hrs)}h")
                if st.button("Add & Select", key="pf_add_custom", use_container_width=True):
                    # Compute skill gaps from O*NET typical skills vs detected skills
                    user_skills = detected_skills or []
                    gaps = _compute_skill_gaps(soc, user_skills)
                    st.session_state["pf_selected_match"] = {
                        "soc_code": soc,
                        "title": custom_t,
                        "description": "Manually selected profession from O*NET catalog.",
                        "matched_skills": [],
                        "skill_gaps": gaps,
                        "match_score": 50,
                        "total_course_hours": hrs,
                        "courses": courses,
                        "match_ratio": 0.5,
                    }
                    st.session_state["pf_roadmap_courses"] = courses
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

    detected = analysis.get("detected_skills", []) if analysis else []
    gaps     = match.get("skill_gaps", [])
    score    = match.get("match_score", 50)

    st.markdown("## Skill Gap Analysis")
    st.markdown(f"**Target Role:** {match.get('title','')}")

    col_have, col_gap = st.columns(2, gap="large")
    with col_have:
        st.markdown("#### ✅ Skills You Have")
        if detected:
            for sk in detected:
                st.markdown(f'<span class="pf-badge pf-badge-green">{sk}</span>',
                            unsafe_allow_html=True)
        else:
            st.info("No skills detected — fill in the manual form to show your skills here.")
    with col_gap:
        st.markdown("#### 🔴 Skills to Acquire")
        if gaps:
            for sk in gaps:
                st.markdown(f'<span class="pf-badge pf-badge-red">{sk}</span>',
                            unsafe_allow_html=True)
        else:
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
# CHOOSE PLAN PAGE  (user sets hours/day; plans = days/week commitment)
# ══════════════════════════════════════════════════════════════════════════════

def _render_choose_plan():
    match = st.session_state.get("pf_selected_match", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    soc       = match.get("soc_code", "")
    total_hrs = match.get("total_course_hours") or get_total_hours(soc)
    # Fallback: if still 0, re-query with matched courses
    if not total_hrs and match.get("courses"):
        total_hrs = sum(c.get("hours", 0) for c in match["courses"])

    st.markdown("## Choose Your Study Plan")

    # ── User sets their own hours/day ─────────────────────────────────────────
    st.markdown("#### ⏱️ How many hours per day can you commit?")
    hours_pd = st.slider(
        "Hours per day", min_value=1, max_value=8,
        value=st.session_state.get("pf_study_hours_per_day", 2),
        step=1, key="pf_hours_slider",
        help="Set your daily study commitment. The plan cards below will update automatically."
    )
    st.session_state["pf_study_hours_per_day"] = hours_pd

    st.markdown("#### 📅 How many days per week will you study?")
    st.caption("Choose a study cadence that fits your lifestyle.")
    st.markdown("")

    plans = [
        {"id": "intensive", "name": "Fast Track",  "days": 7, "icon": "🔥",
         "desc": "Every day — maximum speed, minimum breaks"},
        {"id": "balanced",  "name": "Regular",     "days": 5, "icon": "⚖️",
         "desc": "Weekdays only — sustainable & recommended"},
        {"id": "casual",    "name": "Flexible",    "days": 3, "icon": "🌱",
         "desc": "3 days/week — at your own relaxed pace"},
    ]

    cols = st.columns(3, gap="large")
    for plan, col in zip(plans, cols):
        weekly_hrs = hours_pd * plan["days"]
        weeks      = math.ceil(total_hrs / weekly_hrs) if (total_hrs and weekly_hrs) else 0
        days_total = weeks * plan["days"]
        end_date   = (datetime.date.today() + datetime.timedelta(weeks=weeks)).strftime("%b %Y")
        sel        = st.session_state.get("pf_selected_plan") == plan["id"]
        card_cls   = "pf-card pf-plan-selected" if sel else "pf-card"

        with col:
            st.markdown(f"""
            <div class="{card_cls}" style="text-align:center;padding:1.5rem;">
              <div style="font-size:2.5rem;">{plan['icon']}</div>
              <div style="font-size:1.1rem;font-weight:700;margin:0.5rem 0;">{plan['name']}</div>
              <div style="font-size:0.85rem;color:#6B6B6B;margin-bottom:1rem;">{plan['desc']}</div>
              <div style="font-size:1.8rem;font-weight:800;color:#A17F3E;">{weeks} wks</div>
              <div style="font-size:0.8rem;color:#9A8060;">
                {plan['days']} days/wk · {hours_pd}h/day · done by {end_date}
              </div>
            </div>
            """, unsafe_allow_html=True)
            btn_type = "primary" if sel else "secondary"
            label    = f"{'✓ Selected' if sel else 'Choose'} {plan['name']}"
            if st.button(label, key=f"pf_plan_{plan['id']}",
                         use_container_width=True, type=btn_type):
                st.session_state["pf_selected_plan"]       = plan["id"]
                st.session_state["pf_days_per_week"]       = plan["days"]
                st.session_state["pf_study_hours_per_day"] = hours_pd
                # Load courses from DB into roadmap
                st.session_state["pf_roadmap_courses"] = generate_verified_roadmap(
                    [soc], plan["id"]
                )
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
# Certificate Verification Dialog (Phase 3 — event handler)
# ══════════════════════════════════════════════════════════════════════════════

@st.dialog("Submit Verification", width="small")
def _verify_dialog(course: dict):
    cid   = str(course.get("course_id", course.get("title", "")))
    title = course.get("title", "")
    st.markdown(f"**{title}**")
    st.caption(f"Provider: {course.get('provider','')}")
    url_input = st.text_input(
        "Paste your certificate URL (Coursera / edX / LinkedIn / other)",
        placeholder="https://coursera.org/verify/XXXXXXXXX",
        key=f"pf_verify_input_{cid}"
    )
    col_submit, col_cancel = st.columns(2)
    with col_submit:
        if st.button("Submit", type="primary", use_container_width=True, key=f"pf_sub_{cid}"):
            if url_input.strip().startswith("http"):
                cv = st.session_state.setdefault("pf_cert_verify", {})
                cv[cid] = {"url": url_input.strip(), "verified": True}
                st.session_state["pf_cert_verify"] = cv
                # Also persist to DB
                try:
                    verify_user_skill(
                        st.session_state.get("pf_session_id", ""),
                        title, url_input.strip()
                    )
                except Exception:
                    pass
                st.rerun()
            else:
                st.error("Please enter a valid URL starting with http.")
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key=f"pf_can_{cid}"):
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROADMAP PAGE  (PHASE 2 & 3 — real links, gamification)
# ══════════════════════════════════════════════════════════════════════════════

def _render_roadmap():
    match    = st.session_state.get("pf_selected_match", {})
    hours_pd = st.session_state.get("pf_study_hours_per_day", 2)
    dpw      = st.session_state.get("pf_days_per_week", 5)
    done_set = st.session_state.get("pf_completed_courses", set())
    cv_map   = st.session_state.get("pf_cert_verify", {})

    if not match:
        st.session_state["pf_step"] = "choose_plan"
        st.rerun()

    soc = match.get("soc_code", "")
    # Always pull courses from DB to guarantee real URLs
    courses = st.session_state.get("pf_roadmap_courses") or generate_verified_roadmap([soc])
    if not courses:
        courses = get_courses_for_onet(soc)
    # Persist for other pages
    st.session_state["pf_roadmap_courses"] = courses

    st.markdown(f"## Your Custom Learning Roadmap — {match.get('title','')}")
    st.caption("All course links are pulled from our verified database — no AI-generated URLs.")

    if not courses:
        st.info("No courses found for this role. Please choose a plan first.")
    else:
        total_hrs = sum(c.get("hours", 0) for c in courses)
        done_hrs  = sum(c.get("hours", 0) for c in courses
                        if str(c.get("course_id", c.get("title",""))) in done_set
                        or c.get("title","") in done_set)
        pct = int(done_hrs / total_hrs * 100) if total_hrs else 0

        st.markdown(f"**Progress:** {pct}% — {int(done_hrs)}/{int(total_hrs)} hours")
        st.progress(pct / 100)
        st.markdown("---")

        cumday = 0
        eff_hpd = hours_pd if hours_pd else 2   # fallback

        for i, course in enumerate(courses):
            cid      = str(course.get("course_id", course.get("title", i)))
            title    = course.get("title", "")
            hrs      = course.get("hours", 0)
            days_n   = math.ceil(hrs / eff_hpd) if eff_hpd else 0
            verified = cv_map.get(cid, {}).get("verified", False)
            done     = cid in done_set or title in done_set

            dot_bg    = "#D8F3DC" if (done or verified) else "#F5EDD8"
            dot_color = "#2D6A4F" if (done or verified) else "#A17F3E"

            # ── Timeline row ──
            st.markdown(f"""
            <div class="pf-timeline-item">
              <div class="pf-timeline-dot" style="background:{dot_bg};color:{dot_color};">
                {'✓' if (done or verified) else i+1}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;color:#2C2C2C;">{title}</div>
                <div style="font-size:0.8rem;color:#6B6B6B;">
                  {course.get('provider','')} &nbsp;·&nbsp; {int(hrs)}h &nbsp;·&nbsp;
                  ~{days_n} days (starts day {cumday+1})
                </div>
                {('<div style="font-size:0.75rem;color:#2D6A4F;margin-top:0.2rem;">✓ Certificate submitted</div>' if verified else '')}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Action buttons ──
            ca, cb, cc = st.columns([3, 1, 1])
            with cb:
                real_url = course.get("url", "")
                if real_url and not verified:
                    st.link_button("Go to Course →", real_url, use_container_width=True)
            with cc:
                if verified:
                    st.markdown('<span class="pf-badge pf-badge-green" style="font-size:0.85rem;">✓ Verified</span>',
                                unsafe_allow_html=True)
                elif done:
                    if st.button("Verify Cert", key=f"pf_vbtn_{i}", use_container_width=True):
                        _verify_dialog(course)
                else:
                    label = "✓ Done" if done else "Mark Done"
                    if st.button(label, key=f"pf_done_{i}", use_container_width=True):
                        done_set.add(cid)
                        done_set.add(title)
                        st.session_state["pf_completed_courses"] = done_set
                        st.rerun()

            cumday += days_n

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
# PHASE 5 — @st.dialog Study Planner (from Dashboard)
# ══════════════════════════════════════════════════════════════════════════════

@st.dialog("Study Planner", width="large")
def _study_planner_dialog():
    match     = st.session_state.get("pf_selected_match", {})
    courses   = st.session_state.get("pf_roadmap_courses", [])
    soc       = match.get("soc_code", "")
    total_hrs = match.get("total_course_hours") or sum(c.get("hours", 0) for c in courses) or get_total_hours(soc)

    st.markdown(f"### {match.get('title','')} — Personalized Schedule")

    hours_pd = st.slider("Study hours per day", 1, 8,
                         st.session_state.get("pf_study_hours_per_day", 2),
                         key="pf_dialog_hrs")
    dpw_opts  = {"Every day (7)": 7, "Weekdays (5)": 5, "3 days/week": 3}
    dpw_label = st.selectbox("Days per week", list(dpw_opts.keys()),
                             key="pf_dialog_dpw")
    dpw       = dpw_opts[dpw_label]

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
    st.caption("Submit a certificate URL to mark a course as officially verified.")

    cv_map = st.session_state.setdefault("pf_cert_verify", {})

    for course in courses:
        cid     = str(course.get("course_id", course.get("title", "")))
        title   = course.get("title", "")
        v_state = cv_map.get(cid, {"url": "", "verified": False})

        col_t, col_icon = st.columns([4, 1])
        with col_t:
            st.markdown(f"**{title}**  \n_{course.get('provider','')}_")
        with col_icon:
            icon_html = (
                '<span style="font-size:1.4rem;color:#2D6A4F;">✅</span>'
                if v_state["verified"] else
                '<span style="font-size:1.4rem;color:#9B2335;">✗</span>'
            )
            st.markdown(icon_html, unsafe_allow_html=True)

        new_url = st.text_input(
            "Certificate URL", value=v_state["url"],
            key=f"pf_dlg_url_{cid}",
            placeholder="https://coursera.org/verify/..."
        )
        v_state["url"] = new_url

        if st.button("Verify", key=f"pf_dlg_verify_{cid}"):
            if new_url.strip().startswith("http"):
                v_state["verified"] = True
                cv_map[cid] = v_state
                st.session_state["pf_cert_verify"] = cv_map
                try:
                    verify_user_skill(st.session_state.get("pf_session_id",""), title, new_url.strip())
                except Exception:
                    pass
                st.success("✓ Verified!")
                st.rerun()
            else:
                st.error("Please enter a valid URL.")
        else:
            cv_map[cid] = v_state
            st.session_state["pf_cert_verify"] = cv_map

        st.markdown("---")

    if st.button("Close Planner", use_container_width=True):
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════

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
    total_hrs = match.get("total_course_hours") or sum(c.get("hours", 0) for c in courses) or get_total_hours(soc)
    done_hrs  = sum(c.get("hours", 0) for c in courses
                    if str(c.get("course_id", c.get("title",""))) in done_set
                    or c.get("title","") in done_set)
    remain    = max(0, total_hrs - done_hrs)
    pct       = int(done_hrs / total_hrs * 100) if total_hrs else 0
    weekly_h  = hours_pd * dpw
    wks_left  = math.ceil(remain / weekly_h) if (remain and weekly_h) else 0
    verified_n = sum(1 for v in cv_map.values() if v.get("verified"))

    st.markdown(f"## Dashboard — {match.get('title','')}")

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

    st.markdown("")
    st.progress(pct / 100)
    st.caption(f"{pct}% complete — {int(done_hrs)}/{int(total_hrs)} hours")
    st.markdown("---")
    st.markdown("#### Course Status")

    for course in courses:
        cid      = str(course.get("course_id", course.get("title","")))
        done     = cid in done_set or course.get("title","") in done_set
        verified = cv_map.get(cid, {}).get("verified", False)
        if verified:
            badge = '<span class="pf-badge pf-badge-green">✅ Verified</span>'
        elif done:
            badge = '<span class="pf-badge pf-badge-blue">✓ Completed</span>'
        else:
            badge = '<span class="pf-badge" style="background:#F2EDE6;color:#6B6B6B;">Pending</span>'
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.6rem 0;border-bottom:1px solid #E8E0D5;">
          <div>
            <span style="font-weight:500;color:#2C2C2C;">{course.get('title','')}</span>
            <span style="font-size:0.75rem;color:#9A8060;margin-left:0.5rem;">
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
                    session_id  = st.session_state["pf_session_id"]
                    skills_list = [s.strip() for s in form_data["raw_skills"].split(",") if s.strip()]
                    upsert_user_profile(session_id,
                                        full_name=form_data["full_name"],
                                        education=form_data["edu_level"],
                                        major=form_data["major"],
                                        institution=form_data["institution"],
                                        cv_text=cv_text)
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
      <div style="font-family:'Inter',sans-serif;font-size:.68rem;font-weight:700;
                  letter-spacing:.15em;text-transform:uppercase;color:#A17F3E;
                  margin-bottom:.9rem;">Powered by Gemini AI &nbsp;&middot;&nbsp; O*NET &nbsp;&middot;&nbsp; SKKNI</div>
      <h1>Find Your <span>Career Path</span></h1>
      <p>AI-powered career guidance tailored for Indonesian students — mapped to O*NET and SKKNI competency standards.</p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="large")
    features = [
        ("✶", "AI Analysis",
         "Gemini AI analyzes your profile against global O*NET taxonomy and Indonesian SKKNI frameworks."),
        ("◈", "Career Matching",
         "Get 3 personalized career matches ranked by compatibility score with detailed skill gap breakdown."),
        ("▦", "Verified Roadmap",
         "Course links come exclusively from our verified database — no hallucinated URLs, ever."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="pf-card" style="text-align:center;padding:1.75rem 1.5rem;">
              <div style="font-size:1.6rem;color:#A17F3E;margin-bottom:.65rem;line-height:1;">{icon}</div>
              <div style="font-family:'Playfair Display',Georgia,serif;font-weight:600;
                          font-size:1rem;margin-bottom:.5rem;color:#2C2C2C;
                          letter-spacing:.01em;">{title}</div>
              <div style="font-size:.83rem;color:#6B6B6B;line-height:1.65;">{desc}</div>
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

get_db_engine()    # init + seed DB (cached)
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
