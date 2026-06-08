"""
PATHFINDER - AI-powered career guidance for ASEAN students
Production-ready single-file app (Streamlit + SQLAlchemy + google-genai + pypdf)
"""

import streamlit as st
import os, io, json, re, uuid, datetime, math, base64
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

# ── Logo helper ───────────────────────────────────────────────────────────────
def _logo_tag() -> str:
    """
    Return an <img> tag for the logo embedded as base64.
    Priority: spaced-name new logo > underscore variants > .png > .svg.
    """
    assets = Path(__file__).parent / "assets"

    # Check raster candidates in priority order (space-name first = newest upload)
    candidates = [
        (assets / "pathfinder logo.jpeg",  "image/jpeg"),
        (assets / "pathfinder logo.jpg",   "image/jpeg"),
        (assets / "pathfinder_logo.jpeg",  "image/jpeg"),
        (assets / "pathfinder_logo.jpg",   "image/jpeg"),
        (assets / "pathfinder_logo.png",   "image/png"),
    ]
    for path, mime in candidates:
        if path.exists():
            b64 = base64.b64encode(path.read_bytes()).decode()
            return (
                f'<img src="data:{mime};base64,{b64}" '
                f'style="height:36px;vertical-align:middle;margin-right:8px;'
                f'object-fit:contain;">'
            )

    svg = assets / "pathfinder_logo.svg"
    if svg.exists():
        b64 = base64.b64encode(svg.read_bytes()).decode()
        return (
            f'<img src="data:image/svg+xml;base64,{b64}" '
            f'style="height:36px;vertical-align:middle;margin-right:8px;">'
        )
    return ""


# Keep old name for any residual callers
def _logo_b64() -> str:
    assets = Path(__file__).parent / "assets"
    for name, mime in [("pathfinder_logo.png", "image/png"),
                       ("pathfinder_logo.svg", "image/svg+xml")]:
        p = assets / name
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return ""

# ── Comprehensive skill list for autocomplete ─────────────────────────────────
_TECHNICAL_SKILLS = [
    # Programming Languages
    "Python","JavaScript","TypeScript","Java","C++","C#","R","Go","Swift","Kotlin",
    "PHP","Ruby","Rust","Scala","MATLAB","Bash/Shell","Dart","Perl","Haskell","Lua",
    "Assembly","COBOL","Fortran","Elixir","Clojure","F#","Groovy","PowerShell",
    # Web Development
    "HTML/CSS","React","Vue.js","Angular","Node.js","Django","Flask","Spring Boot",
    "REST APIs","GraphQL","WordPress","Next.js","Svelte","Laravel","FastAPI",
    "Express.js","jQuery","Bootstrap","Tailwind CSS","WebSockets","Redux",
    "Nuxt.js","Gatsby","Remix","Astro","WebAssembly",
    # Data & AI
    "SQL","PostgreSQL","MySQL","MongoDB","Redis","Elasticsearch","Cassandra",
    "Excel","Tableau","Power BI","Google Analytics","Pandas","NumPy","SciPy",
    "TensorFlow","PyTorch","Scikit-learn","Keras","Hugging Face","OpenAI API",
    "Machine Learning","Deep Learning","NLP","Computer Vision","Reinforcement Learning",
    "Data Visualization","Statistical Analysis","A/B Testing","R Programming",
    "Data Mining","Feature Engineering","LLMs","Generative AI",
    "ETL Pipelines","Apache Spark","Hadoop","Apache Kafka","Airflow","dbt",
    "BigQuery","Snowflake","Databricks","Looker","Metabase",
    # Cloud & DevOps
    "AWS","Azure","Google Cloud","Docker","Kubernetes","Terraform","CI/CD","Git",
    "GitHub Actions","GitLab CI","Linux","Agile/Scrum","DevOps","Microservices",
    "Jenkins","Ansible","Puppet","Chef","Prometheus","Grafana","Nginx","Apache",
    "Serverless","Cloud Functions","AWS Lambda","Azure Functions","Vault",
    # Business & Operations
    "Financial Modeling","Budgeting","Financial Analysis","Forecasting",
    "Risk Management","Accounting (GAAP/IFRS)","Auditing","Tax Compliance",
    "Business Analysis","Process Improvement","Six Sigma","Lean","Kaizen",
    "Project Management","SAP","ERP Systems","Oracle ERP","Odoo",
    "Supply Chain Management","Procurement","Logistics","Inventory Management",
    "Power Automate","RPA (UiPath / Automation Anywhere)",
    # Marketing & Sales
    "Digital Marketing","SEO/SEM","Content Marketing","Social Media Marketing",
    "Email Marketing","Brand Management","CRM","Salesforce","HubSpot","Zoho CRM",
    "Copywriting","Market Research","Lead Generation","Sales Strategy",
    "Google Ads","Facebook Ads","TikTok Ads","E-commerce","Shopify",
    "Marketing Automation","Affiliate Marketing","Influencer Marketing",
    "Customer Segmentation","Conversion Rate Optimization",
    # Design & Creative
    "Adobe Photoshop","Adobe Illustrator","Adobe InDesign","Figma","Sketch",
    "UI/UX Design","Wireframing","Prototyping","Typography","Brand Identity",
    "Video Editing","Adobe Premiere Pro","After Effects","Blender","Cinema 4D",
    "Canva","Adobe XD","User Research","Accessibility Design","Motion Graphics",
    "3D Modeling","Illustration","Graphic Design","Photography",
    # Engineering Tools
    "AutoCAD","SolidWorks","MATLAB/Simulink","Circuit Design","PLC Programming",
    "Structural Analysis","HYSYS/Aspen Plus","CATIA","Ansys","LabVIEW",
    "Revit","Civil 3D","Arena Simulation","ETAP","STAAD.Pro","SCADA",
    "Embedded Systems","IoT","PCB Design (Altium/Eagle)","VHDL/Verilog",
    # Healthcare & Sciences
    "Patient Care","Clinical Assessment","Electronic Health Records (EHR)",
    "Medical Procedures","Pharmacology","First Aid & CPR","Nutrition Assessment",
    "Laboratory Techniques","PCR","Cell Culture","GCP/GMP Compliance",
    "Medical Imaging","Epidemiology","Clinical Research","SPSS",
    # Security & Networking
    "Cybersecurity","Penetration Testing","Network Security","Ethical Hacking",
    "SIEM","Firewall Management","Cisco Networking","VPN","TCP/IP","DNS",
    "ISO 27001","SOC Operations","Cryptography","Incident Response",
    # Languages (Proficiency)
    "English (Professional)","Bahasa Indonesia","Mandarin Chinese","Japanese",
    "Korean","French","German","Arabic","Spanish","Portuguese","Hindi",
    # Productivity & Collaboration
    "Microsoft Office Suite","Google Workspace","Slack","Jira","Notion",
    "Asana","Trello","Zoom","Confluence","SharePoint","Monday.com",
    "ClickUp","Miro","Figma (Collaborative)","Airtable",
]

_SOFT_SKILLS = [
    # Communication
    "Public Speaking","Presentation Skills","Technical Writing","Business Writing",
    "Active Listening","Storytelling","Report Writing","Persuasion",
    "Cross-cultural Communication","Negotiation","Copywriting",
    # Leadership & Management
    "Leadership","Team Management","Delegation","Coaching & Mentoring",
    "Stakeholder Management","Change Management","Decision Making",
    "Strategic Thinking","People Management","Talent Development",
    "Performance Management","Conflict Resolution","Facilitation",
    "Crisis Management","Visionary Thinking",
    # Thinking & Problem Solving
    "Critical Thinking","Problem Solving","Analytical Thinking",
    "Creative Thinking","Systems Thinking","First Principles Thinking",
    "Design Thinking","Research Skills","Data-driven Decision Making",
    "Root Cause Analysis","Lateral Thinking",
    # Work Ethic & Productivity
    "Time Management","Prioritization","Self-motivation","Attention to Detail",
    "Multitasking","Goal Setting","Accountability","Work Ethics",
    "Adaptability","Resilience","Continuous Learning","Growth Mindset",
    "Self-discipline","Stress Management","Initiative",
    # Interpersonal & Collaboration
    "Teamwork","Collaboration","Empathy","Emotional Intelligence",
    "Networking","Customer Service","Client Relations",
    "Cross-functional Collaboration","Inclusivity","Cultural Sensitivity",
    "Mentoring","Community Building","Conflict Management",
    # Project & Process
    "Project Management","Process Improvement","Risk Awareness","Planning",
    "Coordination","Documentation","Reporting","Quality Mindset",
    "Agile Mindset","Scrum Practices","Kanban","OKR Framework",
]

# Combined for backward compat
_ALL_SKILLS = _TECHNICAL_SKILLS + _SOFT_SKILLS

# ── Seed data ──────────────────────────────────────────────────────────────────
_MAJORS = [
    # Computing & IT
    "Computer Science", "Information Technology", "Information Systems",
    "Software Engineering", "Computer Engineering", "Cybersecurity & Information Security",
    "Data Science & Analytics", "Artificial Intelligence & Machine Learning",
    "Game Development & Design", "Network Engineering", "Cloud Computing",
    "Mobile Application Development", "Web Development", "Database Administration",
    "Digital Forensics",
    # Engineering
    "Electrical Engineering", "Mechanical Engineering", "Civil Engineering",
    "Industrial Engineering", "Chemical Engineering", "Aerospace Engineering",
    "Biomedical Engineering", "Environmental Engineering", "Petroleum Engineering",
    "Mining Engineering", "Materials Science & Engineering",
    "Telecommunications Engineering", "Automotive Engineering", "Marine Engineering",
    "Electronics Engineering", "Control Systems Engineering",
    # Business & Economics
    "Business Administration", "Management", "Accounting", "Finance", "Economics",
    "International Business", "Marketing", "Human Resource Management",
    "Supply Chain Management & Logistics", "Entrepreneurship & Innovation",
    "Banking & Finance", "Taxation", "Business Analytics & Intelligence",
    "Operations Management", "Project Management", "E-Commerce & Digital Business",
    "Retail Management",
    # Social Sciences & Humanities
    "International Relations", "Political Science", "Sociology", "Anthropology",
    "History", "Philosophy", "English Literature & Linguistics",
    "Indonesian Literature", "Japanese Studies", "Chinese Studies", "Korean Studies",
    "Communication Studies", "Journalism & Media Studies", "Broadcasting",
    "Public Relations", "Library & Information Science", "Geography", "Urban Studies",
    # Psychology & Social Work
    "Psychology", "Clinical Psychology", "Industrial & Organizational Psychology",
    "Counseling", "Social Work",
    # Law & Governance
    "Law", "International Law", "Business Law", "Constitutional Law", "Criminal Law",
    "Notary Studies", "Public Administration", "Government Science",
    # Medicine & Health Sciences
    "Medicine (MD)", "Dentistry", "Pharmacy", "Nursing", "Public Health",
    "Nutrition & Dietetics", "Physiotherapy", "Occupational Therapy",
    "Medical Laboratory Technology", "Radiology", "Optometry", "Midwifery",
    "Veterinary Medicine", "Biomedical Science", "Health Information Management",
    "Hospital Management",
    # Natural Sciences
    "Mathematics", "Statistics & Actuarial Science", "Physics", "Chemistry",
    "Biology", "Biochemistry", "Earth Science & Geology", "Environmental Science",
    "Marine Science", "Astronomy",
    # Agriculture & Natural Resources
    "Agribusiness", "Agriculture Science", "Animal Husbandry",
    "Aquaculture & Fisheries", "Forestry & Wood Technology",
    "Food Technology & Science", "Agricultural Engineering", "Plantation Science",
    "Agronomy", "Horticulture", "Agricultural Biotechnology",
    # Arts & Design
    "Graphic Design & Visual Communication", "Interior Design",
    "Industrial & Product Design", "Fashion Design", "Fine Arts",
    "Animation & Multimedia", "Architecture", "Film & Television Production",
    "Photography", "Theatre & Performing Arts", "Music",
    # Education
    "Primary Education", "Secondary Education", "Early Childhood Education",
    "Special Education", "Mathematics Education", "Science Education",
    "English Language Education", "Physical Education & Sports",
    "Educational Technology",
    # Tourism & Hospitality
    "Hospitality Management", "Tourism Management", "Hotel & Resort Management",
    "Culinary Arts", "Event Management", "Travel & Tourism Management",
    # Transportation & Logistics
    "Transportation Management", "Logistics & Supply Chain",
    "Maritime Studies & Technology", "Aviation Management",
    "Port & Shipping Management",
    # Creative & Media
    "Digital Media & Content Creation", "Advertising", "Creative Writing",
    "Music Production",
    # Diploma Programs
    "Diploma in Accounting", "Diploma in Computer Science",
    "Diploma in Business Administration", "Diploma in Nursing",
    "Diploma in Hospitality", "Diploma in Engineering Technology",
    "Diploma in Graphic Design",
]

_OCCUPATIONS = [
    # Computing & IT
    ("15-1252.00", "Software Developer", "Design, build, and maintain software systems and applications."),
    ("15-1255.00", "Web Developer", "Design, create, and modify websites and web applications."),
    ("15-1211.00", "Computer Systems Analyst", "Analyze IT requirements and recommend technology solutions."),
    ("15-2051.00", "Data Scientist", "Use statistical methods and machine learning to analyze large data sets."),
    ("15-2061.00", "Data Engineer", "Design and build pipelines that transform raw data into usable formats."),
    ("15-1243.00", "Database Administrator", "Coordinate changes to computer databases and ensure system availability."),
    ("15-1244.00", "Network and Computer Systems Administrator", "Install and maintain networking hardware and software."),
    ("15-1231.00", "Computer Network Architect", "Design and build data communication networks."),
    ("15-1241.00", "Network Support Specialist", "Analyze, test, and evaluate network systems."),
    ("15-1232.00", "Computer User Support Specialist", "Provide technical assistance to computer users."),
    ("15-1221.00", "Computer and Information Research Scientist", "Invent and design new approaches to computing technology."),
    ("15-1299.00", "AI/ML Engineer", "Develop machine learning models and AI systems for production."),
    ("15-1212.00", "Information Security Analyst", "Plan and carry out security measures to protect computer systems."),
    ("15-2041.00", "Statistician", "Develop and apply mathematical or statistical theory to collect and analyze data."),
    ("15-2031.00", "Operations Research Analyst", "Use mathematics and logic to examine complex business problems."),
    ("11-3021.00", "IT Manager", "Direct and coordinate IT department activities and plan technology solutions."),
    # Business & Finance
    ("13-2011.00", "Accountant", "Examine and prepare financial records and ensure accuracy."),
    ("13-2051.00", "Financial Analyst", "Assess the performance of investments and provide guidance."),
    ("13-2041.00", "Credit Analyst", "Analyze credit risk of applicants and make lending recommendations."),
    ("11-3031.00", "Financial Manager", "Direct financial activities of an organization."),
    ("13-1111.00", "Management Analyst", "Propose ways to improve organizational efficiency."),
    ("11-1021.00", "General and Operations Manager", "Oversee day-to-day operations and plan organizational goals."),
    ("11-2021.00", "Marketing Manager", "Plan programs to generate interest in products or services."),
    ("11-2011.00", "Advertising and Promotions Manager", "Plan and coordinate advertising campaigns and promotions."),
    ("13-1161.00", "Market Research Analyst", "Research market conditions to examine sales potential and consumer preferences."),
    ("41-3099.00", "Sales Representative", "Sell products and services to businesses or individuals."),
    ("13-1151.00", "Training and Development Specialist", "Help plan, conduct, and administer training programs."),
    ("13-1071.00", "Human Resources Specialist", "Recruit, screen, and interview job applicants."),
    ("11-3121.00", "Human Resources Manager", "Plan and coordinate human resources activities."),
    ("11-9199.00", "Business Development Manager", "Identify and develop new business opportunities and partnerships."),
    ("11-3051.00", "Industrial Production Manager", "Oversee the daily operations of manufacturing plants."),
    ("11-3061.00", "Purchasing Manager", "Plan and direct procurement activities."),
    ("11-3071.00", "Transportation and Distribution Manager", "Direct logistics and distribution operations."),
    ("13-1081.00", "Logistician", "Analyze and coordinate supply chain activities."),
    ("43-3031.00", "Bookkeeping and Accounting Clerk", "Compute, classify, and record financial data."),
    # Engineering
    ("17-2071.00", "Electrical Engineer", "Design, develop, and test electrical equipment and systems."),
    ("17-2141.00", "Mechanical Engineer", "Design, develop, build, and test mechanical devices and equipment."),
    ("17-2051.00", "Civil Engineer", "Design and supervise construction of infrastructure projects."),
    ("17-2112.00", "Industrial Engineer", "Find efficient ways to eliminate waste in production processes."),
    ("17-2041.00", "Chemical Engineer", "Apply chemistry and engineering principles in production processes."),
    ("17-2011.00", "Aerospace Engineer", "Design aircraft, spacecraft, and related components."),
    ("17-2031.00", "Biomedical Engineer", "Design and develop medical devices and healthcare solutions."),
    ("17-2081.00", "Environmental Engineer", "Develop solutions to environmental problems using engineering principles."),
    ("17-2171.00", "Petroleum Engineer", "Design methods for extracting oil and gas from deposits."),
    ("17-2151.00", "Mining and Geological Engineer", "Design safe and efficient mine operations."),
    # Media & Creative
    ("27-3031.00", "Public Relations Specialist", "Create and maintain a favorable public image for organizations."),
    ("27-1024.00", "Graphic Designer", "Create visual concepts to communicate ideas to inspire and inform."),
    ("27-1011.00", "Art Director", "Formulate design concepts and presentation approaches for visual media."),
    ("27-1014.00", "Multimedia Artist and Animator", "Create special effects, animation, or other visual art for media."),
    ("27-3041.00", "Editor", "Plan, coordinate, and revise material for publication across all media."),
    ("27-3043.00", "Writer and Author", "Originate and prepare written material including articles and scripts."),
    ("27-3021.00", "Broadcast News Analyst", "Analyze, interpret, and broadcast news received from various sources."),
    ("27-2012.00", "Producer and Director", "Produce and direct stage, television, radio, and motion picture productions."),
    ("11-2031.00", "Public Relations Manager", "Direct and coordinate public relations programs and activities."),
    # Education
    ("25-1099.00", "Education Administrator", "Direct activities of education programs in schools and institutions."),
    ("25-2011.00", "Preschool Teacher", "Teach and care for children below the age of formal schooling."),
    ("25-2021.00", "Elementary School Teacher", "Teach academic subjects to students in kindergarten through grade 6."),
    ("25-2031.00", "Secondary School Teacher", "Teach students in public or private secondary schools."),
    ("25-9031.00", "Instructional Coordinator", "Develop instructional materials and train teachers."),
    ("25-3011.00", "Adult Literacy Instructor", "Teach basic education and literacy skills to adult learners."),
    # Healthcare
    ("29-1141.00", "Registered Nurse", "Provide care for patients and coordinate with healthcare workers."),
    ("29-1051.00", "Pharmacist", "Dispense medications prescribed by physicians and counsel patients."),
    ("29-1123.00", "Physical Therapist", "Provide services to restore movement and manage pain."),
    ("29-1031.00", "Dietitian and Nutritionist", "Plan food and nutrition programs and promote healthy eating."),
    ("29-2011.00", "Medical Laboratory Technologist", "Perform complex laboratory procedures to analyze body fluids."),
    ("21-1021.00", "Child and Family Social Worker", "Support families in crisis and connect them with community resources."),
    # Hospitality & Tourism
    ("11-9051.00", "Food Service Manager", "Plan, direct, and coordinate food service activities."),
    ("35-1011.00", "Chef and Head Cook", "Direct and participate in the preparation and presentation of meals."),
    ("11-9081.00", "Lodging Manager", "Plan, direct, or coordinate activities of accommodation facilities."),
    ("39-7011.00", "Tour Guide and Escort", "Escort individuals or groups on sightseeing tours."),
    ("41-2011.00", "Retail Sales Associate", "Sell merchandise and assist customers in retail establishments."),
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

    # Public Relations Specialist (27-3031.00)
    ("Strategic Communication & Public Relations", "edX (UC Berkeley)",
     "https://www.edx.org/certificates/professional-certificate/berkeleyx-strategic-communication-and-public-relations",
     "27-3031.00", 20),
    ("Introduction to Public Relations", "Coursera",
     "https://www.coursera.org/learn/introduction-to-public-relations",
     "27-3031.00", 15),

    # Graphic Designer & Art Director (27-1024.00, 27-1011.00)
    ("Google UX Design Professional Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-ux-design",
     "27-1024.00", 40),
    ("Graphic Design Specialization", "Coursera (California Institute of Arts)",
     "https://www.coursera.org/specializations/graphic-design",
     "27-1024.00", 35),
    ("Figma UI UX Design Essentials", "Udemy",
     "https://www.udemy.com/course/figma-ux-ui-design-user-experience-tutorial-course/",
     "27-1024.00", 20),
    ("Interaction Design Specialization", "Interaction Design Foundation (IxDF)",
     "https://www.interaction-design.org/courses/interaction-design-specialization",
     "27-1024.00", 50),
    ("Brand Identity Design on Domestika", "Domestika",
     "https://www.domestika.org/en/courses/categories/graphic-design",
     "27-1011.00", 25),

    # Financial Manager (11-3031.00)
    ("Financial Management Specialization", "Coursera (University of Illinois)",
     "https://www.coursera.org/specializations/financial-management",
     "11-3031.00", 50),
    ("Corporate Finance Fundamentals", "Corporate Finance Institute",
     "https://corporatefinanceinstitute.com/course/corporate-finance-fundamentals/",
     "11-3031.00", 35),
    ("CFA Level 1 Exam Prep", "CFA Institute",
     "https://www.cfainstitute.org/en/programs/cfa",
     "11-3031.00", 60),

    # Accountant (13-2011.00)
    ("Intuit Academy Bookkeeping Certificate", "Coursera (Intuit)",
     "https://www.coursera.org/professional-certificates/intuit-bookkeeping",
     "13-2011.00", 40),
    ("Financial Accounting Fundamentals", "Coursera (University of Virginia)",
     "https://www.coursera.org/learn/uva-darden-financial-accounting",
     "13-2011.00", 30),
    ("Accounting Analytics", "Coursera (University of Pennsylvania)",
     "https://www.coursera.org/learn/accounting-analytics",
     "13-2011.00", 20),
    ("IAI Certified Accountant Program", "Ikatan Akuntan Indonesia (IAI)",
     "https://iai.or.id/",
     "13-2011.00", 40),

    # Data Engineer (15-2061.00)
    ("Data Engineering on Google Cloud", "Google Cloud Skills Boost",
     "https://www.cloudskillsboost.google/paths/16",
     "15-2061.00", 45),
    ("AWS Data Analytics Specialty", "AWS Training and Certification",
     "https://aws.amazon.com/training/learn-about/analytics/",
     "15-2061.00", 30),
    ("DataCamp Data Engineer Career Track", "DataCamp",
     "https://www.datacamp.com/tracks/data-engineer",
     "15-2061.00", 60),

    # Web Developer (15-1255.00)
    ("The Complete Web Development Bootcamp", "Udemy",
     "https://www.udemy.com/course/the-complete-web-development-bootcamp/",
     "15-1255.00", 55),
    ("Learn HTML, CSS, JavaScript", "Codecademy",
     "https://www.codecademy.com/learn/paths/web-development",
     "15-1255.00", 25),
    ("Full Stack Web Development", "Purwadhika Digital Technology School",
     "https://purwadhika.com/program/web-development",
     "15-1255.00", 360),

    # Database Administrator (15-1243.00)
    ("Oracle Database Administration Fundamentals", "Oracle University",
     "https://education.oracle.com/oracle-database-administration-i/pexam_1Z0-082",
     "15-1243.00", 30),
    ("Microsoft SQL Server Administration", "Microsoft Learn",
     "https://learn.microsoft.com/en-us/training/paths/sql-server-2022/",
     "15-1243.00", 25),

    # Statistician (15-2041.00)
    ("Statistics with Python Specialization", "Coursera (University of Michigan)",
     "https://www.coursera.org/specializations/statistics-with-python",
     "15-2041.00", 40),
    ("R Programming", "Coursera (Johns Hopkins University)",
     "https://www.coursera.org/learn/r-programming",
     "15-2041.00", 20),
    ("DataCamp Statistics Fundamentals", "DataCamp",
     "https://www.datacamp.com/tracks/statistics-fundamentals-with-python",
     "15-2041.00", 30),

    # IT Manager (11-3021.00)
    ("IT Management & Leadership", "LinkedIn Learning",
     "https://www.linkedin.com/learning/topics/it-management",
     "11-3021.00", 20),
    ("Agile Leadership Principles", "PMI / Coursera",
     "https://www.coursera.org/learn/agile-leadership-principles",
     "11-3021.00", 15),

    # HR Specialist / Manager (13-1071.00, 11-3121.00)
    ("Human Resource Management Specialization", "Coursera (University of Minnesota)",
     "https://www.coursera.org/specializations/human-resource-management",
     "13-1071.00", 45),
    ("SHRM Certification Prep", "LinkedIn Learning",
     "https://www.linkedin.com/learning/paths/prepare-for-the-shrm-certification",
     "11-3121.00", 25),

    # Market Research Analyst (13-1161.00)
    ("Marketing Analytics", "Coursera (University of Virginia)",
     "https://www.coursera.org/learn/uva-darden-market-research",
     "13-1161.00", 20),

    # Logistician / Supply Chain (13-1081.00)
    ("Supply Chain Principles", "Coursera (Georgia Institute of Technology)",
     "https://www.coursera.org/learn/supply-chain-principles",
     "13-1081.00", 25),
    ("APICS CSCP Certification Prep", "APICS / ASCM",
     "https://www.ascm.org/learning-development/certifications-credentials/cscp/",
     "13-1081.00", 40),
    ("Logistics & Supply Chain Management", "ALFI Institute",
     "https://alfi.or.id/training/",
     "13-1081.00", 30),

    # Business Development Manager (11-9199.00)
    ("Business Development & B2B Sales", "Udemy",
     "https://www.udemy.com/course/business-development-and-b2b-sales/",
     "11-9199.00", 20),
    ("Salesforce Sales Cloud Certification", "Salesforce Trailhead",
     "https://trailhead.salesforce.com/en/credentials/salesrepresentative",
     "11-9199.00", 30),

    # Operations Research (15-2031.00)
    ("Business Analytics Specialization", "Coursera (University of Pennsylvania)",
     "https://www.coursera.org/specializations/business-analytics",
     "15-2031.00", 40),

    # Advertising Manager (11-2011.00)
    ("Digital Advertising on Coursera", "Coursera",
     "https://www.coursera.org/learn/digital-advertising",
     "11-2011.00", 20),
    ("HubSpot Marketing Hub Certification", "HubSpot Academy",
     "https://academy.hubspot.com/courses/hubspot-marketing-software",
     "11-2011.00", 12),

    # Civil Engineer (17-2051.00)
    ("Engineering Project Management Specialization", "Coursera (Rice University)",
     "https://www.coursera.org/specializations/engineering-project-management",
     "17-2051.00", 35),
    ("AutoCAD Civil 3D Fundamentals", "Autodesk University",
     "https://www.autodesk.com/autodesk-university/",
     "17-2051.00", 20),
    ("BIM Fundamentals for Engineers", "BIM Institute Indonesia",
     "https://www.biminstitute.co.id/",
     "17-2051.00", 20),

    # Electrical Engineer (17-2071.00)
    ("Electrical Engineering Fundamentals", "edX (Georgia Tech)",
     "https://www.edx.org/learn/electrical-engineering",
     "17-2071.00", 30),
    ("PLC Programming and Industrial Automation", "Udemy",
     "https://www.udemy.com/course/plc-programming-ladder-logic/",
     "17-2071.00", 20),

    # Industrial Engineer (17-2112.00)
    ("Lean Six Sigma Specialization", "Coursera (University System of Georgia)",
     "https://www.coursera.org/specializations/six-sigma-fundamentals",
     "17-2112.00", 40),
    ("Supply Chain Management Specialization", "Coursera (Rutgers University)",
     "https://www.coursera.org/specializations/supply-chain-management",
     "17-2112.00", 30),

    # Editor / Writer (27-3041.00, 27-3043.00)
    ("English Writing Specialization", "Coursera (Duke University)",
     "https://www.coursera.org/specializations/english-for-research-publication-purposes",
     "27-3041.00", 25),
    ("Freelance Writing for Magazines", "Coursera",
     "https://www.coursera.org/learn/freelance-writing",
     "27-3043.00", 15),

    # Multimedia Artist / Animator (27-1014.00)
    ("Digital Arts & Animation", "Skillshare",
     "https://www.skillshare.com/en/browse/animation",
     "27-1014.00", 25),
    ("Motion Design with After Effects", "LinkedIn Learning",
     "https://www.linkedin.com/learning/motion-graphics-techniques",
     "27-1014.00", 20),
    ("3D Animation with Blender", "CG Master Academy (CGMA)",
     "https://cgmasteracademy.com/",
     "27-1014.00", 40),

    # Secondary School Teacher (25-2031.00)
    ("TESOL Certificate for English Teachers", "TESOL International Association",
     "https://www.tesol.org/professional-development/certification",
     "25-2031.00", 40),
    ("Teaching English Online", "FutureLearn",
     "https://www.futurelearn.com/courses/teaching-english-online",
     "25-2031.00", 20),
    ("Learning & Teaching for Teachers", "Coursera (Hong Kong University)",
     "https://www.coursera.org/specializations/learning-and-teaching",
     "25-2031.00", 30),

    # Instructional Coordinator (25-9031.00)
    ("Instructional Design Foundations", "Coursera (University of Illinois)",
     "https://www.coursera.org/learn/instructional-design-foundations-applications",
     "25-9031.00", 20),

    # Registered Nurse (29-1141.00)
    ("Global Health Delivery", "OpenWHO (WHO)",
     "https://openwho.org/courses",
     "29-1141.00", 15),
    ("Critical Care Nursing Basics", "Coursera",
     "https://www.coursera.org/learn/critical-care-nursing-basics",
     "29-1141.00", 20),

    # Physical Therapist (29-1123.00)
    ("Exercise Prescription for Chronic Disease", "Coursera",
     "https://www.coursera.org/learn/exercise-prescription",
     "29-1123.00", 20),
    ("Sports Science Fundamentals", "FutureLearn",
     "https://www.futurelearn.com/subjects/sport-and-psychology-courses/sport-science",
     "29-1123.00", 15),
    ("NASM Personal Trainer Certification", "NASM",
     "https://www.nasm.org/personal-trainer-certification",
     "29-1123.00", 30),

    # Dietitian (29-1031.00)
    ("Nutrition and Health Specialization", "Coursera (Wageningen University)",
     "https://www.coursera.org/specializations/nutrition-health-lifestyle",
     "29-1031.00", 30),

    # Food Service Manager / Chef (11-9051.00, 35-1011.00)
    ("Professional Cooking Fundamentals", "Rouxbe Culinary RX",
     "https://rouxbe.com/cooking-school/programs",
     "11-9051.00", 30),
    ("Food Safety Management (HACCP)", "Coursera",
     "https://www.coursera.org/learn/food-safety",
     "11-9051.00", 15),
    ("Plant-Based Professional Certificate", "Rouxbe Culinary RX",
     "https://rouxbe.com/programs/plant-based-professional",
     "35-1011.00", 25),
    ("Food & Beverage Service Management", "Typsy",
     "https://typsy.com/courses",
     "35-1011.00", 15),

    # Lodging Manager / Tourism (11-9081.00, 39-7011.00)
    ("Hotel Management: Distribution, Revenue & Demand", "Coursera",
     "https://www.coursera.org/learn/hotel-management",
     "11-9081.00", 20),
    ("IATA Foundation in Travel and Tourism", "IATA Training",
     "https://www.iata.org/en/training/courses/",
     "39-7011.00", 20),

    # Indonesian platforms — broad mapping
    ("Python Programming Basics", "Dicoding Indonesia",
     "https://www.dicoding.com/academies/86",
     "15-1252.00", 15),
    ("Data Analytics Professional Certificate", "MySkill",
     "https://myskill.id/course/data-analytics",
     "15-2051.00", 20),
    ("UI/UX Design Fundamentals", "Binar Academy",
     "https://binaracademy.com/course/ux-design",
     "27-1024.00", 30),
    ("Data Science Bootcamp", "Hacktiv8",
     "https://hacktiv8.com/fullstack-data-science/",
     "15-2051.00", 300),
    ("Digital Marketing Fundamentals", "Skill Academy",
     "https://skillacademy.com/category/marketing-digital",
     "11-2021.00", 15),
    ("Project Management Professional", "Rakamin Academy",
     "https://www.rakamin.com/master-class/project-management",
     "13-1111.00", 20),
    ("Digital Marketing Scholarship", "Digital Talent Scholarship (DTS Kominfo)",
     "https://digitalent.kominfo.go.id/",
     "11-2021.00", 40),
    ("Data Analytics with Python", "Karier.mu",
     "https://karier.mu/kelas/data-analytics",
     "15-2051.00", 25),
    ("Cybersecurity Fundamentals", "Alterra Academy",
     "https://academy.alterra.id/",
     "15-1212.00", 30),

    # Cloud certifications
    ("AWS Cloud Practitioner Essentials", "AWS Training and Certification",
     "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/",
     "15-1244.00", 12),
    ("Microsoft Azure Fundamentals AZ-900", "Microsoft Learn",
     "https://learn.microsoft.com/en-us/training/paths/microsoft-azure-fundamentals-describe-cloud-concepts/",
     "15-1244.00", 15),
    ("Google Cloud Associate Cloud Engineer", "Google Cloud Skills Boost",
     "https://www.cloudskillsboost.google/paths/11",
     "15-1244.00", 50),
    ("Cisco CCNA Networking Fundamentals", "Cisco Networking Academy",
     "https://www.netacad.com/courses/networking",
     "15-1244.00", 70),
    ("Red Hat Enterprise Linux Administration", "Red Hat Training",
     "https://www.redhat.com/en/services/training-and-certification",
     "15-1244.00", 40),

    # Project & Scrum certifications
    ("PMP Certification Prep", "Project Management Institute (PMI)",
     "https://www.pmi.org/certifications/project-management-pmp",
     "13-1111.00", 35),
    ("Professional Scrum Master I", "Scrum.org",
     "https://www.scrum.org/assessments/professional-scrum-master-i-certification",
     "13-1111.00", 16),

    # IBM & global tech
    ("IBM Data Science Professional Certificate", "Coursera (IBM)",
     "https://www.coursera.org/professional-certificates/ibm-data-science",
     "15-2051.00", 130),
    ("Google Data Analytics Professional Certificate", "Coursera (Google)",
     "https://www.coursera.org/professional-certificates/google-data-analytics",
     "15-2051.00", 160),
    ("AI For Everyone", "Coursera (DeepLearning.AI)",
     "https://www.coursera.org/learn/ai-for-everyone",
     "15-1299.00", 10),
    ("HarvardX CS50: Introduction to Computer Science", "edX (Harvard University)",
     "https://cs50.harvard.edu/x/",
     "15-1252.00", 100),
    ("Pluralsight DevOps Skills Assessment", "Pluralsight",
     "https://www.pluralsight.com/product/skills/assessments",
     "15-1252.00", 20),
    ("CFA Investment Fundamentals", "CFA Institute",
     "https://www.cfainstitute.org/",
     "13-2051.00", 120),
    ("Financial Modeling & Valuation (Advanced)", "Corporate Finance Institute",
     "https://corporatefinanceinstitute.com/certifications/financial-modeling-valuation-analyst-fmva-certification/",
     "13-2051.00", 45),
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
    "15-1243.00": ["SQL Server", "Oracle DB", "PostgreSQL", "MySQL", "Backup & Recovery", "Performance Tuning", "Database Security"],
    "15-2061.00": ["Python", "Apache Spark", "SQL", "ETL", "Apache Kafka", "Cloud Platforms", "Data Warehousing", "Airflow"],
    "15-1255.00": ["HTML/CSS", "JavaScript", "React", "Node.js", "Responsive Design", "Git", "WordPress", "SEO Basics"],
    "15-2041.00": ["R", "Python", "SPSS", "Statistical Analysis", "Regression", "Hypothesis Testing", "Data Visualization"],
    "15-2031.00": ["Python", "Linear Programming", "Simulation", "Excel", "R", "Operations Research", "Supply Chain Modeling"],
    "13-1161.00": ["Survey Design", "Data Analysis", "SPSS", "Excel", "Report Writing", "Google Analytics", "Market Segmentation"],
    "13-1071.00": ["Recruitment", "ATS Systems", "Labor Law", "Performance Management", "HRIS", "Employee Relations"],
    "11-3121.00": ["HR Strategy", "Organizational Development", "Talent Management", "Labor Relations", "HR Analytics", "Change Management"],
    "11-9199.00": ["Business Development", "Sales Strategy", "Partnership Management", "Market Analysis", "Negotiation", "CRM"],
    "11-3021.00": ["IT Governance", "Budgeting", "Vendor Management", "ITIL", "Project Oversight", "Risk Management"],
    "13-2041.00": ["Credit Analysis", "Financial Statements", "Risk Assessment", "Banking Regulations", "Excel", "Financial Modeling"],
    "11-2011.00": ["Advertising Strategy", "Media Planning", "Campaign Management", "Creative Direction", "Brand Management", "ROI Analysis"],
    "11-3051.00": ["Production Planning", "Quality Control", "ERP/MRP", "Lean Manufacturing", "Workforce Management"],
    "11-3061.00": ["Procurement Strategy", "Supplier Management", "Contract Negotiation", "Spend Analysis", "Category Management"],
    "11-3071.00": ["Fleet Management", "Route Optimization", "Customs Compliance", "Warehouse Operations", "TMS Software"],
    "13-1081.00": ["Inventory Management", "ERP Systems", "Warehouse Management", "Demand Planning", "Freight Logistics", "SAP"],
    "43-3031.00": ["Bookkeeping", "Data Entry", "Payroll Processing", "Accounting Software", "Financial Reporting"],
    "17-2071.00": ["AutoCAD", "Circuit Design", "Power Systems", "PLC Programming", "Electrical Safety", "MATLAB"],
    "17-2141.00": ["AutoCAD", "SolidWorks", "Thermodynamics", "Materials Science", "FEA/FEM", "Manufacturing Processes"],
    "17-2051.00": ["AutoCAD", "Civil 3D", "Structural Analysis", "Project Management", "Building Codes", "ETABS"],
    "17-2112.00": ["Lean Manufacturing", "Six Sigma", "AutoCAD", "SAP", "Process Improvement", "Statistical Process Control"],
    "17-2041.00": ["Chemical Process Design", "HYSYS/Aspen Plus", "Safety Protocols", "Process Optimization", "Material Balance"],
    "17-2011.00": ["Aerodynamics", "Structural Analysis", "Flight Systems", "CAD/CAE Tools", "MATLAB/Simulink"],
    "17-2031.00": ["Medical Device Design", "FDA Regulations", "Biocompatibility", "Signal Processing", "Clinical Trials"],
    "17-2081.00": ["Environmental Assessment", "EIA", "Waste Management", "Air Quality Monitoring", "Environmental Law", "GIS"],
    "27-1011.00": ["Brand Identity", "Typography", "Visual Communication", "Adobe Creative Suite", "Client Management"],
    "27-1014.00": ["Adobe Premiere", "After Effects", "Cinema 4D", "Blender", "Storyboarding", "Animation Principles"],
    "27-3041.00": ["Content Writing", "Editing", "SEO Writing", "CMS", "Fact-checking", "Research Skills", "Publishing"],
    "27-3043.00": ["Creative Writing", "Research", "Content Strategy", "Editing", "Storytelling", "Publishing"],
    "27-3021.00": ["News Writing", "Research", "Broadcast Journalism", "Social Media", "Video Editing"],
    "27-2012.00": ["Production Management", "Script Writing", "Budget Management", "Crew Management", "Post-Production"],
    "11-2031.00": ["PR Strategy", "Media Relations", "Stakeholder Engagement", "Crisis Management", "Brand Reputation"],
    "25-2031.00": ["Lesson Planning", "Classroom Management", "Assessment Design", "Teaching Methods", "TESOL/TEFL"],
    "25-9031.00": ["Curriculum Design", "LMS Administration", "Teacher Training", "Instructional Design", "E-learning"],
    "25-3011.00": ["Adult Education", "Literacy Instruction", "Curriculum Adaptation", "Assessment", "Communication"],
    "25-2011.00": ["Early Childhood Education", "Child Development", "Play-based Learning", "Parent Communication"],
    "25-2021.00": ["Elementary Education", "Classroom Management", "Lesson Planning", "Differentiated Instruction"],
    "29-1051.00": ["Drug Dispensing", "Pharmacology", "Drug Interaction", "Patient Counseling", "Clinical Pharmacy"],
    "29-1123.00": ["Manual Therapy", "Exercise Prescription", "Anatomy", "Rehabilitation", "Patient Assessment"],
    "29-1031.00": ["Nutritional Assessment", "Meal Planning", "Clinical Nutrition", "Dietary Guidelines", "Food Science"],
    "29-2011.00": ["Laboratory Testing", "Blood Analysis", "Microbiology", "Medical Equipment", "Quality Control"],
    "21-1021.00": ["Case Management", "Social Assessment", "Crisis Intervention", "Community Resources", "Child Development"],
    "11-9051.00": ["Restaurant Management", "Food Safety (HACCP)", "Cost Control", "Menu Planning", "Staff Management"],
    "35-1011.00": ["Culinary Arts", "Menu Development", "Food Safety", "Kitchen Management", "Food Presentation"],
    "11-9081.00": ["Hotel Operations", "Revenue Management", "Guest Relations", "Front Office Management", "Hospitality Software"],
    "39-7011.00": ["Destination Knowledge", "Language Skills", "Customer Service", "Tour Planning", "Cultural Awareness"],
    "41-2011.00": ["Point of Sale Systems", "Cash Handling", "Customer Service", "Inventory Tracking", "Retail Software"],
    "15-1232.00": ["Hardware Troubleshooting", "Windows/macOS/Linux", "Help Desk", "Network Basics", "Remote Support"],
    "15-1241.00": ["Network Monitoring", "Troubleshooting", "VPN", "Firewalls", "TCP/IP", "Network Documentation"],
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

ANALYZE_MODEL = "gemini-3.5-flash"

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
            "GEMINI_API_KEY is not configured. "
            "Add it to .streamlit/secrets.toml or the Streamlit Cloud Secrets dashboard."
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
        ("◉", "Parsing profile data..."),
        ("◆", "Scanning O*NET & SKKNI databases..."),
        ("▲", "Mapping career trajectories..."),
        ("◈", "Calculating skill gap metrics..."),
        ("★", "Finalizing recommendations..."),
    ]
    ph = st.empty()
    for i, (icon, step) in enumerate(steps[:-1]):
        pct = int((i + 1) / len(steps) * 100)
        with ph.container():
            st.markdown(f"""
            <div style="text-align:center;padding:3rem 1rem;background:var(--warm-loading);border-radius:8px;">
              <div style="font-size:3rem;margin-bottom:1rem;">{icon}</div>
              <div style="font-size:1rem;font-weight:600;color:var(--copper);margin-bottom:1rem;
                          font-family:'Playfair Display',Georgia,serif;font-style:italic;">{step}</div>
              <div style="background:var(--warm-border);border-radius:9999px;height:5px;overflow:hidden;max-width:400px;margin:0 auto;">
                <div style="background:linear-gradient(90deg,var(--copper),var(--gold));height:100%;
                            width:{pct}%;border-radius:9999px;"></div>
              </div>
              <div style="font-size:0.78rem;color:var(--copper-muted);margin-top:0.5rem;">{pct}%</div>
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
        /* ── Core neutrals ─────────────────────────────── */
        --white:          #FFFFFF;
        --charcoal:       #2C2C2C;
        --charcoal-mid:   #4A4A4A;
        --charcoal-soft:  #6B6B6B;
        /* ── Brand: copper / gold ───────────────────────── */
        --copper:         #A17F3E;
        --copper-dark:    #7D6130;
        --copper-light:   #C9AC72;
        --copper-muted:   #9A8060;
        --gold:           #C09A51;
        --gold-pale:      #F5EDD8;
        --gold-border:    #D4B87A;
        --gold-warm:      #FFFDF9;
        /* ── Warm backgrounds ───────────────────────────── */
        --app-shell:      #DDD8CE;
        --warm-bg:        #F8F9FA;
        --warm-border:    #E8E0D5;
        --warm-muted:     #F2EDE6;
        --warm-ivory:     #FFFDF8;
        --warm-cream:     #FAF5EB;
        --warm-loading:   #FAF8F5;
        /* ── Semantic ────────────────────────────────────── */
        --success:        #2D6A4F;
        --success-bg:     #D8F3DC;
        --danger:         #9B2335;
        --danger-bg:      #FAE0E4;
        --danger-req:     #C0392B;
        --blue-dark:      #2A4490;
        --blue-light:     #E8EDF8;
        /* ── Warning (roadmap fallback) ─────────────────── */
        --warn-bg:        #FEF3C7;
        --warn-border:    #FDE68A;
        --warn-text:      #92400E;
        /* ── Typography ──────────────────────────────────── */
        --serif:          'Playfair Display', Georgia, 'Times New Roman', serif;
        --sans:           'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Global reset & typography ─────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: var(--sans) !important;
        color: var(--charcoal) !important;
    }

    /* ── App shell — warm tan frame visible on left/right sides ────────────── */
    .stApp {
        background-color: var(--app-shell) !important;
    }

    /* ── PHASE 1: Hide Streamlit native chrome ──────────────────────────────── */
    #MainMenu        { visibility: hidden; }
    header           { visibility: hidden; }
    footer           { visibility: hidden; }
    [data-testid="stHeader"] { visibility: hidden; height: 0 !important; }

    /* ── PHASE 1: Main content block — padding-top matches tall topbar ──────── */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        background-color: var(--warm-bg) !important;
        padding-top:   5.5rem !important;
        padding-left:  2rem   !important;
        padding-right: 2rem   !important;
        max-width: 100% !important;
    }

    /* ── PHASE 2: Fixed topbar — ~56px total height ──────────────────────────── */
    .pf-topbar {
        position: fixed;
        top:   0;
        left:  0;
        right: 0;
        width: 100%;
        box-sizing: border-box;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 2rem;
        background: #FFFFFF;
        border-bottom: 1px solid #E8E0D5;
        box-shadow: 0 2px 8px rgba(44,44,44,.05);
    }
    .pf-logo {
        font-family: var(--serif) !important;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--copper) !important;
        letter-spacing: 0.02em;
    }
    .pf-logo span { color: var(--gold) !important; font-style: italic; }

    /* ── PHASE 3: Step indicator pills ─────────────────────────────────────── */
    .pf-steps {
        display: flex;
        gap: 0.35rem;
        align-items: center;
        flex-wrap: wrap;
    }
    .step-pending,
    .step-active,
    .step-done {
        font-family: var(--sans);
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.06em;
        border-radius: 9999px;
        padding: 4px 12px;
        line-height: 1.4;
        white-space: nowrap;
    }
    .step-pending {
        background: #F2EDE6;
        color: #6B6B6B;
        border: none;
    }
    .step-active {
        background: #C09A51;
        color: #FFFFFF;
        border: 1px solid #C09A51;
    }
    .step-done {
        background: #D8F3DC;
        color: #2D6A4F;
        border: none;
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

    /* ── Card — generic white card (st-card utility) ───────────────────────── */
    .st-card {
        background: var(--white);
        border: 1px solid var(--warm-border);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 6px rgba(44,44,44,.05);
    }
    .st-card-section-label {
        font-family: var(--sans);
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--copper);
        margin-bottom: 0.6rem;
        padding-bottom: 0.35rem;
        border-bottom: 1px solid var(--warm-border);
    }

    /* ── Card — gold/copper accent (Best Match) ────────────────────────────── */
    .pf-card-gold {
        border: 2px solid var(--copper) !important;
        box-shadow: 0 6px 20px rgba(161,127,62,.16) !important;
        background: linear-gradient(160deg, var(--gold-warm) 0%, var(--white) 100%) !important;
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
    .pf-badge-blue  { background: var(--blue-light);  color: var(--blue-dark); }
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
        background: linear-gradient(160deg, var(--warm-ivory) 0%, var(--warm-cream) 60%, var(--gold-pale) 100%);
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

    /* ── PHASE 4: Tab strip — each tab fills its half, text centered ───────── */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #E8E0D5 !important;
        gap: 0 !important;
        justify-content: stretch !important;
        background: transparent !important;
        width: 100% !important;
    }
    /* Inactive tab — centered in its half */
    .stTabs [data-baseweb="tab"] {
        flex: 1 !important;
        justify-content: center !important;
        text-align: center !important;
        font-family: var(--sans) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #6B6B6B !important;
        padding: 0.65rem 1rem !important;
        border-radius: 0 !important;
        letter-spacing: 0.02em !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
    }
    /* Active tab */
    .stTabs [aria-selected="true"] {
        color: #7D6130 !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #A17F3E !important;
        background: rgba(161,127,62,.04) !important;
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

    /* ── Streamlit scroll context — keep default scroll behaviour ───────────── */
    section[data-testid="stMain"] {
        overflow-y: auto !important;
    }

    /* ── Logo wrapper ─────────────────────────────────────────────────────────── */
    .pf-logo-wrap { display: flex; align-items: center; }

    /* ── Profile card ─────────────────────────────────────────────────────────── */
    .pf-profile-card {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        background: var(--white);
        border: 1px solid var(--warm-border);
        border-radius: 4px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(44,44,44,.05);
    }
    .pf-avatar {
        width: 64px; height: 64px; border-radius: 50%;
        background: var(--gold-pale);
        border: 2px solid var(--copper);
        display: flex; align-items: center; justify-content: center;
        font-family: var(--serif); font-size: 1.5rem;
        color: var(--copper); font-weight: 700;
        overflow: hidden; flex-shrink: 0;
    }
    .pf-avatar img { width:100%; height:100%; object-fit:cover; border-radius:50%; }
    .pf-profile-name {
        font-family: var(--serif); font-size: 1.15rem;
        font-weight: 700; color: var(--charcoal);
    }
    .pf-profile-role {
        font-size: 0.78rem; color: var(--copper);
        font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; margin-top: 0.1rem;
    }
    .pf-achievement-row { display:flex; gap:0.5rem; flex-wrap:wrap; margin-top:0.5rem; }
    .pf-achievement {
        display: inline-flex; align-items: center; gap: 0.3rem;
        background: var(--gold-pale); border: 1px solid var(--gold-border);
        border-radius: 2px; padding: 0.18rem 0.55rem;
        font-size: 0.68rem; font-weight: 600; color: var(--copper-dark);
        text-transform: uppercase; letter-spacing: 0.06em;
    }

    /* ── Equal-height columns — consolidated ─────────────────────────────────── */

    /* 1. Row stretches to tallest column */
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }

    /* 2. Every column becomes a flex-column (fills row height) */
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
    }

    /* 3. Streamlit injects an intermediate <div> between stVerticalBlock
          and the actual content / stVerticalBlockBorderWrapper.
          Give it flex:1 so it stretches to fill the column. */
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] > div {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        min-height: 0 !important;
    }

    /* 4. st.container(border=True) wrapper fills its intermediate div
          and enforces minimum height so both upload cards are equal */
    [data-testid="stVerticalBlockBorderWrapper"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        min-height: 360px !important;
    }

    /* 4b. Inner stVerticalBlock inside border wrapper — also flex column */
    [data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* 4c. File uploader stretches to fill remaining card height */
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFileUploader"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFileUploaderDropzone"] {
        flex: 1 !important;
        min-height: 120px !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* 5. pf-result-card keeps its own flex growth */
    .pf-result-card {
        flex: 1;
        min-height: 420px;
        display: flex;
        flex-direction: column;
    }

    /* ── Compact upload zone ──────────────────────────────────────────────────── */
    .pf-cert-zone {
        border: 1.5px dashed var(--warm-border);
        border-radius: 4px;
        padding: 0.6rem 1rem;
        text-align: center;
        color: var(--charcoal-soft);
        font-size: 0.78rem;
        background: var(--warm-muted);
    }

    /* ── Required asterisk ────────────────────────────────────────────────────── */
    .pf-req { color: var(--danger-req); font-weight: 700; margin-left: 2px; }

    /* ── Roadmap provider badge ───────────────────────────────────────────────── */
    .provider-badge {
        display: inline-block;
        background: var(--warm-muted); color: var(--charcoal-mid);
        font-size: 0.72rem; font-weight: 700;
        padding: 3px 8px; border-radius: 3px;
        margin-bottom: 0.3rem;
    }
    .roadmap-card {
        background: var(--white);
        border-left: 4px solid var(--copper);
        padding: 1rem; border-radius: 4px;
        margin-bottom: 0; box-shadow: 0 2px 8px rgba(0,0,0,.06);
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

_STEPS_ORDER = ["landing", "upload", "results", "skill_gap", "roadmap", "dashboard"]
_STEP_LABELS = {
    "landing":   "Home",
    "upload":    "Upload CV",
    "results":   "Matches",
    "skill_gap": "Skill Gap & Plan",
    "roadmap":   "Roadmap",
    "dashboard": "Dashboard",
}

def _render_topbar():
    current = st.session_state.get("pf_step", "landing")
    # treat choose_plan as skill_gap for nav highlighting
    if current == "choose_plan":
        current = "skill_gap"
    idx_current = _STEPS_ORDER.index(current) if current in _STEPS_ORDER else 0
    steps_html = ""
    for i, step in enumerate(_STEPS_ORDER[1:], 1):
        label = _STEP_LABELS[step]
        if i < idx_current:
            cls = "step-done"
        elif step == current:
            cls = "step-active"
        else:
            cls = "step-pending"
        steps_html += f'<span class="{cls}">{label}</span>'

    logo_img = _logo_tag()
    if logo_img:
        logo_html = f'<div class="pf-logo-wrap">{logo_img}</div>'
    else:
        logo_html = (
            '<div class="pf-logo">Path<span>finder</span>'
            '<span style="font-size:.65rem;font-weight:400;color:var(--copper-muted);'
            'letter-spacing:.12em;text-transform:uppercase;'
            'font-family:\'Inter\',sans-serif;margin-left:.6rem;'
            'vertical-align:middle;">Career Intelligence</span></div>'
        )

    st.markdown(f"""
    <div class="pf-topbar">
        {logo_html}
        <div class="pf-steps">{steps_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def _init_session():
    defaults = {
        "pf_step":                "landing",
        "pf_session_id":          str(uuid.uuid4()),
        "pf_analysis":            None,
        "pf_selected_match":      None,
        "pf_selected_plan":       None,
        "pf_study_hours_per_day": 2,
        "pf_days_per_week":       5,
        "pf_roadmap_courses":     [],
        "pf_completed_courses":   set(),
        "pf_cert_verify":         {},
        "pf_work_entries":        [{"id": 0}],
        "pf_work_counter":        1,
        "pf_profile_photo_b64":   "",
        "pf_manual_tech_sel":     [],
        "pf_manual_soft_sel":     [],
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — 3-Column Manual Entry Form
# ══════════════════════════════════════════════════════════════════════════════

def _render_manual_form():
    all_majors = ["-- Select Major --"] + get_all_majors()
    all_titles = ["-- Select Role --"] + get_all_onet_titles() + ["Other"]

    # ── field label helper ────────────────────────────────────────────────────
    def _lbl(text: str, required: bool = False) -> None:
        req = '<span class="pf-req">*</span>' if required else ""
        st.markdown(
            f'<span style="font-size:0.7rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:.08em;color:var(--charcoal-mid);">{text}</span>{req}',
            unsafe_allow_html=True,
        )

    col_edu, col_work, col_skills = st.columns([1, 1.2, 1], gap="large")

    # ── Col 1: Education (all except Graduation Year) ─────────────────────────
    with col_edu:
        st.markdown('<div class="pf-section-header">Education</div>', unsafe_allow_html=True)
        _lbl("Full Name", required=True)
        full_name = st.text_input(
            "Full Name", placeholder="e.g. John Smith",
            key="pf_manual_name", label_visibility="collapsed",
        )
        _lbl("Education Level", required=True)
        edu_options = [
            "Junior High School", "Senior High School / Vocational",
            "Diploma (D1/D2)", "Associate Degree (D3)",
            "Bachelor's Degree (S1)", "Master's Degree (S2)",
            "Doctoral Degree (PhD / S3)", "Professional Degree",
            "Non-Degree / Other",
        ]
        edu_level = st.selectbox(
            "Education Level", edu_options,
            key="pf_manual_edu", label_visibility="collapsed",
        )
        _lbl("Major / Field of Study", required=True)
        major_choice = st.selectbox(
            "Major", all_majors,
            key="pf_manual_major_sel", label_visibility="collapsed",
        )
        major = "" if major_choice == "-- Select Major --" else major_choice
        _lbl("Institution / University")
        institution = st.text_input(
            "Institution / University", placeholder="e.g. University of Indonesia",
            key="pf_manual_inst", label_visibility="collapsed",
        )

    # ── Col 2: Work Experience (all except Add Experience button) ─────────────
    with col_work:
        st.markdown('<div class="pf-section-header">Work Experience</div>',
                    unsafe_allow_html=True)
        entries = st.session_state["pf_work_entries"]
        for idx, entry in enumerate(entries):
            eid = entry["id"]
            job_choice = st.selectbox(
                f"Job Title #{idx + 1}", all_titles, key=f"pf_job_title_sel_{eid}",
            )
            if job_choice in ("-- Select Role --", "Other"):
                st.text_input(
                    "Custom Title", key=f"pf_job_title_txt_{eid}",
                    placeholder="e.g. Data Analyst",
                )
            st.text_input(
                "Company / Organization", key=f"pf_company_{eid}",
                placeholder="e.g. PT Tokopedia",
            )
            dc1, dc2 = st.columns(2)
            with dc1:
                st.selectbox(
                    "Start Year",
                    ["--"] + [str(y) for y in range(2030, 1980, -1)],
                    key=f"pf_start_{eid}",
                )
            with dc2:
                st.selectbox(
                    "End Year",
                    ["--", "Present"] + [str(y) for y in range(2030, 1980, -1)],
                    key=f"pf_end_{eid}",
                )
            if len(entries) > 1:
                if st.button("Remove", key=f"pf_remove_{eid}", use_container_width=True):
                    st.session_state["pf_work_entries"] = [
                        e for e in entries if e["id"] != eid
                    ]
                    st.rerun()

    # ── Col 3: Skills & Certifications ────────────────────────────────────────
    with col_skills:
        st.markdown('<div class="pf-section-header">Skills & Certifications</div>',
                    unsafe_allow_html=True)

        # Technical Skills
        _lbl("Technical Skills", required=True)
        selected_tech = st.multiselect(
            "Technical Skills",
            options=_TECHNICAL_SKILLS,
            default=st.session_state.get("pf_manual_tech_sel", []),
            key="pf_manual_tech_sel",
            placeholder="Type to search technical skills...",
            label_visibility="collapsed",
        )

        # Soft Skills
        _lbl("Soft Skills")
        selected_soft = st.multiselect(
            "Soft Skills",
            options=_SOFT_SKILLS,
            default=st.session_state.get("pf_manual_soft_sel", []),
            key="pf_manual_soft_sel",
            placeholder="Type to search soft skills...",
            label_visibility="collapsed",
        )

        # Unlisted skills
        extra_skills = st.text_input(
            "Add unlisted skills (comma-separated)",
            placeholder="e.g. QGIS, Revit, Arena...",
            key="pf_extra_skills",
        )
        extra_list = [s.strip() for s in extra_skills.split(",") if s.strip()]
        all_user_skills = list(selected_tech) + list(selected_soft) + extra_list
        if all_user_skills:
            pills_html = " ".join(
                f'<span class="pf-pill">{s}</span>' for s in all_user_skills
            )
            st.markdown(pills_html, unsafe_allow_html=True)
            st.caption(f"{len(all_user_skills)} skill(s) selected")

        st.markdown("---")
        _lbl("Certifications / Licenses")
        cert_files = st.file_uploader(
            "Certificates (PDF / PNG / JPG)",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            label_visibility="visible",
            key="pf_cert_files",
        )
        if cert_files:
            for cf in cert_files:
                st.markdown(
                    f'<span class="pf-badge pf-badge-green">Uploaded: {cf.name}</span>',
                    unsafe_allow_html=True,
                )

    # ── Bottom-aligned row: Graduation Year | Add Experience | Cert text ──────
    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    bot_edu, bot_work, bot_skills = st.columns([1, 1.2, 1], gap="large")

    with bot_edu:
        grad_year = st.selectbox(
            "Graduation Year",
            ["--"] + [str(y) for y in range(2030, 1985, -1)],
            key="pf_manual_grad",
        )

    with bot_work:
        # Spacer to visually align button with selects in other columns
        st.markdown('<div style="height:1.55rem;"></div>', unsafe_allow_html=True)
        if st.button("+ Add Experience", use_container_width=True):
            nid = st.session_state["pf_work_counter"]
            st.session_state["pf_work_entries"].append({"id": nid})
            st.session_state["pf_work_counter"] += 1
            st.rerun()

    with bot_skills:
        cert_text = st.text_area(
            "Or list certifications manually",
            placeholder="AWS Certified Developer (2023)\nGoogle Data Analytics Certificate",
            height=70, key="pf_cert_text",
        )

    return {
        "full_name":       full_name,
        "edu_level":       edu_level,
        "major":           major,
        "institution":     institution,
        "grad_year":       grad_year,
        "selected_skills": all_user_skills,
        "raw_skills":      ", ".join(all_user_skills),
        "cert_text":       cert_text,
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
        start   = st.session_state.get(f"pf_start_{eid}", "--")
        end     = st.session_state.get(f"pf_end_{eid}", "--")
        if job_title and job_title not in ("(Select or type below)", ""):
            lines.append(f"  - {job_title} at {company} ({start}–{end})")
    lines += ["", "Skills:"]
    for sk in form_data.get("selected_skills", []) or [s.strip() for s in form_data.get("raw_skills","").split(",") if s.strip()]:
        if sk:
            lines.append(f"  - {sk}")
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
    st.caption("Matched against O*NET taxonomy and SKKNI competency framework. Study hours estimate based on Regular plan (5 days/week, 2 hours/day).")

    result_cols = st.columns(4, gap="medium")

    # Fixed-reference plan for hours estimate on this card (Regular: 5d x 2h = 10h/wk)
    _REF_HPW = 10  # 5 days x 2 hours

    def _fmt_duration(total_hrs: float) -> str:
        if not total_hrs:
            return "N/A"
        wks = math.ceil(total_hrs / _REF_HPW)
        if wks == 0:
            days = math.ceil(total_hrs / 2)
            return f"{days} day(s)"
        return f"~{wks} wk(s)"

    for i, match in enumerate(matches[:3]):
        col      = result_cols[i]
        is_best  = (i == 0)
        soc      = match.get("soc_code", "")
        score    = match.get("match_score", 0)
        gap_count = len(match.get("skill_gaps", []))

        # Ensure total_course_hours is populated from DB (fixes 0h bug)
        total_hrs = match.get("total_course_hours") or get_total_hours(soc)
        if not total_hrs and match.get("courses"):
            total_hrs = sum(c.get("hours", 0) for c in match["courses"])
        match["total_course_hours"] = total_hrs

        with col:
            # Badge row — always present (keeps columns aligned)
            if is_best:
                st.markdown('<span class="pf-badge pf-badge-gold">Best Match</span>',
                            unsafe_allow_html=True)
            else:
                st.markdown('<span style="display:inline-block;height:1.4rem;"></span>',
                            unsafe_allow_html=True)

            card_cls = "pf-card pf-card-gold" if is_best else "pf-card"
            st.markdown(f"""
            <div class="{card_cls}" style="padding:1rem;min-height:72px;">
              <div style="font-size:1.05rem;font-weight:700;color:var(--charcoal);margin-bottom:0.2rem;">
                {match.get('title','')}
              </div>
              <div style="font-size:0.72rem;color:var(--charcoal-soft);font-family:'Inter',sans-serif;">{soc}</div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(score / 100)
            st.caption(f"**{score}%** match · {gap_count} gap(s)")

            with st.expander("Why this role?"):
                st.write(match.get("description", ""))

            with st.expander("Skill Gaps"):
                gaps = match.get("skill_gaps", [])
                if gaps:
                    pills = " ".join(f'<span class="pf-pill">{g}</span>' for g in gaps)
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.success("No major gaps detected.")

            st.metric(
                "Total Study Hours",
                f"{int(total_hrs)}h" if total_hrs else "N/A",
                _fmt_duration(total_hrs)
            )

            if st.button("Select This Career", key=f"pf_sel_{i}",
                         use_container_width=True,
                         type="primary" if is_best else "secondary"):
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
        st.markdown(
            '<span style="display:inline-block;height:1.4rem;"></span>',
            unsafe_allow_html=True
        )
        st.markdown("""
        <div class="pf-card pf-card-dashed pf-result-card"
             style="text-align:center;padding:1.5rem 1rem;justify-content:center;align-items:center;">
          <div style="font-size:1.8rem;color:var(--copper);">+</div>
          <div style="font-weight:600;color:var(--charcoal);font-size:0.95rem;">Add Profession</div>
          <div style="font-size:0.75rem;color:var(--copper-muted);margin-top:0.2rem;">Browse all O*NET roles</div>
        </div>
        """, unsafe_allow_html=True)
        all_onet = get_all_onet_titles()
        custom_t = st.selectbox(
            "Search O*NET Roles", ["--"] + all_onet, key="pf_custom_onet"
        )
        if custom_t and custom_t != "--":
            soc = get_soc_for_title(custom_t)
            if soc:
                hrs     = get_total_hours(soc)
                courses = get_courses_for_onet(soc)
                if courses:
                    st.metric(
                        "Total Study Hours",
                        f"{int(hrs)}h" if hrs else "-",
                        _fmt_duration(hrs) if hrs else ""
                    )
                    if st.button("Add & Select", key="pf_add_custom",
                                 use_container_width=True, type="primary"):
                        gaps = _compute_skill_gaps(soc, detected_skills or [])
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
                else:
                    st.markdown(
                        '<div class="pf-badge pf-badge-red" style="display:block;'
                        'text-align:center;padding:0.4rem 0.6rem;margin-bottom:0.5rem;">'
                        'No courses available for this role</div>',
                        unsafe_allow_html=True
                    )
                    st.metric("Total Study Hours", "-", "")

    st.markdown("---")
    if st.button("Retake Analysis"):
        st.session_state["pf_step"] = "upload"
        st.session_state["pf_analysis"] = None
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SKILL GAP PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_skill_gap():
    """Merged Skill Gap Analysis + Study Plan page."""
    match    = st.session_state.get("pf_selected_match", {})
    analysis = st.session_state.get("pf_analysis", {})
    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    soc      = match.get("soc_code", "")
    detected = analysis.get("detected_skills", []) if analysis else []
    gaps     = match.get("skill_gaps", [])
    score    = match.get("match_score", 50)
    total_hrs = match.get("total_course_hours") or get_total_hours(soc)
    if not total_hrs and match.get("courses"):
        total_hrs = sum(c.get("hours", 0) for c in match["courses"])

    # ── Section 1: Skill Gap Analysis ─────────────────────────────────────────
    st.markdown(f"## Skill Gap & Study Plan")
    st.markdown(f"**Target Role:** {match.get('title','')} &nbsp;|&nbsp; Match Score: **{score}%**")
    st.progress(score / 100)
    st.markdown("")

    st.markdown(
        '<div class="pf-section-header">Competency Assessment</div>',
        unsafe_allow_html=True
    )
    st.caption(
        "Skill requirements are sourced from the O*NET database (U.S. Department of Labor) "
        "and cross-referenced with Indonesian SKKNI competency standards."
    )

    col_have, col_gap = st.columns(2, gap="large")
    with col_have:
        st.markdown(
            '<div style="font-family:\'Playfair Display\',serif;font-size:1rem;'
            'font-weight:700;color:var(--success);margin-bottom:0.6rem;">'
            '&#9679; Skills You Have</div>',
            unsafe_allow_html=True
        )
        if detected:
            pills = " ".join(
                f'<span class="pf-badge pf-badge-green">{sk}</span>' for sk in detected
            )
            st.markdown(pills, unsafe_allow_html=True)
            st.caption(f"{len(detected)} verified skill(s) from your profile")
        else:
            st.info("No skills detected. Fill in the manual form to show your skills here.")

    with col_gap:
        st.markdown(
            '<div style="font-family:\'Playfair Display\',serif;font-size:1rem;'
            'font-weight:700;color:var(--danger);margin-bottom:0.6rem;">'
            '&#9679; Skills to Acquire</div>',
            unsafe_allow_html=True
        )
        if gaps:
            pills = " ".join(
                f'<span class="pf-badge pf-badge-red">{sk}</span>' for sk in gaps
            )
            st.markdown(pills, unsafe_allow_html=True)
            st.caption(f"{len(gaps)} gap(s) based on O*NET role requirements")
        else:
            st.success("No significant skill gaps detected for this role.")

    st.markdown("---")

    # ── Section 2: Study Plan ─────────────────────────────────────────────────
    st.markdown(
        '<div class="pf-section-header">Study Plan</div>',
        unsafe_allow_html=True
    )
    st.markdown("**How many hours per day can you commit?**")
    hours_pd = st.slider(
        "Hours per day", min_value=1, max_value=8,
        value=st.session_state.get("pf_study_hours_per_day", 2),
        step=1, key="pf_hours_slider",
        help="Adjust your daily hours. Plan cards update automatically."
    )
    st.session_state["pf_study_hours_per_day"] = hours_pd
    st.markdown("**Select a study cadence:**")

    plans = [
        {"id": "intensive", "name": "Fast Track",  "days": 7,
         "icon": "◆", "desc": "Every day, maximum pace"},
        {"id": "balanced",  "name": "Regular",     "days": 5,
         "icon": "◈", "desc": "Weekdays only, recommended"},
        {"id": "casual",    "name": "Flexible",    "days": 3,
         "icon": "◦", "desc": "3 days per week, relaxed pace"},
    ]

    # Determine how many courses exist for this role
    _role_courses   = match.get("courses") or get_courses_for_onet(soc)
    _course_count   = len(_role_courses)
    _only_regular   = _course_count <= 1          # restrict if ≤ 1 course

    if _only_regular:
        st.info(
            f"⚠️ Only {'1 course' if _course_count == 1 else 'no courses'} available "
            f"for this role. **Only the Regular plan is applicable.**"
        )

    def _duration_label(hrs, days_per_wk, hpd):
        if not hrs or not days_per_wk or not hpd:
            return "N/A"
        total_days = math.ceil(hrs / hpd)
        wks = math.ceil(hrs / (hpd * days_per_wk))
        if wks == 0:
            return f"{total_days} day(s)"
        return f"{wks} week(s)"

    cols = st.columns(3, gap="large")
    for plan, col in zip(plans, cols):
        weekly_hrs  = hours_pd * plan["days"]
        wks  = math.ceil(total_hrs / weekly_hrs) if (total_hrs and weekly_hrs) else 0
        dur  = _duration_label(total_hrs, plan["days"], hours_pd)
        end_date = (
            datetime.date.today() + datetime.timedelta(weeks=wks)
        ).strftime("%b %Y") if wks else "--"
        sel      = st.session_state.get("pf_selected_plan") == plan["id"]
        card_cls = "pf-card pf-plan-selected" if sel else "pf-card"

        # A plan is available if courses > 1, or it IS the Regular plan
        plan_available = not _only_regular or plan["id"] == "balanced"

        with col:
            opacity = "1" if plan_available else "0.45"
            st.markdown(f"""
            <div class="{card_cls}" style="text-align:center;padding:1.5rem;opacity:{opacity};">
              <div style="font-size:2rem;color:var(--copper);font-weight:700;">{plan['icon']}</div>
              <div style="font-size:1.05rem;font-weight:700;margin:0.5rem 0;">{plan['name']}</div>
              <div style="font-size:0.82rem;color:var(--charcoal-soft);margin-bottom:0.8rem;">{plan['desc']}</div>
              <div style="font-size:1.7rem;font-weight:800;color:var(--copper);font-family:'Playfair Display',serif;">{dur}</div>
              <div style="font-size:0.75rem;color:var(--copper-muted);margin-top:0.3rem;">
                {plan['days']} days/wk &middot; {hours_pd}h/day &middot; finish {end_date}
              </div>
            </div>
            """, unsafe_allow_html=True)
            btn_type = "primary" if sel else "secondary"
            label    = ("Selected: " if sel else "Choose ") + plan["name"]
            if st.button(label, key=f"pf_plan_{plan['id']}",
                         use_container_width=True, type=btn_type,
                         disabled=not plan_available):
                st.session_state["pf_selected_plan"]       = plan["id"]
                st.session_state["pf_days_per_week"]       = plan["days"]
                st.session_state["pf_study_hours_per_day"] = hours_pd
                st.session_state["pf_roadmap_courses"] = generate_verified_roadmap(
                    [soc], plan["id"]
                )
                st.rerun()

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back to Matches", use_container_width=True):
            st.session_state["pf_step"] = "results"
            st.rerun()
    with c2:
        if st.session_state.get("pf_selected_plan"):
            if st.button("View Roadmap", type="primary", use_container_width=True):
                st.session_state["pf_step"] = "roadmap"
                st.rerun()
        else:
            st.info("Select a plan above to continue.")


def _render_choose_plan():
    """Legacy redirect — now merged into skill_gap."""
    st.session_state["pf_step"] = "skill_gap"
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
    done_set = st.session_state.get("pf_completed_courses", set())
    cv_map   = st.session_state.get("pf_cert_verify", {})

    if not match:
        st.session_state["pf_step"] = "skill_gap"
        st.rerun()

    soc = match.get("soc_code", "")
    courses = st.session_state.get("pf_roadmap_courses") or generate_verified_roadmap([soc])
    if not courses:
        courses = get_courses_for_onet(soc)
    st.session_state["pf_roadmap_courses"] = courses

    st.markdown(f"## Learning Roadmap")
    st.markdown(
        f"**Target Role:** {match.get('title','')}",
    )
    st.caption("All course links are sourced exclusively from our verified catalog. No AI-generated URLs.")

    if not courses:
        st.markdown("""
        <div style="background:var(--warn-bg);border:1px solid var(--warn-border);border-radius:4px;
                    padding:1.5rem;text-align:center;">
          <div style="font-size:2rem;margin-bottom:0.5rem;">&#128196;</div>
          <div style="font-weight:600;color:var(--warn-text);">No courses found for this role.</div>
          <div style="font-size:0.83rem;color:var(--warn-text);margin-top:0.25rem;">
            Please go back and select a study plan.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_hrs = sum(c.get("hours", 0) for c in courses)
        done_hrs  = sum(
            c.get("hours", 0) for c in courses
            if str(c.get("course_id", c.get("title",""))) in done_set
            or c.get("title","") in done_set
        )
        pct = int(done_hrs / total_hrs * 100) if total_hrs else 0

        st.markdown(f"**Progress:** {pct}% ({int(done_hrs)}/{int(total_hrs)} hours completed)")
        st.progress(pct / 100)
        st.markdown("---")

        eff_hpd = hours_pd if hours_pd else 2
        cumday  = 0

        for i, course in enumerate(courses):
            cid      = str(course.get("course_id", course.get("title", i)))
            title    = course.get("title", "")
            hrs      = course.get("hours", 0)
            days_n   = math.ceil(hrs / eff_hpd) if eff_hpd else 0
            verified = cv_map.get(cid, {}).get("verified", False)
            done     = cid in done_set or title in done_set
            real_url = course.get("url", "")

            with st.container():
                col_info, col_action = st.columns([3, 1])

                with col_info:
                    dot_bg    = "var(--success-bg)" if (done or verified) else "var(--gold-pale)"
                    dot_color = "var(--success)"    if (done or verified) else "var(--copper)"
                    check_mark = "&#10003;" if (done or verified) else str(i + 1)
                    cert_line = (
                        '<div style="font-size:0.73rem;color:var(--success);margin-top:0.2rem;">'
                        'Certificate submitted</div>'
                        if verified else ""
                    )
                    st.markdown(f"""
                    <div class="roadmap-card">
                      <div style="display:flex;align-items:flex-start;gap:0.85rem;">
                        <div style="width:30px;height:30px;border-radius:50%;flex-shrink:0;
                                    background:{dot_bg};color:{dot_color};display:flex;
                                    align-items:center;justify-content:center;
                                    font-size:0.75rem;font-weight:700;">{check_mark}</div>
                        <div style="flex:1;">
                          <div style="font-weight:700;font-size:0.95rem;color:var(--charcoal);
                                      margin-bottom:0.2rem;">{title}</div>
                          <span class="provider-badge">{course.get('provider','')}</span>
                          <div style="font-size:0.78rem;color:var(--charcoal-soft);margin-top:0.3rem;">
                            {int(hrs)}h &nbsp;&middot;&nbsp; ~{days_n} day(s)
                            &nbsp;&middot;&nbsp; starts day {cumday + 1}
                          </div>
                          {cert_line}
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_action:
                    st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)
                    if real_url and not verified:
                        st.link_button(
                            "Go to Course", real_url, use_container_width=True
                        )
                    if verified:
                        st.markdown(
                            '<span class="pf-badge pf-badge-green">Verified</span>',
                            unsafe_allow_html=True
                        )
                    elif done:
                        if st.button("Verify Cert", key=f"pf_vbtn_{i}",
                                     use_container_width=True):
                            _verify_dialog(course)
                    else:
                        if st.button("Mark Done", key=f"pf_done_{i}",
                                     use_container_width=True):
                            done_set.add(cid)
                            done_set.add(title)
                            st.session_state["pf_completed_courses"] = done_set
                            st.rerun()

            cumday += days_n

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back to Plan", use_container_width=True):
            st.session_state["pf_step"] = "skill_gap"
            st.rerun()
    with c2:
        if st.button("Dashboard", type="primary", use_container_width=True):
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
                '<span style="font-size:1.4rem;color:var(--success);">✅</span>'
                if v_state["verified"] else
                '<span style="font-size:1.4rem;color:var(--danger);">✗</span>'
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
    analysis = st.session_state.get("pf_analysis", {}) or {}

    if not match:
        st.session_state["pf_step"] = "results"
        st.rerun()

    soc        = match.get("soc_code", "")
    total_hrs  = match.get("total_course_hours") or sum(c.get("hours",0) for c in courses) or get_total_hours(soc)
    done_hrs   = sum(c.get("hours",0) for c in courses
                     if str(c.get("course_id", c.get("title",""))) in done_set
                     or c.get("title","") in done_set)
    remain     = max(0, total_hrs - done_hrs)
    pct        = int(done_hrs / total_hrs * 100) if total_hrs else 0
    weekly_h   = hours_pd * dpw
    wks_left   = math.ceil(remain / weekly_h) if (remain and weekly_h) else 0
    verified_n = sum(1 for v in cv_map.values() if v.get("verified"))
    done_n     = sum(1 for c in courses
                     if str(c.get("course_id", c.get("title",""))) in done_set
                     or c.get("title","") in done_set)

    candidate_name = analysis.get("candidate_name", "") or ""

    st.markdown("## Career Dashboard")

    # ── Profile Card ──────────────────────────────────────────────────────────
    profile_photo = st.session_state.get("pf_profile_photo_b64", "")
    if profile_photo:
        avatar_inner = f'<img src="data:image/png;base64,{profile_photo}">'
    else:
        initials = "".join(w[0].upper() for w in candidate_name.split()[:2]) if candidate_name else "U"
        avatar_inner = initials

    achievements = []
    if done_n > 0:
        achievements.append(f"{done_n} Course(s) Completed")
    if verified_n > 0:
        achievements.append(f"{verified_n} Certificate(s) Verified")
    if pct >= 50:
        achievements.append("Halfway There")
    if pct == 100:
        achievements.append("Roadmap Complete")

    ach_html = "".join(
        f'<span class="pf-achievement">{a}</span>' for a in achievements
    ) if achievements else '<span style="font-size:0.75rem;color:var(--copper-muted);">No achievements yet. Start completing courses!</span>'

    st.markdown(f"""
    <div class="pf-profile-card">
      <div class="pf-avatar">{avatar_inner}</div>
      <div style="flex:1;">
        <div class="pf-profile-name">{candidate_name or "Your Profile"}</div>
        <div class="pf-profile-role">{match.get('title','')}</div>
        <div class="pf-achievement-row">{ach_html}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Photo upload ─────────────────────────────────────────────────────────
    with st.expander("Upload / Change Profile Photo"):
        photo_f = st.file_uploader(
            "Profile photo (JPG/PNG)", type=["jpg","jpeg","png"],
            label_visibility="collapsed", key="pf_photo_upload"
        )
        if photo_f:
            b64 = base64.b64encode(photo_f.read()).decode()
            st.session_state["pf_profile_photo_b64"] = b64
            st.rerun()

    # ── Stats ─────────────────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, f"{pct}%",           "Overall Progress"),
        (s2, f"{int(done_hrs)}h", "Hours Completed"),
        (s3, f"{wks_left}w",      "Weeks Remaining"),
        (s4, str(verified_n),     "Certificates Verified"),
    ]:
        with col:
            st.markdown(f"""
            <div class="pf-stat">
              <div class="pf-stat-num">{num}</div>
              <div class="pf-stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.progress(pct / 100)
    st.caption(f"{pct}% complete ({int(done_hrs)}/{int(total_hrs)} hours)")
    st.markdown("---")

    # ── Course Status ─────────────────────────────────────────────────────────
    st.markdown('<div class="pf-section-header">Course Status</div>', unsafe_allow_html=True)
    for course in courses:
        cid      = str(course.get("course_id", course.get("title","")))
        done     = cid in done_set or course.get("title","") in done_set
        verified = cv_map.get(cid, {}).get("verified", False)
        hrs      = int(course.get("hours", 0))
        if verified:
            badge = '<span class="pf-badge pf-badge-green">Verified</span>'
        elif done:
            badge = '<span class="pf-badge pf-badge-blue">Completed</span>'
        else:
            badge = '<span class="pf-badge" style="background:var(--warm-muted);color:var(--charcoal-soft);">Pending</span>'
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.65rem 0;border-bottom:1px solid var(--warm-border);">
          <div>
            <span style="font-weight:600;color:var(--charcoal);font-size:0.88rem;">{course.get('title','')}</span>
            <span style="font-size:0.72rem;color:var(--copper-muted);margin-left:0.5rem;">
              {course.get('provider','')} &middot; {hrs}h
            </span>
          </div>
          {badge}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Back to Roadmap", use_container_width=True):
            st.session_state["pf_step"] = "roadmap"
            st.rerun()
    with c2:
        if st.button("Open Study Planner", use_container_width=True, type="primary"):
            _study_planner_dialog()
    with c3:
        if st.button("Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("pf_"):
                    del st.session_state[k]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_upload():
    # ── Centered page header ────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="text-align:center;margin-bottom:0.2rem;">Analyze Your Profile</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align:center;font-size:0.88rem;color:var(--charcoal-soft);'
        'margin-top:0;margin-bottom:1.75rem;">'
        'Upload your CV and certificates, or fill in the form manually. '
        'Analyzed by Gemini AI against O*NET and SKKNI.</p>',
        unsafe_allow_html=True,
    )

    tab_upload, tab_manual = st.tabs([
        "\U0001F4C4  Upload CV & Certificate",
        "\U0000270F  Manual Data Entry",
    ])

    # ── Tab 1: Upload CV & Certificate ────────────────────────────────────────
    with tab_upload:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        col_cv, col_cert = st.columns([1, 1], gap="large")

        # ---- Left: CV / Resume -----------------------------------------------
        with col_cv:
            with st.container(border=True):
                st.markdown(
                    '<div class="st-card-section-label">CV / Resume</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<p style="font-size:0.82rem;color:var(--charcoal-soft);margin:0.1rem 0 0.75rem;">'
                    'Upload your CV or resume in PDF format. Text will be extracted '
                    'and analyzed by AI.</p>',
                    unsafe_allow_html=True,
                )
                uploaded = st.file_uploader(
                    "CV (PDF only)", type=["pdf"],
                    key="pf_pdf_upload", label_visibility="visible",
                )
                # Mirror structure: paste area (matches Certs card height exactly)
                cv_paste = st.text_area(
                    "Or paste your CV text directly",
                    placeholder="Paste your CV content here if you don't have a PDF...",
                    height=130, key="pf_cv_paste_text",
                )
                # Determine source and show Analyze button
                has_input = uploaded or cv_paste.strip()
                if has_input:
                    if uploaded:
                        st.success(f"Ready: {uploaded.name}")
                    if st.button("Analyze CV", type="primary",
                                 use_container_width=True, key="pf_analyze_pdf"):
                        try:
                            if uploaded:
                                cv_text = extract_pdf_text(uploaded.read())
                                if not cv_text.strip():
                                    st.error("Could not extract text. Try the manual form instead.")
                                    st.stop()
                            else:
                                cv_text = cv_paste.strip()
                            result = _run_with_loading(_call_gemini, cv_text)
                            st.session_state["pf_analysis"] = result
                            upsert_user_profile(
                                st.session_state["pf_session_id"], cv_text=cv_text
                            )
                            st.session_state["pf_step"] = "results"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")

        # ---- Right: Certificates & Licenses -----------------------------------
        with col_cert:
            with st.container(border=True):
                st.markdown(
                    '<div class="st-card-section-label">Certificates & Licenses '
                    '<span style="font-weight:400;color:var(--copper-muted);">(Optional)</span></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<p style="font-size:0.82rem;color:var(--charcoal-soft);margin:0.1rem 0 0.75rem;">'
                    'Upload certificates or licenses (PDF, PNG, JPG). '
                    'These will be attached to your profile.</p>',
                    unsafe_allow_html=True,
                )
                cert_files = st.file_uploader(
                    "Certificates & Licenses", type=["pdf", "png", "jpg", "jpeg"],
                    accept_multiple_files=True, label_visibility="visible",
                    key="pf_cert_files_upload",
                )
                if cert_files:
                    badges = " ".join(
                        f'<span class="pf-badge pf-badge-green">{cf.name}</span>'
                        for cf in cert_files
                    )
                    st.markdown(badges, unsafe_allow_html=True)
                    st.caption(f"{len(cert_files)} file(s) uploaded")
                cert_list_text = st.text_area(
                    "Or list certifications manually (one per line)",
                    placeholder="AWS Certified Developer (2023)\nGoogle Data Analytics Certificate",
                    height=130, key="pf_cert_upload_text",
                )
                if cert_list_text.strip():
                    n = len([l for l in cert_list_text.splitlines() if l.strip()])
                    st.caption(f"{n} certificate(s) listed")

    # ── Tab 2: Manual Data Entry ───────────────────────────────────────────────
    with tab_manual:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        form_data = _render_manual_form()

        # Bottom action bar — centered
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        _al, act_center, _ar = st.columns([2, 3, 2])
        with act_center:
            if st.button("Analyze Now", type="primary",
                         use_container_width=True, key="pf_analyze_manual"):
                if not form_data["full_name"].strip():
                    st.warning("Full name is required.")
                elif not form_data["selected_skills"]:
                    st.warning("Please select or enter at least one skill.")
                else:
                    cv_text = _build_cv_text(form_data)
                    try:
                        result = _run_with_loading(_call_gemini, cv_text)
                        st.session_state["pf_analysis"] = result
                        session_id = st.session_state["pf_session_id"]
                        upsert_user_profile(
                            session_id,
                            full_name=form_data["full_name"],
                            education=form_data["edu_level"],
                            major=form_data["major"],
                            institution=form_data["institution"],
                            cv_text=cv_text,
                        )
                        upsert_user_skills(session_id, form_data["selected_skills"])
                        st.session_state["pf_step"] = "results"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Back to Home"):
        st.session_state["pf_step"] = "landing"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════

def _render_landing():
    st.markdown("""
    <div class="pf-hero">
      <div style="font-family:'Inter',sans-serif;font-size:.68rem;font-weight:700;
                  letter-spacing:.15em;text-transform:uppercase;color:var(--copper);
                  margin-bottom:.9rem;">Powered by Gemini AI &nbsp;&middot;&nbsp; O*NET &nbsp;&middot;&nbsp; SKKNI</div>
      <h1>From Career Confusion to an <span>Actionable, Adaptive Career Route</span></h1>
      <p>AI-powered career guidance for ASEAN students, mapped to global O*NET standards and Indonesian SKKNI competency frameworks.</p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="large")
    features = [
        ("✶", "AI Analysis",
         "Gemini AI analyzes your profile against global O*NET taxonomy and Indonesian SKKNI frameworks."),
        ("◈", "Career Matching",
         "Get 3 personalized career matches ranked by compatibility score with detailed skill gap breakdown."),
        ("▦", "Verified Roadmap",
         "Course links come exclusively from our verified database. No hallucinated URLs, ever."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="pf-card" style="text-align:center;padding:1.75rem 1.5rem;">
              <div style="font-size:1.6rem;color:var(--copper);margin-bottom:.65rem;line-height:1;">{icon}</div>
              <div style="font-family:'Playfair Display',Georgia,serif;font-weight:600;
                          font-size:1rem;margin-bottom:.5rem;color:var(--charcoal);
                          letter-spacing:.01em;">{title}</div>
              <div style="font-size:.83rem;color:var(--charcoal-soft);line-height:1.65;">{desc}</div>
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
