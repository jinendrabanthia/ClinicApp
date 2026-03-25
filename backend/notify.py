"""
notify.py — Patient Notification System for TriageAID
Handles medication reminders and appointment reminders via Gmail SMTP.
"""

import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an HTML email. Returns True on success."""
    if not SMTP_PASS or not SMTP_USER:
        print(f"[notify] SMTP not configured — skipping email to {to_email}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"TriageAID <{SMTP_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"[notify] Email sent → {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"[notify] Email error: {e}")
        return False


def _html_template(patient_name: str, headline: str, body_html: str, color: str = "#0891b2") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f8fafc;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:30px 16px;">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.1);">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,{color},{'#4f46e5'});padding:28px 32px;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">🏥</div>
          <div style="color:#fff;font-size:22px;font-weight:700;">TriageAID</div>
          <div style="color:rgba(255,255,255,.8);font-size:13px;">Rural Health Clinic — Patient Notification</div>
        </td></tr>
        <!-- Body -->
        <tr><td style="padding:32px;">
          <div style="font-size:20px;font-weight:700;color:#0f172a;margin-bottom:8px;">{headline}</div>
          <div style="font-size:14px;color:#475569;margin-bottom:20px;">Dear <strong>{patient_name}</strong>,</div>
          {body_html}
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
          <div style="font-size:12px;color:#94a3b8;text-align:center;">
            ⚕️ This is an automated reminder from TriageAID.<br/>
            For emergencies, call <strong>108</strong>.
          </div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def send_medication_reminder(patient_name: str, email: str, medications: list, schedule: str, ticket: str) -> bool:
    """
    Send a medication reminder email to the patient.
    medications: list of dicts with keys: name, dose, frequency, duration
    schedule: human-readable time info e.g. "Morning (8 AM), Night (9 PM)"
    """
    med_rows = "".join([
        f"""<tr>
          <td style="padding:10px 12px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#0f172a;">{m.get('name','—')}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f1f5f9;color:#475569;">{m.get('dose','—')}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f1f5f9;color:#475569;">{m.get('frequency','Once Daily')}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f1f5f9;color:#475569;">{m.get('duration','—')} day(s)</td>
        </tr>"""
        for m in medications
    ])
    body = f"""
    <div style="background:#ecfeff;border:1px solid #a5f3fc;border-radius:10px;padding:14px 18px;margin-bottom:20px;">
      <div style="font-size:13px;font-weight:700;color:#0e7490;margin-bottom:4px;">💊 Medication Schedule</div>
      <div style="font-size:13px;color:#164e63;">Take your medicines as prescribed. Skipping doses can delay recovery.</div>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:20px;">
      <thead>
        <tr style="background:#0f172a;">
          <th style="padding:10px 12px;color:#fff;font-size:12px;text-align:left;">Medicine</th>
          <th style="padding:10px 12px;color:#fff;font-size:12px;text-align:left;">Dose</th>
          <th style="padding:10px 12px;color:#fff;font-size:12px;text-align:left;">Frequency</th>
          <th style="padding:10px 12px;color:#fff;font-size:12px;text-align:left;">Duration</th>
        </tr>
      </thead>
      <tbody>{med_rows}</tbody>
    </table>
    <div style="font-size:13px;color:#475569;"><strong>Reminder Times:</strong> {schedule}</div>
    <div style="margin-top:8px;font-size:13px;color:#475569;"><strong>Ticket No.:</strong> {ticket}</div>
    """
    html = _html_template(patient_name, "💊 Medication Reminder", body, color="#0891b2")
    return _send_email(email, f"[TriageAID] Medication Reminder — {patient_name}", html)


def send_appointment_reminder(patient_name: str, email: str, appointment_date: str,
                               appointment_time: str, clinic_name: str, ticket: str, notes: str = "") -> bool:
    """Send an appointment reminder to the patient."""
    body = f"""
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px 20px;margin-bottom:20px;">
      <div style="font-size:22px;font-weight:800;color:#15803d;margin-bottom:4px;">📅 {appointment_date} at {appointment_time}</div>
      <div style="font-size:14px;color:#166534;">Please arrive 10 minutes early for registration.</div>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:20px;">
      <tr><td style="padding:10px 16px;background:#f8fafc;font-weight:600;color:#475569;font-size:13px;width:35%;">Clinic</td>
          <td style="padding:10px 16px;color:#0f172a;font-size:13px;">{clinic_name}</td></tr>
      <tr><td style="padding:10px 16px;background:#f8fafc;font-weight:600;color:#475569;font-size:13px;">Ticket No.</td>
          <td style="padding:10px 16px;color:#0891b2;font-size:13px;font-weight:700;">{ticket}</td></tr>
      {'<tr><td style="padding:10px 16px;background:#f8fafc;font-weight:600;color:#475569;font-size:13px;">Notes</td><td style="padding:10px 16px;color:#0f172a;font-size:13px;">' + notes + '</td></tr>' if notes else ''}
    </table>
    <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:12px 16px;font-size:13px;color:#92400e;">
      ⚠️ If you are unable to attend, please contact the clinic as soon as possible.
    </div>
    """
    html = _html_template(patient_name, "📅 Appointment Reminder", body, color="#16a34a")
    return _send_email(email, f"[TriageAID] Appointment Reminder — {appointment_date}", html)


def send_triage_confirmation(patient_name: str, email: str, level: str, ticket: str,
                              recommended_action: str, urgency_note: str) -> bool:
    """Send patient their triage result confirmation with urgency note."""
    colors = {"CRITICAL": "#dc2626", "URGENT": "#ea580c", "ROUTINE": "#16a34a"}
    color = colors.get(level, "#0891b2")
    icons = {"CRITICAL": "🚨", "URGENT": "⚠️", "ROUTINE": "✅"}
    icon = icons.get(level, "📋")

    body = f"""
    <div style="text-align:center;padding:20px;background:{'#fef2f2' if level=='CRITICAL' else '#fff7ed' if level=='URGENT' else '#f0fdf4'};border-radius:12px;margin-bottom:20px;">
      <div style="font-size:48px;margin-bottom:8px;">{icon}</div>
      <div style="font-size:24px;font-weight:800;color:{color};">{level}</div>
      <div style="font-size:13px;color:#64748b;margin-top:4px;">{urgency_note}</div>
    </div>
    <div style="font-size:14px;color:#0f172a;background:#f8fafc;border-radius:10px;padding:14px 18px;margin-bottom:16px;">
      <strong>Recommended Action:</strong><br/>{recommended_action}
    </div>
    <div style="font-size:13px;color:#64748b;">Your ticket number: <strong style="color:#0891b2;">{ticket}</strong></div>
    """
    html = _html_template(patient_name, f"{icon} Your Triage Result: {level}", body, color=color)
    return _send_email(email, f"[TriageAID] Triage Result — {level} | Ticket {ticket}", html)
