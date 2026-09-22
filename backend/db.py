import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Doctors Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                specialization TEXT,
                license TEXT,
                clinic TEXT,
                pincode TEXT,
                fee INTEGER,
                upi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Waiting List Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waiting_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE,
                doctor_id TEXT,
                patient_name TEXT,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                email TEXT,
                symptoms TEXT,
                duration TEXT,
                pain_scale INTEGER,
                consciousness TEXT,
                medical_history TEXT,
                medications TEXT,
                allergies TEXT,
                triage_level TEXT,
                ai_reasoning TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')

def get_doctor_by_id(doctor_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_doctor_by_email(email):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_doctor(doctor_data):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO doctors (id, name, email, password, specialization, license, clinic, pincode, fee, upi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doctor_data.get('id'), doctor_data.get('name'), doctor_data.get('email'),
            doctor_data.get('password'), doctor_data.get('specialization'),
            doctor_data.get('license'), doctor_data.get('clinic'),
            doctor_data.get('pincode'), doctor_data.get('fee', 0),
            doctor_data.get('upi')
        ))
        return doctor_data.get('id')

def get_all_doctors():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, specialization, clinic, pincode, fee, upi FROM doctors")
        return [dict(row) for row in cursor.fetchall()]

# Initialize on import
init_db()
