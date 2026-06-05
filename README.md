# Pathfinder — AI-Powered Career Mapping Platform

Pathfinder is a SaaS career mapping platform powered by AI that helps users discover the right profession based on their current skills, then guides them to build missing skills through a standardized learning roadmap (O*NET + SKKNI) until they are job-ready.

## Features

- **AI Skill Matching** — Analyzes CV/profile against 1,000+ O*NET professions
- **Skill Gap Analysis** — Visual map of owned vs. missing skills
- **Personalized Roadmap** — Curated learning path with certified courses
- **Progress Dashboard** — Track learning progress and certificate uploads
- **Adaptive Scheduling** — Roadmap duration adjusts to daily study hours

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (embedded in Streamlit)
- **Backend**: Python 3.11+, Streamlit
- **Standards**: O*NET, SKKNI

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed on [Streamlit Cloud](https://streamlit.io/cloud) from this repository.

## Project Structure

```
├── app.py                  # Main Streamlit application
├── assets/
│   ├── styles.css          # Global CSS design system
│   └── script.js           # Navigation & interactions
├── pages/                  # Additional Streamlit pages (reserved)
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── requirements.txt
```

---

*Built for IBC 2026 — Indonesia Business Competition*
