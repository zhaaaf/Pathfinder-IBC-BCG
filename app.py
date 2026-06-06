import streamlit as st
import os

st.set_page_config(
    page_title="Pathfinder — AI Career Mapping",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
JS  = load_file("assets/script.js")

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pathfinder — AI Career Mapping</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{CSS}
/* ── SCREEN 1 ── */
.hero {{ background:var(--navy-bg); display:flex; justify-content:center; min-height:calc(100vh - 64px); }}
.hero-inner {{
  display:flex; width:100%; max-width:1200px; padding:0 48px;
}}
.hero-left {{
  flex:0 0 55%; padding:72px 16px 72px 0;
  display:flex; flex-direction:column; justify-content:center; gap:28px;
}}
.hero-eyebrow {{ font-size:11px; letter-spacing:3px; font-weight:700; color:var(--gold); text-transform:uppercase; }}
.hero-heading {{ font-family:'Playfair Display',serif; font-size:48px; font-weight:800; line-height:1.1; color:var(--heading-on-dark); }}
.hero-heading span {{ color:var(--gold); }}
.hero-sub {{ font-size:16px; color:var(--text-on-dark); opacity:0.78; max-width:460px; line-height:1.7; }}
.hero-ctas {{ display:flex; gap:14px; flex-wrap:wrap; }}
.hero-microcopy {{ font-family:'Inter',sans-serif; font-size:12px; font-weight:400; color:var(--text-on-dark); opacity:0.45; }}
.hero-right {{
  flex:0 0 45%; padding:72px 0 72px 16px;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:20px;
  position:relative;
}}
.floating-card-wrap {{ position:relative; width:100%; max-width:380px; }}
.example-output-badge {{
  position:absolute; top:-13px; right:18px; z-index:2;
  font-family:'Inter',sans-serif; font-size:11px; font-weight:600; letter-spacing:0.5px;
  color:var(--gold); background:#FFFFFF; border:1px solid rgba(180,142,75,0.35);
  border-radius:99px; padding:4px 14px; box-shadow:0 4px 10px rgba(0,0,0,0.12);
}}
.floating-card {{
  background:white; border:1px solid var(--border); border-radius:14px;
  padding:28px; width:100%; max-width:380px;
  box-shadow:0 20px 48px rgba(0,0,0,0.28);
}}
.floating-card-header {{ font-family:'Inter',sans-serif; font-size:11px; text-transform:uppercase; letter-spacing:2px; color:var(--text-muted); margin-bottom:20px; font-weight:600; }}
.prof-row {{ margin-bottom:16px; }}
.prof-row:last-child {{ margin-bottom:0; }}
.prof-label {{ display:flex; justify-content:space-between; font-family:'Inter',sans-serif; font-size:13px; font-weight:600; margin-bottom:6px; color:var(--navy); }}
.prof-label span {{ color:var(--gold); }}
.floating-badge {{ font-size:11px; color:var(--text-muted); display:flex; align-items:center; gap:6px; }}
.step-cards {{ display:grid; grid-template-columns:1fr auto 1fr auto 1fr auto 1fr; align-items:center; gap:8px; padding:64px 48px; background:white; }}
.step-connector {{ display:flex; align-items:center; justify-content:center; color:var(--border); width:48px; }}
.step-connector svg {{ width:48px; height:18px; display:block; }}
.step-card {{ background:var(--white); border:1px solid var(--border); border-radius:12px; padding:28px 24px; box-shadow:0px 4px 20px rgba(15,23,42,0.05); transition:box-shadow .2s,transform .2s; }}
.step-card:hover {{ box-shadow:0px 8px 28px rgba(15,23,42,0.09); transform:translateY(-2px); }}
.step-icon {{ width:28px; height:28px; margin-bottom:14px; color:var(--gold); }}
.step-icon svg {{ width:28px; height:28px; display:block; }}
.step-title {{ font-family:'Inter',sans-serif; font-size:16px; font-weight:600; color:var(--navy); margin-bottom:8px; }}
.step-desc {{ font-family:'Inter',sans-serif; font-size:14px; font-weight:400; color:var(--text-muted); line-height:1.5; }}
.stats-section {{ background:var(--navy-bg); padding:64px 48px; display:flex; justify-content:center; gap:64px; }}
.stat-item {{ text-align:center; }}
.stat-num {{ font-family:'Playfair Display',serif; font-size:42px; font-weight:800; color:var(--heading-on-dark); margin-bottom:8px; }}
.stat-label {{ font-family:'Inter',sans-serif; font-size:14px; font-weight:400; color:var(--stat-label); }}
.cta-section {{ background:var(--surface); padding:80px 48px; text-align:center; }}
.cta-section h2 {{ font-family:'Playfair Display',serif; font-size:32px; font-weight:800; color:var(--navy); margin-bottom:16px; }}
.cta-section p {{ font-family:'Inter',sans-serif; color:var(--text-muted); font-size:15px; font-weight:400; margin-bottom:32px; }}

/* ── SCREEN 2 ── */
.upload-section {{ padding:64px 48px; max-width:960px; margin:0 auto; }}
.upload-heading {{ text-align:center; margin-bottom:8px; font-family:'Inter',sans-serif; font-size:36px; font-weight:800; color:var(--navy); }}
.upload-sub {{ text-align:center; color:var(--text-muted); margin-bottom:48px; font-size:16px; }}
.upload-cards {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-bottom:32px; }}
.upload-card {{ border:1px solid var(--border); border-radius:12px; padding:36px 28px; background:white; transition:border-color .2s,box-shadow .2s; }}
.upload-card:hover {{ border-color:var(--blue); box-shadow:0 4px 16px rgba(156,122,74,0.14); }}
.upload-card.selected {{ border-color:var(--blue); background:var(--blue-light); }}
.upload-icon {{ font-size:40px; margin-bottom:16px; }}
.upload-card h3 {{ font-family:'Inter',sans-serif; font-size:20px; font-weight:700; color:var(--navy); margin-bottom:10px; }}
.upload-card p {{ font-size:14px; color:var(--text-muted); margin-bottom:20px; line-height:1.5; }}
.drop-zone {{
  border:2px dashed var(--border); border-radius:8px; padding:32px;
  text-align:center; color:var(--text-muted); font-size:13px; margin-bottom:20px;
  transition:border-color .2s,background .2s; cursor:pointer; user-select:none;
}}
.drop-zone:hover {{ border-color:var(--blue); color:var(--blue); }}
.drop-zone.drag-over {{ border-color:var(--blue); background:var(--blue-light); color:var(--blue); }}
.drop-zone.file-ready {{ border-color:var(--success); background:#f0fdf4; color:var(--success); }}
#file-name-display {{ margin-top:8px; font-size:13px; font-weight:600; min-height:18px; }}
.form-field {{ margin-bottom:14px; }}
.form-field label {{ display:block; font-size:13px; font-weight:600; color:var(--navy); margin-bottom:5px; }}
.form-field input,.form-field select,.form-field textarea {{
  width:100%; padding:10px 12px; border:1px solid var(--border); border-radius:8px;
  font-family:'Inter',sans-serif; font-size:14px; color:var(--text-main);
  background:var(--surface); outline:none; transition:border-color .2s;
}}
.form-field input:focus,.form-field select:focus,.form-field textarea:focus {{ border-color:var(--blue); background:white; }}
.form-field textarea {{ resize:vertical; min-height:80px; }}
.scan-bar-wrap {{ background:var(--border); border-radius:99px; height:4px; overflow:hidden; margin-top:8px; }}
#scan-progress {{ height:100%; background:var(--blue); border-radius:99px; width:0%; transition:width .1s linear; }}
.security-note {{ text-align:center; color:var(--text-muted); font-size:13px; margin-top:16px; }}

/* ── SCREEN 3 ── */
.results-section {{ padding:48px; max-width:960px; margin:0 auto; }}
.skill-chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:40px; }}
.profession-card {{
  border:1px solid var(--border); border-radius:12px; padding:24px 28px;
  margin-bottom:16px; display:flex; align-items:center; gap:24px;
  background:white; transition:box-shadow .2s; cursor:pointer; position:relative;
}}
.profession-card:hover {{ box-shadow:0 4px 16px rgba(0,0,0,0.08); }}
.profession-card.best {{ border-left:4px solid var(--blue); background:var(--blue-light); }}
.profession-card.selected {{ border-color:var(--blue); box-shadow:0 0 0 2px rgba(156,122,74,0.22); }}
.prof-rank {{ font-family:'Inter',sans-serif; font-size:28px; font-weight:800; color:var(--blue-light); flex-shrink:0; width:48px; }}
.prof-info {{ flex:1; }}
.prof-name {{ font-family:'Inter',sans-serif; font-size:18px; font-weight:700; color:var(--navy); margin-bottom:4px; }}
.prof-desc {{ font-size:13px; color:var(--text-muted); margin-bottom:12px; }}
.prof-bar-label {{ font-size:12px; font-weight:600; color:var(--text-muted); margin-bottom:5px; display:flex; justify-content:space-between; }}
.prof-meta {{ flex-shrink:0; text-align:right; display:flex; flex-direction:column; gap:8px; align-items:flex-end; }}
.prof-meta-item {{ font-size:12px; color:var(--text-muted); }}
.prof-badge-wrap {{ position:absolute; top:16px; right:16px; }}
.custom-prof-card {{ border:2px dashed var(--border); border-radius:12px; padding:28px; background:var(--surface); }}
.custom-prof-card h3 {{ font-family:'Inter',sans-serif; font-size:16px; font-weight:700; color:var(--navy); margin-bottom:6px; }}
.custom-prof-card p {{ font-size:13px; color:var(--text-muted); margin-bottom:16px; }}
.custom-input-row {{ display:flex; gap:10px; margin-bottom:12px; }}
.custom-input-row input {{ flex:1; padding:10px 14px; border:1px solid var(--border); border-radius:8px; font-family:'Inter',sans-serif; font-size:14px; outline:none; }}
.custom-input-row input:focus {{ border-color:var(--blue); }}
#custom-prof-chips {{ display:flex; flex-wrap:wrap; gap:6px; min-height:28px; }}
.nav-bottom {{ display:flex; justify-content:space-between; align-items:center; padding:32px 48px; border-top:1px solid var(--border); background:white; position:sticky; bottom:0; }}

/* ── SCREEN 4 ── */
.gap-section {{ padding:48px; max-width:1000px; margin:0 auto; }}
.readiness-bar-wrap {{ background:var(--blue-light); border-radius:12px; padding:24px 28px; margin-bottom:40px; }}
.readiness-bar-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }}
.readiness-bar-header span:first-child {{ font-size:14px; font-weight:600; color:var(--navy); }}
.readiness-bar-header span:last-child {{ font-family:'Inter',sans-serif; font-size:22px; font-weight:800; color:var(--blue); }}
.readiness-sub {{ font-size:12px; color:var(--text-muted); margin-top:8px; }}
.skill-cols {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
.skill-col-card {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; background:white; }}
.skill-col-header {{ padding:16px 20px; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:10px; }}
.skill-col-header h3 {{ font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:var(--navy); flex:1; }}
.skill-list {{ padding:8px 0; }}
.skill-item {{ display:flex; align-items:center; gap:12px; padding:10px 20px; border-bottom:1px solid var(--border); font-size:13px; font-weight:500; }}
.skill-item:last-child {{ border-bottom:none; }}
.skill-check {{ color:var(--success); font-size:16px; flex-shrink:0; }}
.skill-circle {{ width:18px; height:18px; border-radius:50%; border:2px solid var(--blue); flex-shrink:0; }}
.skill-standard {{ margin-left:auto; }}
.skill-callout {{ margin:16px 20px 20px; background:var(--blue-light); border-left:3px solid var(--blue); border-radius:6px; padding:12px 14px; font-size:12px; color:var(--blue); }}

/* ── SCREEN 5 ── */
.packages-section {{ padding:48px; max-width:1100px; margin:0 auto; }}
.slider-wrap {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:24px 28px; margin-bottom:36px; }}
.slider-label {{ font-size:14px; font-weight:600; color:var(--navy); margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; }}
.slider-label span:last-child {{ font-family:'Inter',sans-serif; font-size:18px; font-weight:700; color:var(--blue); }}
input[type=range] {{ width:100%; accent-color:var(--blue); cursor:pointer; }}
.slider-note {{ font-size:12px; color:var(--text-muted); margin-top:8px; }}
.packages-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; }}
.package-card {{
  border:1px solid var(--border); border-radius:12px; padding:28px 24px;
  background:white; position:relative; cursor:pointer;
  transition:box-shadow .2s,border-color .2s; display:flex; flex-direction:column;
}}
.package-card:hover {{ box-shadow:0 4px 20px rgba(0,0,0,0.08); }}
.package-card.recommended {{ border:2px solid var(--blue); background:var(--blue-light); }}
.package-card.selected {{ box-shadow:0 0 0 3px rgba(156,122,74,0.22); }}
.pkg-recommended-badge {{ position:absolute; top:-13px; left:50%; transform:translateX(-50%); white-space:nowrap; }}
.pkg-icon {{ font-size:28px; margin-bottom:12px; }}
.pkg-name {{ font-family:'Inter',sans-serif; font-size:18px; font-weight:700; color:var(--navy); margin-bottom:4px; }}
.pkg-days {{ font-family:'Inter',sans-serif; font-size:32px; font-weight:800; color:var(--blue); }}
.pkg-days-label {{ font-size:12px; color:var(--text-muted); margin-bottom:6px; }}
.pkg-hours {{ font-size:13px; color:var(--text-muted); margin-bottom:20px; padding-bottom:20px; border-bottom:1px solid var(--border); }}
.pkg-courses {{ display:flex; flex-direction:column; gap:12px; flex:1; margin-bottom:20px; }}
.course-item {{ font-size:13px; }}
.course-name {{ font-weight:600; color:var(--navy); margin-bottom:4px; }}
.course-meta {{ display:flex; align-items:center; gap:6px; color:var(--text-muted); font-size:12px; }}
.pkg-cert {{ font-size:12px; color:var(--text-muted); padding:10px 0; border-top:1px solid var(--border); margin-bottom:16px; }}
.packages-note {{ text-align:center; color:var(--text-muted); font-size:13px; margin-top:24px; padding:0 48px; }}

/* ── SCREEN 6 ── */
.roadmap-section {{ padding:48px; max-width:900px; margin:0 auto; }}
.roadmap-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:40px; gap:24px; }}
.roadmap-stats {{ display:flex; gap:12px; flex-wrap:wrap; }}
.roadmap-stat-chip {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:8px 16px; font-size:13px; font-weight:600; color:var(--navy); white-space:nowrap; }}
.timeline {{ position:relative; }}
.timeline-item {{ display:flex; gap:20px; margin-bottom:0; }}
.timeline-left {{ display:flex; flex-direction:column; align-items:center; gap:0; flex-shrink:0; }}
.timeline-bullet {{
  width:36px; height:36px; border-radius:50%; border:2px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  font-family:'Inter',sans-serif; font-size:13px; font-weight:700; color:var(--text-muted);
  background:white; flex-shrink:0; z-index:1;
}}
.timeline-bullet.active {{ background:var(--blue); border-color:var(--blue); color:white; }}
.timeline-bullet.done {{ background:var(--success); border-color:var(--success); color:white; }}
.timeline-line {{ flex:1; width:2px; background:var(--border); margin:4px 0; min-height:40px; }}
.timeline-line.active {{ background:var(--blue); }}
.timeline-card {{
  flex:1; background:white; border:1px solid var(--border); border-radius:12px;
  padding:20px 24px; margin-bottom:24px; position:relative;
}}
.timeline-card.active {{ background:var(--blue-light); border-left:4px solid var(--blue); }}
.timeline-card-inner {{ display:flex; gap:20px; }}
.timeline-card-main {{ flex:1; }}
.timeline-card-side {{ flex-shrink:0; text-align:right; min-width:140px; }}
.tl-skill-label {{ font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:var(--text-muted); font-weight:600; margin-bottom:4px; }}
.tl-skill-name {{ font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:var(--navy); margin-bottom:4px; }}
.tl-course-name {{ font-size:13px; color:var(--text-muted); margin-bottom:12px; }}
.tl-duration {{ font-size:12px; color:var(--text-muted); margin-top:10px; }}
.tl-date {{ font-size:12px; color:var(--text-muted); margin-bottom:4px; }}
.tl-date strong {{ color:var(--navy); }}
.tl-badge {{ position:absolute; top:16px; right:16px; }}
.end-node {{
  display:flex; align-items:center; gap:16px;
  background:#F0FDF9; border:1px solid var(--success); border-radius:12px;
  padding:20px 24px; margin-top:4px;
}}
.end-bullet {{ width:36px; height:36px; border-radius:50%; background:var(--success); color:white; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; }}
.end-text h3 {{ font-family:'Inter',sans-serif; font-size:16px; font-weight:700; color:var(--success); }}
.end-text p {{ font-size:13px; color:var(--text-muted); }}

/* ── SCREEN 7 ── */
.dashboard-section {{ padding:32px 48px; max-width:1100px; margin:0 auto; }}
.greeting-row {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:32px; }}
.greeting-text h2 {{ font-family:'Inter',sans-serif; font-size:24px; font-weight:800; color:var(--navy); margin-bottom:4px; }}
.greeting-text p {{ font-size:14px; color:var(--text-muted); }}
.metric-cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }}
.metric-card {{ border:1px solid var(--border); border-radius:12px; padding:20px; background:white; }}
.metric-label {{ font-size:12px; color:var(--text-muted); font-weight:500; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.5px; }}
.metric-value {{ font-family:'Inter',sans-serif; font-size:28px; font-weight:800; color:var(--navy); margin-bottom:4px; }}
.metric-sub {{ font-size:12px; color:var(--text-muted); }}
.active-stage-card {{ border:1px solid var(--border); border-radius:12px; padding:28px; margin-bottom:24px; background:white; }}
.active-stage-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }}
.active-stage-title {{ font-family:'Inter',sans-serif; font-size:18px; font-weight:700; color:var(--navy); }}
.active-course-meta {{ font-size:14px; color:var(--text-muted); margin-bottom:16px; }}
.progress-label {{ display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:var(--navy); margin-bottom:8px; }}
.active-stage-actions {{ display:flex; gap:12px; margin-top:20px; flex-wrap:wrap; }}
.active-stage-note {{ font-size:12px; color:var(--text-muted); margin-top:10px; }}
.skill-progress-card {{ border:1px solid var(--border); border-radius:12px; padding:28px; margin-bottom:24px; background:white; }}
.skill-progress-card h3 {{ font-family:'Inter',sans-serif; font-size:16px; font-weight:700; color:var(--navy); margin-bottom:20px; }}
.skill-progress-row {{ margin-bottom:14px; }}
.skill-progress-row:last-child {{ margin-bottom:0; }}
.skill-progress-meta {{ display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px; }}
.skill-progress-meta .name {{ font-weight:600; color:var(--navy); }}
.skill-progress-meta .pct {{ color:var(--text-muted); }}
.owned-chips {{ padding-top:16px; border-top:1px solid var(--border); margin-top:16px; }}
.owned-chips p {{ font-size:12px; color:var(--text-muted); margin-bottom:8px; }}
.owned-chips-list {{ display:flex; flex-wrap:wrap; gap:6px; }}
.upload-proof-card {{ border:1px solid var(--border); border-radius:12px; padding:28px; margin-bottom:24px; background:white; }}
.upload-proof-card h3 {{ font-family:'Inter',sans-serif; font-size:16px; font-weight:700; color:var(--navy); margin-bottom:4px; }}
.upload-proof-sub {{ font-size:13px; color:var(--text-muted); margin-bottom:16px; }}
.upload-proof-drop {{ border:2px dashed var(--border); border-radius:8px; padding:28px; text-align:center; color:var(--text-muted); font-size:13px; margin-bottom:14px; cursor:pointer; transition:border-color .2s; }}
.upload-proof-drop:hover {{ border-color:var(--blue); color:var(--blue); }}
.upload-proof-note {{ font-size:12px; color:var(--text-muted); }}
.motivation-card {{ background:var(--navy-bg); border-radius:12px; padding:24px 28px; margin-bottom:32px; }}
.motivation-card p {{ color:rgba(255,255,255,0.85); font-size:15px; line-height:1.6; font-style:italic; }}
.motivation-card p strong {{ color:white; font-style:normal; }}

@media (max-width:768px) {{
  .hero-inner {{ flex-direction:column; padding:0 24px; }}
  .hero-left {{ flex:none; padding:48px 0; }}
  .hero-heading {{ font-size:32px; }}
  .hero-right {{ flex:none; padding:0 0 40px 0; }}
  .step-cards {{ grid-template-columns:1fr 1fr; padding:40px 20px; }}
  .step-connector {{ display:none; }}
  .stats-section {{ flex-direction:column; gap:32px; padding:48px 24px; text-align:center; }}
  .upload-section {{ padding:40px 20px; }}
  .upload-cards {{ grid-template-columns:1fr; }}
  .results-section,.gap-section,.packages-section,.roadmap-section,.dashboard-section {{ padding:40px 20px; }}
  .packages-grid {{ grid-template-columns:1fr; }}
  .skill-cols {{ grid-template-columns:1fr; }}
  .metric-cards {{ grid-template-columns:1fr 1fr; }}
  .roadmap-header {{ flex-direction:column; }}
  .profession-card {{ flex-direction:column; }}
  .prof-meta {{ align-items:flex-start; text-align:left; }}
  .timeline-card-inner {{ flex-direction:column; }}
  .timeline-card-side {{ text-align:left; }}
  .nav-bottom {{ padding:20px; }}
  .greeting-row {{ flex-direction:column; gap:16px; }}
  .progress-steps {{ gap:4px; }}
}}
</style>
</head>
<body>

<!-- ============================================================ SCREEN 1 — LANDING -->
<div class="screen" id="screen-1">
  <nav class="navbar">
    <a class="navbar-logo">PATHFINDER</a>
    <div class="navbar-links">
      <a onclick="document.getElementById('how-it-works').scrollIntoView({{behavior:'smooth'}})">How It Works</a>
      <a>About</a>
      <a onclick="showScreen('screen-5')">Pricing</a>
    </div>
    <div class="navbar-right">
      <button class="btn btn-primary" onclick="showScreen('screen-2')">Get Started</button>
    </div>
  </nav>

  <div class="hero">
   <div class="hero-inner">
    <div class="hero-left">
      <p class="hero-eyebrow">AI-Powered Career Mapping</p>
      <h1 class="hero-heading">Discover Your Career<br><span>Path Today</span></h1>
      <p class="hero-sub">Know exactly what skills you need for your dream career. Pathfinder compares your CV with global industry standards to build a personalized learning roadmap.</p>
      <div class="hero-ctas">
        <button class="btn btn-primary btn-lg" onclick="showScreen('screen-2')">Analyze My CV</button>
        <button class="btn btn-outline-white btn-lg" onclick="document.getElementById('how-it-works').scrollIntoView({{behavior:'smooth'}})">See How It Works</button>
      </div>
      <p class="hero-microcopy">PDF or DOCX. 100% Free &amp; Secure.</p>
    </div>
    <div class="hero-right">
      <div class="floating-card-wrap">
        <span class="example-output-badge">Example Output</span>
        <div class="floating-card">
        <p class="floating-card-header">Profile Analysis Results</p>
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
      </div>
      <p class="floating-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7D8591" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        Analyzed using O*NET standards
      </p>
    </div>
   </div>
  </div>

  <div id="how-it-works">
    <div class="step-cards">
      <div class="step-card">
        <div class="step-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6M9 9h1"/></svg></div>
        <div class="step-title">1. Upload CV or fill in your data</div>
        <div class="step-desc">Upload your CV or fill in a quick form to start your profile analysis.</div>
      </div>
      <div class="step-connector"><svg viewBox="0 0 64 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="2" y1="12" x2="50" y2="12" stroke-dasharray="4 5"/><path d="M44 6l8 6-8 6"/></svg></div>
      <div class="step-card">
        <div class="step-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4M8 16h.01M16 16h.01"/></svg></div>
        <div class="step-title">2. AI analyzes your profile</div>
        <div class="step-desc">Pathfinder AI matches your skills against thousands of O*NET and SKKNI standardized professions.</div>
      </div>
      <div class="step-connector"><svg viewBox="0 0 64 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="2" y1="12" x2="50" y2="12" stroke-dasharray="4 5"/><path d="M44 6l8 6-8 6"/></svg></div>
      <div class="step-card">
        <div class="step-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l-5 2V4l5-2 6 2 5-2v16l-5 2-6-2z"/><path d="M9 2v16M15 4v16"/></svg></div>
        <div class="step-title">3. Get your career roadmap</div>
        <div class="step-desc">Receive a personalized learning map showing exactly what skills you need to master.</div>
      </div>
      <div class="step-connector"><svg viewBox="0 0 64 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="2" y1="12" x2="50" y2="12" stroke-dasharray="4 5"/><path d="M44 6l8 6-8 6"/></svg></div>
      <div class="step-card">
        <div class="step-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"/><path d="M9.5 13.5 8 22l4-2 4 2-1.5-8.5"/></svg></div>
        <div class="step-title">4. Build skills, land your career</div>
        <div class="step-desc">Take certified courses and prove your competence to the world of work.</div>
      </div>
    </div>
  </div>

  <div class="stats-section">
    <div class="stat-item"><div class="stat-num">1,000+</div><div class="stat-label">O*NET Professions</div></div>
    <div class="stat-item"><div class="stat-num">500+</div><div class="stat-label">Certified Courses</div></div>
    <div class="stat-item"><div class="stat-num">SKKNI</div><div class="stat-label">Standardized</div></div>
  </div>

  <div class="cta-section">
    <h2>Ready to start your career journey?</h2>
    <p>Join thousands of professionals who've already found their best career path with Pathfinder.</p>
    <button class="btn btn-primary btn-lg" onclick="showScreen('screen-2')">Analyze CV Now</button>
  </div>
</div>

<!-- ============================================================ SCREEN 2 — UPLOAD CV -->
<div class="screen" id="screen-2">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')" style="cursor:pointer">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Home</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-1')">← Back</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle active">1</div><div class="step-label active">Upload Profile</div></div>
      <div class="progress-step"><div class="step-circle">2</div><div class="step-label">Results</div></div>
      <div class="progress-step"><div class="step-circle">3</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle">4</div><div class="step-label">Choose Plan</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="upload-section">
    <h2 class="upload-heading">Start with your profile</h2>
    <p class="upload-sub">Pathfinder will automatically read your skills, experience, and education</p>

    <div class="upload-cards">
      <!-- Upload CV Card -->
      <div class="upload-card" id="card-upload">
        <div class="upload-icon">📄</div>
        <h3>Upload CV</h3>
        <p>PDF or DOCX format. AI will automatically extract your skills and experience.</p>

        <!-- Hidden file input -->
        <input type="file" id="cv-file-input" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" style="display:none">

        <!-- Drop zone -->
        <div class="drop-zone" id="drop-zone">
          <div style="font-size:28px;margin-bottom:8px" id="drop-icon">☁️</div>
          <div id="drop-text">Drag & drop your CV here, or click to browse</div>
          <small style="color:var(--text-muted)">PDF, DOCX · Max 5MB</small>
        </div>
        <div id="file-name-display"></div>
        <button class="btn btn-primary" style="width:100%;margin-top:12px" id="browse-btn">Choose CV File</button>
      </div>

      <!-- Manual Form Card -->
      <div class="upload-card" id="card-manual">
        <div class="upload-icon">✏️</div>
        <h3>Fill Manually</h3>
        <p>Don't have a CV yet? Fill in a short form that mirrors a CV structure.</p>
        <div class="form-field">
          <label>Full Name</label>
          <input type="text" placeholder="Enter your full name">
        </div>
        <div class="form-field">
          <label>Latest Education</label>
          <select>
            <option>B.S. Accounting — Universitas Padjadjaran</option>
            <option>B.S. Management</option>
            <option>B.S. Economics</option>
            <option>Master's Degree</option>
          </select>
        </div>
        <div class="form-field">
          <label>Work Experience</label>
          <textarea placeholder="e.g. 2 years as Finance Staff at PT ABC, managing financial reports and account reconciliation..."></textarea>
        </div>
        <div class="form-field">
          <label>Skills You Have</label>
          <input type="text" placeholder="e.g. Excel, SAP, Financial Modeling, Data Analysis...">
        </div>
        <button class="btn btn-outline" style="width:100%;margin-top:8px" onclick="selectCard('manual');enableAnalyze()">Continue with Form</button>
      </div>
    </div>

    <div style="text-align:center">
      <div class="scan-bar-wrap" id="scan-wrap" style="max-width:400px;margin:0 auto 16px;visibility:hidden">
        <div id="scan-progress"></div>
      </div>
      <button id="analyze-btn" class="btn btn-primary btn-lg btn-disabled" disabled onclick="startAnalysis()">
        Analyze Now
      </button>
    </div>
    <p class="security-note">🔒 Your data is secure and never shared with third parties</p>
  </div>
</div>

<!-- ============================================================ SCREEN 3 — TOP 3 PROFESSIONS -->
<div class="screen" id="screen-3">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')" style="cursor:pointer">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Home</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-2')">← Back</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profile</div></div>
      <div class="progress-step"><div class="step-circle active">2</div><div class="step-label active">Results</div></div>
      <div class="progress-step"><div class="step-circle">3</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle">4</div><div class="step-label">Choose Plan</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="results-section">
    <h2 style="font-family:'Inter',sans-serif;font-size:32px;font-weight:800;color:var(--navy);margin-bottom:8px">Professions most suited for you</h2>
    <p class="text-muted" style="margin-bottom:24px;font-size:15px">Based on <strong>14 skills</strong> detected from your profile, here are the top 3 profession matches</p>

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

    <div class="profession-card best" id="prof-financial-analyst" onclick="selectProfession('financial-analyst');showScreen('screen-4')">
      <div class="prof-rank">01</div>
      <div class="prof-info">
        <div class="prof-name">Financial Analyst</div>
        <div class="prof-desc">Analyzes financial data to support business and investment decision-making</div>
        <div class="prof-bar-label"><span>Skill Match</span><span style="color:var(--blue);font-weight:700">79%</span></div>
        <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:79%"></div></div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">15 of 19 skills matched</div>
      </div>
      <div class="prof-meta">
        <div class="prof-meta-item">Gap: <strong style="color:var(--navy)">4 skills</strong></div>
        <div class="prof-meta-item">Est. roadmap: <strong style="color:var(--navy)">68 days</strong></div>
        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation();selectProfession('financial-analyst');showScreen('screen-4')">Select</button>
      </div>
      <div class="prof-badge-wrap"><span class="badge badge-blue">Best Match</span></div>
    </div>

    <div class="profession-card" id="prof-accountant" onclick="selectProfession('accountant');showScreen('screen-4')">
      <div class="prof-rank" style="color:var(--border)">02</div>
      <div class="prof-info">
        <div class="prof-name">Accountant</div>
        <div class="prof-desc">Prepares and analyzes financial reports according to applicable accounting standards</div>
        <div class="prof-bar-label"><span>Skill Match</span><span style="color:var(--blue);font-weight:700">68%</span></div>
        <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:68%"></div></div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">13 of 19 skills matched</div>
      </div>
      <div class="prof-meta">
        <div class="prof-meta-item">Gap: <strong style="color:var(--navy)">6 skills</strong></div>
        <div class="prof-meta-item">Est. roadmap: <strong style="color:var(--navy)">84 days</strong></div>
        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();selectProfession('accountant');showScreen('screen-4')">Select</button>
      </div>
    </div>

    <div class="profession-card" id="prof-auditor" onclick="selectProfession('auditor');showScreen('screen-4')">
      <div class="prof-rank" style="color:var(--border)">03</div>
      <div class="prof-info">
        <div class="prof-name">Auditor</div>
        <div class="prof-desc">Examines and verifies financial reports and regulatory compliance</div>
        <div class="prof-bar-label"><span>Skill Match</span><span style="color:var(--blue);font-weight:700">58%</span></div>
        <div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:58%"></div></div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">11 of 19 skills matched</div>
      </div>
      <div class="prof-meta">
        <div class="prof-meta-item">Gap: <strong style="color:var(--navy)">8 skills</strong></div>
        <div class="prof-meta-item">Est. roadmap: <strong style="color:var(--navy)">105 days</strong></div>
        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();selectProfession('auditor');showScreen('screen-4')">Select</button>
      </div>
    </div>

    <div class="divider">— or —</div>

    <div class="custom-prof-card">
      <h3>Add a profession you're interested in</h3>
      <p>Even if your skills aren't yet a strong match, Pathfinder will still build you a complete roadmap for it</p>
      <div class="custom-input-row">
        <input id="custom-prof-input" type="text" placeholder="Search profession... (e.g. Data Scientist, UI/UX Designer)" onkeydown="if(event.key==='Enter') addProfession()">
        <button class="btn btn-outline btn-sm" onclick="addProfession()">+ Add Profession</button>
      </div>
      <div id="custom-prof-chips"></div>
    </div>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-2')">← Back</button>
    <button class="btn btn-primary" onclick="showScreen('screen-4')">Continue to Skill Gap →</button>
  </div>
</div>

<!-- ============================================================ SCREEN 4 — SKILL GAP -->
<div class="screen" id="screen-4">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')" style="cursor:pointer">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Home</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-3')">← Back</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profile</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Results</div></div>
      <div class="progress-step"><div class="step-circle active">3</div><div class="step-label active">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle">4</div><div class="step-label">Choose Plan</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="gap-section">
    <h2 style="font-family:'Inter',sans-serif;font-size:32px;font-weight:800;color:var(--navy);margin-bottom:8px">Skill map toward Financial Analyst</h2>
    <p class="text-muted" style="margin-bottom:28px">You already have <strong>15 of 19 skills</strong> required. Here's the full breakdown.</p>

    <div class="readiness-bar-wrap">
      <div class="readiness-bar-header">
        <span>Current Career Readiness</span>
        <span>79% / 100%</span>
      </div>
      <div class="progress-bar-wrap" style="height:12px"><div class="progress-bar-fill" style="width:79%"></div></div>
      <p class="readiness-sub">Complete the roadmap to reach 100% job-ready</p>
    </div>

    <div class="skill-cols">
      <div class="skill-col-card">
        <div class="skill-col-header">
          <span style="font-size:18px">✅</span>
          <h3>Skills you already have</h3>
          <span class="badge badge-green">15 skills</span>
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

      <div class="skill-col-card">
        <div class="skill-col-header">
          <span style="font-size:18px;color:var(--blue)">🎯</span>
          <h3>Skills you need to build</h3>
          <span class="badge badge-blue">4 skills</span>
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
          These four skills will be built through your curated learning roadmap based on O*NET and SKKNI standards.
        </div>
      </div>
    </div>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-3')">← Back</button>
    <button class="btn btn-primary" onclick="showScreen('screen-5')">Choose Learning Plan →</button>
  </div>
</div>

<!-- ============================================================ SCREEN 5 — CHOOSE PLAN -->
<div class="screen" id="screen-5">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')" style="cursor:pointer">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Home</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-4')">← Back</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profile</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Results</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle active">4</div><div class="step-label active">Choose Plan</div></div>
      <div class="progress-step"><div class="step-circle">5</div><div class="step-label">Roadmap</div></div>
    </div>
  </div>

  <div class="packages-section">
    <h2 style="font-family:'Inter',sans-serif;font-size:32px;font-weight:800;color:var(--navy);margin-bottom:8px">Choose your learning pace</h2>
    <p class="text-muted" style="margin-bottom:32px">All plans cover the same certified courses at the same standard. The difference is in depth of content.</p>

    <div class="slider-wrap">
      <div class="slider-label">
        <span>How many hours can you study per day?</span>
        <span id="hours-display">2 hrs / day</span>
      </div>
      <input type="range" id="hours-slider" min="1" max="8" value="2">
      <p class="slider-note">⏱ Roadmap duration adjusts automatically based on your daily study hours</p>
    </div>

    <div class="packages-grid">
      <div class="package-card" id="pkg-cepat" onclick="selectPackage('cepat')">
        <div class="pkg-icon">⚡</div>
        <div class="pkg-name">Fast Track</div>
        <div class="pkg-days" id="fast-days">34 days</div>
        <div class="pkg-days-label">estimated completion</div>
        <div class="pkg-hours">68 hrs total content</div>
        <div class="pkg-courses">
          <div class="course-item">
            <div class="course-name">Bloomberg Terminal Essentials</div>
            <div class="course-meta">12 hrs <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Intro to Financial Derivatives</div>
            <div class="course-meta">18 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">CFA Level 1 Fundamentals</div>
            <div class="course-meta">22 hrs <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Portfolio Analysis Basics</div>
            <div class="course-meta">16 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
        </div>
        <div class="pkg-cert">🎓 Certificates: 4 certificates</div>
        <button class="btn btn-outline" style="width:100%" onclick="event.stopPropagation();selectPackage('cepat');showScreen('screen-6')">Choose This Plan</button>
      </div>

      <div class="package-card recommended" id="pkg-sedang" onclick="selectPackage('sedang')">
        <div class="pkg-recommended-badge"><span class="badge badge-blue">Most Popular</span></div>
        <div class="pkg-icon" style="color:var(--blue)">🎯</div>
        <div class="pkg-name">Standard</div>
        <div class="pkg-days" id="mid-days">51 days</div>
        <div class="pkg-days-label">estimated completion</div>
        <div class="pkg-hours">102 hrs total content</div>
        <div class="pkg-courses">
          <div class="course-item">
            <div class="course-name">Bloomberg Terminal Complete Guide</div>
            <div class="course-meta">24 hrs <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Financial Derivatives & Risk Mgmt</div>
            <div class="course-meta">28 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">CFA Level 1 Complete Program</div>
            <div class="course-meta">32 hrs <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Portfolio Analysis & Management</div>
            <div class="course-meta">18 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
        </div>
        <div class="pkg-cert">🎓 Certificates: 4 certificates</div>
        <button class="btn btn-primary" style="width:100%" onclick="event.stopPropagation();selectPackage('sedang');showScreen('screen-6')">Choose This Plan</button>
      </div>

      <div class="package-card" id="pkg-komprehensif" onclick="selectPackage('komprehensif')">
        <div class="pkg-icon">📚</div>
        <div class="pkg-name">Comprehensive</div>
        <div class="pkg-days" id="full-days">78 days</div>
        <div class="pkg-days-label">estimated completion</div>
        <div class="pkg-hours">156 hrs total content</div>
        <div class="pkg-courses">
          <div class="course-item">
            <div class="course-name">Bloomberg Terminal Mastery + Practice</div>
            <div class="course-meta">38 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Complete Derivatives & Structured Products</div>
            <div class="course-meta">42 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">CFA Level 1 + 2 Preparation</div>
            <div class="course-meta">52 hrs <span class="chip chip-blue" style="font-size:10px">Udemy</span></div>
          </div>
          <div class="course-item">
            <div class="course-name">Advanced Portfolio & Asset Management</div>
            <div class="course-meta">24 hrs <span class="chip chip-muted" style="font-size:10px">Coursera</span></div>
          </div>
        </div>
        <div class="pkg-cert">🎓 Certificates: 4 certificates</div>
        <button class="btn btn-outline" style="width:100%" onclick="event.stopPropagation();selectPackage('komprehensif');showScreen('screen-6')">Choose This Plan</button>
      </div>
    </div>

    <p class="packages-note">All courses are curated by Pathfinder — every certificate issued is recognized as proof of industry-standard competence</p>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-4')">← Back</button>
    <button class="btn btn-primary" onclick="showScreen('screen-6')">See Full Roadmap →</button>
  </div>
</div>

<!-- ============================================================ SCREEN 6 — ROADMAP -->
<div class="screen" id="screen-6">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')" style="cursor:pointer">PATHFINDER</a>
    <div class="navbar-links"><a onclick="showScreen('screen-1')">Home</a></div>
    <div class="navbar-right"><button class="btn btn-outline btn-sm" onclick="showScreen('screen-5')">← Back</button></div>
  </nav>
  <div class="progress-indicator">
    <div class="progress-steps">
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Upload Profile</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Results</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Skill Gap</div></div>
      <div class="progress-step"><div class="step-circle done">✓</div><div class="step-label">Choose Plan</div></div>
      <div class="progress-step"><div class="step-circle active">5</div><div class="step-label active">Roadmap</div></div>
    </div>
  </div>

  <div class="roadmap-section">
    <div class="roadmap-header">
      <div>
        <h2 style="font-family:'Inter',sans-serif;font-size:28px;font-weight:800;color:var(--navy);margin-bottom:8px">Your Roadmap to Financial Analyst</h2>
        <p class="text-muted" style="font-size:14px">Standard Plan · 2 hrs/day · Starting Today</p>
      </div>
      <div class="roadmap-stats">
        <div class="roadmap-stat-chip">📋 4 Stages</div>
        <div class="roadmap-stat-chip">⏱ 102 Total Hours</div>
        <div class="roadmap-stat-chip">📅 51 Days Est.</div>
      </div>
    </div>

    <div class="timeline">
      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet active">1</div>
          <div class="timeline-line active"></div>
        </div>
        <div class="timeline-card active" style="flex:1">
          <div class="tl-badge"><span class="badge badge-blue">In Progress</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill being built</div>
              <div class="tl-skill-name">Bloomberg Terminal</div>
              <div class="tl-course-name">Bloomberg Terminal Complete Guide · <span class="chip chip-blue" style="font-size:11px">Udemy</span> <span class="chip chip-green" style="font-size:11px">Certified ✓</span></div>
              <div class="tl-duration">24 hrs total · 12 days at 2 hrs/day</div>
              <div style="margin-top:12px">
                <div style="font-size:12px;color:var(--text-muted);margin-bottom:5px;display:flex;justify-content:space-between"><span>Course Progress</span><span>0%</span></div>
                <div class="progress-bar-wrap" style="height:6px"><div class="progress-bar-fill" style="width:0%"></div></div>
              </div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Start: <strong>Day 1</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target: <strong>Day 12</strong></div>
              <button class="btn btn-primary btn-sm" onclick="showScreen('screen-7')">Start Learning →</button>
            </div>
          </div>
        </div>
      </div>

      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet">2</div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-card" style="flex:1;opacity:0.75">
          <div class="tl-badge"><span class="badge badge-surface">Waiting for Stage 1</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill being built</div>
              <div class="tl-skill-name">Financial Derivatives</div>
              <div class="tl-course-name">Financial Derivatives & Risk Mgmt · <span class="chip chip-muted" style="font-size:11px">Coursera</span></div>
              <div class="tl-duration">28 hrs total · 14 days at 2 hrs/day</div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Start: <strong>Day 13</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target: <strong>Day 26</strong></div>
              <button class="btn btn-disabled btn-sm" disabled>🔒 Locked</button>
            </div>
          </div>
        </div>
      </div>

      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet">3</div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-card" style="flex:1;opacity:0.65">
          <div class="tl-badge"><span class="badge badge-surface">Waiting for Stage 2</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill being built</div>
              <div class="tl-skill-name">CFA Knowledge Base</div>
              <div class="tl-course-name">CFA Level 1 Complete Program · <span class="chip chip-blue" style="font-size:11px">Udemy</span></div>
              <div class="tl-duration">32 hrs total · 16 days at 2 hrs/day</div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Start: <strong>Day 27</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target: <strong>Day 42</strong></div>
              <button class="btn btn-disabled btn-sm" disabled>🔒 Locked</button>
            </div>
          </div>
        </div>
      </div>

      <div class="timeline-item">
        <div class="timeline-left">
          <div class="timeline-bullet">4</div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-card" style="flex:1;opacity:0.55">
          <div class="tl-badge"><span class="badge badge-surface">Waiting for Stage 3</span></div>
          <div class="timeline-card-inner">
            <div class="timeline-card-main">
              <div class="tl-skill-label">Skill being built</div>
              <div class="tl-skill-name">Investment Portfolio Analysis</div>
              <div class="tl-course-name">Portfolio Analysis & Management · <span class="chip chip-muted" style="font-size:11px">Coursera</span></div>
              <div class="tl-duration">18 hrs total · 9 days at 2 hrs/day</div>
            </div>
            <div class="timeline-card-side">
              <div class="tl-date">Start: <strong>Day 43</strong></div>
              <div class="tl-date" style="margin-bottom:16px">Target: <strong>Day 51</strong></div>
              <button class="btn btn-disabled btn-sm" disabled>🔒 Locked</button>
            </div>
          </div>
        </div>
      </div>

      <div class="timeline-item">
        <div class="timeline-left"><div class="timeline-bullet done">✓</div></div>
        <div class="end-node" style="flex:1;margin-bottom:32px">
          <div class="end-text">
            <h3>Financial Analyst — Job Ready ✓</h3>
            <p>All O*NET and SKKNI standardized skills fulfilled · Day 52 onwards</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="nav-bottom">
    <button class="btn btn-outline" onclick="showScreen('screen-5')">← Back</button>
    <button class="btn btn-primary" onclick="showScreen('screen-7')">Begin Journey →</button>
  </div>
</div>

<!-- ============================================================ SCREEN 7 — DASHBOARD -->
<div class="screen" id="screen-7">
  <nav class="navbar">
    <a class="navbar-logo" onclick="showScreen('screen-1')" style="cursor:pointer">PATHFINDER</a>
    <div class="navbar-links">
      <a onclick="showScreen('screen-6')">Roadmap</a>
      <a onclick="showScreen('screen-4')">Skill Gap</a>
    </div>
    <div class="navbar-right"><div class="avatar">RD</div></div>
  </nav>

  <div class="dashboard-section">
    <div class="greeting-row">
      <div class="greeting-text">
        <h2>Welcome back, Rizky 👋</h2>
        <p>You're on your journey to becoming a <strong>Financial Analyst</strong></p>
      </div>
      <button class="btn btn-outline" onclick="showScreen('screen-6')">View Full Roadmap</button>
    </div>

    <div class="metric-cards">
      <div class="metric-card">
        <div class="metric-label">Job-Readiness Score</div>
        <div class="metric-value" style="color:var(--blue)">79%</div>
        <div class="metric-sub">Up 0% this week (just started)</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Active Stage</div>
        <div class="metric-value">1 / 4</div>
        <div class="metric-sub">Bloomberg Terminal</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Days Remaining</div>
        <div class="metric-value">51</div>
        <div class="metric-sub">Estimated completion</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Certificates Earned</div>
        <div class="metric-value">0 / 4</div>
        <div class="metric-sub">Complete a stage to unlock</div>
      </div>
    </div>

    <div class="active-stage-card">
      <div class="active-stage-header">
        <div class="active-stage-title">Stage 1 — Bloomberg Terminal</div>
        <span class="badge badge-blue">In Progress</span>
      </div>
      <div class="active-course-meta">Bloomberg Terminal Complete Guide · Udemy · 24 total hours</div>
      <div class="progress-label">
        <span>Learning Progress</span>
        <span>0 of 24 hours completed</span>
      </div>
      <div class="progress-bar-wrap" style="height:10px"><div class="progress-bar-fill" style="width:0%"></div></div>
      <div class="active-stage-actions">
        <button class="btn btn-primary">Continue Learning</button>
        <button class="btn btn-outline">Upload Certificate</button>
      </div>
      <p class="active-stage-note">Upload your certificate after completion to unlock the next stage</p>
    </div>

    <div class="skill-progress-card">
      <h3>Skill Progress toward Financial Analyst</h3>
      <div class="skill-progress-row">
        <div class="skill-progress-meta">
          <span class="name">Bloomberg Terminal</span>
          <span class="pct" style="color:var(--blue)">0% — In Progress</span>
        </div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%"></div></div>
      </div>
      <div class="skill-progress-row">
        <div class="skill-progress-meta"><span class="name">Financial Derivatives</span><span class="pct">Locked 🔒</span></div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%;background:var(--border)"></div></div>
      </div>
      <div class="skill-progress-row">
        <div class="skill-progress-meta"><span class="name">CFA Knowledge Base</span><span class="pct">Locked 🔒</span></div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%;background:var(--border)"></div></div>
      </div>
      <div class="skill-progress-row" style="margin-bottom:0">
        <div class="skill-progress-meta"><span class="name">Investment Portfolio Analysis</span><span class="pct">Locked 🔒</span></div>
        <div class="progress-bar-wrap" style="height:7px"><div class="progress-bar-fill" style="width:0%;background:var(--border)"></div></div>
      </div>
      <div class="owned-chips">
        <p>Skills already owned (15 skills):</p>
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

    <div class="upload-proof-card">
      <h3>Submit course certificate</h3>
      <p class="upload-proof-sub">Every certificate you upload will be verified and become official proof of competence</p>
      <div class="upload-proof-drop">
        <div style="font-size:28px;margin-bottom:8px">📎</div>
        Drag & drop your certificate PDF or image here
      </div>
      <button class="btn btn-outline btn-sm">Choose File</button>
      <p class="upload-proof-note" style="margin-top:10px">Accepted formats: PDF, JPG, PNG · Max 10MB</p>
    </div>

    <div class="motivation-card">
      <p>💡 <strong>Consistency is the key.</strong> With 2 hrs/day, you'll become a <strong>Financial Analyst</strong> in just <strong>51 days</strong>. Every hour you invest today is a real step toward your dream career.</p>
    </div>
  </div>
</div>

<script>
{JS}

function selectCard(type) {{
  document.querySelectorAll('.upload-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('card-' + type).classList.add('selected');
}}

function enableAnalyze() {{
  const btn = document.getElementById('analyze-btn');
  btn.classList.remove('btn-disabled');
  btn.disabled = false;
}}

function startAnalysis() {{
  const wrap = document.getElementById('scan-wrap');
  if (wrap) wrap.style.visibility = 'visible';
  runAIScanning();
}}

// ── DRAG & DROP CV ──────────────────────────────────────────
function initDropZone() {{
  const dropZone  = document.getElementById('drop-zone');
  const fileInput = document.getElementById('cv-file-input');
  const browseBtn = document.getElementById('browse-btn');
  const dropText  = document.getElementById('drop-text');
  const dropIcon  = document.getElementById('drop-icon');
  const nameDisp  = document.getElementById('file-name-display');
  const card      = document.getElementById('card-upload');

  if (!dropZone || !fileInput) return;

  // Click on drop zone or button → open file picker
  dropZone.addEventListener('click', () => fileInput.click());
  browseBtn.addEventListener('click', (e) => {{ e.stopPropagation(); fileInput.click(); }});

  // Drag events
  dropZone.addEventListener('dragover',  (e) => {{ e.preventDefault(); dropZone.classList.add('drag-over'); }});
  dropZone.addEventListener('dragenter', (e) => {{ e.preventDefault(); dropZone.classList.add('drag-over'); }});
  dropZone.addEventListener('dragleave', ()  => dropZone.classList.remove('drag-over'));

  dropZone.addEventListener('drop', (e) => {{
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
  }});

  fileInput.addEventListener('change', (e) => {{
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
  }});

  function handleFile(file) {{
    const allowed = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    if (!allowed.includes(file.type) && !file.name.match(/\\.(pdf|docx)$/i)) {{
      alert('Please upload a PDF or DOCX file.');
      return;
    }}
    if (file.size > 5 * 1024 * 1024) {{
      alert('File size must be less than 5MB.');
      return;
    }}
    dropZone.classList.add('file-ready');
    dropIcon.textContent = '✅';
    dropText.textContent  = file.name;
    nameDisp.textContent  = 'File ready · ' + (file.size / 1024).toFixed(0) + ' KB';
    nameDisp.style.color  = 'var(--success)';
    card.classList.add('selected');
    document.getElementById('card-manual').classList.remove('selected');
    enableAnalyze();
    localStorage.setItem('pathfinder_cv_file', file.name);
  }}
}}

// ── INIT ────────────────────────────────────────────────────
showScreen('screen-1');
initSlider();
initDropZone();
</script>
</body>
</html>"""

st.components.v1.html(HTML, height=900, scrolling=True)
