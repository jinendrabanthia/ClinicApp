# TriageAID — Frontend

All HTML pages, JavaScript, images, and React/JSX components for the TriageAID clinic system.

## Folder Overview

```
frontend/
├── static/                      ← Served directly by Flask backend
│   ├── index.html               ← Landing page
│   ├── intake.html              ← Patient symptom intake form
│   ├── results.html             ← Triage results display
│   ├── admin.html               ← Admin waiting-list panel
│   ├── doctor-login.html        ← Doctor login / registration
│   ├── doctor-dashboard.html    ← Doctor dashboard & prescriptions
│   ├── doctor-discovery.html    ← Location-based doctor search + UPI pay
│   ├── prescription-demo.html   ← Prescription writer demo
│   ├── prescription-print.html  ← Print-ready prescription template
│   ├── stt.js                   ← Multi-language speech-to-text helper
│   ├── hero_doctor.png
│   ├── medical_instruments.png
│   ├── rural_clinic_team.png
│   └── triage_ai_concept.png
│
└── components/                  ← React/JSX component files (reference / future use)
    ├── DoctorDiscovery.jsx
    ├── DoctorRegistration.jsx
    └── SmartPrescriptionPanel.jsx
```

## Development Workflow

### UI-Only (no backend needed)
Open any `static/*.html` file directly in your browser to preview layout and styles.  
API calls will fail without the backend, but static rendering and CSS work fine.

### With Live Backend
1. Start the backend: `cd ../backend && python app.py`
2. All pages are now served at `http://localhost:5000`
3. All API calls (triage, notify, waiting-list) will work

## API Base URL

All `fetch()` / `XMLHttpRequest` calls in the HTML files target:
```
http://localhost:5000/api/...
```
Make sure the backend is running before testing API-dependent features.

## Pages

| File | Route (via backend) | Description |
|------|---------------------|-------------|
| `index.html` | `/` | Landing / home |
| `intake.html` | `/intake` | Patient symptom form |
| `results.html` | `/results` | AI triage result view |
| `admin.html` | `/admin` | Clinic admin dashboard |
| `doctor-login.html` | `/doctor-login` | Doctor auth |
| `doctor-dashboard.html` | `/doctor-dashboard` | Doctor tools |
| `doctor-discovery.html` | `/doctor-discovery` | Find doctors + UPI payment |
| `prescription-demo.html` | `/prescription-demo` | Prescription writer |
| `prescription-print.html` | `/prescription-print` | Print view |
