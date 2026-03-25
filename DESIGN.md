# TriageAID Design System

> Clinical-grade UI/UX documentation for the TriageAID Intelligent Triage System.

---

## 1. Brand Identity

| Property | Value |
|---|---|
| **Product Name** | TriageAID |
| **Tagline** | *Intelligent Triage for Rural Clinics* |
| **Personality** | Trustworthy · Clinical · Calm · Decisive |
| **Target Users** | Doctors & nurses on tablets in rural primary health centres |
| **Primary Constraint** | Low-bandwidth environments; minimal external dependencies |

---

## 2. Colour Palette

### Primary (Cyan — Interactive)
| Token | Hex | Usage |
|---|---|---|
| `cyan-600` | `#0891b2` | Primary buttons, active states, headings |
| `cyan-500` | `#06b6d4` | Hover states, light borders |
| `cyan-50`  | `#ecfeff` | Active frequency toggle background |
| `cyan-100` | `#cffafe` | Badge backgrounds |

### Triage Levels
| Level | Background | Border / Text | Dot |
|---|---|---|---|
| **CRITICAL** | `#fee2e2` (red-100) | `#991b1b` (red-800) | `#ef4444` (red-500) |
| **URGENT**   | `#fef3c7` (amber-100) | `#92400e` (amber-800) | `#f59e0b` (amber-500) |
| **ROUTINE**  | `#d1fae5` (emerald-100) | `#065f46` (emerald-900) | `#10b981` (emerald-500) |

### Neutrals
| Token | Hex | Usage |
|---|---|---|
| `slate-800` | `#1e293b` | Primary text, headings |
| `slate-600` | `#475569` | Body text |
| `slate-400` | `#94a3b8` | Placeholder, labels |
| `slate-200` | `#e2e8f0` | Borders, dividers |
| `slate-100` | `#f1f5f9` | Input backgrounds |
| `slate-50`  | `#f8fafc` | Page background |
| `white`     | `#ffffff` | Card backgrounds |

### Semantic
| Token | Hex | Usage |
|---|---|---|
| `rose-500` | `#f43f5e` | Delete / danger actions |
| `emerald-600` | `#059669` | Success states, toast |
| `violet-600` | `#7c3aed` | Meal timing (Before/After Food) |
| `amber-500` | `#f59e0b` | Warning, Urgent triage |
| `red-500` | `#ef4444` | Critical triage, recording mic |

---

## 3. Typography

| Role | Font | Weight | Size |
|---|---|---|---|
| **Display / Letterhead** | Noto Serif | 700 | 26px |
| **Page heading (h1)** | Inter | 900 (Black) | 20–24px |
| **Section heading (h2)** | Inter | 700 (Bold) | 16px |
| **Body text** | Inter | 400 | 14px |
| **Labels / Captions** | Inter | 600 | 11–12px — uppercase, letter-spacing |
| **Monospace** | System mono | 400 | 13px |

**Google Fonts import:**
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Serif:wght@400;700&display=swap" rel="stylesheet">
```

---

## 4. Spacing & Layout

- **Max content width:** `800px` (prescription), `896px` (panel — `max-w-4xl`)
- **Page padding:** `px-4 py-6` (mobile), `px-8` (desktop)
- **Card padding:** `p-4` (compact), `p-5` (standard)
- **Section gap:** `space-y-5` (20px) between cards

---

## 5. Component Specifications

### Cards
```css
background: white;
border-radius: 16px;        /* rounded-2xl */
border: 1px solid #e2e8f0; /* border-slate-200 */
box-shadow: 0 1px 2px rgba(0,0,0,.05); /* shadow-sm */
```

### Buttons — Primary
```css
background: #0891b2;       /* cyan-600 */
color: white;
border-radius: 12px;       /* rounded-xl */
min-height: 48px;          /* touch-friendly */
font-weight: 700;
transition: background .15s;
```

### Buttons — Frequency Toggle (Time of Day)
```css
/* Active state */
border: 2px solid #0891b2; /* cyan-500 */
background: #ecfeff;        /* cyan-50 */
transform: scale(1.05);
```

### Buttons — Frequency Toggle (Meal Timing)
```css
/* Active state */
border: 2px solid #7c3aed; /* violet-600 */
background: #f5f3ff;        /* violet-50 */
color: #6d28d9;             /* violet-700 */
transform: scale(1.05);
```

### Inputs / Textareas
```css
border: 1px solid #e2e8f0;
border-radius: 12px;
background: #f8fafc;
min-height: 48px;           /* touch minimum */
padding: 12px 16px;
font-size: 14px;
/* Focus */
box-shadow: 0 0 0 2px #22d3ee;
border-color: transparent;
```

### Toast (Success)
```css
background: #059669;
border-radius: 16px;
padding: 14px 22px;
box-shadow: 0 10px 40px rgba(5,150,105,.35);
animation: slideUp 0.35s cubic-bezier(.34,1.56,.64,1);
```

---

## 6. Frequency Icon System

The medication builder uses two groups of visual frequency indicators:

### Group A — Time of Day (cyan theme)
| Icon | Label | Meaning |
|---|---|---|
| ☀️ | Morning | Take in the morning |
| 🌤️ | Afternoon | Take in the afternoon |
| 🌙 | Night | Take at night |

### Group B — Meal Timing (violet theme)
| Icon | Label | Meaning |
|---|---|---|
| 🌿 | Before Food | Take before meals |
| 🍽️ | After Food | Take after meals |

> **Why icons?** Patients with lower literacy can directly read the prescription symbols. Doctors in the field (rural India) report this significantly reduces medication errors.

---

## 7. Print Template Design

### Letterhead
- Deep cyan gradient: `#0c4a6e → #0891b2`
- Clinic name in Noto Serif 26px (serif = trust/formality)
- Large `℞` watermark at low opacity (18%) — international prescription symbol
- Must pass `print-color-adjust: exact` for colour accuracy

### Triage Strip
- Full-width band below letterhead
- Background and text colour driven by triage level (Critical/Urgent/Routine)

### Print-specific CSS
```css
@media print {
  .no-print { display: none !important; }
  /* Ensure background colours print correctly */
  .letterhead, .rx-table thead, .advice-pill {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```

---

## 8. Accessibility Standards

- Minimum touch target: **48×48px** (WCAG 2.5.5)
- Font minimum: **13px** body, **11px** labels
- Colour contrast: AAA on all interactive elements
- All inputs have visible focus ring (`box-shadow: 0 0 0 2px #22d3ee`)
- Screen reader: all icon buttons have `title` attributes
- Form inputs have explicit `label` elements (hidden on desktop, shown on mobile)

---

## 9. Responsive Breakpoints

Using Tailwind default breakpoints:

| Breakpoint | Width | Layout |
|---|---|---|
| `sm` | 640px | Switch medication table to horizontal grid |
| `md` | 768px | Full multi-column layout |
| (default) | <640px | Single column, stacked labels |

---

## 10. Motion & Animation

| Animation | Duration | Easing | Usage |
|---|---|---|---|
| Mic pulse ring | `1s infinite` | `cubic-bezier(0,0,.2,1)` | Recording state |
| Recording indicator | `1.5s infinite` | `ease-in-out` | STT status bar opacity |
| Toast slide-up | `0.35s` | `cubic-bezier(.34,1.56,.64,1)` | Successful print generation |
| Frequency toggle scale | `0.15s` | `ease` | Button active state |
| Triage pulse dot | `1s infinite` | CSS `pulse` | Header badge |

All animations respect `prefers-reduced-motion` (future enhancement).

---

## 11. File Conventions

| Type | Convention | Example |
|---|---|---|
| HTML pages | kebab-case `.html` | `prescription-print.html` |
| JS modules | kebab-case `.js` | `stt.js` |
| React components | PascalCase `.jsx` | `SmartPrescriptionPanel.jsx` |
| Python modules | snake_case `.py` | `triage_agent.py` |
| Static assets | kebab/snake `.png/.jpg` | `hero_doctor.png` |
