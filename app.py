import streamlit as st
import os
import html
import io
import json
import re
import uuid
import datetime
import math

import pdfplumber
import google.generativeai as genai

from database import (
    init_db,
    get_courses_for_onet,
    get_total_hours_for_onet,
    upsert_user_profile,
    upsert_user_skills,
    verify_user_skill,
    get_user_skills,
)

# ── Phase 1: initialise database (idempotent) ─────────────────────────────
init_db()

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

/* ── Native Landing → Upload Profile → Results steps ───────────────
   These three steps need real input/output, which a sandboxed
   st.components.v1.html iframe structurally cannot provide (no channel
   back to Python for clicks, files, or typed text). So they're rendered
   natively — ONE set of controls each, genuinely wired end to end — and
   styled to read as a continuation of Pathfinder's gold/navy/cream
   identity. Only "demo" (the illustrative Skill Gap → Roadmap tour,
   which never needed real data) still uses the polished preview. */
.pf-native-navbar { max-width: 1200px; margin: 0 auto; padding: 18px 48px; font-family: 'Playfair Display', serif; font-weight: 700; font-size: 19px; color: #0F172A; letter-spacing: 1px; border-bottom: 1px solid #E2E8F0; }
.pf-native-hero { max-width: 760px; margin: 0 auto; padding: 56px 48px 8px; text-align: center; font-family: 'Inter', sans-serif; }
.pf-native-hero .eyebrow { font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #B48E4B; margin: 0 0 12px; }
.pf-native-hero h1 { font-family: 'Playfair Display', serif; font-size: 38px; font-weight: 700; color: #0F172A; line-height: 1.25; margin: 0 0 16px; }
.pf-native-hero h1 span { color: #B48E4B; }
.pf-native-hero p { font-size: 15px; color: #64748B; line-height: 1.6; max-width: 540px; margin: 0 auto 8px; }
.pf-native-hero .micro { font-size: 12px; color: #94A3B8; margin-top: 14px; }
.pf-step-cta-wrap { max-width: 1200px; margin: 12px auto 32px; padding: 0 48px; text-align: center; }
.pf-step-cta-wrap [data-testid="stBaseButton-primary"] { background: #B48E4B; border-color: #B48E4B; border-radius: 8px; font-weight: 600; padding: 10px 28px; }
.pf-step-cta-wrap [data-testid="stBaseButton-primary"]:hover { background: #9C7A4A; border-color: #9C7A4A; }
.pf-native-howit { max-width: 1080px; margin: 28px auto; padding: 0 48px; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.pf-native-howit-card { text-align: center; padding: 20px 16px; border: 1px solid #E2E8F0; border-radius: 12px; background: #FAFAF7; font-family: 'Inter', sans-serif; }
.pf-native-howit-card .num { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #B48E4B; color: #fff; font-weight: 700; font-size: 12px; margin-bottom: 10px; }
.pf-native-howit-card h4 { font-size: 13px; font-weight: 700; color: #0F172A; margin: 0 0 6px; }
.pf-native-howit-card p { font-size: 12px; color: #64748B; line-height: 1.5; margin: 0; }
.pf-native-stats { max-width: 640px; margin: 8px auto 48px; padding: 0 48px; display: flex; justify-content: space-around; text-align: center; font-family: 'Inter', sans-serif; }
.pf-native-stats .num { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; color: #0F172A; }
.pf-native-stats .label { font-size: 12px; color: #64748B; }
.pf-native-results-head { max-width: 1200px; margin: 36px auto 0; padding: 0 48px; font-family: 'Inter', sans-serif; }
.pf-native-results-head h2 { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: #0F172A; margin: 0 0 6px; }
.pf-native-results-head p { font-size: 14px; color: #64748B; margin: 0 0 16px; }
.pf-native-skills-row { max-width: 1200px; margin: 0 auto 28px; padding: 0 48px; display: flex; flex-wrap: wrap; gap: 8px; }
.pf-native-skill-chip { font-size: 12px; font-weight: 600; color: #9C7A40; background: #FBF1E0; border: 1px solid #F1E3C8; border-radius: 99px; padding: 6px 14px; }
.pf-native-match-card { border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px; background: #fff; box-shadow: 0 4px 20px rgba(15,23,42,0.05); font-family: 'Inter', sans-serif; margin-bottom: 12px; }
.pf-native-match-card.best { border-color: #B48E4B; box-shadow: 0 8px 28px rgba(180,142,75,0.18); }
.pf-native-match-badge { display: inline-block; font-size: 11px; font-weight: 700; color: #fff; background: #B48E4B; border-radius: 99px; padding: 3px 10px; margin-bottom: 10px; }
.pf-native-match-card h3 { font-size: 18px; font-weight: 700; color: #0F172A; margin: 0 0 4px; }
.pf-native-match-onet { font-size: 11px; font-weight: 600; color: #94A3B8; letter-spacing: .4px; margin-bottom: 8px; }
.pf-native-match-desc { font-size: 13px; color: #64748B; line-height: 1.5; margin-bottom: 14px; min-height: 60px; }
.pf-native-match-bar-wrap { background: #E2E8F0; border-radius: 99px; height: 8px; overflow: hidden; margin-bottom: 6px; }
.pf-native-match-bar-fill { background: #B48E4B; height: 100%; border-radius: 99px; }
.pf-native-match-stats { display: flex; justify-content: space-between; font-size: 12px; color: #64748B; }
.pf-native-match-meta { font-size: 12px; color: #94A3B8; margin-bottom: 10px; }
/* Match-card Select buttons — container key has an index suffix (pf_match_col_0 etc.)
   so we use [class*=] to match all variants */
[class*="st-key-pf_match_col"] [data-testid="stBaseButton-primary"],
[class*="st-key-pf_match_col"] [data-testid="stBaseButton-secondary"] { border-radius: 8px; font-weight: 600; }
[class*="st-key-pf_match_col"] [data-testid="stBaseButton-primary"] { background: #B48E4B; border-color: #B48E4B; }
[class*="st-key-pf_match_col"] [data-testid="stBaseButton-primary"]:hover { background: #9C7A4A; border-color: #9C7A4A; }
.pf-native-heading { max-width: 1200px; margin: 36px auto 0; padding: 0 48px; font-family: 'Inter', sans-serif; text-align: center; }
.pf-native-heading h2 { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: #0F172A; margin: 0 0 6px; }
.pf-native-heading p { font-size: 14px; color: #64748B; margin: 0 0 22px; }
.pf-native-progress { max-width: 620px; margin: 0 auto 28px; display: flex; justify-content: space-between; gap: 8px; font-family: 'Inter', sans-serif; }
.pf-native-step { flex: 1; text-align: center; font-size: 12px; font-weight: 600; color: #94A3B8; padding: 7px 10px; border-radius: 99px; background: #F1F5F9; }
.pf-native-step.current { color: #FFFFFF; background: #B48E4B; }
.pf-native-step.done { color: #B48E4B; background: #FBF1E0; }
.st-key-pf_upload_page { max-width: 1100px; margin: 0 auto 12px; padding: 0 48px; }
.st-key-pf_upload_page [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #E2E8F0; }
.st-key-pf_upload_page [aria-selected="true"] { color: #B48E4B !important; }
.st-key-pf_upload_page [data-testid="stFileUploaderDropzone"] { border-radius: 10px; border-color: #CBD5E1; background: #F8FAFC; }
.st-key-pf_upload_page [data-testid="stWidgetLabel"] p { font-size: 12px; font-weight: 600; letter-spacing: .4px; text-transform: uppercase; color: #64748B; }
.st-key-pf_upload_page [data-testid="stBaseButton-primary"] { background: #B48E4B; border-color: #B48E4B; border-radius: 8px; font-weight: 600; }
.st-key-pf_upload_page [data-testid="stBaseButton-primary"]:hover { background: #9C7A4A; border-color: #9C7A4A; }
.pf-upload-back-wrap { max-width: 1100px; margin: 0 auto 32px; padding: 0 48px; }

/* ── Phase 3: Loading animation ─────────────────────────────────── */
.pf-loading-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:80px 48px; text-align:center; font-family:'Inter',sans-serif; background:#F8F6F0; min-height:420px; }
.pf-loading-ring { position:relative; width:80px; height:80px; margin-bottom:28px; }
.pf-loading-ring-track { position:absolute; inset:0; border:3px solid #F1E3C8; border-radius:50%; }
.pf-loading-ring-spin { position:absolute; inset:0; border:3px solid transparent; border-top-color:#B48E4B; border-radius:50%; animation:pf-spin 0.9s linear infinite; }
.pf-loading-ring-pulse { position:absolute; inset:12px; background:#B48E4B; border-radius:50%; opacity:0.12; animation:pf-pulse 1.6s ease-in-out infinite; }
@keyframes pf-spin { to { transform:rotate(360deg); } }
@keyframes pf-pulse { 0%,100% { opacity:0.12; transform:scale(0.85); } 50% { opacity:0.28; transform:scale(1); } }
.pf-loading-main-text { font-size:17px; font-weight:700; color:#0F172A; min-height:26px; animation:pf-fade-in 0.3s ease; }
@keyframes pf-fade-in { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
.pf-loading-sub-text { font-size:13px; color:#64748B; margin-top:6px; }
.pf-loading-steps { display:flex; gap:6px; margin-top:28px; }
.pf-loading-dot { width:8px; height:8px; border-radius:50%; background:#E2E8F0; }
.pf-loading-dot.active { background:#B48E4B; animation:pf-dot-pulse 1s ease-in-out infinite; }
@keyframes pf-dot-pulse { 0%,100% { transform:scale(1); } 50% { transform:scale(1.4); } }

/* ── Phase 4: 4-column results ──────────────────────────────────── */
.pf-add-profession-card { border:2px dashed #CBD5E1; border-radius:12px; padding:22px; background:#F8FAFC; height:100%; box-sizing:border-box; font-family:'Inter',sans-serif; }
.pf-add-profession-card h3 { font-size:15px; font-weight:700; color:#0F172A; margin:0 0 6px; }
.pf-add-profession-card p { font-size:12px; color:#64748B; margin:0 0 14px; line-height:1.5; }
.pf-match-card-hours { font-size:12px; color:#B48E4B; font-weight:600; margin-top:4px; }
.pf-match-card-courses { margin:12px 0 0; }
.pf-match-card-courses-label { font-size:11px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:.5px; margin-bottom:6px; }
.pf-course-row { display:flex; align-items:center; gap:8px; font-size:12px; color:#64748B; margin-bottom:5px; }
.pf-course-provider { font-size:10px; font-weight:700; color:#B48E4B; background:#FBF1E0; border-radius:4px; padding:1px 6px; white-space:nowrap; }
.pf-gap-skills-wrap { margin:10px 0 4px; display:flex; flex-wrap:wrap; gap:4px; }
.pf-gap-skill-chip { font-size:11px; font-weight:600; color:#DC2626; background:#FEF2F2; border:1px solid #FECACA; border-radius:99px; padding:3px 9px; }

/* ── Phase 5: Study planner + Certificate verification ─────────── */
.pf-planner-metric { text-align:center; padding:20px 16px; border:1px solid #E2E8F0; border-radius:12px; background:#FAFAF7; }
.pf-planner-metric .pf-pm-val { font-family:'Playfair Display',serif; font-size:36px; font-weight:700; color:#B48E4B; line-height:1; }
.pf-planner-metric .pf-pm-lbl { font-size:12px; color:#64748B; margin-top:4px; }
.pf-cert-row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 16px; border:1px solid #E2E8F0; border-radius:10px; background:#fff; margin-bottom:10px; font-family:'Inter',sans-serif; }
.pf-cert-row.verified { border-color:#16A34A; background:#F0FDF4; }
.pf-cert-status-icon { font-size:18px; flex-shrink:0; }
.pf-cert-title { font-size:13px; font-weight:600; color:#0F172A; }
.pf-cert-provider { font-size:11px; color:#94A3B8; margin-top:2px; }
.pf-cert-hours { font-size:11px; color:#B48E4B; font-weight:600; white-space:nowrap; }
.pf-section-divider { max-width:1200px; margin:32px auto; padding:0 48px; }
.pf-section-divider hr { border:none; border-top:1px solid #E2E8F0; }
.pf-section-heading { font-family:'Inter',sans-serif; font-size:18px; font-weight:700; color:#0F172A; margin:0 0 4px; }
.pf-section-subheading { font-size:13px; color:#64748B; margin:0 0 16px; }

/* ── Skill Gap page ──────────────────────────────────────────────── */
.pf-readiness-wrap { max-width:1100px; margin:24px auto; padding:0 48px; }
.pf-readiness-card { background:#FBF1E0; border:1px solid #F1E3C8; border-radius:14px; padding:24px 28px; }
.pf-readiness-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; font-family:'Inter',sans-serif; }
.pf-readiness-label { font-size:14px; font-weight:600; color:#0F172A; }
.pf-readiness-pct { font-family:'Playfair Display',serif; font-size:26px; font-weight:700; color:#B48E4B; }
.pf-readiness-bar-bg { background:#E2E8F0; border-radius:99px; height:12px; overflow:hidden; }
.pf-readiness-bar-fg { background:linear-gradient(90deg,#B48E4B,#9C7A40); height:100%; border-radius:99px; transition:width 0.5s ease; }
.pf-readiness-sub { font-size:12px; color:#64748B; margin-top:8px; font-family:'Inter',sans-serif; }
.pf-skill-cols-wrap { max-width:1100px; margin:20px auto; padding:0 48px; display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.pf-skill-col { border:1px solid #E2E8F0; border-radius:12px; overflow:hidden; background:#fff; }
.pf-skill-col-head { padding:16px 20px; border-bottom:1px solid #E2E8F0; display:flex; align-items:center; gap:10px; font-family:'Inter',sans-serif; }
.pf-skill-col-head h3 { font-size:14px; font-weight:700; color:#0F172A; flex:1; margin:0; }
.pf-skill-col-head .pf-badge { font-size:11px; font-weight:700; padding:3px 10px; border-radius:99px; }
.pf-badge-green { background:#DCFCE7; color:#16A34A; }
.pf-badge-gold { background:#FBF1E0; color:#B48E4B; }
.pf-skill-list { padding:6px 0; }
.pf-skill-row { display:flex; align-items:center; gap:10px; padding:10px 20px; border-bottom:1px solid #F1F5F9; font-family:'Inter',sans-serif; font-size:13px; font-weight:500; color:#0F172A; }
.pf-skill-row:last-child { border-bottom:none; }
.pf-skill-have-icon { color:#16A34A; font-size:15px; flex-shrink:0; }
.pf-skill-need-icon { width:16px; height:16px; border-radius:50%; border:2px solid #B48E4B; flex-shrink:0; }
.pf-skill-skkni { font-size:10px; font-weight:700; color:#B48E4B; background:#FBF1E0; border-radius:4px; padding:1px 6px; margin-left:auto; white-space:nowrap; }
.pf-skill-callout { margin:12px 20px 16px; background:#FBF1E0; border-left:3px solid #B48E4B; border-radius:6px; padding:10px 14px; font-size:12px; color:#9C7A40; font-family:'Inter',sans-serif; line-height:1.5; }

/* ── Choose Plan page ────────────────────────────────────────────── */
.pf-plan-wrap { max-width:1100px; margin:0 auto; padding:0 48px 48px; }
.pf-hours-slider-card { background:#FAFAF7; border:1px solid #E2E8F0; border-radius:12px; padding:22px 24px; margin-bottom:24px; font-family:'Inter',sans-serif; }
.pf-hours-slider-label { display:flex; justify-content:space-between; align-items:center; font-size:14px; font-weight:600; color:#0F172A; margin-bottom:12px; }
.pf-hours-slider-val { font-size:20px; font-weight:700; color:#B48E4B; font-family:'Playfair Display',serif; }
.pf-plan-cards { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:4px; }
.pf-plan-card { border:1px solid #E2E8F0; border-radius:12px; padding:24px; background:#fff; display:flex; flex-direction:column; position:relative; }
.pf-plan-card.recommended { border:2px solid #B48E4B; background:#FDFAF4; }
.pf-plan-recommended-badge { position:absolute; top:-13px; left:50%; transform:translateX(-50%); background:#B48E4B; color:#fff; font-size:11px; font-weight:700; padding:3px 14px; border-radius:99px; white-space:nowrap; font-family:'Inter',sans-serif; }
.pf-plan-icon { font-size:28px; margin-bottom:10px; }
.pf-plan-name { font-family:'Inter',sans-serif; font-size:18px; font-weight:700; color:#0F172A; margin-bottom:2px; }
.pf-plan-days { font-family:'Playfair Display',serif; font-size:32px; font-weight:700; color:#B48E4B; line-height:1; }
.pf-plan-days-label { font-size:12px; color:#64748B; margin-bottom:4px; font-family:'Inter',sans-serif; }
.pf-plan-hours { font-size:13px; color:#64748B; padding-bottom:14px; border-bottom:1px solid #E2E8F0; margin-bottom:14px; font-family:'Inter',sans-serif; }
.pf-plan-course-list { flex:1; display:flex; flex-direction:column; gap:10px; margin-bottom:14px; }
.pf-plan-course-item { font-size:12px; }
.pf-plan-course-name { font-weight:600; color:#0F172A; margin-bottom:3px; font-family:'Inter',sans-serif; }
.pf-plan-course-meta { display:flex; align-items:center; gap:6px; color:#94A3B8; }
.pf-plan-cert-note { font-size:12px; color:#64748B; padding-top:10px; border-top:1px solid #E2E8F0; font-family:'Inter',sans-serif; }

/* ── Roadmap page ────────────────────────────────────────────────── */
.pf-roadmap-wrap { max-width:900px; margin:0 auto; padding:0 48px 48px; }
.pf-roadmap-header-row { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:28px; flex-wrap:wrap; gap:12px; }
.pf-roadmap-title { font-family:'Inter',sans-serif; font-size:26px; font-weight:800; color:#0F172A; margin:0 0 4px; }
.pf-roadmap-sub { font-size:13px; color:#64748B; margin:0; }
.pf-roadmap-stat-chips { display:flex; gap:10px; flex-wrap:wrap; align-items:flex-start; }
.pf-roadmap-stat-chip { background:#F1F5F9; border:1px solid #E2E8F0; border-radius:8px; padding:7px 14px; font-size:12px; font-weight:600; color:#0F172A; font-family:'Inter',sans-serif; white-space:nowrap; }
.pf-timeline { position:relative; }
.pf-tl-item { display:flex; gap:16px; margin-bottom:0; }
.pf-tl-left { display:flex; flex-direction:column; align-items:center; flex-shrink:0; }
.pf-tl-bullet { width:36px; height:36px; border-radius:50%; border:2px solid #E2E8F0; display:flex; align-items:center; justify-content:center; font-family:'Inter',sans-serif; font-size:13px; font-weight:700; color:#94A3B8; background:#fff; z-index:1; }
.pf-tl-bullet.active { background:#B48E4B; border-color:#B48E4B; color:#fff; }
.pf-tl-bullet.done { background:#16A34A; border-color:#16A34A; color:#fff; }
.pf-tl-line { flex:1; width:2px; background:#E2E8F0; margin:3px 0; min-height:40px; }
.pf-tl-line.active { background:#B48E4B; }
.pf-tl-line.done { background:#16A34A; }
.pf-tl-card { flex:1; border:1px solid #E2E8F0; border-radius:12px; padding:18px 22px; margin-bottom:20px; background:#fff; }
.pf-tl-card.active { border-left:4px solid #B48E4B; background:#FDFAF4; }
.pf-tl-card.done { border-left:4px solid #16A34A; background:#F0FDF4; }
.pf-tl-card-inner { display:flex; gap:16px; }
.pf-tl-card-main { flex:1; }
.pf-tl-card-side { flex-shrink:0; text-align:right; min-width:130px; }
.pf-tl-stage-label { font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#94A3B8; font-weight:600; margin-bottom:3px; font-family:'Inter',sans-serif; }
.pf-tl-skill-name { font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:#0F172A; margin-bottom:3px; }
.pf-tl-course-name { font-size:13px; color:#64748B; margin-bottom:10px; }
.pf-tl-duration { font-size:12px; color:#94A3B8; margin-top:8px; }
.pf-tl-date { font-size:12px; color:#64748B; margin-bottom:4px; font-family:'Inter',sans-serif; }
.pf-tl-date strong { color:#0F172A; }
.pf-tl-end-node { display:flex; align-items:center; gap:14px; background:#F0FDF9; border:1px solid #16A34A; border-radius:12px; padding:18px 22px; margin-top:4px; margin-left:52px; }
.pf-tl-end-bullet { width:36px; height:36px; border-radius:50%; background:#16A34A; color:#fff; display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0; }
.pf-tl-end-text h3 { font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:#16A34A; margin:0 0 2px; }
.pf-tl-end-text p { font-size:12px; color:#64748B; margin:0; }

/* ── Dashboard page ──────────────────────────────────────────────── */
.pf-dash-wrap { max-width:1100px; margin:0 auto; padding:0 48px 48px; }
.pf-dash-greeting { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:28px; flex-wrap:wrap; gap:12px; }
.pf-dash-greeting h2 { font-family:'Inter',sans-serif; font-size:22px; font-weight:800; color:#0F172A; margin:0 0 4px; }
.pf-dash-greeting p { font-size:14px; color:#64748B; margin:0; }
.pf-metric-cards { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:24px; }
.pf-metric-card { border:1px solid #E2E8F0; border-radius:12px; padding:18px 20px; background:#fff; font-family:'Inter',sans-serif; }
.pf-metric-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:#94A3B8; margin-bottom:6px; }
.pf-metric-value { font-family:'Playfair Display',serif; font-size:26px; font-weight:700; color:#0F172A; margin-bottom:2px; }
.pf-metric-sub { font-size:11px; color:#94A3B8; }
.pf-active-stage-card { border:1px solid #E2E8F0; border-radius:12px; padding:24px; background:#fff; margin-bottom:20px; font-family:'Inter',sans-serif; }
.pf-active-stage-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }
.pf-active-stage-title { font-size:17px; font-weight:700; color:#0F172A; }
.pf-active-course-meta { font-size:13px; color:#64748B; margin-bottom:14px; }
.pf-progress-label { display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#0F172A; margin-bottom:6px; }
.pf-dash-actions { display:flex; gap:10px; margin-top:16px; flex-wrap:wrap; }
.pf-motivation-card { background:#0F172A; border-radius:12px; padding:20px 24px; margin-top:20px; font-family:'Inter',sans-serif; }
.pf-motivation-card p { color:rgba(255,255,255,0.85); font-size:14px; line-height:1.6; font-style:italic; margin:0; }
.pf-motivation-card strong { color:#B48E4B; font-style:normal; }
</style>
""", unsafe_allow_html=True)


def load_file(path):
    base = os.path.dirname(__file__)
    full = os.path.join(base, path)
    if os.path.exists(full):
        with open(full, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ────────────────────────────────────────────────────────────────────
# REAL CV ANALYSIS PIPELINE  (PDF text extraction → LLM skill mapping)
#
# This replaces the previous mock "RESULTS_MOCK" payload with a live,
# end-to-end pipeline: an uploaded PDF's raw bytes are parsed into text
# server-side, then sent to Claude with structured-output instructions
# that map the candidate's real skills onto O*NET "Technology Skills" /
# "Knowledge" categories + Indonesian SKKNI competency unit codes, and
# surface the top 3 closest O*NET-SOC profession matches with an
# absolute (matched / total_required) match ratio — no arbitrary
# weighting, no hardcoded professions.
# ────────────────────────────────────────────────────────────────────

ANALYZE_SYSTEM_PROMPT = (
    "You are an expert career data encoder. Analyse the provided raw CV text.\n"
    "1. Extract ALL technical hard skills and cross-functional soft skills present.\n"
    "2. Map these skills to official O*NET 'Technology Skills' or 'Knowledge' categories and "
    "assign the closest Indonesian SKKNI competency unit code where applicable.\n"
    "3. Identify the top 3 closest O*NET Standard Occupational Classification (SOC) profession "
    "titles that match the candidate's actual background. Prioritise domain alignment: a "
    "Mathematics/Python background → Data Scientist / Operations Research Analyst, not Finance.\n"
    "4. For each matched profession:\n"
    "   a. matched_count = number of extracted skills that directly satisfy that profession's "
    "requirements.\n"
    "   b. total_required = total skills that profession standardly requires.\n"
    "   c. gap_count = total_required − matched_count (never negative).\n"
    "   d. gap_skills = list of specific skill names the candidate is MISSING for that profession "
    "(maximum 8, most impactful first).\n"
    "   e. estimated_days = realistic days to close the gap at 2 hrs/day study pace.\n"
    "5. Calculate the ABSOLUTE match ratio (matched_count / total_required) — do NOT apply "
    "arbitrary weighting.\n\n"
    "Respond with ONLY a single raw JSON object — no markdown fences, no commentary:\n"
    "{\n"
    '  "detected_skills": ["string"],\n'
    '  "top_matches": [\n'
    "    {\n"
    '      "title": "string",\n'
    '      "onet_code": "string (O*NET-SOC code, e.g. 15-2051.00)",\n'
    '      "description": "string (1–2 sentence profession description)",\n'
    '      "matched_count": number,\n'
    '      "total_required": number,\n'
    '      "gap_count": number,\n'
    '      "gap_skills": ["string"],\n'
    '      "estimated_days": number\n'
    "    }\n"
    "  ]\n"
    "}"
)

ANALYZE_MODEL = "gemini-2.5-flash"   # free tier: 15 RPM, 1M tokens/day


def extract_pdf_text(file_bytes: bytes) -> str:
    """Step 1 — read the raw binary buffer of the uploaded PDF and extract clean text."""
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())
    return "\n\n".join(pages).strip()


def _coerce_match_record(raw):
    """Normalise one top_matches entry from the LLM into the exact numeric/string contract."""
    matched = int(raw.get("matched_count", 0) or 0)
    total = int(raw.get("total_required", 0) or 0)
    gap = raw.get("gap_count")
    gap = int(gap) if gap is not None else max(total - matched, 0)
    raw_gap_skills = raw.get("gap_skills", [])
    gap_skills = [str(s).strip() for s in (raw_gap_skills or []) if str(s).strip()][:8]
    return {
        "title": str(raw.get("title", "")).strip(),
        "onet_code": str(raw.get("onet_code", "")).strip(),
        "description": str(raw.get("description", "")).strip(),
        "matched_count": matched,
        "total_required": total,
        "gap_count": gap,
        "gap_skills": gap_skills,
        "estimated_days": int(raw.get("estimated_days", 0) or 0),
    }


def analyze_profile_with_gemini(cv_text: str) -> dict:
    """Step 2 — send extracted CV text to Gemini 3.5 Flash (free tier) and parse structured output."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY belum dikonfigurasi. "
            "Dapatkan key GRATIS di aistudio.google.com/apikey "
            "lalu tambahkan ke .streamlit/secrets.toml:\n"
            'GEMINI_API_KEY = "AIzaSy..."'
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=ANALYZE_MODEL,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    full_prompt = (
        ANALYZE_SYSTEM_PROMPT
        + "\n\nHere is the raw CV text. Analyse it and respond with ONLY the JSON object "
        "described above — no markdown fences, no extra text:\n\n"
        "--- BEGIN CV TEXT ---\n"
        + cv_text
        + "\n--- END CV TEXT ---"
    )

    response = model.generate_content(full_prompt)
    raw_text = response.text.strip()

    # Defensive: strip markdown fences if model wraps despite mime-type hint
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw_text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        raw_text = fenced.group(1).strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemini returned invalid JSON ({exc}). "
            f"Raw output (truncated): {raw_text[:500]}"
        ) from exc

    detected_skills = [str(s).strip() for s in data.get("detected_skills", []) if str(s).strip()]
    top_matches = [_coerce_match_record(m) for m in data.get("top_matches", [])]

    if not detected_skills or not top_matches:
        raise RuntimeError(
            "Response missing 'detected_skills' or 'top_matches'. "
            f"Keys returned: {list(data.keys())}"
        )

    return {"detected_skills": detected_skills, "top_matches": top_matches}


def run_profile_analysis(file_bytes: bytes) -> dict:
    """Full pipeline: raw PDF bytes → extracted text → Gemini structured analysis."""
    cv_text = extract_pdf_text(file_bytes)
    if not cv_text:
        raise RuntimeError(
            "Tidak ada teks yang bisa diekstrak dari PDF ini — kemungkinan file scan/gambar. "
            "Coba upload PDF hasil export teks dari Word/Google Docs."
        )
    return analyze_profile_with_gemini(cv_text)


CSS = load_file("assets/styles.css")
JS  = load_file("assets/script.js")


# ────────────────────────────────────────────────────────────────────
# Flow control — "pf_step" decides which Pathfinder step Python renders:
#   landing → upload → results → demo
# A sandboxed st.components.v1.html() iframe has NO channel to send real
# data (a file, typed text, a button click) back to Python — so any step
# that needs real input/output (Landing's CTA, Upload Profile, Results)
# is rendered NATIVELY: one set of controls, genuinely wired end to end,
# no mockup duplicate sitting next to it. Only "demo" — the illustrative
# Skill Gap → Choose Plan → Roadmap → Dashboard tour, which never needed
# real data — still uses the polished HTML/CSS/JS preview, opened
# straight on its first screen.
# ────────────────────────────────────────────────────────────────────
st.session_state.setdefault("pf_step", "landing")
st.session_state.setdefault("analysis_result", None)
st.session_state.setdefault("analysis_error", None)
st.session_state.setdefault("session_id", str(uuid.uuid4()))
st.session_state.setdefault("pf_show_planner", False)
st.session_state.setdefault("pf_selected_match", None)
st.session_state.setdefault("pf_cert_states", {})   # {course_id: {"url": str, "verified": bool}}
st.session_state.setdefault("pf_selected_plan", None)   # "fast" | "standard" | "comprehensive"
st.session_state.setdefault("pf_study_hours_per_day", 2)
st.session_state.setdefault("pf_roadmap_courses", [])   # ordered list of course dicts for roadmap
st.session_state.setdefault("pf_completed_courses", set())  # set of course ids marked done


# ─────────────────────────────────────────────────────────────────────────────
# Phase 5 — Study Planner modal  (@st.dialog requires Streamlit ≥ 1.36)
# ─────────────────────────────────────────────────────────────────────────────

@st.dialog("📅 Study Planner", width="large")
def _study_planner_dialog():
    match = st.session_state.get("pf_selected_match") or {}
    onet_code = match.get("onet_code", "")
    title = match.get("title", "your chosen profession")

    total_hours = match.get("total_course_hours") or get_total_hours_for_onet(onet_code) or max(
        match.get("estimated_days", 60) * 2, 40
    )

    st.markdown(
        f"<p style='font-family:Inter,sans-serif;font-size:15px;color:#64748B;margin:0 0 20px'>"
        f"Personalise your learning timeline for <strong style='color:#0F172A'>{html.escape(title)}</strong> "
        f"— <strong style='color:#B48E4B'>{total_hours} total course hours</strong> to complete.</p>",
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "Plan by:", ["⏱ Hours per day", "📅 Target completion date"],
        horizontal=True, key="pf_planner_mode", label_visibility="collapsed",
    )

    st.divider()

    if mode == "⏱ Hours per day":
        hrs = st.slider("Hours you can study per day", min_value=1, max_value=12, value=2,
                        step=1, key="pf_planner_hrs")
        days_needed = max(1, round(total_hours / hrs))
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f'<div class="pf-planner-metric"><div class="pf-pm-val">{days_needed}</div>'
                f'<div class="pf-pm-lbl">Estimated days to complete</div></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            finish = datetime.date.today() + datetime.timedelta(days=days_needed)
            st.markdown(
                f'<div class="pf-planner-metric"><div class="pf-pm-val" style="font-size:22px">'
                f'{finish.strftime("%d %b %Y")}</div>'
                f'<div class="pf-pm-lbl">Estimated finish date</div></div>',
                unsafe_allow_html=True,
            )
    else:
        target = st.date_input(
            "Target completion date", value=datetime.date.today() + datetime.timedelta(days=90),
            min_value=datetime.date.today() + datetime.timedelta(days=1),
            key="pf_planner_date",
        )
        days_available = max(1, (target - datetime.date.today()).days)
        hrs_daily = round(total_hours / days_available, 1)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f'<div class="pf-planner-metric"><div class="pf-pm-val">{days_available}</div>'
                f'<div class="pf-pm-lbl">Days until target</div></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f'<div class="pf-planner-metric"><div class="pf-pm-val">{hrs_daily}</div>'
                f'<div class="pf-pm-lbl">Hours to study daily</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    courses = get_courses_for_onet(onet_code)
    if courses:
        st.markdown(
            "<p style='font-size:13px;font-weight:700;color:#0F172A;margin:0 0 8px'>"
            "Recommended courses for this plan</p>",
            unsafe_allow_html=True,
        )
        for crs in courses[:4]:
            st.markdown(
                f'<div class="pf-cert-row">'
                f'<div><div class="pf-cert-title">{html.escape(crs["title"])}</div>'
                f'<div class="pf-cert-provider">{crs["provider"]}</div></div>'
                f'<div class="pf-cert-hours">{crs["total_hours"]} hrs</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    if st.button("🚀 Start My Journey — View Skill Gap", type="primary", use_container_width=True,
                 key="pf_planner_start"):
        st.session_state["pf_show_planner"] = False
        st.session_state["pf_step"] = "skill_gap"
        st.rerun()


PF_STEP = st.session_state["pf_step"]

# Trigger study-planner dialog (must be called before any other rendering)
if st.session_state.get("pf_show_planner"):
    _study_planner_dialog()

_analysis_result = st.session_state.get("analysis_result")
RESULTS_DATA_JSON = json.dumps(_analysis_result) if _analysis_result else "null"
INITIAL_SCREEN_JS = "'screen-4'" if PF_STEP == "demo" else "'screen-1'"


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
.upload-section {{ padding:64px 48px; max-width:1400px; margin:0 auto; }}
.upload-heading {{ text-align:center; margin-bottom:8px; font-family:'Inter',sans-serif; font-size:36px; font-weight:800; color:var(--navy); }}
.upload-sub {{ text-align:center; color:var(--text-muted); margin-bottom:48px; font-size:16px; }}
.upload-card-single {{
  max-width:1200px; margin:0 auto; background:var(--white);
  border:1px solid var(--border); border-radius:14px; overflow:hidden;
  box-shadow:0px 4px 24px rgba(15,23,42,0.06);
}}
.upload-tabs {{ display:flex; border-bottom:1px solid var(--border); }}
.upload-tab {{
  flex:1; padding:18px; text-align:center; cursor:pointer; user-select:none;
  font-family:'Inter',sans-serif; font-size:15px; font-weight:600; color:var(--text-muted);
  background:transparent; border:none; border-bottom:2px solid transparent; transition:color .2s,border-color .2s,background .2s;
}}
.upload-tab.active {{ color:var(--navy); border-bottom-color:var(--gold); background:var(--surface); }}
.upload-panel {{ padding:36px; }}
.drop-zone {{
  border:1.5px dashed var(--border); border-radius:10px; padding:44px 28px;
  text-align:center; color:var(--text-muted); font-size:14px;
  display:flex; flex-direction:column; align-items:center; gap:6px;
  transition:border-color .2s,background .2s; cursor:pointer; user-select:none;
}}
.drop-zone:hover {{ border-color:var(--gold); }}
.drop-zone.drag-over {{ border-color:var(--gold); background:var(--blue-light); }}
.drop-zone.file-ready {{ border-color:var(--success); background:#f0fdf4; }}
.drop-icon {{ color:var(--text-muted); margin-bottom:6px; }}
.drop-icon svg {{ width:40px; height:40px; display:block; }}
.drop-zone.file-ready .drop-icon {{ color:var(--success); }}
#drop-text {{ font-family:'Inter',sans-serif; font-size:15px; font-weight:500; color:var(--navy); }}
.drop-hint {{ font-size:13px; color:var(--text-muted); }}
#file-name-display {{ margin-top:14px; text-align:center; font-size:13px; font-weight:600; min-height:18px; }}
.upload-action {{ padding:0 36px 36px; text-align:center; }}
.upload-action .security-note {{ display:flex; align-items:center; justify-content:center; gap:6px; margin-top:14px; }}
.form-field {{ margin-bottom:14px; }}
.form-field label {{ display:block; font-size:13px; font-weight:600; color:var(--navy); margin-bottom:5px; }}
.form-field input,.form-field select,.form-field textarea {{
  width:100%; padding:10px 12px; border:1px solid var(--border); border-radius:8px;
  font-family:'Inter',sans-serif; font-size:14px; color:var(--text-main);
  background:var(--surface); outline:none; transition:border-color .2s;
}}
.form-field input:focus,.form-field select:focus,.form-field textarea:focus {{ border-color:var(--blue); background:white; }}
.form-field textarea {{ resize:vertical; min-height:80px; }}
.form-grid-3col {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:0 28px; align-items:start; }}
.form-grid-3col .form-field textarea {{ min-height:90px; }}
.work-exp-head {{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; }}
.work-exp-head .form-section-label {{ margin-bottom:0; }}
.work-exp-head .text-link-btn {{ margin:0; white-space:nowrap; }}
.upload-divider {{ margin-top:28px; }}
.upload-doc-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:32px; align-items:start; }}
.cert-upload-zone.compact {{ padding:16px 14px; }}
.cert-upload-zone.compact svg {{ width:22px; height:22px; margin-bottom:2px; }}
.form-section-label {{ display:block; font-family:'Inter',sans-serif; font-size:12px; font-weight:700; color:var(--navy); margin-bottom:12px; text-transform:uppercase; letter-spacing:0.5px; }}
.optional-tag {{ font-weight:400; text-transform:none; letter-spacing:normal; color:var(--text-muted); font-size:12px; }}
.exp-block,.cert-block {{ position:relative; border:1px solid var(--border); border-radius:10px; padding:18px 18px 6px; margin-bottom:14px; background:var(--surface); }}
.block-remove-btn {{ position:absolute; top:10px; right:10px; width:22px; height:22px; border:none; border-radius:50%; background:transparent; color:var(--text-muted); font-size:16px; line-height:1; cursor:pointer; transition:background .2s,color .2s; }}
.block-remove-btn:hover {{ background:var(--border); color:var(--navy); }}
.text-link-btn {{ display:inline-block; background:none; border:none; padding:0; margin:0 0 28px; font-family:'Inter',sans-serif; font-size:13px; font-weight:600; color:var(--gold); cursor:pointer; }}
.text-link-btn:hover {{ color:var(--gold-deep); text-decoration:underline; }}
.combobox-field {{ position:relative; }}
.combobox-list {{
  display:none; position:absolute; top:100%; left:0; right:0; margin-top:4px; z-index:20;
  background:var(--white); border:1px solid var(--border); border-radius:8px; max-height:220px; overflow-y:auto;
  box-shadow:0 8px 24px rgba(15,23,42,0.12);
}}
.combobox-option {{ padding:9px 12px; font-family:'Inter',sans-serif; font-size:13px; color:var(--text-main); cursor:pointer; }}
.combobox-option:hover {{ background:var(--blue-light); color:var(--gold-deep); }}
.combobox-option-other {{ border-top:1px solid var(--border); color:var(--text-muted); font-style:italic; }}
.chip-input {{
  display:flex; flex-wrap:wrap; align-items:center; gap:6px; width:100%;
  padding:8px 10px; border:1px solid var(--border); border-radius:8px;
  background:var(--surface); cursor:text; transition:border-color .2s;
}}
.chip-input:focus-within {{ border-color:var(--blue); background:var(--white); }}
.chip-token {{
  display:inline-flex; align-items:center; gap:6px; padding:4px 8px 4px 12px;
  border-radius:99px; background:var(--blue-light); color:var(--gold-deep);
  font-family:'Inter',sans-serif; font-size:13px; font-weight:600; white-space:nowrap;
}}
.chip-token i {{ font-style:normal; cursor:pointer; opacity:0.6; }}
.chip-token i:hover {{ opacity:1; }}
.chip-input input {{ flex:1; min-width:120px; border:none; outline:none; background:transparent; font-family:'Inter',sans-serif; font-size:14px; padding:4px; }}
.cert-upload-zone {{
  border:1.5px dashed var(--border); border-radius:10px; padding:22px 16px;
  text-align:center; color:var(--text-muted); font-size:13px;
  display:flex; flex-direction:column; align-items:center; gap:4px;
  cursor:pointer; user-select:none; transition:border-color .2s,background .2s;
}}
.cert-upload-zone:hover {{ border-color:var(--gold); }}
.cert-upload-zone.drag-over {{ border-color:var(--gold); background:var(--blue-light); }}
.cert-upload-zone svg {{ width:26px; height:26px; display:block; color:var(--text-muted); margin-bottom:4px; }}
.cert-upload-zone .cert-zone-text {{ font-family:'Inter',sans-serif; font-size:13px; font-weight:500; color:var(--navy); }}
.cert-upload-zone .cert-zone-hint {{ font-size:12px; color:var(--text-muted); }}
.cert-file-list {{ display:flex; flex-direction:column; gap:6px; margin-top:10px; }}
.cert-file-item {{
  display:flex; align-items:center; gap:8px; padding:8px 10px;
  border:1px solid var(--border); border-radius:8px; background:var(--surface);
  font-family:'Inter',sans-serif; font-size:13px; color:var(--text-main);
}}
.cert-file-item svg {{ width:16px; height:16px; flex-shrink:0; color:var(--gold); }}
.cert-file-name {{ flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.cert-file-remove {{ cursor:pointer; color:var(--text-muted); font-weight:700; padding:0 4px; line-height:1; transition:color .2s; }}
.cert-file-remove:hover {{ color:var(--navy); }}
.scan-bar-wrap {{ background:var(--border); border-radius:99px; height:4px; overflow:hidden; margin-top:8px; }}
#scan-progress {{ height:100%; background:var(--blue); border-radius:99px; width:0%; transition:width .1s linear; }}
.security-note {{ text-align:center; color:var(--text-muted); font-size:13px; margin-top:16px; }}

/* ── SCREEN 3 — Profession Match Results ── */
.results-section {{ padding:48px; max-width:1280px; margin:0 auto; }}
.results-title {{ font-size:34px; font-weight:700; color:var(--navy); margin-bottom:8px; }}
.skill-chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:36px; }}
.skill-detected-chip {{
  display:inline-flex; align-items:center; gap:6px; padding:6px 14px 6px 10px;
  border-radius:99px; background:#F1F5F9; color:var(--navy);
  font-family:'Inter',sans-serif; font-size:13px; font-weight:600;
}}
.skill-detected-chip svg {{ width:14px; height:14px; color:var(--success); flex-shrink:0; }}
.results-loading {{ display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px; padding:96px 0; color:var(--text-muted); font-size:14px; }}
.results-spinner {{ width:32px; height:32px; border:3px solid var(--border); border-top-color:var(--gold); border-radius:50%; animation:results-spin .8s linear infinite; }}
@keyframes results-spin {{ to {{ transform:rotate(360deg); }} }}

.results-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:24px; align-items:stretch; }}
.match-card {{
  position:relative; display:flex; flex-direction:column; gap:10px;
  border:1px solid var(--border); border-radius:12px; padding:24px;
  background:white; cursor:pointer; transition:box-shadow .2s,transform .2s;
}}
.match-card:hover {{ transform:translateY(-2px); box-shadow:0 8px 24px rgba(15,23,42,0.08); }}
.match-card.best {{ border-top:4px solid var(--gold); box-shadow:0 6px 24px rgba(15,23,42,0.08); }}
.match-card.selected {{ border-color:var(--blue); box-shadow:0 0 0 2px rgba(156,122,74,0.22); }}
.match-best-badge {{ position:absolute; top:16px; right:16px; }}
.match-rank {{ font-family:'Inter',sans-serif; font-size:24px; font-weight:800; color:var(--blue-light); }}
.match-title {{ font-family:'Inter',sans-serif; font-size:17px; font-weight:700; color:var(--navy); }}
.match-onet-code {{ font-family:'Inter',sans-serif; font-size:11px; font-weight:600; letter-spacing:0.4px; color:var(--text-muted); text-transform:uppercase; }}
.match-desc {{ font-size:13px; color:var(--text-muted); flex:1; }}
.match-meta-line {{ font-size:12px; color:var(--text-muted); }}
.match-stats-row {{ display:flex; justify-content:space-between; gap:8px; font-size:12px; color:var(--text-muted); }}
.match-select-btn {{ width:100%; justify-content:center; margin-top:4px; }}

.match-add-card {{
  display:flex; flex-direction:column; border:2px dashed #CBD5E1; border-radius:12px;
  padding:24px; background:#F8FAFC;
}}
.match-add-card h3 {{ font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:var(--navy); margin-bottom:6px; }}
.match-add-card p {{ font-size:12px; color:var(--text-muted); margin-bottom:16px; }}
.match-add-card .custom-input-row {{ display:flex; flex-direction:column; gap:10px; margin-bottom:12px; }}
.match-add-card input {{ width:100%; padding:10px 14px; border:1px solid var(--border); border-radius:8px; font-family:'Inter',sans-serif; font-size:14px; outline:none; background:white; }}
.match-add-card input:focus {{ border-color:var(--blue); }}
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
  .form-grid-3col {{ grid-template-columns:1fr; }}
  .upload-doc-grid {{ grid-template-columns:1fr; }}
  .upload-panel {{ padding:24px; }}
  .upload-action {{ padding:0 24px 24px; }}
  .results-section,.gap-section,.packages-section,.roadmap-section,.dashboard-section {{ padding:40px 20px; }}
  .packages-grid {{ grid-template-columns:1fr; }}
  .results-grid {{ grid-template-columns:1fr 1fr; }}
  .skill-cols {{ grid-template-columns:1fr; }}
  .metric-cards {{ grid-template-columns:1fr 1fr; }}
  .roadmap-header {{ flex-direction:column; }}
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

    <div class="upload-card-single">
      <div class="upload-tabs">
        <button class="upload-tab active" id="tab-upload" type="button" onclick="selectTab('upload')">Upload Document</button>
        <button class="upload-tab" id="tab-manual" type="button" onclick="selectTab('manual')">Enter Manually</button>
      </div>

      <!-- Upload Document panel -->
      <div class="upload-panel" id="panel-upload">
        <div class="upload-doc-grid">
          <!-- LEFT — CV / Resume -->
          <div>
            <label class="form-section-label">Upload CV / Resume</label>
            <input type="file" id="cv-file-input" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" style="display:none">
            <div class="drop-zone" id="drop-zone">
              <div class="drop-icon" id="drop-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6M9 9h1"/></svg></div>
              <div id="drop-text">Click to browse or drag and drop your CV here</div>
              <div class="drop-hint">PDF or DOCX. Max 5MB</div>
            </div>
            <div id="file-name-display"></div>
          </div>

          <!-- RIGHT — Certificates -->
          <div>
            <label class="form-section-label">Upload Certificates <span class="optional-tag">(Optional)</span></label>
            <input type="file" id="cert-file-input-doc" multiple accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" style="display:none">
            <div class="cert-upload-zone" id="cert-drop-zone-doc">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/></svg>
              <div class="cert-zone-text">Drag &amp; drop certificate files here, or click to browse</div>
              <div class="cert-zone-hint">PDF, JPG or PNG &middot; multiple files allowed</div>
            </div>
            <div class="cert-file-list" id="cert-file-list-doc"></div>
          </div>
        </div>
      </div>

      <!-- Enter Manually panel -->
      <div class="upload-panel" id="panel-manual" style="display:none">
        <div class="form-grid-3col">
          <!-- COLUMN 1 — Personal & Education -->
          <div>
            <div class="form-field">
              <label>Full Name</label>
              <input type="text" id="m-full-name" placeholder="Enter your full name">
            </div>
            <div class="form-field">
              <label>Education Level</label>
              <select id="m-edu-level" onchange="handleEduLevelChange(this.value)">
                <option>High School Diploma / GED</option>
                <option>Certificate / Diploma</option>
                <option>Associate Degree</option>
                <option selected>Bachelor's Degree</option>
                <option>Master's Degree</option>
                <option>Doctorate (Ph.D.)</option>
                <option>Professional Degree</option>
                <option>Other</option>
              </select>
            </div>
            <div class="form-field" id="m-edu-other-wrap" style="display:none">
              <label>Please specify your degree</label>
              <input type="text" id="m-edu-other" placeholder="e.g. Vocational Certificate in Culinary Arts">
            </div>
            <div class="form-field combobox-field">
              <label>Major / Field of Study</label>
              <input type="text" id="m-major-input" placeholder="Type to search, e.g. Accounting, Computer Science..." autocomplete="off"
                     oninput="filterMajorOptions(this.value)" onfocus="filterMajorOptions(this.value)" onblur="setTimeout(closeMajorList,150)">
              <div class="combobox-list" id="m-major-list"></div>
            </div>
            <div class="form-field">
              <label>Institution Name</label>
              <input type="text" id="m-institution" placeholder="e.g. Universitas Padjadjaran">
            </div>
          </div>

          <!-- COLUMN 2 — Work Experience -->
          <div>
            <div class="work-exp-head">
              <label class="form-section-label">Work Experience</label>
              <button type="button" class="text-link-btn" onclick="addExperienceBlock()">+ Add Another</button>
            </div>
            <div id="work-exp-list">
              <div class="exp-block" data-exp-block>
                <div class="form-field"><label>Job Title</label><input type="text" class="exp-title" placeholder="e.g. Finance Staff"></div>
                <div class="form-field"><label>Company Name</label><input type="text" class="exp-company" placeholder="e.g. PT ABC Indonesia"></div>
                <div class="form-field">
                  <label>Duration</label>
                  <select class="exp-duration">
                    <option>Less than 1 year</option>
                    <option>1-3 years</option>
                    <option>3-5 years</option>
                    <option>5+ years</option>
                  </select>
                </div>
                <div class="form-field"><label>Key Responsibilities</label><textarea class="exp-desc" placeholder="Describe your main responsibilities and achievements..."></textarea></div>
              </div>
            </div>
          </div>

          <!-- COLUMN 3 — Skills & Certifications -->
          <div>
            <div class="form-field">
              <label>Skills You Have</label>
              <div class="chip-input" id="skills-chip-input" onclick="document.getElementById('skills-input').focus()">
                <input type="text" id="skills-input" placeholder="Type a skill and press Enter or comma..." onkeydown="handleSkillInput(event)">
              </div>
            </div>

            <label class="form-section-label">Upload Certificates <span class="optional-tag">(Optional)</span></label>
            <input type="file" id="cert-file-input-manual" multiple accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" style="display:none">
            <div class="cert-upload-zone compact" id="cert-drop-zone-manual">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/></svg>
              <div class="cert-zone-text">Drop certificate files here to verify your credentials.</div>
              <div class="cert-zone-hint">PDF, JPG or PNG &middot; multiple files allowed</div>
            </div>
            <div class="cert-file-list" id="cert-file-list-manual"></div>
          </div>
        </div>
      </div>

      <div class="upload-action">
        <div class="scan-bar-wrap" id="scan-wrap" style="max-width:400px;margin:0 auto 16px;visibility:hidden">
          <div id="scan-progress"></div>
        </div>
        <button id="analyze-btn" class="btn btn-primary btn-lg btn-disabled" disabled onclick="startAnalysis()">
          Analyze Now
        </button>
        <p class="security-note">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>
          Your data is secure and never shared with third parties.
        </p>
      </div>
    </div>
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
    <h1 class="font-display results-title">Professions most suited for you</h1>
    <p class="text-muted" id="results-subtitle" style="margin-bottom:24px;font-size:15px">Analyzing your profile&hellip;</p>

    <div id="results-loading" class="results-loading">
      <div class="results-spinner"></div>
      <div>Matching your skills against O*NET and SKKNI profession standards&hellip;</div>
    </div>

    <div id="results-content" style="display:none">
      <div class="skill-chips" id="detected-skills-list"></div>
      <div class="results-grid" id="results-grid"></div>
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

function selectTab(tab) {{
  document.querySelectorAll('.upload-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.getElementById('panel-upload').style.display = (tab === 'upload') ? '' : 'none';
  document.getElementById('panel-manual').style.display = (tab === 'manual') ? '' : 'none';

  const dropZone = document.getElementById('drop-zone');
  if (tab === 'manual') {{
    enableAnalyze();
  }} else if (!dropZone.classList.contains('file-ready')) {{
    disableAnalyze();
  }}
}}

function enableAnalyze() {{
  const btn = document.getElementById('analyze-btn');
  btn.classList.remove('btn-disabled');
  btn.disabled = false;
}}

function disableAnalyze() {{
  const btn = document.getElementById('analyze-btn');
  btn.classList.add('btn-disabled');
  btn.disabled = true;
}}

// ── MAJOR / FIELD OF STUDY — searchable combobox ───────────
// Comprehensive list spanning CIP / ISCED-F instructional-program families.
const MAJOR_OPTIONS = [
  // Agriculture & Natural Resources
  'Agricultural Business', 'Agricultural Economics', 'Agronomy and Crop Science', 'Animal Science',
  'Aquaculture', 'Fishery and Wildlife Sciences', 'Food Science and Technology', 'Forestry',
  'Horticulture', 'Natural Resources Management', 'Soil Science', 'Sustainable Agriculture', 'Veterinary Science',
  // Architecture & Construction
  'Architecture', 'Architectural Engineering', 'Construction Management', 'Interior Design',
  'Landscape Architecture', 'Urban and Regional Planning',
  // Arts, Design & Humanities
  'Animation and Visual Effects', 'Art History', 'Creative Writing', 'Fashion Design',
  'Film and Media Production', 'Fine Arts', 'Game Design', 'Graphic Design', 'Industrial Design',
  'Music', 'Music Performance', 'Music Production', 'Philosophy', 'Photography',
  'Theatre Arts', 'Visual Communication Design',
  // Business & Management
  'Accounting', 'Actuarial Science', 'Business Administration', 'Business Analytics',
  'Digital Marketing', 'E-commerce', 'Entrepreneurship', 'Finance', 'Hospitality Management',
  'Human Resource Management', 'International Business', 'Logistics and Supply Chain Management',
  'Management', 'Management Information Systems', 'Marketing', 'Operations Management',
  'Project Management', 'Real Estate', 'Retail Management', 'Risk Management and Insurance',
  // Communication & Media
  'Advertising', 'Broadcast Journalism', 'Communication Studies', 'Digital Media',
  'Journalism', 'Mass Communication', 'Media and Communication Studies', 'Public Relations',
  // Computer Science & Information Technology
  'Artificial Intelligence', 'Bioinformatics', 'Cloud Computing', 'Computer Engineering',
  'Computer Science', 'Cybersecurity', 'Data Science', 'Game Development', 'Information Systems',
  'Information Technology', 'Mobile App Development', 'Network and Systems Administration',
  'Software Engineering', 'UX/UI Design', 'Web Development',
  // Education
  'Curriculum and Instruction', 'Early Childhood Education', 'Educational Leadership',
  'Educational Psychology', 'Elementary Education', 'Secondary Education', 'Special Education',
  'Teaching English as a Foreign Language',
  // Engineering
  'Aerospace Engineering', 'Agricultural Engineering', 'Automotive Engineering', 'Biomedical Engineering',
  'Chemical Engineering', 'Civil Engineering', 'Electrical Engineering', 'Electronics Engineering',
  'Environmental Engineering', 'Geotechnical Engineering', 'Industrial Engineering',
  'Materials Science and Engineering', 'Mechanical Engineering', 'Mechatronics Engineering',
  'Mining Engineering', 'Naval Architecture and Marine Engineering', 'Nuclear Engineering',
  'Petroleum Engineering', 'Renewable Energy Engineering', 'Robotics Engineering',
  'Structural Engineering', 'Telecommunications Engineering',
  // Health Professions
  'Audiology', 'Clinical Laboratory Science', 'Dentistry', 'Dietetics and Nutrition',
  'Health Administration', 'Health Informatics', 'Medicine', 'Midwifery', 'Nursing',
  'Occupational Therapy', 'Optometry', 'Pharmacy', 'Physical Therapy', 'Public Health',
  'Radiologic Technology', 'Speech-Language Pathology', 'Veterinary Medicine',
  // Humanities, Languages & Religion
  'Arabic Studies', 'Chinese Studies', 'Classics', 'English Language and Literature',
  'French Studies', 'German Studies', 'History', 'Islamic Studies', 'Japanese Studies',
  'Korean Studies', 'Linguistics', 'Literature', 'Religious Studies', 'Spanish Studies',
  'Theology', 'Translation and Interpretation',
  // Law & Legal Studies
  'Criminal Justice', 'International Law', 'Law', 'Legal Studies', 'Paralegal Studies',
  // Mathematics & Statistics
  'Actuarial Mathematics', 'Applied Mathematics', 'Mathematics', 'Statistics',
  // Natural & Physical Sciences
  'Astronomy', 'Biochemistry', 'Biology', 'Biotechnology', 'Chemistry', 'Environmental Science',
  'Genetics', 'Geology', 'Geophysics', 'Marine Biology', 'Meteorology', 'Microbiology',
  'Molecular Biology', 'Oceanography', 'Physics', 'Zoology',
  // Psychology
  'Clinical Psychology', 'Cognitive Science', 'Counseling Psychology',
  'Industrial-Organizational Psychology', 'Psychology',
  // Social Sciences
  'Anthropology', 'Archaeology', 'Criminology', 'Demography', 'Development Studies', 'Economics',
  'Gender Studies', 'Geography', 'International Relations', 'Political Science',
  'Public Administration', 'Public Policy', 'Social Work', 'Sociology', 'Urban Studies',
  // Sports, Trades & Technical
  'Aviation Maintenance', 'Automotive Technology', 'Culinary Arts', 'Electrical Technology',
  'Exercise Science', 'HVAC Technology', 'Kinesiology', 'Sports Management', 'Sports Science',
  'Welding Technology'
];

function filterMajorOptions(query) {{
  const list = document.getElementById('m-major-list');
  const q = query.trim().toLowerCase();
  const matches = q ? MAJOR_OPTIONS.filter(m => m.toLowerCase().includes(q)) : MAJOR_OPTIONS.slice(0, 8);
  list.innerHTML = '';
  matches.forEach(m => {{
    const opt = document.createElement('div');
    opt.className = 'combobox-option';
    opt.textContent = m;
    opt.onmousedown = () => selectMajor(m);
    list.appendChild(opt);
  }});
  if (q && !MAJOR_OPTIONS.some(m => m.toLowerCase() === q)) {{
    const other = document.createElement('div');
    other.className = 'combobox-option combobox-option-other';
    other.textContent = "Add '" + query.trim() + "' as custom major";
    other.onmousedown = () => selectMajor(document.getElementById('m-major-input').value);
    list.appendChild(other);
  }}
  list.style.display = list.children.length ? 'block' : 'none';
}}
function selectMajor(value) {{
  document.getElementById('m-major-input').value = value;
  closeMajorList();
}}
function closeMajorList() {{
  const list = document.getElementById('m-major-list');
  if (list) list.style.display = 'none';
}}

// ── EDUCATION LEVEL — "Other" reveals a free-text degree field ──
function handleEduLevelChange(value) {{
  const wrap  = document.getElementById('m-edu-other-wrap');
  const input = document.getElementById('m-edu-other');
  if (!wrap || !input) return;
  wrap.style.display = value === 'Other' ? 'block' : 'none';
  if (value !== 'Other') input.value = '';
}}

// ── WORK EXPERIENCE — dynamic blocks ────────────────────────
function addExperienceBlock() {{
  const list = document.getElementById('work-exp-list');
  const block = document.createElement('div');
  block.className = 'exp-block';
  block.setAttribute('data-exp-block', '');
  block.innerHTML =
    '<button type="button" class="block-remove-btn" onclick="this.parentElement.remove()">&times;</button>' +
    '<div class="form-field"><label>Job Title</label><input type="text" class="exp-title" placeholder="e.g. Finance Staff"></div>' +
    '<div class="form-field"><label>Company Name</label><input type="text" class="exp-company" placeholder="e.g. PT ABC Indonesia"></div>' +
    '<div class="form-field"><label>Duration</label><select class="exp-duration">' +
      '<option>Less than 1 year</option><option>1-3 years</option><option>3-5 years</option><option>5+ years</option>' +
    '</select></div>' +
    '<div class="form-field"><label>Key Responsibilities</label><textarea class="exp-desc" placeholder="Describe your main responsibilities and achievements..."></textarea></div>';
  list.appendChild(block);
}}

// ── SKILLS — chip / token input ──────────────────────────────
function handleSkillInput(e) {{
  if (e.key === 'Enter' || e.key === ',') {{
    e.preventDefault();
    const input = e.target;
    const val = input.value.trim().replace(/,$/, '');
    if (val) addSkillChip(val);
    input.value = '';
  }} else if (e.key === 'Backspace' && !e.target.value) {{
    const chips = document.querySelectorAll('#skills-chip-input .chip-token');
    if (chips.length) chips[chips.length - 1].remove();
  }}
}}
function addSkillChip(value) {{
  const input = document.getElementById('skills-input');
  const chip = document.createElement('span');
  chip.className = 'chip-token';
  chip.setAttribute('data-skill', value);
  chip.appendChild(document.createTextNode(value + ' '));
  const remove = document.createElement('i');
  remove.textContent = '×';
  remove.onclick = (e) => {{ e.stopPropagation(); chip.remove(); }};
  chip.appendChild(remove);
  input.parentElement.insertBefore(chip, input);
}}

// ── BUILD JSON PAYLOAD — matches the user_profile contract ──
function buildProfilePayload() {{
  const workExperience = Array.from(document.querySelectorAll('#work-exp-list [data-exp-block]')).map(block => ({{
    job_title:    block.querySelector('.exp-title').value.trim(),
    company_name: block.querySelector('.exp-company').value.trim(),
    duration:     block.querySelector('.exp-duration').value,
    description:  block.querySelector('.exp-desc').value.trim()
  }}));

  const skills = Array.from(document.querySelectorAll('#skills-chip-input .chip-token')).map(c => c.getAttribute('data-skill'));

  const eduLevel = document.getElementById('m-edu-level').value;
  const eduOther = document.getElementById('m-edu-other').value.trim();

  return {{
    user_profile: {{
      full_name: document.getElementById('m-full-name').value.trim(),
      education: {{
        level:       eduLevel === 'Other' && eduOther ? eduOther : eduLevel,
        major:       document.getElementById('m-major-input').value.trim(),
        institution: document.getElementById('m-institution').value.trim()
      }},
      work_experience: workExperience,
      skills: skills,
      certifications: []
    }}
  }};
}}

// Certificates are verified via uploaded files rather than typed-in text,
// so they travel alongside the JSON payload as a multipart file array.
function collectCertificateFiles() {{
  return ['cert-file-list-doc', 'cert-file-list-manual'].flatMap(listId => {{
    const list = document.getElementById(listId);
    return list ? Array.from(list.children).map(item => item._file).filter(Boolean) : [];
  }});
}}

function startAnalysis() {{
  if (document.getElementById('tab-manual').classList.contains('active')) {{
    const payload = buildProfilePayload();
    const certificateFiles = collectCertificateFiles();
    console.log('PATHFINDER user_profile payload:', JSON.stringify(payload, null, 2));
    console.log('PATHFINDER certificate files:', certificateFiles.map(f => f.name));
    localStorage.setItem('pathfinder_profile_payload', JSON.stringify(payload));
    localStorage.setItem('pathfinder_certificate_files', JSON.stringify(certificateFiles.map(f => f.name)));
  }}
  const wrap = document.getElementById('scan-wrap');
  if (wrap) wrap.style.visibility = 'visible';
  runAIScanning();
}}

// ── DRAG & DROP CV ──────────────────────────────────────────
function initDropZone() {{
  const dropZone  = document.getElementById('drop-zone');
  const fileInput = document.getElementById('cv-file-input');
  const dropText  = document.getElementById('drop-text');
  const dropIcon  = document.getElementById('drop-icon');
  const nameDisp  = document.getElementById('file-name-display');

  if (!dropZone || !fileInput) return;

  // Click on drop zone → open file picker
  dropZone.addEventListener('click', () => fileInput.click());

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
    dropIcon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
    dropText.textContent  = file.name;
    nameDisp.textContent  = 'File ready · ' + (file.size / 1024).toFixed(0) + ' KB';
    nameDisp.style.color  = 'var(--success)';
    enableAnalyze();
    localStorage.setItem('pathfinder_cv_file', file.name);
  }}
}}

// ── CERTIFICATE DRAG & DROP (multi-file, reusable) ─────────
const CERT_ALLOWED_EXT = /\\.(pdf|jpe?g|png)$/i;
const CERT_MAX_SIZE = 5 * 1024 * 1024;

function initCertDropZone(zoneId, inputId, listId) {{
  const zone  = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  const list  = document.getElementById(listId);
  if (!zone || !input || !list) return;

  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover',  (e) => {{ e.preventDefault(); zone.classList.add('drag-over'); }});
  zone.addEventListener('dragenter', (e) => {{ e.preventDefault(); zone.classList.add('drag-over'); }});
  zone.addEventListener('dragleave', ()  => zone.classList.remove('drag-over'));

  zone.addEventListener('drop', (e) => {{
    e.preventDefault();
    zone.classList.remove('drag-over');
    addCertFiles(e.dataTransfer.files, list);
  }});

  input.addEventListener('change', (e) => {{
    addCertFiles(e.target.files, list);
    input.value = '';
  }});
}}

function addCertFiles(fileList, listEl) {{
  Array.from(fileList).forEach((file) => {{
    if (!CERT_ALLOWED_EXT.test(file.name)) {{
      alert('Please upload a PDF, JPG or PNG file.');
      return;
    }}
    if (file.size > CERT_MAX_SIZE) {{
      alert('File size must be less than 5MB.');
      return;
    }}

    const item = document.createElement('div');
    item.className = 'cert-file-item';
    item._file = file;

    const icon = document.createElement('span');
    icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>';

    const name = document.createElement('span');
    name.className = 'cert-file-name';
    name.textContent = file.name;

    const size = document.createElement('span');
    size.className = 'text-muted';
    size.style.fontSize = '12px';
    size.style.flexShrink = '0';
    size.textContent = (file.size / 1024).toFixed(0) + ' KB';

    const remove = document.createElement('span');
    remove.className = 'cert-file-remove';
    remove.textContent = '\\u00D7';
    remove.onclick = () => item.remove();

    item.appendChild(icon);
    item.appendChild(name);
    item.appendChild(size);
    item.appendChild(remove);
    listEl.appendChild(item);
  }});
}}

// ── PROFESSION MATCH RESULTS ────────────────────────────────
// RESULTS_DATA is injected directly from Python — it is the LIVE output
// of run_profile_analysis() / analyze_profile_with_claude() (the native
// "Upload Profile" step's real PDF/text → Claude → O*NET/SKKNI pipeline).
// Python only opens this screen once that step has produced real data
// (see PF_STEP / INITIAL_SCREEN_JS), but the empty state below stays as
// a defensive fallback — there is still no mock/static data here.
const RESULTS_DATA = {RESULTS_DATA_JSON};

function escHtml(value) {{
  const div = document.createElement('div');
  div.textContent = String(value);
  return div.innerHTML;
}}

function slugifyTitle(title) {{
  return String(title).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-+|-+$)/g, '');
}}

function buildMatchCard(match, index) {{
  const ratio  = match.total_required > 0 ? Math.round((match.matched_count / match.total_required) * 100) : 0;
  const isBest = index === 0;
  const slug   = slugifyTitle(match.title);

  const card = document.createElement('div');
  card.className = 'match-card' + (isBest ? ' best' : '');
  card.id = 'prof-' + slug;
  card.innerHTML =
    (isBest ? '<span class="badge badge-blue match-best-badge">Best Match</span>' : '') +
    '<div class="match-rank" style="' + (isBest ? '' : 'color:var(--border)') + '">' + String(index + 1).padStart(2, '0') + '</div>' +
    '<div class="match-title">' + escHtml(match.title) + '</div>' +
    '<div class="match-onet-code">O*NET-SOC ' + escHtml(match.onet_code) + '</div>' +
    '<div class="match-desc">' + escHtml(match.description) + '</div>' +
    '<div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-muted)"><span>Skill Match</span><span style="color:var(--blue);font-weight:700">' + ratio + '%</span></div>' +
    '<div class="progress-bar-wrap" style="height:8px"><div class="progress-bar-fill" style="width:' + ratio + '%"></div></div>' +
    '<div class="match-meta-line">' + match.matched_count + ' of ' + match.total_required + ' skills matched</div>' +
    '<div class="match-stats-row">' +
      '<span>Gap: <strong style="color:var(--navy)">' + match.gap_count + ' skills</strong></span>' +
      '<span>Roadmap: <strong style="color:var(--navy)">' + match.estimated_days + ' days</strong></span>' +
    '</div>' +
    '<button type="button" class="btn ' + (isBest ? 'btn-primary' : 'btn-outline') + ' btn-sm match-select-btn">Select</button>';

  const goToProfile = () => {{ selectProfession(slug); showScreen('screen-4'); }};
  card.addEventListener('click', goToProfile);
  card.querySelector('.match-select-btn').addEventListener('click', (e) => {{ e.stopPropagation(); goToProfile(); }});
  return card;
}}

function buildAddProfessionCard() {{
  const card = document.createElement('div');
  card.className = 'match-add-card';
  card.innerHTML =
    '<h3>Add a profession you\\'re interested in</h3>' +
    '<p>Even if your skills aren\\'t yet a strong match, Pathfinder will still build you a complete roadmap for it.</p>' +
    '<div class="custom-input-row">' +
      '<input id="custom-prof-input" type="text" placeholder="Search profession... e.g. Data Scientist">' +
      '<button type="button" class="btn btn-outline btn-sm" id="add-profession-btn">+ Add Profession</button>' +
    '</div>' +
    '<div id="custom-prof-chips"></div>';

  const input = card.querySelector('#custom-prof-input');
  card.querySelector('#add-profession-btn').addEventListener('click', addProfession);
  input.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') addProfession(); }});
  return card;
}}

function buildEmptyResultsState() {{
  const wrap = document.createElement('div');
  wrap.style.cssText = 'grid-column:1 / -1;text-align:center;padding:72px 24px;border:1px dashed var(--border);border-radius:12px;background:#F8FAFC;';
  const h = document.createElement('h3');
  h.style.cssText = "font-family:'Inter',sans-serif;font-size:18px;font-weight:700;color:var(--navy);margin:0 0 8px;";
  h.textContent = 'No analysis yet — your results will appear here';
  const p = document.createElement('p');
  p.style.cssText = 'font-size:14px;color:var(--text-muted);max-width:480px;margin:0 auto;line-height:1.6;';
  p.textContent = 'Scroll down to "Run it for real" below this preview, then upload your CV or type your '
    + 'profile in. Pathfinder will extract your real skills, map them to O*NET / SKKNI '
    + 'standards with Claude, and compute your actual profession-match percentages — nothing here is mocked.';
  wrap.appendChild(h);
  wrap.appendChild(p);
  return wrap;
}}

function renderResultsScreen() {{
  const data = RESULTS_DATA;
  const subtitle = document.getElementById('results-subtitle');
  const chipList = document.getElementById('detected-skills-list');
  const grid     = document.getElementById('results-grid');

  if (!data) {{
    if (subtitle) subtitle.textContent = 'Scroll down to "Run it for real" below this preview and upload your CV or type your profile in to generate your real, AI-powered profession matches.';
    if (chipList) chipList.innerHTML = '';
    if (grid) {{ grid.innerHTML = ''; grid.appendChild(buildEmptyResultsState()); }}
    return;
  }}

  if (subtitle) {{
    subtitle.innerHTML = '';
    subtitle.appendChild(document.createTextNode('Based on '));
    const strong = document.createElement('strong');
    strong.textContent = data.detected_skills.length + ' skills';
    subtitle.appendChild(strong);
    subtitle.appendChild(document.createTextNode(' detected from your profile, here are your top profession matches.'));
  }}

  if (chipList) {{
    chipList.innerHTML = '';
    data.detected_skills.forEach((skill) => {{
      const chip = document.createElement('span');
      chip.className = 'skill-detected-chip';
      const check = document.createElement('span');
      check.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
      chip.appendChild(check);
      chip.appendChild(document.createTextNode(skill));
      chipList.appendChild(chip);
    }});
  }}

  if (grid) {{
    grid.innerHTML = '';
    data.top_matches.slice(0, 3).forEach((match, i) => grid.appendChild(buildMatchCard(match, i)));
    grid.appendChild(buildAddProfessionCard());
  }}
}}

function loadResultsScreen() {{
  const loading = document.getElementById('results-loading');
  const content = document.getElementById('results-content');
  if (!loading || !content) return;
  if (content.dataset.loaded === '1') return;

  if (!RESULTS_DATA) {{
    // Nothing has been analyzed yet (no server round-trip happened) — go
    // straight to the explicit empty state instead of faking a fetch.
    loading.style.display = 'none';
    content.style.display = 'block';
    renderResultsScreen();
    content.dataset.loaded = '1';
    return;
  }}

  // The real analysis (PDF extraction + Claude O*NET/SKKNI mapping) has
  // already completed server-side during the Streamlit rerun that produced
  // this page — RESULTS_DATA is live data, not a placeholder. This brief
  // loader is purely a render transition, not a simulated network call.
  loading.style.display = 'flex';
  content.style.display = 'none';
  setTimeout(() => {{
    renderResultsScreen();
    loading.style.display = 'none';
    content.style.display = 'block';
    content.dataset.loaded = '1';
  }}, 450);
}}

// ── NAVBAR SHADOW ON SCROLL ─────────────────────────────────
window.addEventListener('scroll', () => {{
  document.querySelectorAll('.navbar').forEach(n => n.classList.toggle('scrolled', window.scrollY > 4));
}});

// ── INIT ────────────────────────────────────────────────────
// Python decides which screen to open based on the current Pathfinder
// step (INITIAL_SCREEN_JS): the landing screen for "landing", or the
// results screen — populated with real RESULTS_DATA — for "results".
showScreen({INITIAL_SCREEN_JS});
initSlider();
initDropZone();
initCertDropZone('cert-drop-zone-doc', 'cert-file-input-doc', 'cert-file-list-doc');
initCertDropZone('cert-drop-zone-manual', 'cert-file-input-manual', 'cert-file-list-manual');
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Native Pages: Skill Gap → Choose Plan → Roadmap → Dashboard
# All pages read real session data & query the SQLite database.
# ─────────────────────────────────────────────────────────────────────────────

def _render_skill_gap():
    """Page 3 — Skill Gap: shows acquired skills vs gap skills, readiness bar."""
    sel = st.session_state.get("pf_selected_match") or {}
    title = sel.get("title", "Your Chosen Profession")
    onet_code = sel.get("onet_code", "")
    match_ratio = sel.get("match_ratio", 0)
    gap_skills = sel.get("gap_skills", [])
    # matched_skills: use CV's detected_skills as the "have" column
    _ar = st.session_state.get("analysis_result") or {}
    matched_skills = [s for s in _ar.get("detected_skills", []) if s]

    st.markdown('<div class="pf-native-navbar">PATHFINDER</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pf-native-progress">'
        '<div class="pf-native-step done">✓ Upload Profile</div>'
        '<div class="pf-native-step done">✓ Results</div>'
        '<div class="pf-native-step current">3 · Skill Gap</div>'
        '<div class="pf-native-step">4 · Choose Plan</div>'
        '<div class="pf-native-step">5 · Roadmap</div>'
        '<div class="pf-native-step">6 · Dashboard</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="pf-readiness-wrap">', unsafe_allow_html=True)

    # Header
    st.markdown(
        f'<h2 class="pf-section-heading">Skill Gap Analysis</h2>'
        f'<p class="pf-section-subheading">Target role: <strong>{html.escape(title)}</strong>'
        + (f' &nbsp;·&nbsp; O*NET {html.escape(onet_code)}' if onet_code else '')
        + '</p>',
        unsafe_allow_html=True,
    )

    # Readiness card
    ratio_pct = min(int(match_ratio), 100)
    bar_color = "#16A34A" if ratio_pct >= 70 else ("#B48E4B" if ratio_pct >= 40 else "#EF4444")
    st.markdown(
        f'<div class="pf-readiness-card">'
        f'  <div class="pf-readiness-header">'
        f'    <span class="pf-readiness-label">Profile Readiness Score</span>'
        f'    <span class="pf-readiness-pct" style="color:{bar_color}">{ratio_pct}%</span>'
        f'  </div>'
        f'  <div class="pf-readiness-bar-bg">'
        f'    <div class="pf-readiness-bar-fg" style="width:{ratio_pct}%;background:{bar_color}"></div>'
        f'  </div>'
        f'  <div class="pf-readiness-sub">'
        f'    {len(matched_skills)} of {len(matched_skills)+len(gap_skills)} required skills detected in your profile'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Two-column skill list
    col_have, col_need = st.columns(2)

    with col_have:
        have_html = (
            '<div class="pf-skill-col">'
            f'  <div class="pf-skill-col-head">'
            f'    <h3>✅ Skills You Have</h3>'
            f'    <span class="pf-badge pf-badge-green">{len(matched_skills)}</span>'
            f'  </div>'
            f'  <div class="pf-skill-list">'
        )
        if matched_skills:
            for sk in matched_skills:
                have_html += (
                    f'<div class="pf-skill-row">'
                    f'  <span class="pf-skill-have-icon">✓</span>'
                    f'  {html.escape(str(sk))}'
                    f'</div>'
                )
        else:
            have_html += '<div class="pf-skill-row" style="color:#94A3B8;font-style:italic;">No matched skills detected</div>'
        have_html += '</div></div>'
        st.markdown(have_html, unsafe_allow_html=True)

    with col_need:
        need_html = (
            '<div class="pf-skill-col">'
            f'  <div class="pf-skill-col-head">'
            f'    <h3>🎯 Skills to Acquire</h3>'
            f'    <span class="pf-badge pf-badge-gold">{len(gap_skills)}</span>'
            f'  </div>'
            f'  <div class="pf-skill-list">'
        )
        if gap_skills:
            for sk in gap_skills:
                need_html += (
                    f'<div class="pf-skill-row">'
                    f'  <span class="pf-skill-need-icon"></span>'
                    f'  {html.escape(str(sk))}'
                    f'</div>'
                )
            need_html += (
                '<div class="pf-skill-callout">'
                '💡 These are the specific skills identified as missing from your profile. '
                'Your learning plan will target each one with a dedicated course.'
                '</div>'
            )
        else:
            need_html += '<div class="pf-skill-row" style="color:#16A34A;font-style:italic;">No skill gaps detected — great profile!</div>'
        need_html += '</div></div>'
        st.markdown(need_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Results", key="sg_back", use_container_width=True):
            st.session_state["pf_step"] = "results"
            st.rerun()
    with col_next:
        if st.button("Choose My Learning Plan →", key="sg_next", type="primary", use_container_width=True):
            st.session_state["pf_step"] = "choose_plan"
            st.rerun()


def _render_choose_plan():
    """Page 4 — Choose Plan: 3 pace tiers with real courses from DB, hours/day slider."""
    sel = st.session_state.get("pf_selected_match") or {}
    title = sel.get("title", "Your Chosen Profession")
    onet_code = sel.get("onet_code", "")
    total_hours = sel.get("total_course_hours", 0)

    st.markdown('<div class="pf-native-navbar">PATHFINDER</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pf-native-progress">'
        '<div class="pf-native-step done">✓ Upload Profile</div>'
        '<div class="pf-native-step done">✓ Results</div>'
        '<div class="pf-native-step done">✓ Skill Gap</div>'
        '<div class="pf-native-step current">4 · Choose Plan</div>'
        '<div class="pf-native-step">5 · Roadmap</div>'
        '<div class="pf-native-step">6 · Dashboard</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="pf-plan-wrap">', unsafe_allow_html=True)
    st.markdown(
        f'<h2 class="pf-section-heading">Choose Your Learning Plan</h2>'
        f'<p class="pf-section-subheading">Role: <strong>{html.escape(title)}</strong>'
        + (f' &nbsp;·&nbsp; {total_hours} total hours' if total_hours else '')
        + '</p>',
        unsafe_allow_html=True,
    )

    # Hours/day slider
    hours_per_day = st.slider(
        "Study hours per day",
        min_value=1, max_value=8, value=st.session_state.get("pf_study_hours_per_day", 2),
        key="cp_hours_slider",
        help="Adjust to see how long each plan takes",
    )
    st.session_state["pf_study_hours_per_day"] = hours_per_day

    # Fetch courses from DB
    courses = get_courses_for_onet(onet_code, limit=9) if onet_code else []
    if not courses:
        # fallback: generic 3 stubs so UI isn't empty
        courses = [
            {"id": f"stub_{i}", "title": f"Core Competency Module {i+1}", "provider": "ONLINE",
             "total_hours": 20 + i * 10, "url": "#"} for i in range(6)
        ]

    # Split courses across 3 tiers
    fast_courses = courses[:2]
    std_courses  = courses[:4]
    comp_courses = courses[:min(6, len(courses))]

    def _days(course_list):
        h = sum(c.get("total_hours", 0) for c in course_list)
        return max(1, math.ceil(h / hours_per_day))

    plans = [
        {
            "key": "fast",
            "icon": "⚡",
            "name": "Fast Track",
            "courses": fast_courses,
            "cert_note": "Essential certificates only",
        },
        {
            "key": "standard",
            "icon": "🎯",
            "name": "Standard",
            "courses": std_courses,
            "cert_note": "Core + advanced certificates",
            "recommended": True,
        },
        {
            "key": "comprehensive",
            "icon": "🏆",
            "name": "Comprehensive",
            "courses": comp_courses,
            "cert_note": "Full certificate portfolio",
        },
    ]

    cols = st.columns(3)
    for i, plan in enumerate(plans):
        days = _days(plan["courses"])
        total_h = sum(c.get("total_hours", 0) for c in plan["courses"])
        is_selected = st.session_state.get("pf_selected_plan") == plan["key"]

        card_class = "pf-plan-card" + (" recommended" if plan.get("recommended") else "")
        badge_html = '<span class="pf-plan-recommended-badge">⭐ Recommended</span>' if plan.get("recommended") else ""

        course_items_html = ""
        for c in plan["courses"]:
            course_items_html += (
                f'<div class="pf-plan-course-item">'
                f'  <div class="pf-plan-course-name">{html.escape(c["title"])}</div>'
                f'  <div class="pf-plan-course-meta">'
                f'    <span style="font-size:11px;background:#F1F5F9;padding:2px 7px;border-radius:4px;font-weight:600;">{c.get("provider","")}</span>'
                f'    <span>·</span><span>{c.get("total_hours",0)} hrs</span>'
                f'  </div>'
                f'</div>'
            )

        with cols[i]:
            st.markdown(
                f'<div class="{card_class}">'
                f'  {badge_html}'
                f'  <div class="pf-plan-icon">{plan["icon"]}</div>'
                f'  <div class="pf-plan-name">{plan["name"]}</div>'
                f'  <div class="pf-plan-days">{days}</div>'
                f'  <div class="pf-plan-days-label">days to complete</div>'
                f'  <div class="pf-plan-hours">{total_h} hrs &nbsp;·&nbsp; {len(plan["courses"])} courses</div>'
                f'  <div class="pf-plan-course-list">{course_items_html}</div>'
                f'  <div class="pf-plan-cert-note">🎓 {plan["cert_note"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            btn_label = "✓ Selected" if is_selected else "Select This Plan"
            if st.button(btn_label, key=f"cp_select_{plan['key']}", use_container_width=True,
                         type="primary" if is_selected else "secondary"):
                st.session_state["pf_selected_plan"] = plan["key"]
                st.session_state["pf_roadmap_courses"] = plan["courses"]
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Skill Gap", key="cp_back", use_container_width=True):
            st.session_state["pf_step"] = "skill_gap"
            st.rerun()
    with col_next:
        has_plan = bool(st.session_state.get("pf_selected_plan"))
        if st.button("View My Roadmap →", key="cp_next", type="primary",
                     use_container_width=True, disabled=not has_plan):
            st.session_state["pf_step"] = "roadmap"
            st.rerun()


def _render_roadmap():
    """Page 5 — Roadmap: sequential timeline with calculated dates, cert upload per stage."""
    sel = st.session_state.get("pf_selected_match") or {}
    title = sel.get("title", "Your Chosen Profession")
    hours_per_day = st.session_state.get("pf_study_hours_per_day", 2)
    courses = st.session_state.get("pf_roadmap_courses", [])
    completed = st.session_state.get("pf_completed_courses", set())
    session_id = st.session_state.get("session_id", "")
    plan_key = st.session_state.get("pf_selected_plan", "standard")
    plan_names = {"fast": "Fast Track", "standard": "Standard", "comprehensive": "Comprehensive"}

    st.markdown('<div class="pf-native-navbar">PATHFINDER</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pf-native-progress">'
        '<div class="pf-native-step done">✓ Upload Profile</div>'
        '<div class="pf-native-step done">✓ Results</div>'
        '<div class="pf-native-step done">✓ Skill Gap</div>'
        '<div class="pf-native-step done">✓ Choose Plan</div>'
        '<div class="pf-native-step current">5 · Roadmap</div>'
        '<div class="pf-native-step">6 · Dashboard</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    total_hours = sum(c.get("total_hours", 0) for c in courses)
    total_days = max(1, math.ceil(total_hours / hours_per_day)) if hours_per_day else total_hours
    end_date = datetime.date.today() + datetime.timedelta(days=total_days)

    st.markdown(
        f'<div class="pf-roadmap-wrap">'
        f'<div class="pf-roadmap-header-row">'
        f'  <div>'
        f'    <h2 class="pf-roadmap-title">Your Learning Roadmap</h2>'
        f'    <p class="pf-roadmap-sub">{html.escape(title)} · {plan_names.get(plan_key,"Standard")} plan</p>'
        f'  </div>'
        f'  <div class="pf-roadmap-stat-chips">'
        f'    <div class="pf-roadmap-stat-chip">📚 {len(courses)} courses</div>'
        f'    <div class="pf-roadmap-stat-chip">⏱ {total_hours} hrs total</div>'
        f'    <div class="pf-roadmap-stat-chip">📅 {hours_per_day} hrs/day</div>'
        f'    <div class="pf-roadmap-stat-chip">🏁 {end_date.strftime("%b %d, %Y")}</div>'
        f'  </div>'
        f'</div>'
        f'<div class="pf-timeline">',
        unsafe_allow_html=True,
    )

    current_date = datetime.date.today()
    for idx, course in enumerate(courses):
        course_hours = course.get("total_hours", 0)
        course_days = max(1, math.ceil(course_hours / hours_per_day)) if hours_per_day else course_hours
        finish_date = current_date + datetime.timedelta(days=course_days)
        cid = course.get("id", f"course_{idx}")
        is_done = cid in completed
        is_active = not is_done and idx == min(
            [i for i, c in enumerate(courses) if c.get("id", f"course_{i}") not in completed],
            default=idx
        )
        bullet_class = "done" if is_done else ("active" if is_active else "")
        card_class = "pf-tl-card " + bullet_class
        line_class = "pf-tl-line " + ("done" if is_done else ("active" if is_active else ""))
        bullet_icon = "✓" if is_done else str(idx + 1)
        status_label = "✓ Completed" if is_done else ("🔵 In Progress" if is_active else "⏳ Upcoming")

        st.markdown(
            f'<div class="pf-tl-item">'
            f'  <div class="pf-tl-left">'
            f'    <div class="pf-tl-bullet {bullet_class}">{bullet_icon}</div>'
            + (f'    <div class="{line_class}"></div>' if idx < len(courses) - 1 else '')
            + f'  </div>'
            f'  <div class="{card_class}">'
            f'    <div class="pf-tl-card-inner">'
            f'      <div class="pf-tl-card-main">'
            f'        <div class="pf-tl-stage-label">Stage {idx+1} · {status_label}</div>'
            f'        <div class="pf-tl-skill-name">{html.escape(course.get("title",""))}</div>'
            f'        <div class="pf-tl-course-name">Provider: {course.get("provider","")}</div>'
            f'        <div class="pf-tl-duration">⏱ {course_hours} hrs &nbsp;·&nbsp; ~{course_days} days</div>'
            f'      </div>'
            f'      <div class="pf-tl-card-side">'
            f'        <div class="pf-tl-date">Start: <strong>{current_date.strftime("%b %d")}</strong></div>'
            f'        <div class="pf-tl-date">End: <strong>{finish_date.strftime("%b %d, %Y")}</strong></div>'
            f'      </div>'
            f'    </div>',
            unsafe_allow_html=True,
        )

        # Certificate upload + mark complete
        if not is_done:
            cert_col, btn_col = st.columns([3, 1])
            with cert_col:
                cert_url = st.text_input(
                    "Certificate URL (optional)",
                    key=f"rm_cert_{idx}",
                    placeholder="https://coursera.org/verify/...",
                    label_visibility="collapsed",
                )
            with btn_col:
                if st.button("✓ Mark Done", key=f"rm_done_{idx}", use_container_width=True):
                    completed.add(cid)
                    st.session_state["pf_completed_courses"] = completed
                    if cert_url.strip() and session_id:
                        verify_user_skill(session_id, course.get("title", ""), cert_url.strip())
                    st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)
        current_date = finish_date

    # Finish node
    all_done = all(c.get("id", f"course_{i}") in completed for i, c in enumerate(courses))
    finish_icon = "🎓" if all_done else "🏁"
    finish_text = "Congratulations! All courses completed." if all_done else f"Complete all {len(courses)} courses to earn your full certificate portfolio."
    st.markdown(
        f'<div class="pf-tl-end-node">'
        f'  <div class="pf-tl-end-bullet">{finish_icon}</div>'
        f'  <div class="pf-tl-end-text">'
        f'    <h3>{"Profile Complete!" if all_done else "Target Completion"}</h3>'
        f'    <p>{finish_text} · {end_date.strftime("%B %d, %Y")}</p>'
        f'  </div>'
        f'</div>'
        f'</div>'  # close pf-timeline
        f'</div>',  # close pf-roadmap-wrap
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Plan", key="rm_back", use_container_width=True):
            st.session_state["pf_step"] = "choose_plan"
            st.rerun()
    with col_next:
        if st.button("Go to Dashboard →", key="rm_next", type="primary", use_container_width=True):
            st.session_state["pf_step"] = "dashboard"
            st.rerun()


def _render_dashboard():
    """Page 6 — Dashboard: progress metrics, active course, certificate verification."""
    sel = st.session_state.get("pf_selected_match") or {}
    title = sel.get("title", "Your Chosen Profession")
    onet_code = sel.get("onet_code", "")
    match_ratio = sel.get("match_ratio", 0)
    courses = st.session_state.get("pf_roadmap_courses", [])
    completed = st.session_state.get("pf_completed_courses", set())
    hours_per_day = st.session_state.get("pf_study_hours_per_day", 2)
    session_id = st.session_state.get("session_id", "")
    cert_states = st.session_state.get("pf_cert_states", {})

    done_count = sum(1 for i, c in enumerate(courses) if c.get("id", f"course_{i}") in completed)
    total_count = len(courses)
    total_hours = sum(c.get("total_hours", 0) for c in courses)
    done_hours = sum(
        c.get("total_hours", 0) for i, c in enumerate(courses)
        if c.get("id", f"course_{i}") in completed
    )
    progress_pct = int(done_hours / total_hours * 100) if total_hours else 0
    days_elapsed = math.ceil(done_hours / hours_per_day) if hours_per_day else 0
    remaining_hours = total_hours - done_hours
    days_remaining = math.ceil(remaining_hours / hours_per_day) if hours_per_day and remaining_hours > 0 else 0
    eta = (datetime.date.today() + datetime.timedelta(days=days_remaining)).strftime("%b %d, %Y") if days_remaining else "Completed!"

    st.markdown('<div class="pf-native-navbar">PATHFINDER</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pf-native-progress">'
        '<div class="pf-native-step done">✓ Upload Profile</div>'
        '<div class="pf-native-step done">✓ Results</div>'
        '<div class="pf-native-step done">✓ Skill Gap</div>'
        '<div class="pf-native-step done">✓ Choose Plan</div>'
        '<div class="pf-native-step done">✓ Roadmap</div>'
        '<div class="pf-native-step current">6 · Dashboard</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="pf-dash-wrap">', unsafe_allow_html=True)

    # Greeting
    st.markdown(
        f'<div class="pf-dash-greeting">'
        f'  <div>'
        f'    <h2>Learning Dashboard</h2>'
        f'    <p>Target: <strong>{html.escape(title)}</strong>'
        + (f' &nbsp;·&nbsp; O*NET {html.escape(onet_code)}' if onet_code else '')
        + '</p>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 4 metric cards
    st.markdown(
        f'<div class="pf-metric-cards">'
        f'  <div class="pf-metric-card">'
        f'    <div class="pf-metric-label">Profile Match</div>'
        f'    <div class="pf-metric-value">{int(match_ratio)}%</div>'
        f'    <div class="pf-metric-sub">Based on CV analysis</div>'
        f'  </div>'
        f'  <div class="pf-metric-card">'
        f'    <div class="pf-metric-label">Courses Done</div>'
        f'    <div class="pf-metric-value">{done_count}/{total_count}</div>'
        f'    <div class="pf-metric-sub">Courses completed</div>'
        f'  </div>'
        f'  <div class="pf-metric-card">'
        f'    <div class="pf-metric-label">Hours Logged</div>'
        f'    <div class="pf-metric-value">{done_hours}</div>'
        f'    <div class="pf-metric-sub">of {total_hours} total hrs</div>'
        f'  </div>'
        f'  <div class="pf-metric-card">'
        f'    <div class="pf-metric-label">ETA</div>'
        f'    <div class="pf-metric-value" style="font-size:18px;">{eta}</div>'
        f'    <div class="pf-metric-sub">{days_remaining} days remaining</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Overall progress bar
    bar_color = "#16A34A" if progress_pct == 100 else "#B48E4B"
    st.markdown(
        f'<div class="pf-active-stage-card">'
        f'  <div class="pf-active-stage-header">'
        f'    <div class="pf-active-stage-title">Overall Progress</div>'
        f'    <span style="font-weight:700;color:{bar_color}">{progress_pct}%</span>'
        f'  </div>'
        f'  <div class="pf-progress-label"><span>{done_hours} hrs done</span><span>{remaining_hours} hrs left</span></div>'
        f'  <div class="pf-readiness-bar-bg">'
        f'    <div class="pf-readiness-bar-fg" style="width:{progress_pct}%;background:{bar_color}"></div>'
        f'  </div>',
        unsafe_allow_html=True,
    )

    # Active / next course
    active_courses = [c for i, c in enumerate(courses) if c.get("id", f"course_{i}") not in completed]
    if active_courses:
        next_c = active_courses[0]
        st.markdown(
            f'<div style="margin-top:16px;padding-top:14px;border-top:1px solid #E2E8F0;">'
            f'  <div class="pf-active-course-meta">📖 Currently up next: <strong>{html.escape(next_c["title"])}</strong>'
            f'  &nbsp;·&nbsp; {next_c.get("provider","")} &nbsp;·&nbsp; {next_c.get("total_hours",0)} hrs</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Certificate verification panel
    if courses:
        st.markdown('<div class="pf-section-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<h3 class="pf-section-heading">🎓 Certificate Verification</h3>'
            '<p class="pf-section-subheading">Paste your certificate URL to verify and unlock your credential badge.</p>',
            unsafe_allow_html=True,
        )

        for idx, course in enumerate(courses):
            cid = course.get("id", f"course_{idx}")
            is_done = cid in completed
            c_state = cert_states.get(cid, {})
            is_verified = c_state.get("verified", False)

            verified_class = " verified" if is_verified else ""
            status_icon = "✅" if is_verified else ("⏳" if not is_done else "📋")
            row_html = (
                f'<div class="pf-cert-row{verified_class}">'
                f'  <div style="flex:1;font-family:\'Inter\',sans-serif;font-size:13px;font-weight:600;color:#0F172A;">'
                f'    {status_icon} {html.escape(course["title"])}'
                f'  </div>'
                f'  <div class="pf-course-provider" style="margin:0 12px;">{course.get("provider","")}</div>'
                f'  <div class="pf-match-card-hours" style="font-size:12px;">{course.get("total_hours",0)} hrs</div>'
                f'</div>'
            )
            st.markdown(row_html, unsafe_allow_html=True)

            if not is_verified:
                cv_col, vbtn_col = st.columns([3, 1])
                with cv_col:
                    cert_url = st.text_input(
                        "Certificate URL",
                        key=f"dash_cert_{idx}",
                        placeholder="https://coursera.org/verify/...",
                        label_visibility="collapsed",
                    )
                with vbtn_col:
                    if st.button("Verify", key=f"dash_vbtn_{idx}", use_container_width=True):
                        if cert_url.strip():
                            ok = verify_user_skill(session_id, course["title"], cert_url.strip())
                            cert_states[cid] = {"url": cert_url.strip(), "verified": True}
                            st.session_state["pf_cert_states"] = cert_states
                            completed.add(cid)
                            st.session_state["pf_completed_courses"] = completed
                            st.success(f"✓ Verified: {course['title']}")
                            st.rerun()
                        else:
                            st.warning("Paste your certificate URL first.")

    # Motivational card
    st.markdown(
        f'<div class="pf-motivation-card">'
        f'  <p>You\'re building a <strong>future-proof career</strong> in {html.escape(title)}. '
        f'  Each course you complete brings you one step closer to your goal. '
        f'  Keep going — your future self will thank you. 🚀</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_restart = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Roadmap", key="db_back", use_container_width=True):
            st.session_state["pf_step"] = "roadmap"
            st.rerun()
    with col_restart:
        if st.button("↺ Start New Analysis", key="db_restart", use_container_width=True):
            for key in ["pf_step", "analysis_result", "analysis_error", "pf_cert_states",
                        "pf_selected_match", "pf_selected_plan", "pf_roadmap_courses",
                        "pf_completed_courses", "pf_show_planner"]:
                st.session_state.pop(key, None)
            st.rerun()


if PF_STEP == "landing":
    # Native landing — ONE real "Get Started" CTA (no mockup duplicate
    # sitting beside it). Visuals are hand-styled to match Pathfinder's
    # gold/navy/cream identity rather than imported wholesale from the
    # preview's stylesheet (which resets body/h1-h6/etc. globally and
    # would break Streamlit's own chrome if loaded outside the iframe).
    st.markdown('<div class="pf-native-navbar">PATHFINDER</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pf-native-hero">'
        '<p class="eyebrow">AI-Powered Career Mapping</p>'
        '<h1>Discover Your Career<br><span>Path Today</span></h1>'
        '<p>Know exactly what skills you need for your dream career. Pathfinder compares your CV with '
        'global industry standards — using a real AI pipeline against O*NET and SKKNI — to build your '
        'personalized learning roadmap.</p>'
        '<p class="micro">PDF or DOCX. 100% Free &amp; Secure.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="pf-step-cta-wrap">', unsafe_allow_html=True)
    if st.button("🚀  Analyze My CV — Get Started", type="primary", key="pf_get_started"):
        st.session_state["pf_step"] = "upload"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pf-native-howit">'
        '<div class="pf-native-howit-card"><div class="num">1</div><h4>Upload CV or fill in your data</h4>'
        '<p>Upload your CV or describe your profile to start your analysis.</p></div>'
        '<div class="pf-native-howit-card"><div class="num">2</div><h4>AI analyzes your profile</h4>'
        '<p>Claude maps your real skills against O*NET and SKKNI standardized professions.</p></div>'
        '<div class="pf-native-howit-card"><div class="num">3</div><h4>See your matches &amp; gaps</h4>'
        '<p>Get your top profession matches with an honest, computed skill-match ratio.</p></div>'
        '<div class="pf-native-howit-card"><div class="num">4</div><h4>Explore your roadmap</h4>'
        '<p>Tour Pathfinder\'s learning roadmap, plans, and dashboard experience.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="pf-native-stats">'
        '<div><div class="num">1,000+</div><div class="label">O*NET Professions</div></div>'
        '<div><div class="num">500+</div><div class="label">Certified Courses</div></div>'
        '<div><div class="num">SKKNI</div><div class="label">Standardized</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

elif PF_STEP == "upload":
    # ── Phase 3 loading helper ────────────────────────────────────────────
    _LOADING_MSGS = [
        "Extracting document…",
        "Mapping to O*NET &amp; SKKNI…",
        "Calculating absolute skill gaps…",
        "Building your career profile…",
    ]
    _LOADING_HTML = (
        '<div class="pf-loading-wrap">'
        '<div class="pf-loading-ring">'
        '<div class="pf-loading-ring-track"></div>'
        '<div class="pf-loading-ring-spin"></div>'
        '<div class="pf-loading-ring-pulse"></div>'
        '</div>'
        '<div class="pf-loading-main-text" id="pf-lt">Extracting document…</div>'
        '<div class="pf-loading-sub-text">AI pipeline · O*NET · SKKNI</div>'
        '<div class="pf-loading-steps">'
        + ''.join(
            f'<div class="pf-loading-dot{" active" if i == 0 else ""}" id="pf-dot-{i}"></div>'
            for i in range(4)
        )
        + '</div>'
        '<script>'
        'var _pfMsgs=['
        + ",".join(f'"{m}"' for m in _LOADING_MSGS)
        + '];'
        'var _pfIdx=0;'
        'function _pfTick(){'
        '  var el=document.getElementById("pf-lt");'
        '  if(!el)return;'
        '  el.style.opacity="0";'
        '  setTimeout(function(){'
        '    _pfIdx=(_pfIdx+1)%_pfMsgs.length;'
        '    el.innerHTML=_pfMsgs[_pfIdx];'
        '    el.style.opacity="1";'
        '    document.querySelectorAll(".pf-loading-dot").forEach(function(d,i){'
        '      d.classList.toggle("active",i===_pfIdx);'
        '    });'
        '  },280);'
        '}'
        'setInterval(_pfTick,1900);'
        '</script>'
        '</div>'
    )

    def _run_analysis_with_loading(fn, *args):
        """Show premium loading animation while blocking analysis runs, then return result."""
        _placeholder = st.empty()
        _placeholder.markdown(_LOADING_HTML, unsafe_allow_html=True)
        try:
            _result = fn(*args)
        finally:
            _placeholder.empty()
        return _result

    # ────────────────────────────────────────────────────────────────────
    # THE real "Upload Profile" step — rendered natively (not inside the
    # iframe) so its "Upload Document" / "Enter Manually" tabs are genuine
    # working inputs. Whatever is submitted here runs through the real
    # PDF-extraction → Claude → O*NET/SKKNI pipeline.
    # ────────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="pf-native-progress">'
        '<div class="pf-native-step current">1 · Upload Profile</div>'
        '<div class="pf-native-step">2 · Results</div>'
        '<div class="pf-native-step">3 · Skill Gap</div>'
        '<div class="pf-native-step">4 · Choose Plan</div>'
        '<div class="pf-native-step">5 · Roadmap</div>'
        '</div>'
        '<div class="pf-native-heading">'
        '<h2>Start with your profile</h2>'
        '<p>Pathfinder will automatically read your skills, experience, and education</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(key="pf_upload_page"):
        tab_doc, tab_manual = st.tabs(["📄  Upload Document", "✍️  Enter Manually"])

        with tab_doc:
            cv_pdf_file = st.file_uploader("Upload CV / Resume (PDF)", type=["pdf"], key="pf_cv_pdf")
            if st.button("Analyze Now", type="primary", key="pf_analyze_doc", disabled=cv_pdf_file is None):
                st.session_state["analysis_error"] = None
                st.session_state["analysis_result"] = None
                try:
                    result = _run_analysis_with_loading(run_profile_analysis, cv_pdf_file.getvalue())
                    st.session_state["analysis_result"] = result
                    # Persist CV text + skills to DB
                    upsert_user_profile(st.session_state["session_id"],
                                        extract_pdf_text(cv_pdf_file.getvalue()))
                    upsert_user_skills(st.session_state["session_id"],
                                       result.get("detected_skills", []),
                                       result.get("top_matches", [{}])[0].get("onet_code"))
                    st.session_state["pf_step"] = "results"
                except Exception as exc:
                    st.session_state["analysis_error"] = str(exc)
                st.rerun()

        with tab_manual:
            manual_profile_text = st.text_area(
                "Describe your profile — education, work experience, and skills",
                placeholder=(
                    "e.g. Bachelor's in Mathematics from ITB, 2 years as a data analyst building "
                    "Python/SQL dashboards. Skills: statistics, machine learning basics, Excel, SQL…"
                ),
                height=180, key="pf_manual_text",
            )
            if st.button("Analyze Now", type="primary", key="pf_analyze_manual",
                         disabled=not manual_profile_text.strip()):
                st.session_state["analysis_error"] = None
                st.session_state["analysis_result"] = None
                try:
                    result = _run_analysis_with_loading(analyze_profile_with_gemini,
                                                        manual_profile_text.strip())
                    st.session_state["analysis_result"] = result
                    upsert_user_profile(st.session_state["session_id"], manual_profile_text.strip())
                    upsert_user_skills(st.session_state["session_id"],
                                       result.get("detected_skills", []),
                                       result.get("top_matches", [{}])[0].get("onet_code"))
                    st.session_state["pf_step"] = "results"
                except Exception as exc:
                    st.session_state["analysis_error"] = str(exc)
                st.rerun()

        if st.session_state.get("analysis_error"):
            st.error(f"Analysis failed: {st.session_state['analysis_error']}")

    st.markdown('<div class="pf-upload-back-wrap">', unsafe_allow_html=True)
    if st.button("← Back", key="pf_upload_back"):
        st.session_state["pf_step"] = "landing"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif PF_STEP == "results":
    # ── Phase 4 — Native 4-column results ─────────────────────────────────
    # Columns 1-3: real AI matches with O*NET code, absolute match ratio,
    # gap skills, and DB-sourced course recommendations.
    # Column 4: manual "add a target profession" input.
    # ──────────────────────────────────────────────────────────────────────
    _result = st.session_state.get("analysis_result") or {"detected_skills": [], "top_matches": []}
    _skills = _result.get("detected_skills", [])
    _matches = _result.get("top_matches", [])

    st.markdown(
        '<div class="pf-native-progress">'
        '<div class="pf-native-step done">✓ Upload Profile</div>'
        '<div class="pf-native-step current">2 · Results</div>'
        '<div class="pf-native-step">3 · Skill Gap</div>'
        '<div class="pf-native-step">4 · Choose Plan</div>'
        '<div class="pf-native-step">5 · Roadmap</div>'
        '</div>'
        '<div class="pf-native-results-head">'
        '<h2>Professions most suited for you</h2>'
        '<p>Based on the skills Claude detected in your profile, matched against O*NET / SKKNI standards.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Extracted skills chips (✓) ────────────────────────────────────────
    if _skills:
        chips = "".join(
            f'<span class="pf-native-skill-chip">✓ {html.escape(s)}</span>' for s in _skills
        )
        st.markdown(f'<div class="pf-native-skills-row">{chips}</div>', unsafe_allow_html=True)

    # ── 4-column grid: 3 AI matches + 1 manual input ──────────────────────
    _padded_matches = (_matches + [{}, {}, {}])[:3]   # always exactly 3 slots
    cols = st.columns(4, gap="medium")

    for i, match in enumerate(_padded_matches):
        if not match:
            continue
        ratio = (
            round((match["matched_count"] / match["total_required"]) * 100)
            if match.get("total_required") else 0
        )
        is_best = i == 0

        # Enrich with DB data (Phase 1 + Phase 2 query)
        onet_code = match.get("onet_code", "")
        db_courses = get_courses_for_onet(onet_code, limit=3)
        total_course_hrs = get_total_hours_for_onet(onet_code)

        # Build gap-skills chips HTML
        gap_skills = match.get("gap_skills", [])
        gap_html = ""
        if gap_skills:
            gap_chips = "".join(
                f'<span class="pf-gap-skill-chip">{html.escape(g)}</span>' for g in gap_skills[:4]
            )
            gap_html = f'<div class="pf-gap-skills-wrap">{gap_chips}</div>'

        # Build course rows HTML
        courses_html = ""
        if db_courses:
            rows = "".join(
                f'<div class="pf-course-row">'
                f'<span class="pf-course-provider">{c["provider"]}</span>'
                f'<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{html.escape(c["title"])}</span>'
                f'<span style="white-space:nowrap;color:#B48E4B;font-weight:600">{c["total_hours"]}h</span>'
                f'</div>'
                for c in db_courses
            )
            courses_html = (
                f'<div class="pf-match-card-courses">'
                f'<div class="pf-match-card-courses-label">Recommended Courses</div>'
                f'{rows}'
                f'</div>'
            )

        hours_html = (
            f'<div class="pf-match-card-hours">⏱ {total_course_hrs} hrs total course content</div>'
            if total_course_hrs else ""
        )

        with cols[i]:
            st.markdown(
                f'<div class="pf-native-match-card{" best" if is_best else ""}">'
                + ('<span class="pf-native-match-badge">Best Match</span>' if is_best else '')
                + f'<h3>{html.escape(match["title"])}</h3>'
                + f'<div class="pf-native-match-onet">O*NET-SOC {html.escape(onet_code)}</div>'
                + f'<div class="pf-native-match-desc">{html.escape(match.get("description", ""))}</div>'
                + '<div class="pf-native-match-stats"><span>Skill Match</span>'
                + f'<span style="color:#B48E4B;font-weight:700">{ratio}%</span></div>'
                + f'<div class="pf-native-match-bar-wrap"><div class="pf-native-match-bar-fill" style="width:{ratio}%"></div></div>'
                + f'<div class="pf-native-match-meta">{match.get("matched_count",0)} of {match.get("total_required",0)} skills matched'
                + f' · Gap: {match.get("gap_count",0)} · Roadmap: {match.get("estimated_days",0)} days</div>'
                + gap_html
                + hours_html
                + courses_html
                + '</div>',
                unsafe_allow_html=True,
            )
            with st.container(key=f"pf_match_col_{i}"):
                if st.button(
                    "Select & Plan Study →" if is_best else "Select this profession",
                    type="primary" if is_best else "secondary",
                    key=f"pf_select_match_{i}",
                    use_container_width=True,
                ):
                    st.session_state["pf_selected_match"] = {
                        **match,
                        "total_course_hours": total_course_hrs,
                        "match_ratio": ratio,
                    }
                    st.session_state["pf_show_planner"] = True
                    st.rerun()

    # ── Column 4 — manual profession target ───────────────────────────────
    with cols[3]:
        st.markdown(
            '<div class="pf-add-profession-card">'
            '<h3>Add a target profession</h3>'
            '<p>Even without a strong AI match, Pathfinder will build you a complete '
            'roadmap for any profession you aspire to.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        custom_prof = st.text_input("Search profession…", key="pf_custom_prof_input",
                                    placeholder="e.g. UX Designer, Product Manager…",
                                    label_visibility="collapsed")
        if st.button("Get Roadmap →", key="pf_custom_prof_btn",
                     disabled=not (custom_prof or "").strip(), use_container_width=True):
            st.session_state["pf_selected_match"] = {
                "title": custom_prof.strip(),
                "onet_code": "",
                "description": "Custom profession target selected by user.",
                "matched_count": 0, "total_required": 0, "gap_count": 0,
                "gap_skills": [], "estimated_days": 60,
                "total_course_hours": 0,
                "match_ratio": 0,
            }
            st.session_state["pf_show_planner"] = True
            st.rerun()

    # ── Phase 5: Certificate verification ─────────────────────────────────
    st.markdown(
        '<div class="pf-section-divider"><hr></div>'
        '<div style="max-width:1200px;margin:0 auto;padding:0 48px">'
        '<p class="pf-section-heading">🎓 Verify Your Skills with Certificates</p>'
        '<p class="pf-section-subheading">Upload certificate URLs to mark skills as verified — '
        'they turn green (✓) instantly and are stored in your session profile.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Build a combined list from the top match's courses + detected skills
    _top_match = _matches[0] if _matches else {}
    _top_onet = _top_match.get("onet_code", "")
    _verify_courses = get_courses_for_onet(_top_onet, limit=6) if _top_onet else []
    _cert_states = st.session_state.get("pf_cert_states", {})

    if _verify_courses:
        st.markdown('<div style="max-width:1200px;margin:0 auto 8px;padding:0 48px">', unsafe_allow_html=True)
        for crs in _verify_courses:
            cid = crs["course_id"]
            is_verified = _cert_states.get(cid, {}).get("verified", False)
            row_class = "pf-cert-row verified" if is_verified else "pf-cert-row"
            status_icon = "✅" if is_verified else "❌"
            st.markdown(
                f'<div class="{row_class}">'
                f'<span class="pf-cert-status-icon">{status_icon}</span>'
                f'<div style="flex:1">'
                f'<div class="pf-cert-title">{html.escape(crs["title"])}</div>'
                f'<div class="pf-cert-provider">{crs["provider"]}</div>'
                f'</div>'
                f'<div class="pf-cert-hours">{crs["total_hours"]} hrs</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if not is_verified:
                with st.expander(f"Upload certificate for: {crs['title'][:50]}…", expanded=False):
                    cert_url = st.text_input(
                        "Certificate URL (e.g. Coursera, LinkedIn Learning URL)",
                        key=f"pf_cert_url_{cid}",
                        placeholder="https://coursera.org/verify/...",
                        label_visibility="visible",
                    )
                    if st.button("✓ Verify Certificate", key=f"pf_cert_btn_{cid}",
                                 disabled=not (cert_url or "").strip(), type="primary"):
                        ok = verify_user_skill(st.session_state["session_id"],
                                               crs["title"], cert_url.strip())
                        if ok:
                            _cert_states[cid] = {"url": cert_url.strip(), "verified": True}
                            st.session_state["pf_cert_states"] = _cert_states
                            st.success(f"✓ Verified: {crs['title']}")
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Run the analysis to see recommended courses and certificate verification here.")

    # ── Bottom actions ─────────────────────────────────────────────────────
    st.markdown('<div class="pf-step-cta-wrap">', unsafe_allow_html=True)
    if st.button("↺  Run a New Analysis", key="pf_new_analysis"):
        st.session_state["pf_step"] = "upload"
        st.session_state["analysis_result"] = None
        st.session_state["analysis_error"] = None
        st.session_state["pf_cert_states"] = {}
        st.session_state["pf_selected_match"] = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif PF_STEP == "skill_gap":
    _render_skill_gap()

elif PF_STEP == "choose_plan":
    _render_choose_plan()

elif PF_STEP == "roadmap":
    _render_roadmap()

elif PF_STEP == "dashboard":
    _render_dashboard()

else:
    # Unknown step — fall back to landing
    st.session_state["pf_step"] = "landing"
    st.rerun()
