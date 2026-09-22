"""
Flask application for the Rural Clinic Intelligent Patient Triage System.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Import modules
from triage_agent import triage_patient
from mailer import send_critical_alert, send_routine_confirmation
from excel_log import add_to_waiting_list, get_waiting_list
from notify import send_medication_reminder, send_appointment_reminder, send_triage_confirmation

app = Flask(__name__, static_folder="../frontend/static", static_url_path="")
CORS(app)


# ─── Serve Frontend ─────────────────────────────────────────────────────────

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


# ─── API Routes ──────────────────────────────────────────────────────────────

@app.route("/api/triage", methods=["POST"])
def api_triage():
    """
    POST /api/triage
    Body: patient data JSON
    Returns: triage result
    """
    try:
        patient_data = request.get_json()
        if not patient_data:
            return jsonify({"error": "No patient data provided"}), 400

        # Required fields check
        required = ["name", "age", "symptoms"]
        missing = [f for f in required if not patient_data.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Run AI triage
        result = triage_patient(patient_data)
        level = result["level"]

        # Handle based on level
        actions = {}

        if level in ("CRITICAL", "URGENT"):
            # Send alert to doctor
            alert = send_critical_alert(patient_data, result)
            actions["doctor_alert"] = alert
            actions["ticket_number"] = None

        if level == "ROUTINE":
            # Log to Excel
            log = add_to_waiting_list(patient_data, result)
            actions["waiting_list"] = log
            actions["ticket_number"] = log.get("ticket_number")

            # Send confirmation to patient if email provided
            if patient_data.get("email"):
                conf = send_routine_confirmation(patient_data, log.get("ticket_number", ""), result)
                actions["patient_confirmation"] = conf

        if level == "URGENT":
            # Also add to Excel with URGENT flag
            log = add_to_waiting_list(patient_data, result)
            actions["waiting_list"] = log
            actions["ticket_number"] = log.get("ticket_number")

        return jsonify({
            "success": True,
            "triage": result,
            "actions": actions,
            "patient_data": patient_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/waiting-list", methods=["GET"])
def api_waiting_list():
    """GET /api/waiting-list — Return all entries in the waiting list."""
    try:
        rows = get_waiting_list()
        return jsonify({"success": True, "count": len(rows), "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notify", methods=["POST"])
def api_notify():
    """
    POST /api/notify
    Send a medication or appointment reminder to a patient via email.
    Body: {
      type: "medication_reminder" | "appointment_reminder",
      patient_name, email, ticket,
      -- medication_reminder: medications (list), schedule (str)
      -- appointment_reminder: appointment_date, appointment_time, clinic_name, notes
    }
    """
    try:
        body = request.get_json()
        if not body:
            return jsonify({"error": "No data provided"}), 400

        ntype   = body.get("type", "")
        name    = body.get("patient_name", "Patient")
        email   = body.get("email", "")
        ticket  = body.get("ticket", "N/A")

        if not email:
            return jsonify({"error": "Email address required"}), 400

        if ntype == "medication_reminder":
            meds     = body.get("medications", [])
            schedule = body.get("schedule", "As prescribed")
            ok = send_medication_reminder(name, email, meds, schedule, ticket)
            return jsonify({"success": ok, "type": ntype, "sent_to": email})

        elif ntype == "appointment_reminder":
            ok = send_appointment_reminder(
                patient_name    = name,
                email           = email,
                appointment_date= body.get("appointment_date", ""),
                appointment_time= body.get("appointment_time", ""),
                clinic_name     = body.get("clinic_name", "Rural Health Centre"),
                ticket          = ticket,
                notes           = body.get("notes", "")
            )
            return jsonify({"success": ok, "type": ntype, "sent_to": email})

        else:
            return jsonify({"error": f"Unknown notification type: {ntype}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notify/triage-confirm", methods=["POST"])
def api_notify_triage_confirm():
    """POST /api/notify/triage-confirm — Email triage result confirmation to patient."""
    try:
        body = request.get_json()
        ok = send_triage_confirmation(
            patient_name     = body.get("patient_name", "Patient"),
            email            = body.get("email", ""),
            level            = body.get("level", "ROUTINE"),
            ticket           = body.get("ticket", ""),
            recommended_action=body.get("recommended_action", "Please see a doctor."),
            urgency_note     = body.get("urgency_note", "")
        )
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "TriageAID"})


# ─── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  [+]  TriageAID - Rural Clinic Triage System")
    print("=" * 60)
    print(f"  Running at: http://localhost:5000")
    print(f"  Admin Panel: http://localhost:5000/admin")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
