/**
 * SmartPrescriptionPanel.jsx
 * RapidAID — AI-Powered Clinical Prescription Interface
 * For doctor use on tablets in high-volume, low-bandwidth rural clinics.
 *
 * Stack: React (Functional), Tailwind CSS, lucide-react, Web Speech API
 *
 * Usage:
 *   import SmartPrescriptionPanel from './components/SmartPrescriptionPanel';
 *   <SmartPrescriptionPanel patient={patientData} triageResult={triageResult} />
 *
 * Props:
 *   patient      – { name, age, gender, vitals: { bp, spo2, temp, pulse } }
 *   triageResult – { level: 'CRITICAL'|'URGENT'|'ROUTINE', risk_score, confidence }
 */

import { useState, useRef, useEffect, useCallback } from "react";
import {
  Mic,
  MicOff,
  Plus,
  Trash2,
  Sun,
  Cloud,
  Moon,
  Printer,
  CheckCircle,
  AlertTriangle,
  Activity,
  Thermometer,
  Heart,
  Wind,
  ChevronDown,
  Globe,
  Loader2,
  Pill,
  ClipboardList,
  User,
  X,
} from "lucide-react";

// ─── Constants ────────────────────────────────────────────────────────────────

const TRIAGE_CONFIG = {
  CRITICAL: {
    label: "Critical",
    bg: "bg-red-100",
    text: "text-red-700",
    border: "border-red-300",
    dot: "bg-red-500",
    ring: "ring-red-200",
  },
  URGENT: {
    label: "Urgent",
    bg: "bg-amber-100",
    text: "text-amber-700",
    border: "border-amber-300",
    dot: "bg-amber-500",
    ring: "ring-amber-200",
  },
  ROUTINE: {
    label: "Routine",
    bg: "bg-emerald-100",
    text: "text-emerald-700",
    border: "border-emerald-300",
    dot: "bg-emerald-500",
    ring: "ring-emerald-200",
  },
};

const STT_LANGUAGES = [
  { code: "en-IN", label: "English" },
  { code: "hi-IN", label: "हिन्दी" },
  { code: "or-IN", label: "ଓଡ଼ିଆ" },
];

const FREQUENCY_TIME = [
  { id: "morning",   icon: Sun,   label: "Morning",   color: "text-amber-500" },
  { id: "afternoon", icon: Cloud, label: "Afternoon", color: "text-sky-500"  },
  { id: "night",     icon: Moon,  label: "Night",     color: "text-indigo-500" },
];

const FREQUENCY_MEAL = [
  { id: "before", emoji: "🌿", label: "Before Food" },
  { id: "after",  emoji: "🍽️", label: "After Food"  },
];

const LIFESTYLE_ADVICE = [
  "Increase Hydration",
  "Strict Bed Rest",
  "Light Meals Only",
  "Avoid Spicy Food",
  "Review after 3 Days",
  "Review after 1 Week",
  "Refer to District Hospital",
  "Blood Test Required",
];

const createMedRow = () => ({
  id: crypto.randomUUID(),
  drug: "",
  dosage: "",
  frequency: [],
  duration: "",
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

function FrequencyToggle({ freqTime, freqMeal, onTimeChange, onMealChange }) {
  const toggleTime = (id) =>
    onTimeChange(
      freqTime.includes(id) ? freqTime.filter((f) => f !== id) : [...freqTime, id]
    );

  const toggleMeal = (id) =>
    onMealChange(freqMeal === id ? "" : id);

  return (
    <div className="flex flex-col gap-1.5">
      {/* Time of day row — cyan theme */}
      <div className="flex gap-1">
        {FREQUENCY_TIME.map(({ id, icon: Icon, label, color }) => {
          const active = freqTime.includes(id);
          return (
            <button
              key={id}
              type="button"
              title={label}
              onClick={() => toggleTime(id)}
              className={`flex items-center justify-center w-10 h-10 rounded-lg border-2 transition-all duration-150 touch-manipulation
                ${active
                  ? "border-cyan-500 bg-cyan-50 shadow-sm scale-105"
                  : "border-slate-200 bg-white hover:border-slate-300"
                }`}
            >
              <Icon size={18} className={active ? color : "text-slate-400"} />
            </button>
          );
        })}
      </div>
      {/* Meal timing row — violet theme */}
      <div className="flex gap-1">
        {FREQUENCY_MEAL.map(({ id, emoji, label }) => {
          const active = freqMeal === id;
          return (
            <button
              key={id}
              type="button"
              title={label}
              onClick={() => toggleMeal(id)}
              className={`flex items-center gap-1 h-8 px-2.5 rounded-lg border-2 text-xs font-semibold transition-all duration-150 touch-manipulation
                ${active
                  ? "border-violet-500 bg-violet-50 text-violet-700 shadow-sm scale-105"
                  : "border-slate-200 bg-white text-slate-500 hover:border-slate-300"
                }`}
            >
              <span>{emoji}</span>
              <span className="hidden sm:inline">{id === "before" ? "Before" : "After"}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Toast({ show, onClose }) {
  useEffect(() => {
    if (show) {
      const t = setTimeout(onClose, 3500);
      return () => clearTimeout(t);
    }
  }, [show, onClose]);

  if (!show) return null;
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-bounce-once">
      <div className="flex items-center gap-3 bg-emerald-600 text-white px-5 py-3 rounded-2xl shadow-2xl">
        <CheckCircle size={20} />
        <span className="font-semibold text-sm">
          Prescription generated &amp; sent to print queue!
        </span>
        <button onClick={onClose} className="ml-1 opacity-70 hover:opacity-100">
          <X size={16} />
        </button>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function SmartPrescriptionPanel({
  patient = {
    name: "Ramesh Kumar",
    age: 58,
    gender: "Male",
    vitals: { bp: "148/92", spo2: "94%", temp: "38.7°C", pulse: "102 bpm" },
  },
  triageResult = { level: "URGENT", risk_score: 62, confidence: 0.88 },
}) {
  // ── Diagnosis / Notes ─────────────────────────────────────────────────────
  const [notes, setNotes] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [sttLang, setSttLang] = useState(STT_LANGUAGES[0]);
  const [langOpen, setLangOpen] = useState(false);
  const [sttError, setSttError] = useState("");
  const recognitionRef = useRef(null);

  // ── Medications ───────────────────────────────────────────────────────────
  const [medications, setMedications] = useState([createMedRow()]);
  const updateMed = (id, field, value) =>
    setMedications((prev) =>
      prev.map((m) => (m.id === id ? { ...m, [field]: value } : m))
    );
  const updateMedFreqTime = (id, val) => updateMed(id, "frequency", val);
  const updateMedFreqMeal = (id, val) => updateMed(id, "freqMeal", val);
  const addMed = () =>
    setMedications((prev) => [...prev, { ...createMedRow(), freqMeal: "" }]);
  const removeMed = (id) =>
    setMedications((prev) => prev.filter((m) => m.id !== id));

  // ── Lifestyle Advice ──────────────────────────────────────────────────────
  const [activeAdvice, setActiveAdvice] = useState(new Set());
  const toggleAdvice = (label) =>
    setActiveAdvice((prev) => {
      const next = new Set(prev);
      next.has(label) ? next.delete(label) : next.add(label);
      return next;
    });

  // ── Print / Submit ────────────────────────────────────────────────────────
  const [printing, setPrinting] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const handlePrint = async () => {
    setPrinting(true);
    await new Promise((r) => setTimeout(r, 2000));
    setPrinting(false);
    setShowToast(true);
    // Prepare payload and open print template
    const freqLabel = (m) => {
      const time = (m.frequency || []).map((s) => ({ morning: "Morning", afternoon: "Afternoon", night: "Night" }[s])).join(" + ");
      const meal = m.freqMeal === "before" ? "Before Food" : m.freqMeal === "after" ? "After Food" : "";
      return [time, meal].filter(Boolean).join(", ");
    };
    const payload = {
      patient, triage: triageResult,
      notes,
      medications: medications.filter((m) => m.drug).map((m) => ({
        drug: m.drug, dosage: m.dosage, frequency: freqLabel(m), duration: m.duration,
      })),
      advice: [...activeAdvice],
      generatedAt: new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }),
    };
    sessionStorage.setItem("rxPayload", JSON.stringify(payload));
    window.open("/prescription-print", "_blank");
  };

  // ── Speech-to-Text ────────────────────────────────────────────────────────
  const startRecording = useCallback(() => {
    setSttError("");
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSttError("Speech recognition is not supported in this browser.");
      return;
    }

    const rec = new SpeechRecognition();
    rec.lang = sttLang.code;
    rec.continuous = true;
    rec.interimResults = true;

    rec.onresult = (e) => {
      const transcript = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join(" ");
      setNotes((prev) => {
        const base = prev.trimEnd();
        return base ? base + " " + transcript : transcript;
      });
    };

    rec.onerror = (e) => {
      setSttError(`Mic error: ${e.error}`);
      setIsRecording(false);
    };

    rec.onend = () => setIsRecording(false);

    recognitionRef.current = rec;
    rec.start();
    setIsRecording(true);
  }, [sttLang]);

  const stopRecording = useCallback(() => {
    recognitionRef.current?.stop();
    setIsRecording(false);
  }, []);

  const toggleMic = () => (isRecording ? stopRecording() : startRecording());

  // Cleanup on unmount
  useEffect(() => () => recognitionRef.current?.stop(), []);

  // ── Derived ───────────────────────────────────────────────────────────────
  const level = (triageResult.level || "ROUTINE").toUpperCase();
  const cfg = TRIAGE_CONFIG[level] || TRIAGE_CONFIG.ROUTINE;

  // ═════════════════════════════════════════════════════════════════════════
  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased">
      <Toast show={showToast} onClose={() => setShowToast(false)} />

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-5">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <header className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            {/* Patient identity */}
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-cyan-50 border border-cyan-100 flex items-center justify-center shrink-0">
                <User size={22} className="text-cyan-600" />
              </div>
              <div>
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wide">
                  Active Patient
                </p>
                <h1 className="text-xl font-bold text-slate-800 leading-tight">
                  {patient.name}
                </h1>
                <p className="text-sm text-slate-500">
                  {patient.age} yrs &bull; {patient.gender}
                </p>
              </div>
            </div>

            {/* Triage badge */}
            <div
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${cfg.bg} ${cfg.border} ${cfg.ring} ring-2`}
            >
              <span
                className={`w-2.5 h-2.5 rounded-full ${cfg.dot} animate-pulse`}
              />
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Triage Level
                </p>
                <p className={`text-lg font-black ${cfg.text} leading-tight`}>
                  {cfg.label}
                </p>
              </div>
              <div className="ml-3 border-l border-slate-200 pl-3">
                <p className="text-xs text-slate-400">Risk Score</p>
                <p className={`text-xl font-black ${cfg.text}`}>
                  {triageResult.risk_score ?? "—"}
                </p>
              </div>
              <div className="border-l border-slate-200 pl-3">
                <p className="text-xs text-slate-400">Confidence</p>
                <p className="text-xl font-black text-slate-700">
                  {triageResult.confidence
                    ? `${Math.round(triageResult.confidence * 100)}%`
                    : "—"}
                </p>
              </div>
            </div>
          </div>

          {/* Vitals strip */}
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { icon: Heart, label: "Blood Pressure", value: patient.vitals?.bp, color: "text-rose-500" },
              { icon: Activity, label: "Pulse", value: patient.vitals?.pulse, color: "text-amber-500" },
              { icon: Wind, label: "SpO₂", value: patient.vitals?.spo2, color: "text-sky-500" },
              { icon: Thermometer, label: "Temperature", value: patient.vitals?.temp, color: "text-orange-500" },
            ].map(({ icon: Icon, label, value, color }) => (
              <div
                key={label}
                className="flex items-center gap-2.5 bg-slate-50 border border-slate-100 rounded-xl px-3 py-2"
              >
                <Icon size={18} className={color} />
                <div>
                  <p className="text-xs text-slate-400">{label}</p>
                  <p className="text-sm font-semibold text-slate-700">
                    {value ?? "N/A"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </header>

        {/* ── Clinical Notes + STT ─────────────────────────────────────── */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <ClipboardList size={18} className="text-cyan-600" />
              <h2 className="text-base font-semibold text-slate-800">
                Clinical Notes &amp; Diagnosis
              </h2>
            </div>

            {/* Language picker + Mic */}
            <div className="flex items-center gap-2">
              {/* Language dropdown */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setLangOpen((o) => !o)}
                  className="flex items-center gap-1.5 h-10 px-3 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition border border-slate-200"
                >
                  <Globe size={15} className="text-cyan-600" />
                  {sttLang.label}
                  <ChevronDown size={14} />
                </button>
                {langOpen && (
                  <div className="absolute right-0 mt-1 w-36 bg-white border border-slate-200 rounded-xl shadow-lg z-20 overflow-hidden">
                    {STT_LANGUAGES.map((lg) => (
                      <button
                        key={lg.code}
                        type="button"
                        onClick={() => {
                          setSttLang(lg);
                          setLangOpen(false);
                          if (isRecording) {
                            stopRecording();
                          }
                        }}
                        className={`w-full text-left px-4 py-2.5 text-sm transition hover:bg-cyan-50 ${
                          sttLang.code === lg.code
                            ? "text-cyan-700 font-semibold bg-cyan-50"
                            : "text-slate-700"
                        }`}
                      >
                        {lg.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Mic button */}
              <button
                type="button"
                onClick={toggleMic}
                title={isRecording ? "Stop Recording" : "Start Voice Dictation"}
                className={`relative flex items-center gap-2 h-10 px-4 rounded-xl font-semibold text-sm transition-all duration-200 touch-manipulation
                  ${isRecording
                    ? "bg-red-500 text-white shadow-lg shadow-red-200 scale-105"
                    : "bg-cyan-600 text-white hover:bg-cyan-700 shadow-sm"
                  }`}
              >
                {isRecording ? (
                  <>
                    <span className="absolute inset-0 rounded-xl bg-red-400 animate-ping opacity-40" />
                    <MicOff size={16} />
                    <span>Stop</span>
                  </>
                ) : (
                  <>
                    <Mic size={16} />
                    <span>Dictate</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {sttError && (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-2 mb-3">
              <AlertTriangle size={15} />
              {sttError}
            </div>
          )}

          {isRecording && (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2 mb-3 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
              Recording in <strong>{sttLang.label}</strong>… Speak clearly.
            </div>
          )}

          <textarea
            id="clinical-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Type or dictate clinical findings, diagnosis, and doctor's notes here…"
            rows={5}
            className="w-full min-h-12 resize-y rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition"
          />
        </section>

        {/* ── Smart Medication Builder ─────────────────────────────────── */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Pill size={18} className="text-cyan-600" />
              <h2 className="text-base font-semibold text-slate-800">
                Medication Builder
              </h2>
              <span className="ml-1 text-xs bg-cyan-100 text-cyan-700 font-semibold px-2 py-0.5 rounded-full">
                {medications.length} {medications.length === 1 ? "drug" : "drugs"}
              </span>
            </div>
          </div>

          {/* Table header — hidden on small screens, shown as labels on mobile */}
          <div className="hidden sm:grid grid-cols-[2fr_1fr_auto_1fr_auto] gap-3 px-1 mb-2">
            {["Drug Name", "Dosage", "Frequency", "Duration", ""].map((h) => (
              <p key={h} className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                {h}
              </p>
            ))}
          </div>

          <div className="space-y-3">
            {medications.map((med, idx) => (
              <div
                key={med.id}
                className="grid grid-cols-1 sm:grid-cols-[2fr_1fr_auto_1fr_auto] gap-3 items-center bg-slate-50 border border-slate-200 rounded-xl p-3"
              >
                {/* Drug name */}
                <div>
                  <label className="sm:hidden text-xs text-slate-400 font-medium mb-1 block">
                    Drug Name
                  </label>
                  <input
                    type="text"
                    placeholder={`e.g. Paracetamol`}
                    value={med.drug}
                    onChange={(e) => updateMed(med.id, "drug", e.target.value)}
                    className="w-full min-h-12 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition"
                  />
                </div>

                {/* Dosage */}
                <div>
                  <label className="sm:hidden text-xs text-slate-400 font-medium mb-1 block">
                    Dosage
                  </label>
                  <input
                    type="text"
                    placeholder="500mg"
                    value={med.dosage}
                    onChange={(e) => updateMed(med.id, "dosage", e.target.value)}
                    className="w-full min-h-12 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition"
                  />
                </div>

                {/* Frequency icons */}
                <div>
                  <label className="sm:hidden text-xs text-slate-400 font-medium mb-1 block">
                    Frequency
                  </label>
                  <FrequencyToggle
                    freqTime={med.frequency || []}
                    freqMeal={med.freqMeal || ""}
                    onTimeChange={(val) => updateMedFreqTime(med.id, val)}
                    onMealChange={(val) => updateMedFreqMeal(med.id, val)}
                  />
                </div>

                {/* Duration */}
                <div>
                  <label className="sm:hidden text-xs text-slate-400 font-medium mb-1 block">
                    Duration
                  </label>
                  <input
                    type="text"
                    placeholder="5 Days"
                    value={med.duration}
                    onChange={(e) => updateMed(med.id, "duration", e.target.value)}
                    className="w-full min-h-12 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition"
                  />
                </div>

                {/* Delete */}
                <button
                  type="button"
                  onClick={() => removeMed(med.id)}
                  disabled={medications.length === 1}
                  title="Remove medication"
                  className="flex items-center justify-center w-10 h-10 rounded-xl border border-rose-200 bg-rose-50 text-rose-500 hover:bg-rose-100 transition disabled:opacity-30 disabled:cursor-not-allowed touch-manipulation shrink-0"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addMed}
            className="mt-4 flex items-center gap-2 h-11 px-5 rounded-xl border-2 border-dashed border-cyan-300 text-cyan-600 font-semibold text-sm hover:bg-cyan-50 hover:border-cyan-400 transition-all duration-150 touch-manipulation"
          >
            <Plus size={17} />
            Add Medication
          </button>
        </section>

        {/* ── Lifestyle Advice Pills ───────────────────────────────────── */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <h2 className="text-base font-semibold text-slate-800 mb-3">
            Lifestyle &amp; Follow-up Advice
          </h2>
          <div className="flex flex-wrap gap-2.5">
            {LIFESTYLE_ADVICE.map((label) => {
              const active = activeAdvice.has(label);
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => toggleAdvice(label)}
                  className={`h-11 px-4 rounded-full text-sm font-semibold border-2 transition-all duration-150 touch-manipulation select-none
                    ${active
                      ? "bg-cyan-600 text-white border-cyan-600 shadow-md shadow-cyan-100 scale-105"
                      : "bg-white text-slate-600 border-slate-200 hover:border-cyan-300 hover:text-cyan-700"
                    }`}
                >
                  {active && <span className="mr-1.5">✓</span>}
                  {label}
                </button>
              );
            })}
          </div>
          {activeAdvice.size > 0 && (
            <p className="mt-3 text-xs text-slate-400">
              {activeAdvice.size} advice point{activeAdvice.size > 1 ? "s" : ""} selected — will appear on printed prescription.
            </p>
          )}
        </section>

        {/* ── Action Footer ────────────────────────────────────────────── */}
        <footer className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              type="button"
              onClick={handlePrint}
              disabled={printing}
              className={`flex-1 flex items-center justify-center gap-3 min-h-14 rounded-xl font-bold text-base transition-all duration-200 touch-manipulation
                ${printing
                  ? "bg-cyan-400 text-white cursor-wait"
                  : "bg-cyan-600 text-white hover:bg-cyan-700 shadow-lg shadow-cyan-200 active:scale-98"
                }`}
            >
              {printing ? (
                <>
                  <Loader2 size={22} className="animate-spin" />
                  Generating Prescription…
                </>
              ) : (
                <>
                  <Printer size={22} />
                  Generate &amp; Print Prescription
                </>
              )}
            </button>
          </div>

          {/* Summary chips */}
          <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-500">
            <span className="bg-slate-100 px-3 py-1.5 rounded-full">
              🩺 {medications.filter((m) => m.drug).length} medication{medications.filter((m) => m.drug).length !== 1 ? "s" : ""}
            </span>
            <span className="bg-slate-100 px-3 py-1.5 rounded-full">
              📋 {activeAdvice.size} advice point{activeAdvice.size !== 1 ? "s" : ""}
            </span>
            <span className="bg-slate-100 px-3 py-1.5 rounded-full">
              📝 {notes.trim().split(/\s+/).filter(Boolean).length} word{notes.trim().split(/\s+/).filter(Boolean).length !== 1 ? "s" : ""} recorded
            </span>
            <span className={`px-3 py-1.5 rounded-full font-semibold ${cfg.bg} ${cfg.text}`}>
              {cfg.label} Triage
            </span>
          </div>
        </footer>

      </div>
    </div>
  );
}
