import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pathfinder — Pitch Deck",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit default UI chrome for full-screen feel
st.markdown("""
<style>
  #MainMenu, header, footer { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  .stApp { background: #1a1a2e; }
</style>
""", unsafe_allow_html=True)

SLIDE_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --blue-deep: #1B3FAB;
    --blue-mid:  #4B6EF5;
    --blue-light:#EEF2FF;
    --bg:        #F8F9FF;
    --text-primary:   #0D1B3E;
    --text-secondary: #6B7A99;
    --success:    #1A7F5A;
    --success-bg: #ECFAF4;
    --border:     #E2E8F0;
    --white:      #FFFFFF;
    --amber:      #D97706;
    --red:        #DC2626;
  }
  html, body {
    width: 100%; height: 100%;
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #1a1a2e;
    color: var(--text-primary);
    overflow: hidden;
  }
  #app {
    display: flex; flex-direction: column;
    width: 100vw; height: 100vh;
    align-items: center; justify-content: center;
  }
  #slide-container {
    position: relative;
    width: min(96vw, calc(90vh * 16/10));
    aspect-ratio: 16/10;
    background: var(--white);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 32px 80px rgba(0,0,0,0.5);
  }
  .slide {
    position: absolute; inset: 0;
    padding: 40px 48px 34px;
    display: none; flex-direction: column;
    background: var(--white);
  }
  .slide.active { display: flex; }

  /* NAV */
  #nav { display:flex; align-items:center; gap:16px; margin-top:14px; }
  .nav-btn {
    background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2);
    color:#fff; width:40px; height:40px; border-radius:50%; cursor:pointer;
    font-size:16px; display:flex; align-items:center; justify-content:center;
    transition: background .2s;
  }
  .nav-btn:hover { background: rgba(255,255,255,.25); }
  .nav-btn:disabled { opacity:.3; cursor:default; }
  .slide-dots { display:flex; gap:8px; }
  .dot {
    width:8px; height:8px; border-radius:50%;
    background:rgba(255,255,255,.3); cursor:pointer; transition:all .25s;
  }
  .dot.active { background:#fff; width:24px; border-radius:4px; }
  .slide-label { color:rgba(255,255,255,.5); font-size:11px; letter-spacing:.5px; }
  #hint { color:rgba(255,255,255,.22); font-size:10px; margin-top:6px; }

  /* SHARED */
  .section-label {
    font-size:10px; font-weight:500; letter-spacing:1.5px;
    text-transform:uppercase; color:var(--text-secondary); margin-bottom:5px;
  }
  .slide-title {
    font-size:clamp(20px,2.5vw,30px); font-weight:800;
    color:var(--text-primary); line-height:1.2; margin-bottom:22px;
  }

  /* ═══ SLIDE 1 ═══ */
  .journey-stages { display:flex; flex:1; gap:0; align-items:stretch; min-height:0; }
  .stage { flex:1; display:flex; flex-direction:column; position:relative; }
  .stage-connector {
    width:32px; display:flex; align-items:center; justify-content:center;
    flex-shrink:0; padding-top:48px;
  }
  .stage-num { font-size:9px; font-weight:700; letter-spacing:1px; color:var(--blue-mid); margin-bottom:6px; }
  .stage-label { font-size:clamp(10px,1.05vw,12px); font-weight:700; color:var(--text-primary); margin-bottom:2px; }
  .stage-sub { font-size:clamp(9px,.8vw,10px); color:var(--text-secondary); margin-bottom:8px; }
  .stage-card {
    background:var(--white); border:1px solid var(--border); border-radius:12px;
    padding:12px; flex:1; display:flex; flex-direction:column;
    box-shadow:0 2px 12px rgba(27,63,171,.05);
  }
  .upload-options { display:flex; flex-direction:column; gap:7px; flex:1; justify-content:center; }
  .upload-btn {
    border:1.5px dashed var(--blue-mid); border-radius:8px; padding:9px 10px;
    display:flex; align-items:center; gap:7px; font-size:10px;
    color:var(--blue-mid); font-weight:600;
  }
  .form-fields { display:flex; flex-direction:column; gap:4px; }
  .form-field {
    background:var(--bg); border:1px solid var(--border); border-radius:6px;
    padding:5px 8px; font-size:9px; color:var(--text-secondary);
  }
  .divider-or { text-align:center; font-size:9px; color:var(--text-secondary); margin:2px 0; }
  .ai-badge {
    display:inline-flex; align-items:center; gap:4px;
    background:var(--blue-light); border:1px solid #C7D2FE; border-radius:20px;
    padding:3px 7px; font-size:9px; font-weight:600; color:var(--blue-deep);
    margin-top:7px; align-self:flex-start;
  }
  .profession-list { display:flex; flex-direction:column; gap:6px; flex:1; justify-content:center; }
  .prof-card { background:var(--bg); border:1px solid var(--border); border-radius:8px; padding:7px 9px; }
  .prof-card.best { background:var(--success-bg); border-color:#A7F3D0; }
  .prof-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:4px; }
  .prof-name { font-size:10px; font-weight:700; color:var(--text-primary); }
  .best-badge { background:var(--success); color:white; font-size:8px; font-weight:700; padding:2px 5px; border-radius:20px; }
  .prof-bar-track { background:var(--border); border-radius:4px; height:4px; overflow:hidden; margin-bottom:3px; }
  .prof-bar-fill { height:100%; border-radius:4px; background:var(--blue-mid); }
  .prof-card.best .prof-bar-fill { background:var(--success); }
  .prof-score { font-size:9px; color:var(--text-secondary); font-weight:600; }
  .more-link { font-size:9px; color:var(--blue-mid); font-weight:600; margin-top:4px; cursor:pointer; }
  .gap-cols { display:flex; gap:9px; flex:1; }
  .gap-col { flex:1; }
  .gap-col-title { font-size:8px; font-weight:700; margin-bottom:5px; text-transform:uppercase; letter-spacing:.8px; }
  .gap-col-title.have { color:var(--success); }
  .gap-col-title.need { color:var(--text-secondary); }
  .skill-item { display:flex; align-items:center; gap:5px; margin-bottom:4px; font-size:9px; color:var(--text-primary); font-weight:500; }
  .skill-check { color:var(--success); flex-shrink:0; }
  .skill-circle { color:#CBD5E1; flex-shrink:0; }
  .readiness-bar-wrap { margin-top:8px; }
  .readiness-label { font-size:9px; font-weight:700; color:var(--text-primary); margin-bottom:3px; display:flex; justify-content:space-between; align-items:center; }
  .readiness-track { background:var(--border); border-radius:6px; height:7px; overflow:hidden; }
  .readiness-fill { height:100%; border-radius:6px; background:var(--blue-mid); width:68%; }

  /* ═══ SLIDE 2 ═══ */
  #slide-2 { background:var(--bg); }
  .career-map-layout { display:flex; flex:1; gap:18px; min-height:0; }
  .roadmap-zone { flex:6; display:flex; flex-direction:column; min-height:0; }
  .zone-title { font-size:clamp(11px,1.15vw,13px); font-weight:700; color:var(--text-primary); margin-bottom:8px; }
  .roadmap-steps { display:flex; flex-direction:column; gap:6px; flex:1; overflow:hidden; }
  .step-card {
    background:var(--white); border:1px solid var(--border); border-radius:10px;
    padding:9px 12px; display:flex; align-items:center; gap:9px; flex-shrink:0;
  }
  .step-card.done { background:#F0FFF8; border-color:#A7F3D0; }
  .step-card.active { border-color:var(--blue-mid); border-width:1.5px; }
  .step-card.pending { opacity:.65; }
  .step-num { font-size:8px; font-weight:800; color:var(--text-secondary); width:34px; flex-shrink:0; letter-spacing:.5px; }
  .step-card.done .step-num { color:var(--success); }
  .step-card.active .step-num { color:var(--blue-mid); }
  .step-body { flex:1; min-width:0; }
  .step-skill { font-size:clamp(9px,.95vw,11px); font-weight:700; color:var(--text-primary); margin-bottom:2px; }
  .step-course { font-size:clamp(8px,.8vw,9px); color:var(--text-secondary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .step-meta { display:flex; align-items:center; gap:5px; flex-shrink:0; }
  .platform-pill { background:var(--bg); border:1px solid var(--border); border-radius:20px; padding:2px 7px; font-size:8px; font-weight:700; color:var(--text-secondary); }
  .step-card.active .platform-pill { background:var(--blue-light); border-color:#C7D2FE; color:var(--blue-deep); }
  .duration-text { font-size:8px; color:var(--text-secondary); white-space:nowrap; font-weight:600; }
  .cert-icon { color:#F59E0B; }
  .active-badge { background:var(--blue-mid); color:white; font-size:8px; font-weight:700; padding:2px 6px; border-radius:20px; white-space:nowrap; }
  .done-icon { color:var(--success); }
  .divider-v { width:1px; background:var(--border); flex-shrink:0; }
  .package-zone { flex:4; display:flex; flex-direction:column; min-height:0; }
  .pkg-cards { display:flex; flex-direction:column; gap:7px; flex:1; }
  .pkg-card {
    background:var(--white); border:1.5px solid var(--border); border-radius:10px;
    padding:9px 11px; display:flex; gap:9px; align-items:flex-start; flex:1;
  }
  .pkg-card.recommended { background:var(--blue-light); border-color:var(--blue-mid); border-width:2px; }
  .pkg-icon { width:30px; height:30px; border-radius:8px; background:var(--bg); display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:15px; }
  .pkg-card.recommended .pkg-icon { background:rgba(75,110,245,.12); }
  .pkg-body { flex:1; }
  .pkg-header { display:flex; align-items:center; gap:5px; margin-bottom:2px; }
  .pkg-name { font-size:clamp(10px,1.05vw,12px); font-weight:800; color:var(--text-primary); }
  .pkg-rec-badge { background:var(--blue-mid); color:white; font-size:8px; font-weight:700; padding:2px 6px; border-radius:20px; }
  .pkg-duration { font-size:clamp(14px,1.5vw,18px); font-weight:800; color:var(--blue-deep); margin-bottom:2px; }
  .pkg-card.recommended .pkg-duration { color:var(--blue-mid); }
  .pkg-desc { font-size:clamp(8px,.8vw,9px); color:var(--text-secondary); line-height:1.4; }
  .time-slider-wrap { background:var(--white); border:1px solid var(--border); border-radius:10px; padding:9px 11px; margin-top:7px; flex-shrink:0; }
  .time-slider-label { font-size:9px; font-weight:600; color:var(--text-secondary); margin-bottom:5px; }
  .time-val { font-size:12px; font-weight:800; color:var(--text-primary); }
  .time-track { background:var(--border); border-radius:4px; height:4px; margin:5px 0; position:relative; }
  .time-fill { height:100%; background:var(--blue-mid); border-radius:4px; width:33%; }
  .time-thumb { width:11px; height:11px; border-radius:50%; background:var(--blue-mid); border:2px solid white; box-shadow:0 1px 4px rgba(75,110,245,.4); position:absolute; top:-4px; left:calc(33% - 5px); }
  .time-note { font-size:8px; color:var(--text-secondary); }

  /* ═══ SLIDE 3 ═══ */
  .comp-table-wrap { flex:1; overflow:hidden; display:flex; flex-direction:column; min-height:0; }
  table.comp-table { width:100%; border-collapse:collapse; font-size:clamp(8px,.8vw,10px); flex:1; table-layout:fixed; }
  .comp-table th, .comp-table td { padding:5px 7px; text-align:center; border:.5px solid var(--border); }
  .comp-table td:first-child { text-align:left; font-weight:600; color:var(--text-primary); padding-left:10px; }
  .comp-table th.pf-head { background:var(--blue-deep); color:white; font-weight:800; font-size:clamp(9px,.95vw,11px); }
  .comp-table td.pf-col { background:var(--blue-light); font-weight:600; }
  .comp-table th.comp-head { background:#F1F5F9; color:var(--text-primary); font-weight:700; font-size:clamp(8px,.85vw,10px); }
  .comp-table th:first-child { background:#F1F5F9; text-align:left; font-weight:700; color:var(--text-secondary); font-size:clamp(8px,.8vw,9px); letter-spacing:.5px; text-transform:uppercase; padding-left:10px; }
  .comp-table tr:nth-child(even) td { background-color:var(--bg); }
  .comp-table tr:nth-child(even) td.pf-col { background-color:#E8EDFD; }
  .sym-yes { color:var(--success); font-size:14px; font-weight:700; }
  .sym-partial { color:var(--amber); font-size:13px; }
  .sym-no { color:var(--red); font-size:14px; font-weight:700; }
  .callout-box { margin-top:8px; border-left:3px solid var(--blue-mid); background:var(--blue-light); border-radius:0 8px 8px 0; padding:8px 12px; font-size:clamp(9px,.85vw,10px); color:var(--text-primary); font-weight:600; line-height:1.5; flex-shrink:0; }
</style>
</head>
<body>
<div id="app">
  <div id="slide-container">

    <!-- SLIDE 1 -->
    <div class="slide active" id="slide-1">
      <div class="section-label">Solution &amp; How It Works</div>
      <div class="slide-title">Perjalananmu dimulai di sini</div>
      <div class="journey-stages">

        <div class="stage">
          <div class="stage-num">01</div>
          <div class="stage-label">Mulai dengan data kamu</div>
          <div class="stage-sub">Upload CV atau isi form singkat</div>
          <div class="stage-card">
            <div class="upload-options">
              <div class="upload-btn">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
                Upload CV (PDF/DOCX)
              </div>
              <div class="divider-or">— atau —</div>
              <div class="form-fields">
                <div class="form-field">Nama Lengkap</div>
                <div class="form-field">Pengalaman Kerja</div>
                <div class="form-field">Skill &amp; Keahlian</div>
                <div class="form-field">Pendidikan Terakhir</div>
              </div>
            </div>
            <div class="ai-badge">
              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5.64 5.64l2.12 2.12M16.24 16.24l2.12 2.12M5.64 18.36l2.12-2.12M16.24 7.76l2.12-2.12"/></svg>
              AI akan membaca profilmu
            </div>
          </div>
        </div>

        <div class="stage-connector">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4B6EF5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
          </svg>
        </div>

        <div class="stage">
          <div class="stage-num">02</div>
          <div class="stage-label">Profesi yang paling cocok untukmu</div>
          <div class="stage-sub">Berdasarkan skill yang sudah kamu miliki</div>
          <div class="stage-card">
            <div class="profession-list">
              <div class="prof-card best">
                <div class="prof-header"><span class="prof-name">Financial Analyst</span><span class="best-badge">Best Match</span></div>
                <div class="prof-bar-track"><div class="prof-bar-fill" style="width:79%"></div></div>
                <div class="prof-score">79% coverage</div>
              </div>
              <div class="prof-card">
                <div class="prof-header"><span class="prof-name">Accountant</span></div>
                <div class="prof-bar-track"><div class="prof-bar-fill" style="width:68%"></div></div>
                <div class="prof-score">68% coverage</div>
              </div>
              <div class="prof-card">
                <div class="prof-header"><span class="prof-name">Auditor</span></div>
                <div class="prof-bar-track"><div class="prof-bar-fill" style="width:58%"></div></div>
                <div class="prof-score">58% coverage</div>
              </div>
            </div>
            <div class="more-link">+ Pilih profesi lain</div>
          </div>
        </div>

        <div class="stage-connector">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4B6EF5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
          </svg>
        </div>

        <div class="stage">
          <div class="stage-num">03</div>
          <div class="stage-label">Ini yang perlu kamu siapkan</div>
          <div class="stage-sub">Pathfinder akan membimbingmu step by step</div>
          <div class="stage-card">
            <div class="gap-cols">
              <div class="gap-col">
                <div class="gap-col-title have">Sudah dimiliki</div>
                <div class="skill-item"><svg class="skill-check" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>Microsoft Excel</div>
                <div class="skill-item"><svg class="skill-check" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>Financial Reporting</div>
                <div class="skill-item"><svg class="skill-check" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>Akuntansi Dasar</div>
                <div class="skill-item"><svg class="skill-check" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>Analisis Laporan</div>
              </div>
              <div class="gap-col">
                <div class="gap-col-title need">Perlu dibangun</div>
                <div class="skill-item"><svg class="skill-circle" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>Financial Modeling</div>
                <div class="skill-item"><svg class="skill-circle" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>Data Visualization</div>
                <div class="skill-item"><svg class="skill-circle" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>SQL &amp; Business Intel</div>
                <div class="skill-item"><svg class="skill-circle" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>Valuation Methods</div>
              </div>
            </div>
            <div class="readiness-bar-wrap">
              <div class="readiness-label">Kesiapan karir kamu <span style="color:var(--blue-mid);font-weight:800">68%</span></div>
              <div class="readiness-track"><div class="readiness-fill"></div></div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- SLIDE 2 -->
    <div class="slide" id="slide-2">
      <div class="section-label">Solution &amp; How It Works</div>
      <div class="slide-title">Dari gap menjadi siap kerja</div>
      <div class="career-map-layout">

        <div class="roadmap-zone">
          <div class="zone-title">Roadmap menuju Financial Analyst</div>
          <div class="roadmap-steps">

            <div class="step-card done">
              <div class="step-num">STEP 1</div>
              <div class="step-body">
                <div class="step-skill">Akuntansi &amp; Laporan Keuangan</div>
                <div class="step-course">Financial Accounting Fundamentals — Coursera</div>
              </div>
              <div class="step-meta">
                <span class="platform-pill">Coursera</span>
                <span class="duration-text">8 jam</span>
                <svg class="cert-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>
                <svg class="done-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>
              </div>
            </div>

            <div class="step-card done">
              <div class="step-num">STEP 2</div>
              <div class="step-body">
                <div class="step-skill">Excel Advanced &amp; Power Query</div>
                <div class="step-course">Excel Skills for Business — Coursera</div>
              </div>
              <div class="step-meta">
                <span class="platform-pill">Coursera</span>
                <span class="duration-text">10 jam</span>
                <svg class="cert-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>
                <svg class="done-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>
              </div>
            </div>

            <div class="step-card active">
              <div class="step-num">STEP 3</div>
              <div class="step-body">
                <div class="step-skill">Financial Modeling &amp; Valuation</div>
                <div class="step-course">Financial Modeling &amp; Valuation — Udemy</div>
              </div>
              <div class="step-meta">
                <span class="platform-pill">Udemy</span>
                <span class="duration-text">12 jam</span>
                <svg class="cert-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>
                <span class="active-badge">Sedang berjalan</span>
              </div>
            </div>

            <div class="step-card pending">
              <div class="step-num">STEP 4</div>
              <div class="step-body">
                <div class="step-skill">Data Analysis &amp; Visualization</div>
                <div class="step-course">Data Analysis with Python — Coursera</div>
              </div>
              <div class="step-meta">
                <span class="platform-pill">Coursera</span>
                <span class="duration-text">14 jam</span>
                <svg class="cert-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>
              </div>
            </div>

            <div class="step-card pending">
              <div class="step-num">STEP 5</div>
              <div class="step-body">
                <div class="step-skill">SQL &amp; Business Intelligence</div>
                <div class="step-course">SQL for Data Analysis — Udemy</div>
              </div>
              <div class="step-meta">
                <span class="platform-pill">Udemy</span>
                <span class="duration-text">8 jam</span>
                <svg class="cert-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>
              </div>
            </div>

          </div>
        </div>

        <div class="divider-v"></div>

        <div class="package-zone">
          <div class="zone-title">Pilih kecepatanmu</div>
          <div class="pkg-cards">
            <div class="pkg-card">
              <div class="pkg-icon">⚡</div>
              <div class="pkg-body">
                <div class="pkg-header"><span class="pkg-name">Paket Cepat</span></div>
                <div class="pkg-duration">42 hari</div>
                <div class="pkg-desc">Kursus terpendek per skill, tetap bersertifikat</div>
              </div>
            </div>
            <div class="pkg-card recommended">
              <div class="pkg-icon">🎯</div>
              <div class="pkg-body">
                <div class="pkg-header"><span class="pkg-name">Paket Sedang</span><span class="pkg-rec-badge">Recommended</span></div>
                <div class="pkg-duration">68 hari</div>
                <div class="pkg-desc">Kedalaman optimal, paling banyak dipilih</div>
              </div>
            </div>
            <div class="pkg-card">
              <div class="pkg-icon">🎓</div>
              <div class="pkg-body">
                <div class="pkg-header"><span class="pkg-name">Paket Komprehensif</span></div>
                <div class="pkg-duration">95 hari</div>
                <div class="pkg-desc">Materi paling mendalam, siap bersaing</div>
              </div>
            </div>
          </div>
          <div class="time-slider-wrap">
            <div class="time-slider-label">Waktu belajarmu per hari</div>
            <div class="time-val">1 jam / hari</div>
            <div class="time-track"><div class="time-fill"></div><div class="time-thumb"></div></div>
            <div class="time-note">Durasi akan menyesuaikan otomatis</div>
          </div>
        </div>

      </div>
    </div>

    <!-- SLIDE 3 -->
    <div class="slide" id="slide-3">
      <div class="section-label">Competitive Advantage</div>
      <div class="slide-title">Pathfinder mengisi gap yang tidak ada di platform lain</div>
      <div class="comp-table-wrap">
        <table class="comp-table">
          <thead>
            <tr>
              <th>Dimensi</th>
              <th class="pf-head">Pathfinder</th>
              <th class="comp-head">LinkedIn</th>
              <th class="comp-head">Coursera</th>
              <th class="comp-head">Udemy</th>
              <th class="comp-head">Kinobi</th>
              <th class="comp-head">Glints</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Career mapping terstandarisasi</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Standar O*NET / SKKNI</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Skill gap analysis</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-partial">△</span></td></tr>
            <tr><td>Personalized learning path</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Kurikulum berbasis sertifikasi</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Job-readiness score</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Konteks lokal Indonesia (SKKNI)</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Roadmap hingga job-ready</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td></tr>
            <tr><td>Target fresh graduate</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-yes">✓</span></td><td><span class="sym-yes">✓</span></td></tr>
            <tr><td>Evidence-based progress</td><td class="pf-col"><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-yes">✓</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-partial">△</span></td><td><span class="sym-no">✗</span></td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout-box">
        Satu-satunya platform yang menggabungkan standar O*NET + SKKNI dengan evidence-based career roadmap untuk fresh graduate Indonesia.
      </div>
    </div>

  </div><!-- /slide-container -->

  <div id="nav">
    <button class="nav-btn" id="btn-prev" onclick="changeSlide(-1)" disabled>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
    </button>
    <div class="slide-dots">
      <div class="dot active" onclick="goSlide(0)"></div>
      <div class="dot" onclick="goSlide(1)"></div>
      <div class="dot" onclick="goSlide(2)"></div>
    </div>
    <button class="nav-btn" id="btn-next" onclick="changeSlide(1)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
    </button>
    <span class="slide-label" id="slide-count">1 / 3</span>
  </div>
  <div id="hint">← → arrow keys to navigate</div>
</div>

<script>
  let current = 0;
  const slides = document.querySelectorAll('.slide');
  const dots   = document.querySelectorAll('.dot');
  const total  = slides.length;
  function goSlide(n) {
    slides[current].classList.remove('active');
    dots[current].classList.remove('active');
    current = Math.max(0, Math.min(n, total - 1));
    slides[current].classList.add('active');
    dots[current].classList.add('active');
    document.getElementById('btn-prev').disabled = current === 0;
    document.getElementById('btn-next').disabled = current === total - 1;
    document.getElementById('slide-count').textContent = (current+1) + ' / ' + total;
  }
  function changeSlide(dir) { goSlide(current + dir); }
  document.addEventListener('keydown', e => {
    if (e.key==='ArrowRight'||e.key==='ArrowDown') changeSlide(1);
    if (e.key==='ArrowLeft' ||e.key==='ArrowUp')   changeSlide(-1);
  });
</script>
</body>
</html>
"""

components.html(SLIDE_HTML, height=800, scrolling=False)
