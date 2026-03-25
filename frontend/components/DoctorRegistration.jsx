/**
 * DoctorRegistration.jsx — RapidAID
 * Doctor onboarding form: collects name, specialization, license,
 * location, consultation fee, and UPI ID.
 *
 * Usage:
 *   import DoctorRegistration from './components/DoctorRegistration';
 *   <DoctorRegistration onSave={(doctor) => console.log(doctor)} />
 *
 * Props:
 *   onSave(doctor) — called with the new doctor object on submit
 */

import { useState } from "react";
import {
  User, Stethoscope, BadgeCheck, MapPin, Hash,
  IndianRupee, CreditCard, CheckCircle, ChevronRight,
  AlertCircle,
} from "lucide-react";

// ─── Field config ─────────────────────────────────────────────────────────────
const SPECIALIZATIONS = [
  "General Physician", "Pediatrician", "Gynecologist", "Orthopedic Surgeon",
  "Cardiologist", "Dermatologist", "ENT Specialist", "Ophthalmologist",
  "Neurologist", "Psychiatrist", "Dentist", "Radiologist", "Other",
];

const EMPTY_FORM = {
  name: "", specialization: "", license: "",
  city: "", pincode: "", fee: "", upiId: "",
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function Field({ label, icon: Icon, error, children }) {
  return (
    <div>
      <label className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
        <Icon size={13} className="text-cyan-500" />
        {label}
      </label>
      {children}
      {error && (
        <p className="flex items-center gap-1 text-xs text-red-500 mt-1">
          <AlertCircle size={11} /> {error}
        </p>
      )}
    </div>
  );
}

function Input({ value, onChange, placeholder, type = "text", ...rest }) {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full min-h-12 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition"
      {...rest}
    />
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function DoctorRegistration({ onSave }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [saved, setSaved] = useState(false);

  const set = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const validate = () => {
    const e = {};
    if (!form.name.trim())           e.name = "Full name is required";
    if (!form.specialization)        e.specialization = "Select a specialization";
    if (!form.license.trim())        e.license = "License number is required";
    if (!form.city.trim())           e.city = "City / area is required";
    if (!/^\d{6}$/.test(form.pincode)) e.pincode = "Enter a valid 6-digit pincode";
    if (!form.fee || isNaN(form.fee) || +form.fee <= 0)
      e.fee = "Enter a valid consultation fee";
    if (!form.upiId.includes("@"))   e.upiId = "Enter a valid UPI ID (e.g. name@ybl)";
    return e;
  };

  const handleSubmit = (ev) => {
    ev.preventDefault();
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setErrors({});
    const doctor = {
      id: crypto.randomUUID(),
      ...form,
      fee: +form.fee,
      createdAt: new Date().toISOString(),
    };
    onSave?.(doctor);
    setSaved(true);
    setTimeout(() => { setSaved(false); setForm(EMPTY_FORM); }, 3000);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased py-8 px-4">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-6">
          <p className="text-xs text-cyan-600 font-bold uppercase tracking-widest mb-1">RapidAID</p>
          <h1 className="text-2xl font-black text-slate-800">Doctor Registration</h1>
          <p className="text-sm text-slate-500 mt-1">
            Register to be discoverable by patients in your area.
          </p>
        </div>

        {/* Success toast */}
        {saved && (
          <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-200 rounded-2xl px-5 py-4 mb-5">
            <CheckCircle className="text-emerald-500 shrink-0" size={20} />
            <div>
              <p className="font-semibold text-emerald-800 text-sm">Registration saved!</p>
              <p className="text-xs text-emerald-600">Your profile is now visible to nearby patients.</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">

            {/* ── Personal Details ────────────────────────────────── */}
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-100 pb-2">
                Personal Details
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="Full Name" icon={User} error={errors.name}>
                  <Input value={form.name} onChange={set("name")} placeholder="Dr. Priya Sharma" />
                </Field>

                <Field label="Specialization" icon={Stethoscope} error={errors.specialization}>
                  <select
                    value={form.specialization}
                    onChange={set("specialization")}
                    className="w-full min-h-12 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-400 transition appearance-none"
                  >
                    <option value="">Select specialization…</option>
                    {SPECIALIZATIONS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  {errors.specialization && (
                    <p className="flex items-center gap-1 text-xs text-red-500 mt-1">
                      <AlertCircle size={11} /> {errors.specialization}
                    </p>
                  )}
                </Field>

                <div className="sm:col-span-2">
                  <Field label="Medical License No." icon={BadgeCheck} error={errors.license}>
                    <Input value={form.license} onChange={set("license")} placeholder="MCI-OD-2019-XXXXX" />
                  </Field>
                </div>
              </div>
            </div>

            {/* ── Location ─────────────────────────────────────── */}
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-100 pb-2">
                Location
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="City / Area" icon={MapPin} error={errors.city}>
                  <Input value={form.city} onChange={set("city")} placeholder="Patia, Bhubaneswar" />
                </Field>

                <Field label="Pincode" icon={Hash} error={errors.pincode}>
                  <Input
                    value={form.pincode}
                    onChange={set("pincode")}
                    placeholder="751024"
                    type="text"
                    maxLength={6}
                    inputMode="numeric"
                  />
                </Field>
              </div>
            </div>

            {/* ── Payment Details ────────────────────────────────── */}
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-100 pb-2">
                Payment Details
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="Consultation Fee (₹)" icon={IndianRupee} error={errors.fee}>
                  <Input
                    value={form.fee}
                    onChange={set("fee")}
                    placeholder="500"
                    type="number"
                    min="0"
                    inputMode="numeric"
                  />
                </Field>

                <Field label="UPI ID" icon={CreditCard} error={errors.upiId}>
                  <Input
                    value={form.upiId}
                    onChange={set("upiId")}
                    placeholder="priya.sharma@ybl"
                    type="text"
                    inputMode="email"
                    autoCapitalize="none"
                  />
                </Field>
              </div>

              {/* UPI Preview */}
              {form.upiId && form.fee && !errors.upiId && !errors.fee && (
                <div className="mt-3 flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-2.5 text-sm text-emerald-700">
                  <CheckCircle size={14} />
                  <span>UPI Link: <code className="font-mono text-xs">upi://pay?pa={form.upiId}&pn={encodeURIComponent(form.name || "Doctor")}&am={form.fee}&cu=INR</code></span>
                </div>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 min-h-14 rounded-xl bg-cyan-600 text-white font-bold text-base hover:bg-cyan-700 shadow-lg shadow-cyan-100 transition-all duration-200 mt-2"
            >
              Register Profile
              <ChevronRight size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
