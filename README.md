# 🏥 TriageAID — Intelligent Rural Clinic Triage System

> AI-powered patient triage and prescription management for rural clinics in India.  
> Runs on low-bandwidth networks. Optimised for tablet use.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-1.5_Pro-orange?logo=google)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Triage** | Gemini 1.5 Pro classifies patients as CRITICAL / URGENT / ROUTINE with risk score & confidence |
| 🎙️ **Multi-language STT** | Voice dictation in English, हिन्दी, and ଓଡ଼ିଆ via Web Speech API |
| 💊 **Smart Prescription** | Dynamic medication builder with time (☀️🌤️🌙) and meal (🌿🍽️) frequency toggles |
| 🖨️ **Print Template** | Professional clinical prescription with letterhead, triage strip, vitals, and doctor signatures |
| 📧 **Email Notifications** | Medication reminders, appointment confirmations, and critical doctor alerts via Gmail SMTP |
| 📋 **Waiting List** | Excel-backed patient queue with ticket numbers |
| 🏥 **Doctor Dashboard** | Login, nearby patient filtering, prescription history |
| 📱 **Tablet-optimised UI** | Min 48px touch targets, responsive grid |

---

## 🗂️ Mono-Repo Structure

This repo is split into two independent folders so backend and frontend developers can work without conflicts:

```
TriageAI/
├── backend/    ← Python / Flask API (see backend/README.md)
└── frontend/   ← HTML / JS / images + JSX components (see frontend/README.md)
```

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/jinendrabanthia/ClinicApp.git
cd ClinicApp
```

### 2. Create a virtual environment (from repo root)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
# Inside backend/
copy .env.example .env   # Windows
# cp .env.example .env   # Mac/Linux
```

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key — [get one here](https://aistudio.google.com) |
| `SMTP_HOST` | SMTP server (default: `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (default: `587`) |
| `SMTP_USER` | Gmail address |
| `SMTP_PASS` | Gmail **App Password** (not your main password) |
| `DOCTOR_EMAIL` | Email address for critical alerts |
| `PATIENT_FROM_EMAIL` | Sender address for patient emails |

> **Gmail App Password**: Enable 2FA on your Google account, then generate an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### 5. Run locally
```bash
# from inside backend/
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 📄 Pages

| URL | Description |
|---|---|
| `/` | Patient landing page |
| `/intake` | Full patient intake form |
| `/results` | AI triage results |
| `/prescription-demo` | **Doctor prescription panel** (SmartPrescriptionPanel) |
| `/prescription-print` | Printable clinical prescription |
| `/doctor-login` | Doctor authentication |
| `/doctor-dashboard` | Doctor management panel |
| `/admin` | Admin waiting list panel |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/triage` | Submit patient data, get AI triage result |
| `GET`  | `/api/waiting-list` | Fetch all patients in waiting list |
| `POST` | `/api/notify` | Send medication / appointment reminder |
| `POST` | `/api/notify/triage-confirm` | Send triage confirmation email |
| `GET`  | `/api/health` | Health check |

### Example: Triage Request
```bash
curl -X POST http://localhost:5000/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ramesh Kumar",
    "age": 58,
    "gender": "Male",
    "symptoms": "chest pain, shortness of breath",
    "medical_history": "hypertension",
    "pain_scale": 8
  }'
```

---

## 🗂️ Project Structure

```
TriageAI/
├── backend/                       ← Python developer works here
│   ├── app.py                     # Flask app & all API routes
│   ├── triage_agent.py            # Gemini AI triage logic
│   ├── mailer.py                  # SMTP email helpers
│   ├── notify.py                  # Patient notification helpers
│   ├── excel_log.py               # Excel-based waiting list
│   ├── symptom_guide.py           # Symptom severity reference
│   ├── requirements.txt
│   ├── Procfile                   # Gunicorn / deployment
│   ├── .env.example
│   └── README.md                  ← Backend-specific setup guide
│
├── frontend/                      ← Frontend developer works here
│   ├── static/                    # Served by Flask
│   │   ├── index.html
│   │   ├── intake.html
│   │   ├── results.html
│   │   ├── admin.html
│   │   ├── doctor-login.html
│   │   ├── doctor-dashboard.html
│   │   ├── doctor-discovery.html
│   │   ├── prescription-demo.html
│   │   ├── prescription-print.html
│   │   └── stt.js
│   ├── components/                # React/JSX components
│   │   ├── DoctorDiscovery.jsx
│   │   ├── DoctorRegistration.jsx
│   │   └── SmartPrescriptionPanel.jsx
│   └── README.md                  ← Frontend-specific guide
│
├── .venv/                         # Shared Python virtual env
├── DESIGN.md
└── README.md
```

---

## ☁️ Deployment

### Option A — Render (recommended, free tier)
1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set **Root Directory**: `backend`
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
6. Add all environment variables from `backend/.env` in the Render dashboard

### Option B — Heroku
```bash
heroku create triageaid-clinic
heroku config:set GEMINI_API_KEY=your_key SMTP_USER=... SMTP_PASS=...
git subtree push --prefix backend heroku main
```

### Option C — Railway
```bash
railway login
railway new
railway up
# Set environment variables in Railway dashboard
```

> **Note:** The `waiting-list.xlsx` file is written to disk at runtime. On ephemeral filesystems (Render, Heroku free tier), data resets on each deploy. For production, replace `excel_log.py` with a PostgreSQL or Firebase backend.

---

## 🔒 Security Notes

- Never commit `.env` to version control (it is in `.gitignore`)
- Use Gmail **App Passwords**, not your main password
- The Gemini API key grants billing access — rotate if exposed
- For production: enable HTTPS, use a reverse proxy (nginx), and implement doctor JWT authentication

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3, Flask-CORS |
| AI | Google Gemini 1.5 Pro |
| Frontend | Vanilla HTML/CSS/JS, Tailwind CSS (CDN) |
| React Component | React 18, lucide-react, Web Speech API |
| Email | Gmail SMTP via Python `smtplib` |
| Data | openpyxl (Excel) |
| Deployment | Gunicorn, Render/Heroku/Railway |

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

*Built for rural India. Designed for speed, simplicity, and life-saving accuracy.*
