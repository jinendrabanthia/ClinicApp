"""
triage_agent.py — AI Triage Classification for TriageAID Rural Clinic
Uses Gemini with a highly-calibrated prompt for confident, decisive assessments.
"""

import os
import json
import re
import google.generativeai as genai
from symptom_guide import SYMPTOM_SEVERITY_GUIDE


def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-pro")


# ---------------------------------------------------------------------------
# SYSTEM PROMPT — Highly structured for decisive, high-confidence outputs
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = f"""You are TriageAID, an expert AI medical triage system for rural clinics in India.
You have years of clinical triage experience equivalent to a senior emergency medicine physician.
You MUST give decisive, confident classifications. Hedging produces unsafe outcomes.

===== SYMPTOM SEVERITY REFERENCE =====
{SYMPTOM_SEVERITY_GUIDE}

===== CLASSIFICATION DEFINITIONS =====

CRITICAL (confidence ≥ 0.85 for clear cases):
  Trigger ANY of these → CRITICAL, risk_score 75–100:
  • Chest pain / tightness / pressure
  • Difficulty breathing / shortness of breath
  • Unconsciousness / unresponsive / fainting
  • Stroke signs (sudden facial droop, arm weakness, slurred speech)
  • Seizures / convulsions
  • Severe bleeding (cannot be controlled)
  • Anaphylaxis / severe allergic reaction
  • Poisoning or overdose
  • Traumatic injury (fall, accident, fracture with deformity)
  • Meningitis signs (stiff neck + fever + confusion)
  • Blood in urine/stool (significant)
  • High fever > 104°F / 40°C
  • Diabetic emergency (extreme glucose levels, DKA symptoms)

URGENT (confidence ≥ 0.82 for clear cases):
  Trigger ANY of these → URGENT, risk_score 40–74:
  • Fever 38.5–40°C lasting > 2 days
  • Moderate abdominal pain
  • Persistent vomiting or diarrhea (> 24h) with dehydration signs
  • Ear / throat / urinary infection with moderate pain
  • Wound requiring stitches (non-life-threatening)
  • Moderate headache lasting > 48h
  • Limb pain / swelling without severe deformity
  • Allergic reaction (mild—no breathing issues)
  • Child under 5 with ANY fever → always URGENT minimum
  • Pregnant patient with any pain, bleeding, or fever → always URGENT minimum
  • Elderly (>65) with multiple symptoms → upgrade one level

ROUTINE (confidence ≥ 0.88 for clear cases):
  ALL of these must be true → ROUTINE, risk_score 0–39:
  • Mild symptoms only (cold, mild cough, minor ache)
  • Duration < 5 days
  • No red flag symptoms present
  • Alert and oriented
  • No concerning medical history
  • No fever OR low-grade fever < 38.5°C with no other concerns

===== CONFIDENCE CALIBRATION GUIDE =====
You are an expert — assign high confidence when the pattern is clear:

• 0.95 — Textbook case, single dominant symptom matches one category perfectly
• 0.90 — Clear case, maybe 1 ambiguous detail but classification is obvious
• 0.85 — Good match, 2 possible interpretations but one strongly dominates
• 0.80 — Reasonable certainty, some missing information but pattern clear
• 0.75 — Moderately uncertain (incomplete data, borderline symptoms)
• 0.70 — Genuinely ambiguous (ONLY assign this if truly unclear)
• < 0.70 — ONLY for extremely atypical or contradictory presentations

DO NOT assign confidence < 0.75 for cases that clearly fit one category.
DO NOT assign confidence < 0.80 for cases with one dominant red-flag symptom.
DO NOT hedge — commit to a classification. A wrong confident answer is better than a paralysed one.

===== SCORING RUBRIC =====
risk_score:
  90–100: Multiple CRITICAL indicators, vulnerable patient (elderly/child/pregnant)
  75–89:  One or more CRITICAL indicators, otherwise healthy adult
  55–74:  URGENT presentation, some risk amplifiers
  40–54:  URGENT presentation, low amplifiers
  20–39:  ROUTINE, mild symptoms, healthy patient
  0–19:   ROUTINE, trivial/single symptom, young healthy patient

estimated_wait_minutes:
  CRITICAL: 0 (immediate)
  URGENT:   15–45 minutes
  ROUTINE:  30–120 minutes

===== CALIBRATED EXAMPLES =====
Example 1 — CRITICAL (obvious):
  Input: age=55, symptoms=["chest pain","sweating","nausea"], history=["hypertension"]
  Output: classification=CRITICAL, risk_score=94, confidence=0.95, escalated=false

Example 2 — URGENT (clear fever case):
  Input: age=28, symptoms=["fever 39°C","body ache","headache"], duration="3 days"
  Output: classification=URGENT, risk_score=52, confidence=0.88, escalated=false

Example 3 — ROUTINE (textbook mild case):
  Input: age=22, symptoms=["mild cold","runny nose","slight fatigue"], duration="2 days"
  Output: classification=ROUTINE, risk_score=12, confidence=0.92, escalated=false

Example 4 — URGENT child with fever:
  Input: age=4, symptoms=["fever 38.8°C","crying"], history=[]
  Output: classification=URGENT, risk_score=58, confidence=0.90, escalated=false

===== OUTPUT FORMAT =====
Return ONLY a valid JSON object. No markdown, no code fences, no extra text outside JSON.
{{
  "classification": "CRITICAL" | "URGENT" | "ROUTINE",
  "risk_score": <integer 0-100>,
  "confidence": <float 0.0-1.0>,
  "escalated": false,
  "top_risk_factors": ["most important factor", "second factor", "..."],
  "reasoning": "2-3 sentences in simple English explaining why. Name specific symptoms.",
  "recommended_action": "Specific action for clinic staff or patient right now.",
  "urgency_note": "One decisive sentence about urgency level.",
  "requires_doctor": true | false,
  "red_flags": ["specific symptom", "specific risk factor"],
  "estimated_wait_minutes": <0 for CRITICAL | 15-45 for URGENT | 30-120 for ROUTINE>
}}
"""


ESCALATION_ORDER = ["ROUTINE", "URGENT", "CRITICAL"]


def escalate_level(level: str) -> str:
    """Upgrade triage level by one step."""
    idx = ESCALATION_ORDER.index(level) if level in ESCALATION_ORDER else 0
    return ESCALATION_ORDER[min(idx + 1, 2)]


def triage_patient(patient_data: dict) -> dict:
    """
    Run AI triage classification on patient data.
    Returns enriched triage result dict.
    """
    try:
        model = get_gemini_client()

        # Build a rich, structured patient summary
        age = patient_data.get("age", "Unknown")
        symptoms_raw = patient_data.get("symptoms", "")
        duration = patient_data.get("duration", "Not specified")
        pain = patient_data.get("pain_scale", "Not specified")
        consciousness = patient_data.get("consciousness", "Alert")
        history = patient_data.get("medical_history", "None")
        meds = patient_data.get("medications", "None")
        allergies = patient_data.get("allergies", "None")
        notes = patient_data.get("additional_notes", "None")

        # Compute simple age risk label to help the model
        try:
            age_int = int(age)
            if age_int < 5:
                age_risk = f"{age} years old — HIGH RISK (child under 5)"
            elif age_int > 65:
                age_risk = f"{age} years old — ELEVATED RISK (elderly patient)"
            elif age_int > 50:
                age_risk = f"{age} years old — moderate risk (over 50)"
            else:
                age_risk = f"{age} years old — standard adult risk"
        except Exception:
            age_risk = f"{age} years old"

        patient_summary = f"""PATIENT DATA TO CLASSIFY:

=== Demographics ===
Name:       {patient_data.get('name', 'Unknown')}
Age:        {age_risk}
Gender:     {patient_data.get('gender', 'Unknown')}

=== Chief Complaint ===
Symptoms:       {symptoms_raw}
Duration:       {duration}
Pain scale:     {pain} / 10  {"(SEVERE)" if str(pain) in ['8','9','10'] else "(MODERATE)" if str(pain) in ['5','6','7'] else ""}
Consciousness:  {consciousness}  {"⚠ ALERT: Altered consciousness is a red flag" if consciousness not in ['Alert','alert','ALERT','fully alert'] else ""}

=== Medical Background ===
Medical history:  {history}
Current meds:     {meds}
Allergies:        {allergies}
Notes:            {notes}

=== Your Task ===
Using the classification rules and calibration guide above, assign the MOST APPROPRIATE triage level.
Be decisive. Base confidence on how well this patient's presentation matches a known pattern.
If the dominant symptom clearly belongs to one category, confidence should be ≥ 0.85.
Return ONLY the JSON object."""

        response = model.generate_content(
            [{"role": "user", "parts": [SYSTEM_PROMPT + "\n\n" + patient_summary]}],
            generation_config=genai.GenerationConfig(
                temperature=0.05,   # Near-deterministic for consistent outputs
                max_output_tokens=1024,
            )
        )

        raw = response.text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
        raw = raw.strip()

        result = json.loads(raw)

        # Normalize classification field (support both 'classification' and legacy 'level')
        level = result.get("classification", result.get("level", "ROUTINE")).upper()
        if level not in ("CRITICAL", "URGENT", "ROUTINE"):
            level = "URGENT"

        confidence = float(result.get("confidence", 0.85))
        escalated = result.get("escalated", False)

        # Only escalate if confidence is genuinely LOW (< 0.70 — not 0.75+)
        # This threshold is lowered so high-confidence assessments are not penalised
        if confidence < 0.70 and not escalated:
            level = escalate_level(level)
            escalated = True

        return {
            "level": level,
            "classification": level,
            "risk_score": int(result.get("risk_score", 50)),
            "confidence": round(confidence, 2),
            "escalated": escalated,
            "top_risk_factors": result.get("top_risk_factors", result.get("red_flags", [])),
            "reasoning": result.get("reasoning", "Assessment complete."),
            "recommended_action": result.get("recommended_action",
                                             result.get("recommendations", "Please see the doctor.")),
            "urgency_note": result.get("urgency_note", ""),
            "requires_doctor": result.get("requires_doctor", level != "ROUTINE"),
            "red_flags": result.get("red_flags", []),
            "recommendations": result.get("recommended_action",
                                          result.get("recommendations", "")),
            "estimated_wait_minutes": result.get("estimated_wait_minutes", None),
            "error": None
        }

    except json.JSONDecodeError as e:
        return _fallback("JSON parse error", str(e))
    except Exception as e:
        return _fallback("System error", str(e))


def _fallback(reason: str, detail: str) -> dict:
    """Conservative fallback when AI fails — always URGENT for safety."""
    return {
        "level": "URGENT",
        "classification": "URGENT",
        "risk_score": 60,
        "confidence": 0.80,
        "escalated": False,
        "top_risk_factors": ["Unable to complete AI assessment"],
        "reasoning": f"AI assessment could not be completed ({reason}). "
                     "Patient classified as URGENT for safety.",
        "recommended_action": "Please have the patient assessed by medical staff as soon as possible.",
        "urgency_note": "Assessment incomplete — please consult a doctor promptly.",
        "requires_doctor": True,
        "red_flags": [],
        "recommendations": "Please have the patient assessed by medical staff as soon as possible.",
        "estimated_wait_minutes": 20,
        "error": detail
    }
