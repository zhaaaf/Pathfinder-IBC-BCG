import streamlit as st
import os

st.set_page_config(
    page_title="Pathfinder — AI Career Mapping",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome
st.markdown("""
<style>
#MainMenu, header, footer, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)


def load_file(path):
    base = os.path.dirname(__file__)
    full = os.path.join(base, path)
    if os.path.exists(full):
        with open(full, "r", encoding="utf-8") as f:
            return f.read()
    return ""


CSS = load_file("assets/styles.css")
JS = load_file("assets/script.js")

HTML = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pathfinder — AI Career Mapping</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{CSS}
/* ── SCREEN 1 ── */
.hero {{
  display: flex; min-height: calc(100vh - 64px);
}}
.hero-left {{
  flex: 0 0 55%; background: var(--navy); padding: 72px 64px;
  display: flex; flex-direction: column; justify-content: center; gap: 28px;
}}
.hero-eyebrow {{
  font-size: 11px; letter-spacing: 3px; font-weight: 700;
  color: var(--blue); text-transform: uppercase;
}}
.hero-heading {{
  font-family: 'Syne', sans-serif; font-size: 48px; font-weight: 800;
  line-height: 1.1; color: white;
}}
.hero-heading span {{ color: var(--blue); }}
.hero-sub {{ font-size: 16px; color: rgba(255,255,255,0.72); max-width: 460px; line-height: 1.7; }}
.hero-ctas {{ display: flex; gap: 14px; flex-wrap: wrap; }}
.hero-right {{
  flex: 0 0 45%; background: var(--surface); padding: 72px 48px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px;
}}
.floating-card {{
  background: white; border: 1px solid var(--border); border-radius: 14px;
  padding: 28px; width: 100%; max-width: 380px;
  box-shadow: 0 8px 32px rgba(13,27,62,0.10);
}}
.floating-card-header {{ font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: var(--text-muted); margin-bottom: 20px; font-weight: 600; }}
.prof-row {{ margin-bottom: 16px; }}
.prof-row:last-child {{ margin-bottom: 0; }}
.prof-label {{ display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--navy); }}
.prof-label span {{ color: var(--blue); }}
.floating-badge {{ font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }}
.step-cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; padding: 64px 48px; background: white; }}
.step-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 28px 24px; transition: box-shadow 0.2s, transform 0.2s; }}
.step-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }}
.step-num {{ font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; color: var(--blue-light); letter-spacing: -1px; margin-bottom: 12px; }}
.step-icon {{ font-size: 28px; margin-bottom: 12px; }}
.step-title {{ font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; color: var(--navy); margin-bottom: 8px; }}
.step-desc {{ font-size: 13px; color: var(--text-muted); line-height: 1.5; }}
.stats-section {{ background: var(--navy); padding: 64px 48px; display: flex; justify-content: center; gap: 64px; }}
.stat-item {{ text-align: center; }}
.stat-num {{ font-family: 'Syne', sans-serif; font-size: 42px; font-weight: 800; color: white; margin-bottom: 8px; }}
.stat-label {{ font-size: 14px; color: rgba(255,255,255,0.6); }}
.cta-section {{ background: var(--blue-light); padding: 80px 48px; text-align: center; }}
.cta-section h2 {{ font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 800; color: var(--navy); margin-bottom: 16px; }}
.cta-section p {{ color: var(--text-muted); font-size: 16px; margin-bottom: 32px; }}

/* ── SCREEN 2 ── */
.upload-section {{ padding: 64px 48px; max-width: 960px; margin: 0 auto; }}
.upload-heading {{ text-align: center; margin-bottom: 8px; font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; color: var(--navy); }}
.upload-sub {{ text-align: center; color: var(--text-muted); margin-bottom: 48px; font-size: 16px; }}
.upload-cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }}
.upload-card {{ border: 1px solid var(--border); border-radius: 12px; padding: 36px 28px; background: white; transition: border-color 0.2s, box-shadow 0.2s; cursor: pointer; }}
.upload-card:hover {{ border-color: var(--blue); box-shadow: 0 4px 16px rgba(37,99,235,0.10); }}
.upload-card.selected {{ border-color: var(--blue); background: var(--blue-light); }}
.upload-icon {{ font-size: 40px; margin-bottom: 16px; }}
.upload-card h3 {{ font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: var(--navy); margin-bottom: 10px; }}
.upload-card p {{ font-size: 14px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.5; }}
.drop-zone {{ border: 2px dashed var(--border); border-radius: 8px; padding: 32px; text-align: center; color: var(--text-muted); font-size: 13px; margin-bottom: 20px; transition: border-color 0.2s; cursor: pointer; }}
.drop-zone:hover {{ border-color: var(--blue); color: var(--blue); }}
.form-field {{ margin-bottom: 14px; }}
.form-field label {{ display: block; font-size: 13px; font-weight: 600; color: var(--navy); margin-bottom: 5px; }}
.form-field input, .form-field select, .form-field textarea {{
  width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px;
  font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--text-main);
  background: var(--surface); outline: none; transition: border-color 0.2s;
}}
.form-field input:focus, .form-field select:focus, .form-field textarea:focus {{ border-color: var(--blue); background: white; }}
.form-field textarea {{ resize: vertical; min-height: 80px; }}
.scan-bar-wrap {{ background: var(--border); border-radius: 99px; height: 4px; overflow: hidden; margin-top: 8px; display: none; }}
#scan-progress {{ height: 100%; background: var(--blue); border-radius: 99px; width: 0%; transition: width 0.1s linear; }}
.security-note {{ text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 16px; }}

/* ── SCREEN 3 ── */
.results-section {{ padding: 48px; max-width: 960px; margin: 0 auto; }}
.skill-chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 40px; }}
.profession-card {{
  border: 1px solid var(--border); border-radius: 12px; padding: 24px 28px;
  margin-bottom: 16px; display: flex; align-items: center; gap: 24px;
  background: white; transition: box-shadow 0.2s; cursor: pointer; position: relative;
}}
.profession-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
.profession-card.best {{ border-left: 4px solid var(--blue); background: #F5F8FF; }}
.profession-card.selected {{ border-color: var(--blue); box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }}
.prof-rank {{ font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; color: var(--blue-light); flex-shrink: 0; width: 48px; }}
.prof-info {{ flex: 1; }}
.prof-name {{ font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: var(--navy); margin-bottom: 4px; }}
.prof-desc {{ font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }}
.prof-bar-label {{ font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 5px; display: flex; justify-content: space-between; }}
.prof-meta {{ flex-shrink: 0; text-align: right; display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }}
.prof-meta-item {{ font-size: 12px; color: var(--text-muted); }}
.prof-badge-wrap {{ position: absolute; top: 16px; right: 16px; }}
.custom-prof-card {{ border: 2px dashed var(--border); border-radius: 12px; padding: 28px; background: var(--surface); }}
.custom-prof-card h3 {{ font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; color: var(--navy); margin-bottom: 6px; }}
.custom-prof-card p {{ font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }}
.custom-input-row {{ display: flex; gap: 10px; margin-bottom: 12px; }}
.custom-input-row input {{ flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 14px; outline: none; }}
.custom-input-row input:focus {{ border-color: var(--blue); }}
#custom-prof-chips {{ display: flex; flex-wrap: wrap; gap: 6px; min-height: 28px; }}
.nav-bottom {{ display: flex; justify-content: space-between; align-items: center; padding: 32px 48px; border-top: 1px solid var(--border); background: white; position: sticky; bottom: 0; }}

/* ── SCREEN 4 ── */
.gap-section {{ padding: 48px; max-width: 1000px; margin: 0 auto; }}
.readiness-bar-wrap {{ background: var(--blue-light); border-radius: 12px; padding: 24px 28px; margin-bottom: 40px; }}
.readiness-bar-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
.readiness-bar-header span:first-child {{ font-size: 14px; font-weight: 600; color: var(--navy); }}
.readiness-bar-header span:last-child {{ font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; color: var(--blue); }}
.readiness-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 8px; }}
.skill-cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.skill-col-card {{ border: 1px solid var(--border); border-radius: 12px; overflow: hidden; background: white; }}
.skill-col-header {{ padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }}
.skill-col-header h3 {{ font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700; color: var(--navy); flex: 1; }}
.skill-list {{ padding: 8px 0; }}
.skill-item {{ display: flex; align-items: center; gap: 12px; padding: 10px 20px; border-bottom: 1px solid var(--border); font-size: 13px; font-weight: 500; }}
.skill-item:last-child {{ border-bottom: none; }}
.skill-check {{ color: var(--success); font-size: 16px; flex-shrink: 0; }}
.skill-circle {{ width: 18px; height: 18px; border-radius: 50%; border: 2px solid var(--blue); flex-shrink: 0; }}
.skill-standard {{ margin-left: auto; }}
.skill-callout {{ margin: 16px 20px 20px; background: var(--blue-light); border-left: 3px solid var(--blue); border-radius: 6px; padding: 12px 14px; font-size: 12px; color: var(--blue); }}

/* ── SCREEN 5 ── */
.packages-section {{ padding: 48px; max-width: 1100px; margin: 0 auto; }}
.slider-wrap {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px 28px; margin-bottom: 36px; }}
.slider-label {{ font-size: 14px; font-weight: 600; color: var(--navy); margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }}
.slider-label span:last-child {{ font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: var(--blue); }}
input[type=range] {{ width: 100%; accent-color: var(--blue); cursor: pointer; }}
.slider-note {{ font-size: 12px; color: var(--text-muted); margin-top: 8px; }}
.packages-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
.package-card {{
  border: 1px solid var(--border); border-radius: 12px; padding: 28px 24px;
  background: white; position: relative; cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s; display: flex; flex-direction: column;
}}
.package-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
.package-card.recommended {{ border: 2px solid var(--blue); background: #F5F8FF; }}
.package-card.selected {{ box-shadow: 0 0 0 3px rgba(37,99,235,0.2); }}
.pkg-recommended-badge {{ position: absolute; top: -13px; left: 50%; transform: translateX(-50%); white-space: nowrap; }}
.pkg-icon {{ font-size: 28px; margin-bottom: 12px; }}
.pkg-name {{ font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: var(--navy); margin-bottom: 4px; }}
.pkg-days {{ font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 800; color: var(--blue); }}
.pkg-days-label {{ font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }}
.pkg-hours {{ font-size: 13px; color: var(--text-muted); margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }}
.pkg-courses {{ display: flex; flex-direction: column; gap: 12px; flex: 1; margin-bottom: 20px; }}
.course-item {{ font-size: 13px; }}
.course-name {{ font-weight: 600; color: var(--navy); margin-bottom: 4px; }}
.course-meta {{ display: flex; align-items: center; gap: 6px; color: var(--text-muted); font-size: 12px; }}
.pkg-cert {{ font-size: 12px; color: var(--text-muted); padding: 10px 0; border-top: 1px solid var(--border); margin-bottom: 16px; }}
.packages-note {{ text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 24px; padding: 0 48px; }}

/* ── SCREEN 6 ── */
.roadmap-section {{ padding: 48px; max-width: 900px; margin: 0 auto; }}
.roadmap-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; gap: 24px; }}
.roadmap-stats {{ display: flex; gap: 12px; flex-wrap: wrap; }}
.roadmap-stat-chip {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; color: var(--navy); white-space: nowrap; }}
.timeline {{ position: relative; }}
.timeline-item {{ display: flex; gap: 20px; margin-bottom: 0; }}
.timeline-left {{ display: flex; flex-direction: column; align-items: center; gap: 0; flex-shrink: 0; }}
.timeline-bullet {{
  width: 36px; height: 36px; border-radius: 50%; border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; color: var(--text-muted);
  background: white; flex-shrink: 0; z-index: 1;
}}
.timeline-bullet.active {{ background: var(--blue); border-color: var(--blue); color: white; }}
.timeline-bullet.done {{ background: var(--success); border-color: var(--success); color: white; }}
.timeline-line {{ flex: 1; width: 2px; background: var(--border); margin: 4px 0; min-height: 40px; }}
.timeline-line.active {{ background: var(--blue); }}
.timeline-card {{
  flex: 1; background: white; border: 1px solid var(--border); border-radius: 12px;
  padding: 20px 24px; margin-bottom: 24px; position: relative;
}}
.timeline-card.active {{ background: #F5F8FF; border-left: 4px solid var(--blue); }}
.timeline-card.done {{ background: #F0FDF9; border-left: 4px solid var(--success); }}
.timeline-card-inner {{ display: flex; gap: 20px; }}
.timeline-card-main {{ flex: 1; }}
.timeline-card-side {{ flex-shrink: 0; text-align: right; min-width: 140px; }}
.tl-skill-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text-muted); font-weight: 600; margin-bottom: 4px; }}
.tl-skill-name {{ font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700; color: var(--navy); margin-bottom: 4px; }}
.tl-course-name {{ font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }}
.tl-duration {{ font-size: 12px; color: var(--text-muted); margin-top: 10px; }}
.tl-date {{ font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }}
.tl-date strong {{ color: var(--navy); }}
.tl-badge {{ position: absolute; top: 16px; right: 16px; }}
.end-node {{
  display: flex; align-items: center; gap: 16px;
  background: #F0FDF9; border: 1px solid var(--success); border-radius: 12px;
  padding: 20px 24px; margin-top: 4px;
}}
.end-bullet {{ width: 36px; height: 36px; border-radius: 50%; background: var(--success); color: white; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }}
.end-text h3 {{ font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; color: var(--success); }}
.end-text p {{ font-size: 13px; color: var(--text-muted); }}

/* ── SCREEN 7 ── */
.dashboard-section {{ padding: 32px 48px; max-width: 1100px; margin: 0 auto; }}
.greeting-row {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }}
.greeting-text h2 {{ font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 800; color: var(--navy); margin-bottom: 4px; }}
.greeting-text p {{ font-size: 14px; color: var(--text-muted); }}
.metric-cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }}
.metric-card {{ border: 1px solid var(--border); border-radius: 12px; padding: 20px; background: white; }}
.metric-label {{ font-size: 12px; color: var(--text-muted); font-weight: 500; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
.metric-value {{ font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; color: var(--navy); margin-bottom: 4px; }}
.metric-sub {{ font-size: 12px; color: var(--text-muted); }}
.active-stage-card {{ border: 1px solid var(--border); border-radius: 12px; padding: 28px; margin-bottom: 24px; background: white; }}
.active-stage-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
.active-stage-title {{ font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: var(--navy); }}
.active-course-meta {{ font-size: 14px; color: var(--text-muted); margin-bottom: 16px; }}
.progress-label {{ display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: var(--navy); margin-bottom: 8px; }}
.active-stage-actions {{ display: flex; gap: 12px; margin-top: 20px; flex-wrap: wrap; }}
.active-stage-note {{ font-size: 12px; color: var(--text-muted); margin-top: 10px; }}
.skill-progress-card {{ border: 1px solid var(--border); border-radius: 12px; padding: 28px; margin-bottom: 24px; background: white; }}
.skill-progress-card h3 {{ font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; color: var(--navy); margin-bottom: 20px; }}
.skill-progress-row {{ margin-bottom: 14px; }}
.skill-progress-row:last-child {{ margin-bottom: 0; }}
.skill-progress-meta {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px; }}
.skill-progress-meta .name {{ font-weight: 600; color: var(--navy); }}
.skill-progress-meta .pct {{ color: var(--text-muted); }}
.owned-chips {{ padding-top: 16px; border-top: 1px solid var(--border); margin-top: 16px; }}
.owned-chips p {{ font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }}
.owned-chips-list {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.upload-proof-card {{ border: 1px solid var(--border); border-radius: 12px; padding: 28px; margin-bottom: 24px; background: white; }}
.upload-proof-card h3 {{ font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700; color: var(--navy); margin-bottom: 4px; }}
.upload-proof-sub {{ font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }}
.upload-proof-drop {{ border: 2px dashed var(--border); border-radius: 8px; padding: 28px; text-align: center; color: var(--text-muted); font-size: 13px; margin-bottom: 14px; cursor: pointer; transition: border-color 0.2s; }}
.upload-proof-drop:hover {{ border-color: var(--blue); color: var(--blue); }}
.upload-proof-note {{ font-size: 12px; color: var(--text-muted); }}
.motivation-card {{ background: var(--navy); border-radius: 12px; padding: 24px 28px; margin-bottom: 32px; }}
.motivation-card p {{ color: rgba(255,255,255,0.85); font-size: 15px; line-height: 1.6; font-style: italic; }}
.motivation-card p strong {{ color: white; font-style: normal; }}

@media (max-width: 768px) {{
  .hero {{ flex-direction: column; }}
  .hero-left {{ flex: none; padding: 48px 24px; }}
  .hero-heading {{ font-size: 32px; }}
  .hero-right {{ flex: none; padding: 40px 24px; }}
  .step-cards {{ grid-template-columns: 1fr 1fr; padding: 40px 20px; }}
  .stats-section {{ flex-direction: column; gap: 32px; padding: 48px 24px; text-align: center; }}
  .upload-section {{ padding: 40px 20px; }}
  .upload-cards {{ grid-template-columns: 1fr; }}
  .results-section, .gap-section, .packages-section, .roadmap-section, .dashboard-section {{ padding: 40px 20px; }}
  .packages-grid {{ grid-template-columns: 1fr; }}
  .skill-cols {{ grid-template-columns: 1fr; }}
  .metric-cards {{ grid-template-columns: 1fr 1fr; }}
  .roadmap-header {{ flex-direction: column; }}
  .profession-card {{ flex-direction: column; }}
  .prof-meta {{ align-items: flex-start; text-align: left; }}
  .timeline-card-inner {{ flex-direction: column; }}
  .timeline-card-side {{ text-align: left; }}
  .nav-bottom {{ padding: 20px; }}
  .greeting-row {{ flex-direction: column; gap: 16px; }}
  .progress-steps {{ gap: 4px; }}
}}
</style>
</head>
<body>

<!-- ============================================================
     SCREEN 1 — LANDING
     ============================================================ -->
<div class="screen" id="screen-1">
  <!-- Navbar -->
  <nav class="navbar">
    <a class="navbar-logo">PATHFINDER</a>
    <div class="navbar-links">
      <a onclick="document.getElementById('how-it-works').scrollIntoView({{behavior:'smooth'}})">How It Works</a>
      <a>About</a>
      <a onclick="showScreen('screen-5')">Pricing</a>
    </div>
    <div class="navbar-right">
      <button class="btn btn-primary" onclick="showScreen('screen-2')">Mulai Sekarang</button>
    </div>
  </nav>

  <!-- Hero -->
  <div class="hero">
    <div class="hero-left">
      <p class="hero-eyebrow">AI-Powered Career Mapping</p>
      <h1 class="hero-heading">Temukan Jalur Karir<br><span>Terbaik Untukmu</span></h1>
      <p class="hero-sub">Pathfinder menganalisis skill yang kamu miliki, mencocokkannya dengan standar industri O*NET dan SKKNI, lalu membuat roadmap belajar personalmu hingga siap bersaing di dunia kerja.</p>
      <div class="hero-ctas">
        <button class="btn btn-primary btn-lg" onclick="showScreen('screen-2')">Mulai Analisis CV</button>
        <button class="btn btn-outline-white btn-lg" onclick="document.getElementById('how-it-works').scrollIntoView({{behavior:'smooth'}})">Lihat Cara Kerja</button>
      </div>
    </div>
    <div class="hero-right">
      <div class="floating-card">
        <p class="floating-card-header">Hasil Analisis Profil</p>
        <div class="prof-row">
          <div class="prof-label">Financial Analyst <span>79%</span></div>
          <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:79%"></div></div>
        </div>
        <div class="prof-row">
          <div class="prof-label">Accountant <span>68%</span></div>
          <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:68%"></div></div>
        </div>
        <div class="prof-row">
          <div class="prof-label">Auditor <span>58%</span></div>
          <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:58%"></div></div>
        </div>
      </div>
      <p class="floating-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        Dianalisis menggunakan standar O*NET
      </p>
    </div>
  </div>

  <!-- How It Works -->
  <div id="how-it-works">
    <div class="step-cards">
      <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-icon">📄</div>
        <div class="step-title">Upload CV atau isi data</div>
        <div class="step-desc">Unggah CV kamu atau isi form singkat untuk memulai analisis profil.</div>
      </div>
      <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-icon">🤖</div>
        <div class="step-title">AI menganalisis profilmu</div>
        <div class="step-desc">Pathfinder AI mencocokkan skill kamu dengan ribuan profesi standar O*NET dan SKKNI.</div>
      </div>
      <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-icon">🗺️</div>
        <div class="step-title">Dapatkan career roadmap</div>
        <div class="step-desc">Terima peta belajar personal yang menunjukkan persis apa yang perlu dikuasai.</div>
      </div>
      <div class="step-card">
        <div class="step-num">04</div>
        <div class="step-icon">🏆</div>
        <div class="step-title">Bangun skill, raih karir</div>
        <div class="step-desc">Ikuti kursus bersertifikat dan buktikan kompetensimu kepada dunia kerja.</div>
      </div>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats-section">
    <div class="stat-item"><div class="stat-num">1.000+</div><div class="stat-label">Profesi O*NET</div></div>
    <div class="stat-item"><div class="stat-num">500+</div><div class="stat-label">Kursus Bersertifikat</div></div>
    <div class="stat-item"><div class="stat-num">SKKNI</div><div class="stat-label">Terstandarisasi</div></div>
  </div>

  <!-- CTA Bottom -->
  <div class="cta-section">
    <h2>Siap memulai perjalanan karirmu?</h2>
    <p>Bergabung dengan ribuan profesional yang sudah menemukan jalur karir terbaiknya bersama Pathfinder.</p>
    <button class="btn btn-primary btn-lg" onclick="showScreen('screen-2')">Analisis CV Sekarang</button>
  </div>
</div>

<!-- ============================================================
     SCREEN 2 — UPLOAD CV
     ============================================================ -->
<div class="screen" id="screen-2">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')">PATHFINDER</a>
    <div class="navbar-links">
      <a onclick="showScreen('screen-1')">Beranda</a>
    </div>
    <div class="navbar-right">
      <button class="btn btn-outline btn-sm" onclick="showScreen('screen-1')">← Kembali</button>
    </div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle active">1</div><div class="step-label active">Upload Profil</div></div>
      <div class="progress-step"><div class="step-circle">2</div><div class="step-label">Hasil Analisis</div></div>
      <div class="progress-step"><div class="step-circle">3</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle">4</div><div class="step-label">Pilih Paket</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="upload-section">
    <h2 class="upload-heading">Mulai dengan profilmu</h2>
    <p class="upload-sub">Pathfinder akan membaca skill, pengalaman, dan pendidikanmu secara otomatis</p>

    <div class="upload-cards">
      <!-- Upload CV -->
      <div class="upload-card" id="card-upload" onclick="document.getElementById('card-upload').classList.toggle('selected');document.getElementById('card-manual').classList.remove('selected');document.getElementById('analyze-btn').classList.remove('btn-disabled');document.getElementById('analyze-btn').disabled=false;">
        <div class="upload-icon">📄</div>
        <h3>Upload CV</h3>
        <p>Format PDF atau DOCX. AI akan mengekstrak skill dan pengalamanmu secara otomatis.</p>
        <div class="drop-zone" onclick="event.stopPropagation()">
          <div style="font-size:28px;margin-bottom:8px">☁️</div>
          Drag & drop atau klik untuk pilih file<br>
          <small style="color:var(--text-muted)">PDF, DOCX · Maks. 5MB</small>
        </div>
        <button class="btn btn-primary" style="width:100%" onclick="event.stopPropagation()">Pilih File CV</button>
      </div>

      <!-- Manual Form -->
      <div class="upload-card" id="card-manual" onclick="document.getElementById('card-manual').classList.toggle('selected');document.getElementById('card-upload').classList.remove('selected');document.getElementById('analyze-btn').classList.remove('btn-disabled');document.getElementById('analyze-btn').disabled=false;">
        <div class="upload-icon">✏️</div>
        <h3>Isi Data Manual</h3>
        <p>Belum punya CV? Isi form singkat yang menyerupai CV.</p>
        <div class="form-field" onclick="event.stopPropagation()">
          <label>Nama Lengkap</label>
          <input type="text" placeholder="Masukkan nama lengkapmu">
        </div>
        <div class="form-field" onclick="event.stopPropagation()">
          <label>Pendidikan Terakhir</label>
          <select>
            <option>S1 Akuntansi — Universitas Padjadjaran</option>
            <option>S1 Manajemen</option>
            <option>S1 Ekonomi</option>
            <option>S2 / Pascasarjana</option>
          </select>
        </div>
        <div class="form-field" onclick="event.stopPropagation()">
          <label>Pengalaman Kerja</label>
          <textarea placeholder="Contoh: 2 tahun sebagai Finance Staff di PT ABC, mengelola laporan keuangan dan rekonsiliasi akun..."></textarea>
        </div>
        <div class="form-field" onclick="event.stopPropagation()">
          <label>Skill yang Dikuasai</label>
          <input type="text" placeholder="Contoh: Excel, SAP, Financial Modeling, Analisis Data...">
        </div>
        <button class="btn btn-outline" style="width:100%;margin-top:8px" onclick="event.stopPropagation();document.getElementById('card-manual').classList.add('selected');document.getElementById('analyze-btn').classList.remove('btn-disabled');document.getElementById('analyze-btn').disabled=false;">Lanjut dengan Form</button>
      </div>
    </div>

    <div style="text-align:center">
      <div class="scan-bar-wrap" id="scan-wrap" style="max-width:400px;margin:0 auto 16px;display:block;visibility:hidden">
        <div id="scan-progress"></div>
      </div>
      <button id="analyze-btn" class="btn btn-primary btn-lg btn-disabled" disabled onclick="startAnalysis()">
        Analisis Sekarang
      </button>
    </div>
    <p class="security-note" style="margin-top:14px">🔒 Data kamu aman dan tidak dibagikan ke pihak ketiga</p>
  </div>
</div>

<!-- ============================================================
     SCREEN 3 — TOP 3 PROFESI
     ============================================================ -->
<div class="screen" id="screen-3">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Beranda</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-2')">← Kembali</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profil</div></div>
      <div class="progress-step"><div class="step-circle active">2</div><div class="step-label active">Hasil Analisis</div></div>
      <div class="progress-step"><div class="step-circle">3</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle">4</div><div class="step-label">Pilih Paket</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="results-section">
    <h2 style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:var(--navy);margin-bottom:8px">Profesi yang paling cocok untukmu</h2>
    <p class="text-muted" style="margin-bottom:24px;font-size:15px">Berdasarkan <strong>14 skill</strong> yang ditemukan dari profilmu, berikut 3 profesi dengan kecocokan tertinggi</p>

    <div class="skill-chips" style="margin-bottom:36px">
      <span class="chip chip-blue">Financial Modeling ✓</span>
      <span class="chip chip-blue">Microsoft Excel ✓</span>
      <span class="chip chip-blue">Data Analysis ✓</span>
      <span class="chip chip-blue">Accounting ✓</span>
      <span class="chip chip-blue">Auditing ✓</span>
      <span class="chip chip-blue">SAP Basic ✓</span>
      <span class="chip chip-blue">Business Valuation ✓</span>
      <span class="chip chip-blue">Risk Assessment ✓</span>
      <span class="chip chip-blue">Budgeting ✓</span>
      <span class="chip chip-blue">SQL Basic ✓</span>
    </div>

    <!-- Card 1 Best Match -->
    <div class="profession-card best" id="prof-financial-analyst" onclick="selectProfession('financial-analyst');showScreen('screen-4')">
      <div class="prof-rank">01</div>
      <div class="prof-info">
        <div class="prof-name">Financial Analyst</div>
        <div class="prof-desc">Menganalisis data keuangan untuk mendukung keputusan bisnis dan investasi perusahaan</div>
        <div class="prof-bar-label"><span>Kecocokan Skill</span><span style="color:var(--blue);font-weight:700">79%</span></div>
        <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:79%"></div></div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">15 dari 19 skill terpenuhi</div>
      </div>
      <div class="prof-meta">
        <div class="prof-meta-item">Gap: <strong style="color:var(--navy)">4 skill</strong></div>
        <div class="prof-meta-item">Est. roadmap: <strong style="color:var(--navy)">68 hari</strong></div>
        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation();selectProfession('financial-analyst');showScreen('screen-4')">Pilih Ini</button>
      </div>
      <div class="prof-badge-wrap"><span class="badge badge-blue">Best Match</span></div>
    </div>

    <!-- Card 2 -->
    <div class="profession-card" id="prof-accountant" onclick="selectProfession('accountant');showScreen('screen-4')">
      <div class="prof-rank" style="color:var(--border)">02</div>
      <div class="prof-info">
        <div class="prof-name">Accountant</div>
        <div class="prof-desc">Menyusun dan menganalisis laporan keuangan sesuai standar akuntansi yang berlaku</div>
        <div class="prof-bar-label"><span>Kecocokan Skill</span><span style="color:var(--blue);font-weight:700">68%</span></div>
        <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:68%"></div></div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">13 dari 19 skill terpenuhi</div>
      </div>
      <div class="prof-meta">
        <div class="prof-meta-item">Gap: <strong style="color:var(--navy)">6 skill</strong></div>
        <div class="prof-meta-item">Est. roadmap: <strong style="color:var(--navy)">84 hari</strong></div>
        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();selectProfession('accountant');showScreen('screen-4')">Pilih Ini</button>
      </div>
    </div>

    <!-- Card 3 -->
    <div class="profession-card" id="prof-auditor" onclick="selectProfession('auditor');showScreen('screen-4')">
      <div class="prof-rank" style="color:var(--border)">03</div>
      <div class="prof-info">
        <div class="prof-name">Auditor</div>
        <div class="prof-desc">Memeriksa dan memverifikasi keabsahan laporan keuangan serta kepatuhan regulasi</div>
        <div class="prof-bar-label"><span>Kecocokan Skill</span><span style="color:var(--blue);font-weight:700">58%</span></div>
        <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:58%"></div></div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">11 dari 19 skill terpenuhi</div>
      </div>
      <div class="prof-meta">
        <div class="prof-meta-item">Gap: <strong style="color:var(--navy)">8 skill</strong></div>
        <div class="prof-meta-item">Est. roadmap: <strong style="color:var(--navy)">105 hari</strong></div>
        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();selectProfession('auditor');showScreen('screen-4')">Pilih Ini</button>
      </div>
    </div>

    <div class="divider">— atau —</div>

    <!-- Custom Profession -->
    <div class="custom-prof-card">
      <h3>Tambah profesi yang kamu minati</h3>
      <p>Meski skillmu belum banyak untuk profesi ini, Pathfinder tetap akan buatkan roadmap lengkapnya</p>
      <div class="custom-input-row">
        <input id="custom-prof-input" type="text" placeholder="Cari profesi... (contoh: Data Scientist, UI/UX Designer)" onkeydown="if(event.key==='Enter') addProfession()">
        <button class="btn btn-outline btn-sm" onclick="addProfession()">+ Tambah Profesi</button>
      </div>
      <div id="custom-prof-chips"></div>
    </div>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-2')">← Kembali</button>
    <button class="btn btn-primary" onclick="showScreen('screen-4')">Lanjut ke Skill Gap →</button>
  </div>
</div>

<!-- ============================================================
     SCREEN 4 — SKILL GAP
     ============================================================ -->
<div class="screen" id="screen-4">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Beranda</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-3')">← Kembali</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profil</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Hasil Analisis</div></div>
      <div class="progress-step"><div class="step-circle active">3</div><div class="step-label active">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle">4</div><div class="step-label">Pilih Paket</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="gap-section">
    <h2 style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:var(--navy);margin-bottom:8px">Peta skill menuju Financial Analyst</h2>
    <p class="text-muted" style="margin-bottom:28px">Kamu sudah memiliki <strong>15 dari 19 skill</strong> yang dibutuhkan. Berikut detail selengkapnya.</p>

    <!-- Job Readiness Bar -->
    <div class="readiness-bar-wrap">
      <div class="readiness-bar-header">
        <span>Kesiapan Karir Saat Ini</span>
        <span>79% / 100%</span>
      </div>
      <div class="progress-bar-wrap" style="height:12px"><div class="progress-bar-fill" style="width:79%"></div></div>
      <p class="readiness-sub">Selesaikan roadmap untuk mencapai 100% job-ready</p>
    </div>

    <div class="skill-cols">
      <!-- Owned Skills -->
      <div class="skill-col-card">
        <div class="skill-col-header">
          <span style="font-size:18px">✅</span>
          <h3>Skill yang sudah kamu miliki</h3>
          <span class="badge badge-green">15 skill</span>
        </div>
        <div class="skill-list">
          <div class="skill-item"><span class="skill-check">✓</span> Financial Modeling</div>
          <div class="skill-item"><span class="skill-check">✓</span> Microsoft Excel Advanced</div>
          <div class="skill-item"><span class="skill-check">✓</span> Data Analysis</div>
          <div class="skill-item"><span class="skill-check">✓</span> Financial Statement Analysis</div>
          <div class="skill-item"><span class="skill-check">✓</span> Accounting Principles</div>
          <div class="skill-item"><span class="skill-check">✓</span> SAP Financial Module</div>
          <div class="skill-item"><span class="skill-check">✓</span> Business Valuation</div>
          <div class="skill-item"><span class="skill-check">✓</span> Risk Assessment</div>
          <div class="skill-item"><span class="skill-check">✓</span> Budgeting & Forecasting</div>
          <div class="skill-item"><span class="skill-check">✓</span> PowerPoint Presentation</div>
          <div class="skill-item"><span class="skill-check">✓</span> SQL Basic</div>
          <div class="skill-item"><span class="skill-check">✓</span> Pivot Table & Data Viz</div>
          <div class="skill-item"><span class="skill-check">✓</span> Communication Skills</div>
          <div class="skill-item"><span class="skill-check">✓</span> Problem Solving</div>
          <div class="skill-item"><span class="skill-check">✓</span> Attention to Detail</div>
        </div>
      </div>

      <!-- Missing Skills -->
      <div class="skill-col-card">
        <div class="skill-col-header">
          <span style="font-size:18px;color:var(--blue)">🎯</span>
          <h3>Skill yang perlu dibangun</h3>
          <span class="badge badge-blue">4 skill</span>
        </div>
        <div class="skill-list">
          <div class="skill-item">
            <div class="skill-circle"></div>
            <span style="flex:1">Bloomberg Terminal</span>
            <span class="skill-standard"><span class="chip chip-blue" style="font-size:10px">O*NET Standard</span></span>
          </div>
          <div class="skill-item">
            <div class="skill-circle"></div>
            <span style="flex:1">Financial Derivatives</span>
            <span class="skill-standard"><span class="chip chip-blue" style="font-size:10px">O*NET Standard</span></span>
          </div>
          <div class="skill-item">
            <div class="skill-circle"></div>
            <span style="flex:1">CFA Knowledge Base</span>
            <span class="skill-standard"><span class="chip chip-blue" style="font-size:10px">SKKNI Level 5</span></span>
          </div>
          <div class="skill-item">
            <div class="skill-circle"></div>
            <span style="flex:1">Investment Portfolio Analysis</span>
            <span class="skill-standard"><span class="chip chip-blue" style="font-size:10px">O*NET Standard</span></span>
          </div>
        </div>
        <div class="skill-callout">
          Keempat skill ini akan dibangun melalui roadmap belajarmu yang sudah dikurasi berdasarkan standar O*NET dan SKKNI.
        </div>
      </div>
    </div>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-3')">← Kembali</button>
    <button class="btn btn-primary" onclick="showScreen('screen-5')">Pilih Paket Belajar →</button>
  </div>
</div>

<!-- ============================================================
     SCREEN 5 — PILIH PAKET
     ============================================================ -->
<div class="screen" id="screen-5">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Beranda</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-4')">← Kembali</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profil</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Hasil Analisis</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle active">4</div><div class="step-label active">Pilih Paket</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="packages-section">
    <h2 style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:var(--navy);margin-bottom:8px">Pilih kecepatan belajarmu</h2>
    <p class="text-muted" style="margin-bottom:32px">Semua paket mencakup kursus bersertifikat yang sama standarnya. Bedanya pada kedalaman materi.</p>

    <!-- Slider -->
    <div class="slider-wrap">
      <div class="slider-label">
        <span>Berapa jam kamu bisa belajar per hari?</span>
        <span id="hours-display">2 jam / hari</span>
      </div>
      <input type="range" id="hours-slider" min="1" max="8" value="2">
      <p class="slider-note">⏱ Durasi roadmap akan menyesuaikan otomatis berdasarkan jam belajarmu</p>
    </div>

    <div class="packages-grid">
      <!-- Paket Cepat -->
      <div class="package-card" id="pkg-cepat" onclick="selectPackage('cepat')">
        <div class="pkg-icon">⚡</div>
        <div class="pkg-name">Paket Cepat</div>
        <div class="pkg-days" id="fast-days">34 hari</div>
        <div class="pkg-days-label">estimasi penyelesaian</div>
        <div class="pkg-hours">68 jam materi total</div>
        <div class="pkg-courses">
          <div class="course-item">
            <div class="course-name">Bloomberg Terminal Essentials</div>
            <div class="course-meta">12 jam <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Intro to Financial Derivatives</div>
            <div class="course-meta">18 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">CFA Level 1 Fundamentals</div>
            <div class="course-meta">22 jam <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Portfolio Analysis Basics</div>
            <div class="course-meta">16 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
        </div>
        <div class="pkg-cert">🎓 Sertifikat: 4 sertifikat</div>
        <button class="btn btn-outline" style="width:100%" onclick="event.stopPropagation();selectPackage('cepat');showScreen('screen-6')">Pilih Paket Ini</button>
      </div>

      <!-- Paket Sedang (Recommended) -->
      <div class="package-card recommended" id="pkg-sedang" onclick="selectPackage('sedang')">
        <div class="pkg-recommended-badge"><span class="badge badge-blue">Paling Banyak Dipilih</span></div>
        <div class="pkg-icon" style="color:var(--blue)">🎯</div>
        <div class="pkg-name">Paket Sedang</div>
        <div class="pkg-days" id="mid-days">51 hari</div>
        <div class="pkg-days-label">estimasi penyelesaian</div>
        <div class="pkg-hours">102 jam materi total</div>
        <div class="pkg-courses">
          <div class="course-item">
            <div class="course-name">Bloomberg Terminal Complete Guide</div>
            <div class="course-meta">24 jam <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Financial Derivatives & Risk Mgmt</div>
            <div class="course-meta">28 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">CFA Level 1 Complete Program</div>
            <div class="course-meta">32 jam <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Portfolio Analysis & Management</div>
            <div class="course-meta">18 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
        </div>
        <div class="pkg-cert">🎓 Sertifikat: 4 sertifikat</div>
        <button class="btn btn-primary" style="width:100%" onclick="event.stopPropagation();selectPackage('sedang');showScreen('screen-6')">Pilih Paket Ini</button>
      </div>

      <!-- Paket Komprehensif -->
      <div class="package-card" id="pkg-komprehensif" onclick="selectPackage('komprehensif')">
        <div class="pkg-icon">📚</div>
        <div class="pkg-name">Paket Komprehensif</div>
        <div class="pkg-days" id="full-days">78 hari</div>
        <div class="pkg-days-label">estimasi penyelesaian</div>
        <div class="pkg-hours">156 jam materi total</div>
        <div class="pkg-courses">
          <div class="course-item">
            <div class="course-name">Bloomberg Terminal Mastery + Practice</div>
            <div class="course-meta">38 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Complete Derivatives & Structured Products</div>
            <div class="course-meta">42 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">CFA Level 1 + 2 Preparation</div>
            <div class="course-meta">52 jam <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Advanced Portfolio & Asset Management</div>
            <div class="course-meta">24 jam <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
        </div>
        <div class="pkg-cert">🎓 Sertifikat: 4 sertifikat</div>
        <button class="btn btn-outline" style="width:100%" onclick="event.stopPropagation();selectPackage('komprehensif');showScreen('screen-6')">Pilih Paket Ini</button>
      </div>
    </div>

    <p class="packages-note">Semua kursus telah dikurasi Pathfinder — setiap sertifikat yang diterbitkan diakui sebagai bukti kompetensi standar industri</p>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-4')">← Kembali</button>
    <button class="btn btn-primary" onclick="showScreen('screen-6')">Lihat Roadmap Lengkap →</button>
  </div>
</div>

<!-- ============================================================
     SCREEN 6 — ROADMAP TIMELINE
     ============================================================ -->
<div class="screen" id="screen-6">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Beranda</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-5')">← Kembali</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profil</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Hasil Analisis</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Pilih Paket</div></div>
      <div class="progress-step"><div class="step-circle active">5</div><div class="step-label active">Roadmap</div></div>
    </div>
  </div>

  <div class="roadmap-section">
    <div class="roadmap-header">
      <div>
        <h2 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:var(--navy);margin-bottom:8px">Roadmapmu menuju Financial Analyst</h2>
        <p class="text-muted" style="font-size:14px">Paket Sedang · 2 jam/hari · Mulai Hari Ini</p>
      </div>
      <div class="roadmap-stats">
        <div class="roadmap-stat-chip">📋 4 Tahapan</div>
        <div class="roadmap-stat-chip">⏱ 102 Jam Total</div>
        <div class="roadmap-stat-chip">📅 51 Hari Estimasi</div>
      </div>
    </div>

    <div class="timeline">
      <!-- Tahap 1 AKTIF -->
      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet active">1</div>
          <div class="timeline-line active"></div>
        </div>
        <div class="timeline-card active" style="flex:1">
          <div class="tl-badge"><span class="badge badge-blue">Sedang Berjalan</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill yang dibangun</div>
              <div class="tl-skill-name">Bloomberg Terminal</div>
              <div class="tl-course-name">Bloomberg Terminal Complete Guide · <span class="chip chip-blue" style="font-size:11px">Udemy</span> <span class="chip chip-green" style="font-size:11px">Bersertifikat ✓</span></div>
              <div class="tl-duration">24 jam total · 12 hari dengan 2 jam/hari</div>
              <div style="margin-top:12px">
                <div style="font-size:12px;color:var(--text-muted);margin-bottom:5px;display:flex;justify-content:space-between"><span>Progress Kursus</span><span>0%</span></div>
                <div class="progress-bar-wrap" style="height:6px"><div class="progress-bar-fill" style="width:0%"></div></div>
              </div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Mulai: <strong>Hari ke-1</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target selesai: <strong>Hari ke-12</strong></div>
              <button class="btn btn-primary btn-sm" onclick="showScreen('screen-7')">Mulai Belajar →</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tahap 2 -->
      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet">2</div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-card" style="flex:1;opacity:0.75">
          <div class="tl-badge"><span class="badge badge-surface">Menunggu Tahap 1</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill yang dibangun</div>
              <div class="tl-skill-name">Financial Derivatives</div>
              <div class="tl-course-name">Financial Derivatives & Risk Mgmt · <span class="chip chip-muted" style="font-size:11px">Coursera</span></div>
              <div class="tl-duration">28 jam total · 14 hari dengan 2 jam/hari</div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Mulai: <strong>Hari ke-13</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target selesai: <strong>Hari ke-26</strong></div>
              <button class="btn btn-disabled btn-sm" disabled>🔒 Terkunci</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tahap 3 -->
      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet">3</div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-card" style="flex:1;opacity:0.65">
          <div class="tl-badge"><span class="badge badge-surface">Menunggu Tahap 2</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill yang dibangun</div>
              <div class="tl-skill-name">CFA Knowledge Base</div>
              <div class="tl-course-name">CFA Level 1 Complete Program · <span class="chip chip-blue" style="font-size:11px">Udemy</span></div>
              <div class="tl-duration">32 jam total · 16 hari dengan 2 jam/hari</div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Mulai: <strong>Hari ke-27</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target selesai: <strong>Hari ke-42</strong></div>
              <button class="btn btn-disabled btn-sm" disabled>🔒 Terkunci</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tahap 4 -->
      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet">4</div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-card" style="flex:1;opacity:0.55">
          <div class="tl-badge"><span class="badge badge-surface">Menunggu Tahap 3</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill yang dibangun</div>
              <div class="tl-skill-name">Investment Portfolio Analysis</div>
              <div class="tl-course-name">Portfolio Analysis & Management · <span class="chip chip-muted" style="font-size:11px">Coursera</span></div>
              <div class="tl-duration">18 jam total · 9 hari dengan 2 jam/hari</div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Mulai: <strong>Hari ke-43</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target selesai: <strong>Hari ke-51</strong></div>
              <button class="btn btn-disabled btn-sm" disabled>🔒 Terkunci</button>
            </div>
          </div>
        </div>
      </div>

      <!-- End Node -->
      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet done">✓</div>
        </div>
        <div class="end-node" style="flex:1;margin-bottom:32px">
          <div class="end-text">
            <h3>Financial Analyst — Job Ready ✓</h3>
            <p>Semua skill terstandarisasi O*NET dan SKKNI telah terpenuhi · Hari ke-52 dst</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-5')">← Kembali</button>
    <button class="btn btn-primary" onclick="showScreen('screen-7')">Mulai Perjalanan →</button>
  </div>
</div>

<!-- ============================================================
     SCREEN 7 — PROGRESS DASHBOARD
     ============================================================ -->
<div class="screen" id="screen-7">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')">PATHFINDER</a>
    <div class="navbar-links">
      <a onclick="showScreen('screen-6')">Roadmap</a>
      <a onclick="showScreen('screen-4')">Skill Gap</a>
    </div>
    <div class="navbar-right">
      <div class="avatar">RD</div>
    </div>
  </nav>

  <div class="dashboard-section">
    <!-- Greeting -->
    <div class="greeting-row">
      <div class="greeting-text">
        <h2>Selamat datang kembali, Rizky 👋</h2>
        <p>Kamu sedang dalam perjalanan menuju <strong>Financial Analyst</strong></p>
      </div>
      <button class="btn btn-outline" onclick="showScreen('screen-6')">Lihat Roadmap Lengkap</button>
    </div>

    <!-- Metric Cards -->
    <div class="metric-cards">
      <div class="metric-card">
        <div class="metric-label">Job-Readiness Score</div>
        <div class="metric-value" style="color:var(--blue)">79%</div>
        <div class="metric-sub">Naik 0% minggu ini (baru mulai)</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Tahap Aktif</div>
        <div class="metric-value">1 / 4</div>
        <div class="metric-sub">Bloomberg Terminal</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Hari Tersisa</div>
        <div class="metric-value">51</div>
        <div class="metric-sub">Estimasi selesai</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Sertifikat Diperoleh</div>
        <div class="metric-value">0 / 4</div>
        <div class="metric-sub">Selesaikan tahap untuk unlock</div>
      </div>
    </div>

    <!-- Active Stage -->
    <div class="active-stage-card">
      <div class="active-stage-header">
        <div class="active-stage-title">Tahap 1 — Bloomberg Terminal</div>
        <span class="badge badge-blue">Sedang Berjalan</span>
      </div>
      <div class="active-course-meta">Bloomberg Terminal Complete Guide · Udemy · 24 jam total</div>
      <div class="progress-label">
        <span>Progress Belajar</span>
        <span>0 dari 24 jam diselesaikan</span>
      </div>
      <div class="progress-bar-wrap" style="height:10px"><div class="progress-bar-fill" style="width:0%"></div></div>
      <div class="active-stage-actions">
        <button class="btn btn-primary">Lanjutkan Belajar</button>
        <button class="btn btn-outline">Upload Sertifikat</button>
      </div>
      <p class="active-stage-note">Upload sertifikat setelah selesai untuk membuka tahap berikutnya</p>
    </div>

    <!-- Skill Progress -->
    <div class="skill-progress-card">
      <h3>Progress Skill menuju Financial Analyst</h3>
      <div class="skill-progress-row">
        <div class="skill-progress-meta">
          <span class="name">Bloomberg Terminal</span>
          <span class="pct" style="color:var(--blue)">0% — In Progress</span>
        </div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%"></div></div>
      </div>
      <div class="skill-progress-row">
        <div class="skill-progress-meta">
          <span class="name">Financial Derivatives</span>
          <span class="pct">Terkunci 🔒</span>
        </div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%;background:var(--border)"></div></div>
      </div>
      <div class="skill-progress-row">
        <div class="skill-progress-meta">
          <span class="name">CFA Knowledge Base</span>
          <span class="pct">Terkunci 🔒</span>
        </div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%;background:var(--border)"></div></div>
      </div>
      <div class="skill-progress-row" style="margin-bottom:0">
        <div class="skill-progress-meta">
          <span class="name">Investment Portfolio Analysis</span>
          <span class="pct">Terkunci 🔒</span>
        </div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%;background:var(--border)"></div></div>
      </div>
      <div class="owned-chips">
        <p>Skill yang sudah dimiliki (15 skill):</p>
        <div class="owned-chips-list">
          <span class="chip chip-green">Financial Modeling</span>
          <span class="chip chip-green">Microsoft Excel</span>
          <span class="chip chip-green">Data Analysis</span>
          <span class="chip chip-green">Financial Statement</span>
          <span class="chip chip-green">Accounting Principles</span>
          <span class="chip chip-green">SAP Financial</span>
          <span class="chip chip-green">Business Valuation</span>
          <span class="chip chip-green">Risk Assessment</span>
          <span class="chip chip-green">Budgeting</span>
          <span class="chip chip-green">PowerPoint</span>
          <span class="chip chip-green">SQL Basic</span>
          <span class="chip chip-green">Pivot Table</span>
          <span class="chip chip-green">Communication</span>
          <span class="chip chip-green">Problem Solving</span>
          <span class="chip chip-green">Attention to Detail</span>
        </div>
      </div>
    </div>

    <!-- Upload Proof -->
    <div class="upload-proof-card">
      <h3>Submit sertifikat kursus</h3>
      <p class="upload-proof-sub">Setiap sertifikat yang kamu upload akan diverifikasi dan menjadi bukti kompetensi resmi</p>
      <div class="upload-proof-drop">
        <div style="font-size:28px;margin-bottom:8px">📎</div>
        Drag & drop sertifikat PDF atau gambar di sini
      </div>
      <button class="btn btn-outline btn-sm">Pilih File</button>
      <p class="upload-proof-note" style="margin-top:10px">Format yang diterima: PDF, JPG, PNG · Maks. 10MB</p>
    </div>

    <!-- Motivation -->
    <div class="motivation-card">
      <p>💡 <strong>Konsistensi adalah kunci.</strong> Dengan 2 jam/hari, kamu akan menjadi <strong>Financial Analyst</strong> dalam <strong>51 hari</strong>. Setiap jam yang kamu investasikan hari ini adalah langkah nyata menuju karir impianmu.</p>
    </div>
  </div>
</div>

<script>
{JS}

function startAnalysis() {{
  const wrap = document.getElementById('scan-wrap');
  if (wrap) wrap.style.visibility = 'visible';
  runAIScanning();
}}

// Script is at bottom of body — DOM is ready, call directly
showScreen('screen-1');
initSlider();
</script>
</body>
</html>"""

st.components.v1.html(HTML, height=900, scrolling=True)
