"""
Email alert utilities for the Patient Triage System.
Sends critical alerts to doctors and confirmations to patients.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def get_smtp_config():
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", 587)),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASS", ""),
        "from_email": os.environ.get("PATIENT_FROM_EMAIL", ""),
        "doctor_email": os.environ.get("DOCTOR_EMAIL", ""),
    }


def send_email(to_email: str, subject: str, html_body: str) -> dict:
    """Send an HTML email via SMTP. Returns {'success': bool, 'error': str}"""
    cfg = get_smtp_config()
    if not cfg["user"] or not cfg["password"]:
        return {"success": False, "error": "SMTP credentials not configured"}

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["from_email"] or cfg["user"]
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(msg["From"], to_email, msg.as_string())
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_critical_alert(patient_data: dict, triage_result: dict) -> dict:
    """Send an urgent alert email to the doctor for critical/urgent cases."""
    cfg = get_smtp_config()
    doctor_email = cfg["doctor_email"]
    if not doctor_email:
        return {"success": False, "error": "Doctor email not configured"}

    level = triage_result.get("level", "CRITICAL")
    color = "#dc2626" if level == "CRITICAL" else "#ea580c"
    level_label = "🚨 CRITICAL EMERGENCY" if level == "CRITICAL" else "⚠️ URGENT CASE"
    ts = datetime.now().strftime("%d %b %Y, %I:%M %p")

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#0f0f1a;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f1a;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;overflow:hidden;border:1px solid {color};">
        
        <!-- Header -->
        <tr><td style="background:{color};padding:24px 32px;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">🏥</div>
          <h1 style="margin:0;color:#fff;font-size:22px;font-weight:700;">{level_label}</h1>
          <p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:13px;">Rural Health Clinic Triage System · {ts}</p>
        </td></tr>
        
        <!-- Patient Info -->
        <tr><td style="padding:28px 32px;">
          <h2 style="color:#e2e8f0;font-size:16px;margin:0 0 16px;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:10px;">Patient Information</h2>
          <table width="100%" cellpadding="6" cellspacing="0">
            <tr><td style="color:#94a3b8;width:140px;">Name</td><td style="color:#f1f5f9;font-weight:600;">{patient_data.get('name','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Age / Gender</td><td style="color:#f1f5f9;">{patient_data.get('age','N/A')} yrs / {patient_data.get('gender','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Contact</td><td style="color:#f1f5f9;">{patient_data.get('phone','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Chief Complaint</td><td style="color:#f1f5f9;font-weight:600;">{patient_data.get('symptoms','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Duration</td><td style="color:#f1f5f9;">{patient_data.get('duration','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Pain Scale</td><td style="color:#f1f5f9;">{patient_data.get('pain_scale','N/A')} / 10</td></tr>
            <tr><td style="color:#94a3b8;">Consciousness</td><td style="color:#f1f5f9;">{patient_data.get('consciousness','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Medical History</td><td style="color:#f1f5f9;">{patient_data.get('medical_history','None')}</td></tr>
            <tr><td style="color:#94a3b8;">Medications</td><td style="color:#f1f5f9;">{patient_data.get('medications','None')}</td></tr>
            <tr><td style="color:#94a3b8;">Allergies</td><td style="color:#f1f5f9;">{patient_data.get('allergies','None')}</td></tr>
          </table>
        </td></tr>
        
        <!-- AI Assessment -->
        <tr><td style="padding:0 32px 28px;">
          <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:20px;border-left:4px solid {color};">
            <h3 style="color:{color};margin:0 0 12px;font-size:14px;text-transform:uppercase;letter-spacing:1px;">AI Triage Assessment</h3>
            <p style="color:#cbd5e1;margin:0 0 12px;line-height:1.7;">{triage_result.get('reasoning','')}</p>
            <p style="color:#94a3b8;margin:0;font-size:13px;"><strong style="color:#e2e8f0;">Recommended Action:</strong> {triage_result.get('recommendations','')}</p>
          </div>
        </td></tr>
        
        <!-- Footer -->
        <tr><td style="background:rgba(0,0,0,0.3);padding:16px 32px;text-align:center;">
          <p style="color:#475569;margin:0;font-size:12px;">Rural Health Clinic · Intelligent Triage System · This is an automated alert</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""
    subject = f"[{level}] Triage Alert – {patient_data.get('name','Patient')} ({ts})"
    return send_email(doctor_email, subject, html)


def send_routine_confirmation(patient_data: dict, ticket_number: str, triage_result: dict) -> dict:
    """Send a confirmation email to the patient with their ticket number."""
    patient_email = patient_data.get("email", "")
    if not patient_email:
        return {"success": False, "error": "No patient email provided"}

    ts = datetime.now().strftime("%d %b %Y, %I:%M %p")
    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#0f0f1a;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f1a;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;overflow:hidden;border:1px solid rgba(16,185,129,0.4);">
        
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#059669,#10b981);padding:28px 32px;text-align:center;">
          <div style="font-size:40px;margin-bottom:10px;">✅</div>
          <h1 style="margin:0;color:#fff;font-size:22px;">Registration Confirmed</h1>
          <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:13px;">Rural Health Clinic · {ts}</p>
        </td></tr>
        
        <!-- Ticket -->
        <tr><td style="padding:28px 32px;text-align:center;">
          <p style="color:#94a3b8;margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:1px;">Your Ticket Number</p>
          <div style="background:rgba(16,185,129,0.15);border:2px solid #10b981;border-radius:12px;padding:20px;display:inline-block;width:80%;margin:0 auto;">
            <div style="color:#10b981;font-size:32px;font-weight:700;letter-spacing:4px;">{ticket_number}</div>
          </div>
          <p style="color:#64748b;margin:12px 0 0;font-size:13px;">Please show this number at the clinic counter</p>
        </td></tr>
        
        <!-- Patient Details -->
        <tr><td style="padding:0 32px 24px;">
          <table width="100%" cellpadding="6" cellspacing="0" style="background:rgba(255,255,255,0.04);border-radius:10px;padding:16px;">
            <tr><td style="color:#94a3b8;width:140px;">Patient</td><td style="color:#f1f5f9;font-weight:600;">{patient_data.get('name','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Symptoms</td><td style="color:#f1f5f9;">{patient_data.get('symptoms','N/A')}</td></tr>
            <tr><td style="color:#94a3b8;">Triage Level</td><td style="color:#10b981;font-weight:600;">ROUTINE – Regular Queue</td></tr>
          </table>
        </td></tr>
        
        <!-- Advice -->
        <tr><td style="padding:0 32px 28px;">
          <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:20px;border-left:4px solid #10b981;">
            <h3 style="color:#10b981;margin:0 0 10px;font-size:13px;text-transform:uppercase;letter-spacing:1px;">Care Recommendations</h3>
            <p style="color:#cbd5e1;margin:0;line-height:1.7;">{triage_result.get('recommendations','Rest and stay hydrated. You will be seen by a doctor shortly.')}</p>
          </div>
        </td></tr>
        
        <!-- Footer -->
        <tr><td style="background:rgba(0,0,0,0.3);padding:16px 32px;text-align:center;">
          <p style="color:#475569;margin:0;font-size:12px;">⚠️ If your condition worsens, please inform the staff immediately.</p>
          <p style="color:#475569;margin:6px 0 0;font-size:12px;">Rural Health Clinic · Intelligent Triage System</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""
    subject = f"Clinic Registration Confirmed – Ticket {ticket_number}"
    return send_email(patient_email, subject, html)
