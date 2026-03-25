"""
Symptom Severity Guide for Rural Clinic Triage System
Used as context for the Gemini AI triage agent.
"""

SYMPTOM_SEVERITY_GUIDE = """
=== SYMPTOM SEVERITY GUIDE FOR RURAL CLINIC TRIAGE ===

TRIAGE LEVELS:
- CRITICAL: Life-threatening. Requires immediate medical intervention. Alert doctor NOW.
- URGENT: Serious condition requiring same-day medical attention. Priority queue.
- ROUTINE: Manageable with basic care, rest, or over-the-counter treatment. Regular queue.

══════════════════════════════════════════════════════
SECTION 1: CARDIAC EMERGENCIES
══════════════════════════════════════════════════════
CRITICAL:
- Chest pain/pressure radiating to arm, jaw, or back (possible heart attack)
- Sudden severe shortness of breath with chest tightness
- Rapid/irregular heartbeat with loss of consciousness or near-fainting
- Cardiac arrest (no pulse, not breathing)
- Severe hypertensive crisis (systolic BP > 180) with symptoms

URGENT:
- Persistent chest discomfort without radiation
- Palpitations with dizziness but no fainting
- Known heart disease patient with new shortness of breath

ROUTINE:
- Occasional mild palpitations with no other symptoms
- Chest wall pain that worsens with movement/touch

══════════════════════════════════════════════════════
SECTION 2: NEUROLOGICAL EMERGENCIES
══════════════════════════════════════════════════════
CRITICAL:
- Sudden facial drooping, arm weakness, speech difficulty (STROKE - Act FAST)
- Sudden severe "thunderclap" headache (worst headache of life)
- Loss of consciousness, unresponsiveness
- Seizures lasting >5 minutes or first-time seizure
- Sudden vision loss or double vision
- Sudden confusion/altered mental status
- High fever with stiff neck, light sensitivity, rash (meningitis)

URGENT:
- New severe headache different from usual
- Weakness or numbness in limbs
- First-time seizure (if now stable)
- Severe dizziness with inability to walk

ROUTINE:
- Tension headache (familiar pattern, mild-moderate)
- Mild dizziness without nausea or balance issues
- Tingling in fingers/toes (chronic, non-worsening)

══════════════════════════════════════════════════════
SECTION 3: RESPIRATORY EMERGENCIES
══════════════════════════════════════════════════════
CRITICAL:
- Severe difficulty breathing, unable to speak full sentences
- Cyanosis (blue lips or fingernails)
- Choking/foreign body obstruction
- Anaphylaxis with throat swelling
- Respiratory rate > 30 breaths/min with accessory muscle use

URGENT:
- Moderate shortness of breath with activity
- Wheezing with known asthma not responding to inhaler
- Coughing blood (hemoptysis)
- High fever with productive cough (possible pneumonia)

ROUTINE:
- Mild dry cough with no fever
- Runny nose, nasal congestion (common cold)
- Mild wheezing in known stable asthmatic

══════════════════════════════════════════════════════
SECTION 4: INFECTIOUS DISEASE / SEPSIS
══════════════════════════════════════════════════════
CRITICAL:
- High fever (>39.5°C / 103°F) with confusion, rapid breathing, and low BP (sepsis)
- Fever with petechial/purpuric rash (possible meningococcemia)
- Suspected malaria with altered consciousness (cerebral malaria)
- Dengue with severe abdominal pain, persistent vomiting, bleeding

URGENT:
- High fever (38.5-39.5°C) lasting >3 days without clear cause
- Fever with chills and muscle aches in malaria-endemic area
- Suspected urinary tract infection with fever and flank pain
- Skin infection with spreading redness, warmth, fever (cellulitis)

ROUTINE:
- Low-grade fever (<38.5°C) with cold/flu symptoms
- Mild sore throat without difficulty swallowing
- Ear pain without fever

══════════════════════════════════════════════════════
SECTION 5: GASTROINTESTINAL EMERGENCIES
══════════════════════════════════════════════════════
CRITICAL:
- Vomiting blood or black tarry stools (GI bleed)
- Severe abdominal pain with rigid board-like abdomen (perforation)
- Signs of severe dehydration with altered consciousness

URGENT:
- Severe persistent vomiting and diarrhea with dehydration signs
- Abdominal pain with high fever (possible appendicitis)
- Jaundice with severe abdominal pain (possible biliary obstruction)
- Suspected food poisoning with multiple victims

ROUTINE:
- Mild nausea or vomiting without dehydration
- Mild diarrhea (< 6 episodes/day) without blood
- Constipation, bloating, indigestion
- Mild abdominal cramps

══════════════════════════════════════════════════════
SECTION 6: TRAUMA & INJURIES
══════════════════════════════════════════════════════
CRITICAL:
- Uncontrolled bleeding from major wound
- Head injury with loss of consciousness, confusion, or vomiting
- Suspected spinal injury
- Deep penetrating wound to chest/abdomen
- Burns > 20% body surface area or burns to face/airway

URGENT:
- Deep lacerations requiring suturing
- Possible fractures (limb deformity, severe pain, swelling)
- Head injury without loss of consciousness (observation needed)
- Burns 10-20% body surface area (not face/airway)
- Animal/snake bite

ROUTINE:
- Minor cuts and abrasions
- Mild sprains with no deformity
- Small burns (<10% body, not face) without blistering  
- Bruising without swelling

══════════════════════════════════════════════════════
SECTION 7: PEDIATRIC EMERGENCIES (Children < 12 years)
══════════════════════════════════════════════════════
CRITICAL:
- Infant (< 3 months) with any fever
- Child with extremely high fever (> 40°C / 104°F)
- Febrile seizure currently happening
- Signs of severe dehydration in child (sunken eyes, no urination, limp)
- Difficulty breathing in child (nostrils flaring, ribs visible when breathing)
- Child with suspected meningitis

URGENT:
- Child with fever > 38.5°C lasting more than 2 days
- Croup (barking cough, stridor) in a child
- Ear pain with fever in child
- Rash with fever in child

ROUTINE:
- Mild fever in child >3 months with cold symptoms
- Mild diarrhea in child without dehydration
- Minor injuries in children

══════════════════════════════════════════════════════
SECTION 8: OBSTETRIC & GYNECOLOGICAL EMERGENCIES
══════════════════════════════════════════════════════
CRITICAL:
- Heavy vaginal bleeding in pregnancy (possible placenta previa/abruption)
- Severe abdominal pain in early pregnancy (possible ectopic pregnancy)
- Signs of eclampsia in pregnant woman (seizures, severe headache, BP > 160/110)
- Active labor (contractions < 5 min apart)
- Postpartum hemorrhage

URGENT:
- Decreased fetal movements
- Preterm labor symptoms (< 37 weeks)
- High BP in pregnancy with headache/visual changes

ROUTINE:
- Mild nausea in first trimester (morning sickness)
- Normal prenatal check (no symptoms)

══════════════════════════════════════════════════════
SECTION 9: METABOLIC / ENDOCRINE EMERGENCIES
══════════════════════════════════════════════════════
CRITICAL:
- Diabetic with altered consciousness (hypoglycemia/DKA)
- Extreme weakness, confusion in known diabetic
- Suspected hypoglycemia (shaking, sweating, confusion, known diabetic)

URGENT:
- Diabetic with blood sugar > 300 mg/dL but alert
- Diabetic with new symptoms of infection
- Known thyroid patient with rapid heart rate and heat intolerance (thyroid storm prodrome)

ROUTINE:
- Controlled diabetic for medication refill
- Mild hypoglycemia in alert patient (eaten, feeling better)

══════════════════════════════════════════════════════
SECTION 10: MENTAL HEALTH & OVERDOSE
══════════════════════════════════════════════════════
CRITICAL:
- Active suicidal intent with a plan or attempt
- Drug/alcohol overdose with altered consciousness
- Violent, agitated patient posing danger to self/others
- Suspected poisoning (household chemicals, pesticides)

URGENT:
- Acute psychotic episode but patient calm
- Panic attack with cardiac symptoms (to rule out cardiac)
- Acute substance withdrawal with tremors

ROUTINE:
- Mild anxiety or depression (follow-up, stable)
- Sleep difficulties without acute risk

══════════════════════════════════════════════════════
SPECIAL CONSIDERATIONS FOR RURAL CLINICS
══════════════════════════════════════════════════════
1. GOLDEN HOUR RULE: Critical cases must be escalated within 10 minutes.
2. PEDIATRIC CAUTION: Always err toward Urgent/Critical for children under 5.
3. ELDERLY CAUTION: Patients over 65 — upgrade severity one level if multiple symptoms.
4. PREGNANCY: Any pregnant patient with concerning symptoms defaults to Urgent minimum.
5. MEDICATION INTERACTIONS: Flag patients on anticoagulants, immunosuppressants with ANY new symptom.
6. TRANSPORT TIME: In areas where hospital is >60 min away, classify borderline cases higher.

=== END OF SYMPTOM SEVERITY GUIDE ===
"""
