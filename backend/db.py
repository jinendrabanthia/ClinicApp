"""
Supabase database layer for TriageAID.
Replaces the previous SQLite/clinic.db implementation.
Uses the supabase-py client with the service role key so it bypasses RLS.
"""

import os
import json
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# The SUPABASE_SERVICE_KEY in .env is a valid JWT service role key.
# Fall back to anon key if service key not available.
_API_KEY = SUPABASE_SERVICE_KEY if (SUPABASE_SERVICE_KEY and SUPABASE_SERVICE_KEY.startswith("eyJ")) else SUPABASE_ANON_KEY
_supabase: Client = create_client(SUPABASE_URL, _API_KEY)


def get_supabase() -> Client:
    return _supabase


# ─── Doctors ─────────────────────────────────────────────────

def get_doctor_by_id(uid: str) -> dict | None:
    res = _supabase.table("doctors").select("*").eq("id", uid).single().execute()
    return res.data if res.data else None


def get_doctor_by_email(email: str) -> dict | None:
    res = _supabase.table("doctors").select("*").eq("email", email).maybe_single().execute()
    return res.data if res.data else None


def get_all_doctors() -> list:
    res = _supabase.table("doctors").select(
        "id, name, email, specialization, clinic, pincode, fee, upi, is_approved"
    ).execute()
    return res.data or []


def update_doctor_profile(uid: str, updates: dict):
    _supabase.table("doctors").update(updates).eq("id", uid).execute()


# ─── Waiting List ─────────────────────────────────────────────

def _generate_ticket(today_str: str) -> str:
    """Generate unique daily ticket like RHC-20241001-0001."""
    res = _supabase.table("waiting_list").select("ticket_number").eq("date", today_str).execute()
    count = len(res.data) if res.data else 0
    compact = today_str.replace("-", "")
    return f"RHC-{compact}-{count + 1:04d}"


def add_to_waiting_list(patient_data: dict, triage_result: dict) -> dict:
    """Insert a new patient into the Supabase waiting_list table."""
    try:
        today = date.today().isoformat()
        ticket = _generate_ticket(today)
        now = datetime.now()
        level = triage_result.get("level", "ROUTINE")

        row = {
            "ticket_number": ticket,
            "patient_name": patient_data.get("name", ""),
            "age": patient_data.get("age"),
            "gender": patient_data.get("gender", ""),
            "phone": patient_data.get("phone", ""),
            "email": patient_data.get("email", ""),
            "symptoms": patient_data.get("symptoms", ""),
            "duration": patient_data.get("duration", ""),
            "pain_scale": patient_data.get("pain_scale"),
            "consciousness": patient_data.get("consciousness", ""),
            "medical_history": patient_data.get("medical_history", ""),
            "medications": patient_data.get("medications", ""),
            "allergies": patient_data.get("allergies", ""),
            "triage_level": level,
            "ai_reasoning": triage_result.get("reasoning", ""),
            "recommendations": triage_result.get("recommendations", ""),
            "date": today,
        }

        _supabase.table("waiting_list").insert(row).execute()
        return {"success": True, "ticket_number": ticket, "error": None}

    except Exception as e:
        return {"success": False, "ticket_number": None, "error": str(e)}


def get_waiting_list(today_only: bool = True) -> list:
    """
    Return waiting list rows formatted with the same keys as the old Excel system
    so existing frontend code keeps working.
    If today_only=True, only return today's queue.
    """
    try:
        query = _supabase.table("waiting_list").select("*").order("created_at", desc=False)
        if today_only:
            query = query.eq("date", date.today().isoformat())
        res = query.execute()
        rows = res.data or []

        # Map DB column names → old Excel HEADERS keys for backward compat
        def _fmt(r: dict) -> dict:
            ts = r.get("created_at", "")
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                time_str = dt.strftime("%I:%M %p")
            except Exception:
                time_str = ""

            # Use the local date stored by the server rather than UTC timestamp
            raw_date = r.get("date", "")
            if raw_date and "-" in raw_date:
                try:
                    # convert YYYY-MM-DD to DD-MM-YYYY for frontend compat
                    parts = raw_date.split("-")
                    if len(parts[0]) == 4:
                        date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    else:
                        date_str = raw_date
                except Exception:
                    date_str = raw_date
            else:
                try:
                    date_str = dt.strftime("%d-%m-%Y")
                except Exception:
                    date_str = ""

            return {
                "Ticket No.": r.get("ticket_number", ""),
                "Date": date_str,
                "Time": time_str,
                "Patient Name": r.get("patient_name", ""),
                "Age": r.get("age", ""),
                "Gender": r.get("gender", ""),
                "Phone": r.get("phone", ""),
                "Email": r.get("email", ""),
                "Chief Complaint": r.get("symptoms", ""),
                "Duration": r.get("duration", ""),
                "Pain Scale": r.get("pain_scale", ""),
                "Consciousness": r.get("consciousness", ""),
                "Medical History": r.get("medical_history", ""),
                "Medications": r.get("medications", ""),
                "Allergies": r.get("allergies", ""),
                "Triage Level": r.get("triage_level", ""),
                "AI Reasoning": r.get("ai_reasoning", ""),
                "Recommendations": r.get("recommendations", ""),
            }

        return [_fmt(r) for r in rows]
    except Exception:
        return []


def get_all_waiting_list_history() -> list:
    """Return ALL patient records (all dates) — used for history/archive view."""
    return get_waiting_list(today_only=False)


# ─── Prescriptions ────────────────────────────────────────────

def save_prescription(ticket_number: str, patient_name: str, medicines, advice: str, status: str = "COMPLETED"):
    meds = medicines if isinstance(medicines, list) else []
    row = {
        "ticket_number": ticket_number,
        "patient_name": patient_name,
        "medicines_json": meds,
        "advice": advice,
        "status": status,
    }
    # Upsert: insert or update on conflict
    _supabase.table("prescriptions").upsert(row, on_conflict="ticket_number").execute()


def get_prescription(ticket_number: str) -> dict | None:
    res = _supabase.table("prescriptions").select("*").eq("ticket_number", ticket_number).maybe_single().execute()
    if res.data:
        d = dict(res.data)
        d["medicines"] = d.get("medicines_json") or []
        return d
    return None


def get_all_prescriptions() -> dict:
    """Return dict keyed by ticket_number — same interface as old SQLite version."""
    res = _supabase.table("prescriptions").select("*").order("created_at", desc=True).execute()
    result = {}
    for r in (res.data or []):
        d = dict(r)
        d["medicines"] = d.get("medicines_json") or []
        result[d["ticket_number"]] = d
    return result
