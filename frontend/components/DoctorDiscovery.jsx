/**
 * DoctorDiscovery.jsx — RapidAID
 * Patient-facing view: search nearby doctors, view cards,
 * open UPI payment modal with scannable QR code & UPI deeplink.
 *
 * Usage:
 *   import DoctorDiscovery from './components/DoctorDiscovery';
 *   <DoctorDiscovery doctors={doctorList} onQueued={(doctor) => {}} />
 *
 * Dependencies:  react-qr-code  (npm install react-qr-code)
 *
 * Props:
 *   doctors   – Array of doctor objects (uses MOCK_DOCTORS if omitted)
 *   onQueued  – Callback when patient confirms payment & joins queue
 */

import { useState, useMemo } from "react";
import QRCode from "react-qr-code";
import {
  MapPin, IndianRupee, Stethoscope, Search, X,
  CheckCircle, Smartphone, QrCode, Shield, Clock,
  ArrowRight, AlertCircle,
} from "lucide-react";

// ─── Mock Data ─────────────────────────────────────────────────────────────────
export const MOCK_DOCTORS = [
  {
    id: "d1",
    name: "Dr. Priya Sharma",
    specialization: "General Physician",
    city: "Patia",
    pincode: "751024",
    fee: 350,
    upiId: "priya.sharma@ybl",
    availability: "Mon–Sat, 9am–5pm",
    rating: 4.8,
    patients: 120,
  },
  {
    id: "d2",
    name: "Dr. Suresh Mohanty",
    specialization: "Pediatrician",
    city: "Khandagiri",
    pincode: "751030",
    fee: 300,
    upiId: "suresh.mohanty@okaxis",
    availability: "Mon–Fri, 10am–6pm",
    rating: 4.6,
    patients: 87,
  },
  {
    id: "d3",
    name: "Dr. Anita Pati",
    specialization: "Gynecologist",
    city: "Saheed Nagar",
    pincode: "751007",
    fee: 500,
    upiId: "anitapati@paytm",
    availability: "Tue–Sun, 11am–7pm",
    rating: 4.9,
    patients: 210,
  },
];

// ─── UPI Link builder ─────────────────────────────────────────────────────────
const buildUpiLink = (doctor) =>
  `upi://pay?pa=${encodeURIComponent(doctor.upiId)}&pn=${encodeURIComponent(doctor.name)}&am=${doctor.fee}&cu=INR&tn=${encodeURIComponent("Consultation fee - RapidAID")}`;

// ─── Star rating display ──────────────────────────────────────────────────────
function Stars({ rating }) {
  return (
    <span className="flex items-center gap-0.5">
      {[1,2,3,4,5].map((n) => (
        <svg key={n} className={`w-3 h-3 ${n <= Math.round(rating) ? "text-amber-400" : "text-slate-200"}`}
          fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      ))}
      <span className="text-xs text-slate-500 ml-1">{rating}</span>
    </span>
  );
}

// ─── Doctor Card ──────────────────────────────────────────────────────────────
function DoctorCard({ doctor, onBook, queued }) {
  const initials = doctor.name.replace("Dr. ","").split(" ").map(w=>w[0]).join("").slice(0,2);
  return (
    <div className={`bg-white rounded-2xl border shadow-sm p-5 flex flex-col gap-4 transition-all duration-200
      ${queued ? "border-emerald-300 ring-2 ring-emerald-100" : "border-slate-200 hover:shadow-md hover:-translate-y-0.5"}`}>

      {/* Top row */}
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-700 text-white flex items-center justify-center font-bold text-lg shrink-0 shadow-sm">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-bold text-slate-800 text-base leading-tight truncate">
              {doctor.name}
            </h3>
            {queued && (
              <span className="flex items-center gap-1 text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-semibold">
                <CheckCircle size={11} /> In Queue
              </span>
            )}
          </div>
          <div className="flex items-center gap-1.5 mt-0.5">
            <Stethoscope size={12} className="text-cyan-500 shrink-0" />
            <span className="text-sm text-slate-500">{doctor.specialization}</span>
          </div>
          <Stars rating={doctor.rating} />
        </div>
      </div>

      {/* Meta pills */}
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="flex items-center gap-1 bg-slate-100 text-slate-600 px-2.5 py-1.5 rounded-full">
          <MapPin size={11} className="text-rose-400" />
          {doctor.city}, {doctor.pincode}
        </span>
        <span className="flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2.5 py-1.5 rounded-full font-semibold border border-emerald-100">
          <IndianRupee size={11} />
          ₹{doctor.fee} Consultation
        </span>
        <span className="flex items-center gap-1 bg-cyan-50 text-cyan-700 px-2.5 py-1.5 rounded-full">
          <Clock size={11} />
          {doctor.availability}
        </span>
      </div>

      {/* Book button */}
      <button
        onClick={() => onBook(doctor)}
        disabled={queued}
        className={`w-full flex items-center justify-center gap-2 min-h-12 rounded-xl font-bold text-sm transition-all duration-200
          ${queued
            ? "bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default"
            : "bg-emerald-600 text-white hover:bg-emerald-700 shadow-md shadow-emerald-100 active:scale-98"
          }`}
      >
        {queued ? (
          <><CheckCircle size={16} /> Joined Queue</>
        ) : (
          <><IndianRupee size={15} /> Book &amp; Pay ₹{doctor.fee} <ArrowRight size={15} /></>
        )}
      </button>
    </div>
  );
}

// ─── UPI Payment Modal ────────────────────────────────────────────────────────
function UpiModal({ doctor, onClose, onConfirm }) {
  const [confirmed, setConfirmed] = useState(false);
  const upiLink = buildUpiLink(doctor);

  const handleConfirm = () => {
    setConfirmed(true);
    setTimeout(() => { onConfirm(doctor); onClose(); }, 1200);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      style={{ background: "rgba(15,23,42,0.6)", backdropFilter: "blur(4px)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl shadow-2xl overflow-hidden animate-slide-up">

        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 text-white px-6 py-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold opacity-80 uppercase tracking-widest mb-0.5">Secure Payment</p>
            <h2 className="text-lg font-black leading-tight">{doctor.name}</h2>
            <p className="text-sm opacity-85">{doctor.specialization}</p>
          </div>
          <div className="text-right">
            <p className="text-xs opacity-80">Consultation Fee</p>
            <p className="text-3xl font-black">₹{doctor.fee}</p>
          </div>
        </div>

        {/* Trust badges */}
        <div className="flex items-center justify-center gap-4 px-6 py-3 bg-emerald-50 border-b border-emerald-100">
          {[
            { icon: Shield, label: "Secure UPI" },
            { icon: CheckCircle, label: "Instant Transfer" },
            { icon: Smartphone, label: "Pay via Any App" },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-1 text-xs text-emerald-700 font-semibold">
              <Icon size={13} /> {label}
            </div>
          ))}
        </div>

        <div className="px-6 py-5 space-y-5">
          {/* UPI ID display */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide mb-1">Paying to UPI ID</p>
            <p className="font-bold text-slate-800 text-sm break-all">{doctor.upiId}</p>
          </div>

          {/* QR Code — primary on desktop */}
          <div className="hidden sm:flex flex-col items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">
              <QrCode size={14} className="text-cyan-500" />
              Scan with any UPI app
            </div>
            <div className="p-4 bg-white border-2 border-slate-200 rounded-2xl shadow-sm">
              <QRCode
                value={upiLink}
                size={180}
                level="M"
                fgColor="#0f172a"
                bgColor="#ffffff"
              />
            </div>
            <p className="text-xs text-slate-400 text-center max-w-xs">
              Open Google Pay, PhonePe, or Paytm on your phone and scan this code to pay ₹{doctor.fee} instantly.
            </p>
          </div>

          {/* UPI Deeplink button — primary on mobile */}
          <a
            href={upiLink}
            className="flex items-center justify-center gap-3 w-full min-h-14 rounded-xl bg-emerald-600 text-white font-bold text-base hover:bg-emerald-700 shadow-lg shadow-emerald-100 transition-all duration-200"
          >
            <Smartphone size={20} />
            Pay ₹{doctor.fee} via UPI App
          </a>

          {/* QR hint on mobile */}
          <p className="text-xs text-center text-slate-400 sm:hidden">
            Opens Google Pay / PhonePe / Paytm automatically
          </p>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <hr className="flex-1 border-slate-200" />
            <span className="text-xs text-slate-400 font-medium">After payment</span>
            <hr className="flex-1 border-slate-200" />
          </div>

          {/* Confirm payment button */}
          <button
            onClick={handleConfirm}
            disabled={confirmed}
            className={`w-full flex items-center justify-center gap-2 min-h-12 rounded-xl font-bold text-sm border-2 transition-all duration-200
              ${confirmed
                ? "bg-emerald-50 border-emerald-300 text-emerald-700"
                : "bg-white border-slate-200 text-slate-700 hover:border-emerald-400 hover:text-emerald-700 hover:bg-emerald-50"
              }`}
          >
            {confirmed ? (
              <><CheckCircle size={16} className="text-emerald-500" /> Added to Queue!</>
            ) : (
              <><CheckCircle size={16} /> Payment Done — Join Queue</>
            )}
          </button>

          <p className="text-center text-xs text-slate-400">
            <AlertCircle size={11} className="inline mr-1" />
            Click above only after your payment is successful
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function DoctorDiscovery({ doctors = MOCK_DOCTORS, onQueued }) {
  const [query, setQuery] = useState("");
  const [activeDoctor, setActiveDoctor] = useState(null);
  const [queuedIds, setQueuedIds] = useState(new Set());

  const filtered = useMemo(() => {
    if (!query.trim()) return doctors;
    const q = query.toLowerCase();
    return doctors.filter(
      (d) =>
        d.city.toLowerCase().includes(q) ||
        d.pincode.includes(q) ||
        d.name.toLowerCase().includes(q) ||
        d.specialization.toLowerCase().includes(q)
    );
  }, [query, doctors]);

  const handleConfirm = (doctor) => {
    setQueuedIds((prev) => new Set([...prev, doctor.id]));
    onQueued?.(doctor);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased">

      {/* ── Page Header ─────────────────────────────────────── */}
      <div className="bg-gradient-to-br from-cyan-700 to-cyan-500 text-white px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <p className="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">RapidAID</p>
          <h1 className="text-2xl sm:text-3xl font-black mb-1">Find Nearby Doctors</h1>
          <p className="text-sm opacity-85 mb-6">Pay consultation fees instantly via UPI — no cash needed.</p>

          {/* Search bar */}
          <div className="relative">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by area, pincode, or doctor name…"
              className="w-full h-13 min-h-12 pl-11 pr-10 py-3 rounded-2xl border-0 bg-white text-slate-800 text-sm font-medium placeholder:text-slate-400 shadow-lg focus:outline-none focus:ring-4 focus:ring-white/30 transition"
            />
            {query && (
              <button
                onClick={() => setQuery("")}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Doctor Grid ─────────────────────────────────────── */}
      <div className="max-w-4xl mx-auto px-4 py-6">

        {/* Result count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-semibold text-slate-600">
            {filtered.length} doctor{filtered.length !== 1 ? "s" : ""} found
            {query && <span className="text-slate-400"> for "{query}"</span>}
          </p>
          {queuedIds.size > 0 && (
            <span className="flex items-center gap-1.5 text-xs bg-emerald-100 text-emerald-700 font-semibold px-3 py-1.5 rounded-full">
              <CheckCircle size={12} /> {queuedIds.size} in queue
            </span>
          )}
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-16">
            <MapPin size={40} className="mx-auto text-slate-300 mb-3" />
            <p className="text-slate-500 font-semibold">No doctors found</p>
            <p className="text-sm text-slate-400 mt-1">Try a different area name or pincode.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((doc) => (
              <DoctorCard
                key={doc.id}
                doctor={doc}
                queued={queuedIds.has(doc.id)}
                onBook={setActiveDoctor}
              />
            ))}
          </div>
        )}
      </div>

      {/* UPI Modal */}
      {activeDoctor && (
        <UpiModal
          doctor={activeDoctor}
          onClose={() => setActiveDoctor(null)}
          onConfirm={handleConfirm}
        />
      )}

      {/* Slide-up animation */}
      <style>{`
        @keyframes slide-up {
          from { transform: translateY(100%); opacity: 0; }
          to   { transform: translateY(0); opacity: 1; }
        }
        .animate-slide-up { animation: slide-up 0.3s cubic-bezier(.34,1.56,.64,1); }
      `}</style>
    </div>
  );
}
