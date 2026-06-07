"""
Pathfinder — SQLite data layer
Phase 1 of the 5-phase SaaS architecture.

Tables
------
onet_occupations  — O*NET Standard Occupational Classifications
skkni_competencies — Indonesian SKKNI competency units, linked to onet_occupations
course_catalog    — curated course catalogue (COURSERA/EDX/LINKEDIN_LEARNING/UDACITY/DICODING/MYSKILL)
user_profiles     — one row per session, stores raw cv_text
user_skills       — per-session skill rows with is_verified flag and certificate_url
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "pathfinder.db")

# ─────────────────────────────────────────────────────────────────────────────
# Seed data
# ─────────────────────────────────────────────────────────────────────────────

ONET_SEED = [
    ("15-2051.00", "Data Scientists",
     "Apply mathematics, statistics, data mining, and predictive modelling to understand and analyse large datasets."),
    ("15-1245.00", "Data Analysts and Information Analysts",
     "Analyse and synthesise large amounts of data to identify patterns, trends, and actionable insights."),
    ("15-1252.00", "Software Developers",
     "Design, develop, test, and maintain software applications and systems end-to-end."),
    ("15-1243.00", "Database Architects",
     "Design database systems, define data architecture standards, and maintain data infrastructure."),
    ("15-1244.00", "Network and Computer Systems Administrators",
     "Install, configure, and maintain network infrastructure and computer systems."),
    ("15-1231.00", "Computer Network Support Specialists",
     "Analyse, test, troubleshoot, and evaluate computer network problems."),
    ("13-2051.00", "Financial Analysts",
     "Provide analysis of financial data and guidance on investment opportunities for businesses."),
    ("13-2011.00", "Accountants and Auditors",
     "Examine and prepare financial records, ensure accuracy, and assess financial operations."),
    ("11-9021.00", "Project Managers",
     "Plan, coordinate, and supervise activities to complete projects on time and within budget."),
    ("11-2021.00", "Marketing Managers",
     "Plan, direct, and coordinate marketing policies, campaigns, and promotions."),
    ("11-3121.00", "Human Resources Managers",
     "Plan, direct, and coordinate administrative functions and human-capital strategies."),
    ("11-3071.00", "Supply Chain and Logistics Managers",
     "Plan and direct transportation, storage, and distribution operations."),
    ("11-9111.00", "Medical and Health Services Managers",
     "Plan, direct, and coordinate activities of health services organisations."),
    ("17-2112.00", "Industrial Engineers",
     "Design, develop, test, and evaluate integrated systems for managing industrial production processes."),
    ("27-1024.00", "Graphic Designers",
     "Create visual concepts, by hand or using computer software, to communicate ideas."),
    ("15-1211.00", "Computer Systems Analysts",
     "Analyse science, engineering, business, and other data-processing problems to implement and improve systems."),
    ("11-1021.00", "General and Operations Managers",
     "Plan, direct, or coordinate the operations of public or private sector organisations."),
    ("25-1099.00", "Postsecondary Teachers",
     "Teach courses in a specialised field at postsecondary institutions and conduct research."),
]

SKKNI_SEED = [
    ("TIK.JD02.008.01", "Menganalisis Data dengan Metode Statistik", "15-2051.00"),
    ("TIK.JD02.009.01", "Membangun Model Machine Learning", "15-2051.00"),
    ("TIK.JD01.001.01", "Melakukan Eksplorasi dan Visualisasi Data", "15-1245.00"),
    ("TIK.PR05.001.01", "Membuat Program Komputer Berorientasi Objek", "15-1252.00"),
    ("TIK.PR05.002.01", "Mengembangkan Aplikasi Berbasis Web", "15-1252.00"),
    ("TIK.BD01.001.01", "Merancang dan Mengelola Database Relasional", "15-1243.00"),
    ("TIK.NT01.001.01", "Mengkonfigurasi Jaringan Komputer", "15-1244.00"),
    ("KJK.SP02.001.01", "Melakukan Analisis Keuangan dan Valuasi", "13-2051.00"),
    ("KJK.SP01.001.01", "Menyusun Laporan Keuangan Standar", "13-2011.00"),
    ("M.701001.001.01", "Merencanakan dan Mengelola Proyek", "11-9021.00"),
    ("M.702090.023.01", "Melaksanakan Pemasaran Digital Terpadu", "11-2021.00"),
    ("M.701001.002.01", "Mengelola Sumber Daya Manusia Strategis", "11-3121.00"),
    ("LOG.OO07.006.00", "Merencanakan dan Mengatur Logistik", "11-3071.00"),
]

# (course_id, title, provider, url, mapped_onet_code, total_hours)
PROVIDER_VALID = {"COURSERA", "EDX", "LINKEDIN_LEARNING", "UDACITY", "DICODING", "MYSKILL"}

COURSE_SEED = [
    # ── Data Science / ML ────────────────────────────────────────────
    ("DS001", "Python for Data Science and Machine Learning",
     "COURSERA", "https://coursera.org/specializations/data-science-python", "15-2051.00", 40),
    ("DS002", "Machine Learning Specialization",
     "COURSERA", "https://coursera.org/specializations/machine-learning-introduction", "15-2051.00", 60),
    ("DS003", "Deep Learning Specialization",
     "COURSERA", "https://coursera.org/specializations/deep-learning", "15-2051.00", 80),
    ("DS004", "Statistics for Data Science",
     "EDX", "https://edx.org/course/statistics-for-data-science", "15-2051.00", 20),
    ("DS005", "Applied Data Science Capstone",
     "COURSERA", "https://coursera.org/learn/applied-data-science-capstone", "15-2051.00", 16),

    # ── Data Analysis ────────────────────────────────────────────────
    ("DA001", "Google Data Analytics Certificate",
     "COURSERA", "https://coursera.org/professional-certificates/google-data-analytics", "15-1245.00", 48),
    ("DA002", "Data Visualization with Tableau",
     "COURSERA", "https://coursera.org/learn/data-visualization-tableau", "15-1245.00", 18),
    ("DA003", "SQL for Data Analysis",
     "COURSERA", "https://coursera.org/learn/sql-for-data-science", "15-1245.00", 16),
    ("DA004", "Excel to MySQL: Analytics Techniques",
     "COURSERA", "https://coursera.org/specializations/excel-mysql", "15-1245.00", 24),
    ("DA005", "Belajar Analisis Data dengan Python",
     "DICODING", "https://dicoding.com/academies/319", "15-1245.00", 30),

    # ── Software Engineering ─────────────────────────────────────────
    ("SE001", "Full-Stack Web Development Bootcamp",
     "UDACITY", "https://udacity.com/school-of-data-science", "15-1252.00", 64),
    ("SE002", "Meta Back-End Developer Certificate",
     "COURSERA", "https://coursera.org/professional-certificates/meta-back-end-developer", "15-1252.00", 56),
    ("SE003", "AWS Cloud Practitioner Essentials",
     "COURSERA", "https://coursera.org/learn/aws-cloud-practitioner-essentials", "15-1252.00", 16),
    ("SE004", "Docker and Kubernetes: The Complete Guide",
     "UDACITY", "https://udacity.com/course/scalable-microservices-with-kubernetes--ud615", "15-1252.00", 20),
    ("SE005", "Belajar Pengembangan Web",
     "DICODING", "https://dicoding.com/academies/75", "15-1252.00", 40),
    ("SE006", "Agile Software Development",
     "COURSERA", "https://coursera.org/learn/agile-development", "15-1252.00", 12),

    # ── Database Architecture ────────────────────────────────────────
    ("DB001", "Database Management Essentials",
     "COURSERA", "https://coursera.org/learn/database-management", "15-1243.00", 24),
    ("DB002", "Big Data Fundamentals",
     "EDX", "https://edx.org/course/big-data-fundamentals", "15-1243.00", 20),
    ("DB003", "Google Cloud Professional Data Engineer",
     "COURSERA", "https://coursera.org/professional-certificates/gcp-data-engineering", "15-1243.00", 48),

    # ── Networking ───────────────────────────────────────────────────
    ("NET001", "The Bits and Bytes of Computer Networking",
     "COURSERA", "https://coursera.org/learn/computer-networking", "15-1244.00", 30),
    ("NET002", "Cisco CCNA: Introduction to Networking",
     "EDX", "https://edx.org/course/introduction-to-networks", "15-1244.00", 40),

    # ── Finance ──────────────────────────────────────────────────────
    ("FIN001", "Financial Analysis and Valuation for Startups",
     "COURSERA", "https://coursera.org/learn/financial-analysis", "13-2051.00", 24),
    ("FIN002", "Bloomberg Terminal Complete Guide",
     "UDACITY", "https://udacity.com/course/bloomberg-terminal", "13-2051.00", 24),
    ("FIN003", "Financial Derivatives and Risk Management",
     "COURSERA", "https://coursera.org/learn/financial-derivatives", "13-2051.00", 28),
    ("FIN004", "CFA Level 1 Complete Preparation Program",
     "UDACITY", "https://udacity.com/course/cfa-level-1-prep", "13-2051.00", 32),
    ("FIN005", "Portfolio Analysis and Management",
     "COURSERA", "https://coursera.org/learn/portfolio-management", "13-2051.00", 18),
    ("FIN006", "Investment Management Specialization",
     "COURSERA", "https://coursera.org/specializations/investment-management", "13-2051.00", 40),

    # ── Accounting ───────────────────────────────────────────────────
    ("ACC001", "Financial Accounting Fundamentals",
     "COURSERA", "https://coursera.org/learn/uva-darden-foundations-of-accounting", "13-2011.00", 32),
    ("ACC002", "Business Analytics Specialization",
     "COURSERA", "https://coursera.org/specializations/business-analytics", "13-2011.00", 40),
    ("ACC003", "Excel Skills for Business",
     "COURSERA", "https://coursera.org/specializations/excel", "13-2011.00", 20),

    # ── Project Management ───────────────────────────────────────────
    ("PM001", "Google Project Management Certificate",
     "COURSERA", "https://coursera.org/professional-certificates/google-project-management", "11-9021.00", 48),
    ("PM002", "PMP Exam Preparation Masterclass",
     "UDACITY", "https://udacity.com/course/pmp-prep", "11-9021.00", 36),
    ("PM003", "Agile Project Management and Scrum",
     "EDX", "https://edx.org/course/agile-project-management", "11-9021.00", 16),

    # ── Marketing ────────────────────────────────────────────────────
    ("MKT001", "Google Digital Marketing & E-commerce Certificate",
     "COURSERA", "https://coursera.org/professional-certificates/google-digital-marketing-ecommerce", "11-2021.00", 40),
    ("MKT002", "Content Marketing Strategy",
     "LINKEDIN_LEARNING", "https://linkedin.com/learning/content-marketing-foundations", "11-2021.00", 12),
    ("MKT003", "SEO Fundamentals and Strategy",
     "COURSERA", "https://coursera.org/learn/search-engine-optimization", "11-2021.00", 16),
    ("MKT004", "Digital Marketing Bootcamp",
     "MYSKILL", "https://myskill.id/course/digital-marketing-bootcamp", "11-2021.00", 30),
    ("MKT005", "Social Media Marketing Specialization",
     "COURSERA", "https://coursera.org/specializations/social-media-marketing", "11-2021.00", 32),

    # ── Human Resources ──────────────────────────────────────────────
    ("HR001", "Human Resource Management Specialization",
     "COURSERA", "https://coursera.org/specializations/human-resource-management", "11-3121.00", 48),
    ("HR002", "Talent Acquisition and Retention",
     "LINKEDIN_LEARNING", "https://linkedin.com/learning/talent-acquisition", "11-3121.00", 12),
    ("HR003", "Organizational Behavior",
     "COURSERA", "https://coursera.org/learn/organizational-behavior-duke", "11-3121.00", 20),

    # ── Supply Chain ─────────────────────────────────────────────────
    ("SC001", "Supply Chain Management Specialization",
     "COURSERA", "https://coursera.org/specializations/supply-chain-management", "11-3071.00", 60),
    ("SC002", "Logistics and Supply Chain Fundamentals",
     "EDX", "https://edx.org/course/supply-chain-fundamentals", "11-3071.00", 24),

    # ── Healthcare ───────────────────────────────────────────────────
    ("HC001", "Health Informatics Specialization",
     "COURSERA", "https://coursera.org/specializations/health-informatics", "11-9111.00", 40),
    ("HC002", "Healthcare Organization and Financing",
     "COURSERA", "https://coursera.org/learn/healthcare-organization-and-financing", "11-9111.00", 20),

    # ── Systems Analysis ─────────────────────────────────────────────
    ("SY001", "Systems Analysis and Design",
     "COURSERA", "https://coursera.org/learn/systems-analysis-and-design", "15-1211.00", 24),
    ("SY002", "Business Process Improvement",
     "EDX", "https://edx.org/course/business-process-management", "15-1211.00", 20),

    # ── General Management ───────────────────────────────────────────
    ("MG001", "Business Foundations Specialization",
     "COURSERA", "https://coursera.org/specializations/wharton-business-foundations", "11-1021.00", 60),
    ("MG002", "Leadership and Management Certificate",
     "LINKEDIN_LEARNING", "https://linkedin.com/learning/paths/become-a-manager", "11-1021.00", 16),

    # ── Indonesian Platforms ─────────────────────────────────────────
    ("DIC001", "Belajar Machine Learning untuk Pemula",
     "DICODING", "https://dicoding.com/academies/184", "15-2051.00", 40),
    ("DIC002", "Menjadi Data Scientist",
     "DICODING", "https://dicoding.com/academies/62", "15-2051.00", 50),
    ("MS001", "Data Analytics Bootcamp",
     "MYSKILL", "https://myskill.id/course/data-analytics-bootcamp", "15-1245.00", 45),
    ("MS002", "Product Analytics Bootcamp",
     "MYSKILL", "https://myskill.id/course/product-analytics-bootcamp", "15-1245.00", 35),
    ("MS003", "Business Intelligence Bootcamp",
     "MYSKILL", "https://myskill.id/course/business-intelligence-bootcamp", "15-1245.00", 40),
]


# ─────────────────────────────────────────────────────────────────────────────
# Connection helper
# ─────────────────────────────────────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ─────────────────────────────────────────────────────────────────────────────
# Schema creation + seed
# ─────────────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create tables and insert seed data (idempotent — safe to call on every startup)."""
    conn = _connect()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS onet_occupations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            onet_code   TEXT UNIQUE NOT NULL,
            title       TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS skkni_competencies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            skkni_code  TEXT UNIQUE NOT NULL,
            unit_title  TEXT NOT NULL,
            onet_code   TEXT REFERENCES onet_occupations(onet_code)
        );

        CREATE TABLE IF NOT EXISTS course_catalog (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id        TEXT UNIQUE NOT NULL,
            title            TEXT NOT NULL,
            provider         TEXT NOT NULL,
            url              TEXT NOT NULL,
            mapped_onet_code TEXT,
            total_hours      INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            cv_text    TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS user_skills (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            skill_name      TEXT NOT NULL,
            is_verified     INTEGER DEFAULT 0,
            certificate_url TEXT,
            onet_code       TEXT,
            skkni_code      TEXT,
            UNIQUE(session_id, skill_name)
        );
    """)

    for onet_code, title, desc in ONET_SEED:
        c.execute(
            "INSERT OR IGNORE INTO onet_occupations (onet_code, title, description) VALUES (?, ?, ?)",
            (onet_code, title, desc),
        )

    for skkni_code, unit_title, onet_code in SKKNI_SEED:
        c.execute(
            "INSERT OR IGNORE INTO skkni_competencies (skkni_code, unit_title, onet_code) VALUES (?, ?, ?)",
            (skkni_code, unit_title, onet_code),
        )

    for course_id, title, provider, url, onet_code, total_hours in COURSE_SEED:
        assert provider in PROVIDER_VALID, f"Unknown provider: {provider}"
        c.execute(
            "INSERT OR IGNORE INTO course_catalog "
            "(course_id, title, provider, url, mapped_onet_code, total_hours) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (course_id, title, provider, url, onet_code, total_hours),
        )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Course-catalogue queries
# ─────────────────────────────────────────────────────────────────────────────

def get_courses_for_onet(onet_code: str, limit: int = 6) -> list[dict]:
    """Return up to *limit* courses for an O*NET code, shortest first."""
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "SELECT course_id, title, provider, url, total_hours "
        "FROM course_catalog WHERE mapped_onet_code = ? "
        "ORDER BY total_hours ASC LIMIT ?",
        (onet_code, limit),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"course_id": r[0], "title": r[1], "provider": r[2], "url": r[3], "total_hours": r[4]}
        for r in rows
    ]


def get_total_hours_for_onet(onet_code: str) -> int:
    """Sum total_hours across all courses for an O*NET code."""
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "SELECT COALESCE(SUM(total_hours), 0) FROM course_catalog WHERE mapped_onet_code = ?",
        (onet_code,),
    )
    result = c.fetchone()[0]
    conn.close()
    return int(result)


# ─────────────────────────────────────────────────────────────────────────────
# User-profile persistence
# ─────────────────────────────────────────────────────────────────────────────

def upsert_user_profile(session_id: str, cv_text: str) -> None:
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO user_profiles (session_id, cv_text) VALUES (?, ?) "
        "ON CONFLICT(session_id) DO UPDATE SET cv_text = excluded.cv_text",
        (session_id, cv_text),
    )
    conn.commit()
    conn.close()


def upsert_user_skills(session_id: str, skills: list[str], onet_code: str | None = None) -> None:
    conn = _connect()
    c = conn.cursor()
    for skill in skills:
        c.execute(
            "INSERT OR IGNORE INTO user_skills (session_id, skill_name, onet_code) VALUES (?, ?, ?)",
            (session_id, skill, onet_code),
        )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Certificate verification
# ─────────────────────────────────────────────────────────────────────────────

def verify_user_skill(session_id: str, skill_name: str, certificate_url: str) -> bool:
    """Mark a skill as verified with a certificate URL. Returns True if a row was updated."""
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "UPDATE user_skills SET is_verified = 1, certificate_url = ? "
        "WHERE session_id = ? AND skill_name = ?",
        (certificate_url, session_id, skill_name),
    )
    conn.commit()
    affected = c.rowcount
    # If no row existed, insert it as verified
    if affected == 0:
        c.execute(
            "INSERT OR IGNORE INTO user_skills (session_id, skill_name, is_verified, certificate_url) "
            "VALUES (?, ?, 1, ?)",
            (session_id, skill_name, certificate_url),
        )
        conn.commit()
    conn.close()
    return True


def get_user_skills(session_id: str) -> list[dict]:
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "SELECT skill_name, is_verified, certificate_url, onet_code, skkni_code "
        "FROM user_skills WHERE session_id = ?",
        (session_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {
            "skill_name": r[0],
            "is_verified": bool(r[1]),
            "certificate_url": r[2],
            "onet_code": r[3],
            "skkni_code": r[4],
        }
        for r in rows
    ]
