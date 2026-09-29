"""
Flask application for the Rural Clinic Intelligent Patient Triage System.
Auth: Supabase (email + Google OAuth). Storage: Supabase PostgreSQL.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Import modules
from triage_agent import triage_patient
from mailer import send_critical_alert, send_routine_confirmation
from notify import send_medication_reminder, send_appointment_reminder, send_triage_confirmation
from db import (
    add_to_waiting_list, get_waiting_list, get_all_waiting_list_history,
    save_prescription, get_prescription, get_all_prescriptions,
    get_all_doctors, update_doctor_profile, get_supabase
)

app = Flask(__name__, static_folder="../frontend/static", static_url_path="")
CORS(app)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


# ─── Auth Helpers ────────────────────────────────────────────

def _verify_supabase_token(token: str) -> dict | None:
    """
    Verify a Supabase JWT access token server-side.
    Returns the user dict or None if invalid.
    """
    if not token:
        return None
    try:
        sb = get_supabase()
        # get_user() validates the JWT against Supabase auth server
        res = sb.auth.get_user(token)
        return res.user.__dict__ if res.user else None
    except Exception:
        return None


def _require_auth(req):
    """
    Extract and verify Bearer token from request headers.
    Returns (user_dict, None) on success or (None, error_response) on failure.
    """
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    token = auth_header[7:]
    user = _verify_supabase_token(token)
    if not user:
        return None, (jsonify({"error": "Invalid or expired session"}), 401)
    return user, None


# ─── Serve Frontend ──────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/intake")
def intake():
    return send_from_directory(app.static_folder, "intake.html")

@app.route("/results")
def results():
    return send_from_directory(app.static_folder, "results.html")

@app.route("/admin")
def admin():
    return send_from_directory(app.static_folder, "admin.html")

@app.route("/doctor-login")
def doctor_login():
    return send_from_directory(app.static_folder, "doctor-login.html")

@app.route("/doctor-dashboard")
def doctor_dashboard():
    return send_from_directory(app.static_folder, "doctor-dashboard.html")

@app.route("/prescription-demo")
def prescription_demo():
    return send_from_directory(app.static_folder, "prescription-demo.html")

@app.route("/prescription-print")
def prescription_print():
    return send_from_directory(app.static_folder, "prescription-print.html")

@app.route("/doctor-discovery")
def doctor_discovery():
    return send_from_directory(app.static_folder, "doctor-discovery.html")


# ─── Auth API ────────────────────────────────────────────────

@app.route("/api/auth/config", methods=["GET"])
def api_auth_config():
    """Return public Supabase config for frontend JS client — no secrets here."""
    return jsonify({
        "supabase_url": SUPABASE_URL,
        "supabase_anon_key": SUPABASE_ANON_KEY,
    })


@app.route("/api/auth/verify", methods=["POST"])
def api_auth_verify():
    """
    POST /api/auth/verify
    Body: { "access_token": "<jwt>" }
    Returns doctor profile if token is valid.
    """
    try:
        body = request.get_json() or {}
        token = body.get("access_token", "")
        user = _verify_supabase_token(token)
        if not user:
            return jsonify({"success": False, "error": "Invalid session"}), 401

        uid = user.get("id") or getattr(user, "id", None)
        email = user.get("email") or ""
        # Look up extra profile in doctors table
        from db import get_doctor_by_id
        profile = get_doctor_by_id(uid)
        return jsonify({"success": True, "user": {"id": uid, "email": email, "profile": profile}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Triage API ──────────────────────────────────────────────

@app.route("/api/triage", methods=["POST"])
def api_triage():
    """POST /api/triage — Run AI triage on submitted patient data."""
    try:
        patient_data = request.get_json()
        if not patient_data:
            return jsonify({"error": "No patient data provided"}), 400

        required = ["name", "age", "symptoms"]
        missing = [f for f in required if not patient_data.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        result = triage_patient(patient_data)
        level = result["level"]
        actions = {}

        if level in ("CRITICAL", "URGENT"):
            alert = send_critical_alert(patient_data, result)
            actions["doctor_alert"] = alert
            actions["ticket_number"] = None

        if level in ("ROUTINE", "URGENT"):
            log = add_to_waiting_list(patient_data, result)
            actions["waiting_list"] = log
            actions["ticket_number"] = log.get("ticket_number")
            if patient_data.get("email"):
                conf = send_routine_confirmation(patient_data, log.get("ticket_number", ""), result)
                actions["patient_confirmation"] = conf

        return jsonify({"success": True, "triage": result, "actions": actions, "patient_data": patient_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Waiting List API ────────────────────────────────────────

@app.route("/api/waiting-list", methods=["GET"])
def api_waiting_list():
    """GET /api/waiting-list — Today's queue only (resets daily)."""
    try:
        rows = get_waiting_list(today_only=True)
        return jsonify({"success": True, "count": len(rows), "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Prescription API ────────────────────────────────────────

@app.route("/api/prescription", methods=["POST"])
def api_save_prescription():
    """POST /api/prescription — Save digital prescription to Supabase."""
    try:
        body = request.get_json() or {}
        ticket = body.get("ticket_number") or body.get("ticket")
        name = body.get("patient_name", "Patient")
        medicines = body.get("medicines", [])
        advice = body.get("advice", "")
        status = body.get("status", "COMPLETED")
        if not ticket:
            return jsonify({"error": "Ticket number required"}), 400
        save_prescription(ticket, name, medicines, advice, status)
        return jsonify({"success": True, "ticket_number": ticket})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/prescriptions", methods=["GET"])
def api_get_prescriptions():
    """GET /api/prescriptions — All prescriptions from Supabase."""
    try:
        data = get_all_prescriptions()
        return jsonify({"success": True, "prescriptions": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Patient History API ─────────────────────────────────────

@app.route("/api/patient-history", methods=["GET"])
def api_patient_history():
    """GET /api/patient-history — All patients (all dates) + prescriptions."""
    try:
        rows = get_all_waiting_list_history()
        prescriptions = get_all_prescriptions()
        history = []
        for r in rows:
            ticket = r.get("Ticket No.", "")
            item = dict(r)
            item["prescription"] = prescriptions.get(ticket)
            history.append(item)
        return jsonify({"success": True, "count": len(history), "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Doctor Profile API ──────────────────────────────────────

@app.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    """GET /api/doctors — List all approved doctors (for discovery page)."""
    try:
        doctors = get_all_doctors()
        approved = [d for d in doctors if d.get("is_approved")]
        return jsonify({"success": True, "doctors": approved})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/doctor/profile", methods=["PATCH"])
def api_update_doctor_profile():
    """PATCH /api/doctor/profile — Authenticated doctor updates their profile."""
    user, err = _require_auth(request)
    if err:
        return err
    try:
        body = request.get_json() or {}
        uid = user.get("id") or getattr(user, "id", None)
        allowed = ["name", "specialization", "license", "clinic", "pincode", "fee", "upi"]
        updates = {k: v for k, v in body.items() if k in allowed}
        if updates:
            update_doctor_profile(uid, updates)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Notifications API ───────────────────────────────────────

@app.route("/api/notify", methods=["POST"])
def api_notify():
    """POST /api/notify — Send medication or appointment reminder email."""
    try:
        body = request.get_json()
        if not body:
            return jsonify({"error": "No data provided"}), 400

        ntype = body.get("type", "")
        name = body.get("patient_name", "Patient")
        email = body.get("email", "")
        ticket = body.get("ticket", "N/A")

        if not email:
            return jsonify({"error": "Email address required"}), 400

        if ntype == "medication_reminder":
            meds = body.get("medications", [])
            schedule = body.get("schedule", "As prescribed")
            ok = send_medication_reminder(name, email, meds, schedule, ticket)
            return jsonify({"success": ok, "type": ntype, "sent_to": email})

        elif ntype == "appointment_reminder":
            ok = send_appointment_reminder(
                patient_name=name, email=email,
                appointment_date=body.get("appointment_date", ""),
                appointment_time=body.get("appointment_time", ""),
                clinic_name=body.get("clinic_name", "Rural Health Centre"),
                ticket=ticket, notes=body.get("notes", "")
            )
            return jsonify({"success": ok, "type": ntype, "sent_to": email})

        return jsonify({"error": f"Unknown notification type: {ntype}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notify/triage-confirm", methods=["POST"])
def api_notify_triage_confirm():
    """POST /api/notify/triage-confirm — Email triage confirmation to patient."""
    try:
        body = request.get_json()
        ok = send_triage_confirmation(
            patient_name=body.get("patient_name", "Patient"),
            email=body.get("email", ""),
            level=body.get("level", "ROUTINE"),
            ticket=body.get("ticket", ""),
            recommended_action=body.get("recommended_action", "Please see a doctor."),
            urgency_note=body.get("urgency_note", "")
        )
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "TriageAID"})


# ─── Main ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  [+]  TriageAID - Rural Clinic Triage System")
    print("  [DB]  Supabase PostgreSQL")
    print("  [Auth] Supabase Auth (Email + Google)")
    print("=" * 60)
    print(f"  Running at: http://localhost:5000")
    print(f"  Admin Panel: http://localhost:5000/admin")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
