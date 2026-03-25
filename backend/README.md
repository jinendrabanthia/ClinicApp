# TriageAID — Backend

Flask-based REST API for the Rural Clinic Intelligent Patient Triage System.

## Folder Overview

```
backend/
├── app.py            ← Flask entry point + all API routes
├── triage_agent.py   ← Gemini AI triage logic
├── mailer.py         ← Email alert helpers (SMTP/Gmail)
├── notify.py         ← Medication & appointment reminders
├── excel_log.py      ← Waiting-list Excel persistence
├── symptom_guide.py  ← Symptom knowledge base
├── requirements.txt
├── Procfile          ← Gunicorn config for deployment
├── .env.example      ← Copy to .env and fill in secrets
└── .gitignore
```

## Quick Start

```bash
# 1. Create & activate virtual environment (from project root)
python -m venv ../.venv
../.venv/Scripts/activate   # Windows
# source ../.venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
copy .env.example .env      # Windows
# cp .env.example .env      # Mac/Linux
# → fill in GEMINI_API_KEY, SMTP_*, DOCTOR_EMAIL

# 4. Run development server
python app.py
# → http://localhost:5000
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Serve frontend index page |
| GET | `/intake` | Patient intake form |
| GET | `/results` | Triage results page |
| GET | `/admin` | Admin waiting list panel |
| GET | `/doctor-login` | Doctor authentication |
| GET | `/doctor-dashboard` | Doctor dashboard |
| GET | `/doctor-discovery` | Location-based doctor search |
| POST | `/api/triage` | Run AI triage on patient data |
| GET | `/api/waiting-list` | Fetch all waiting-list entries |
| POST | `/api/notify` | Send medication/appointment reminder |
| POST | `/api/notify/triage-confirm` | Email triage confirmation |
| GET | `/api/health` | Health check |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SMTP_HOST` | SMTP server (default: smtp.gmail.com) |
| `SMTP_PORT` | SMTP port (default: 587) |
| `SMTP_USER` | Gmail address used to send emails |
| `SMTP_PASS` | Gmail app password |
| `DOCTOR_EMAIL` | On-call doctor email for critical alerts |
| `PATIENT_FROM_EMAIL` | From-address for patient emails |

## Deployment (Heroku / Render)

```bash
# Gunicorn is already configured in Procfile
git push heroku main
```
