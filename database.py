"""
Database module for College Student Management System.
Handles all SQLite database operations.
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "college.db")
PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")


def _ensure_photos_dir():
    os.makedirs(PHOTOS_DIR, exist_ok=True)


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    """Create all tables if they do not exist and seed default settings."""
    _ensure_photos_dir()
    conn = get_connection()
    cur = conn.cursor()

    # Settings table (key-value store)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Students table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      TEXT    UNIQUE NOT NULL,
            first_name      TEXT    NOT NULL,
            last_name       TEXT    NOT NULL,
            date_of_birth   TEXT,
            gender          TEXT,
            email           TEXT,
            phone           TEXT,
            address         TEXT,
            program         TEXT,
            semester        TEXT,
            enrollment_date TEXT,
            status          TEXT    DEFAULT 'Active',
            photo_path      TEXT,
            father_name     TEXT,
            mother_name     TEXT,
            guardian_name   TEXT,
            guardian_phone  TEXT,
            blood_group     TEXT,
            cnic            TEXT,
            religion        TEXT,
            nationality     TEXT,
            emergency_contact TEXT,
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Migrate students table if columns are missing (upgrade path)
    _add_column_if_missing(cur, "students", "photo_path", "TEXT")
    _add_column_if_missing(cur, "students", "father_name", "TEXT")
    _add_column_if_missing(cur, "students", "mother_name", "TEXT")
    _add_column_if_missing(cur, "students", "guardian_name", "TEXT")
    _add_column_if_missing(cur, "students", "guardian_phone", "TEXT")
    _add_column_if_missing(cur, "students", "blood_group", "TEXT")
    _add_column_if_missing(cur, "students", "cnic", "TEXT")
    _add_column_if_missing(cur, "students", "religion", "TEXT")
    _add_column_if_missing(cur, "students", "nationality", "TEXT")
    _add_column_if_missing(cur, "students", "emergency_contact", "TEXT")

    # Fees table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT    NOT NULL,
            fee_type     TEXT    NOT NULL,
            amount       REAL    NOT NULL,
            currency     TEXT    NOT NULL DEFAULT 'USD',
            due_date     TEXT,
            paid_date    TEXT,
            status       TEXT    DEFAULT 'Pending',
            description  TEXT,
            created_at   TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    # Staff / Salary table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id        TEXT    UNIQUE NOT NULL,
            first_name      TEXT    NOT NULL,
            last_name       TEXT    NOT NULL,
            department      TEXT,
            designation     TEXT,
            email           TEXT,
            phone           TEXT,
            salary          REAL    NOT NULL DEFAULT 0.0,
            currency        TEXT    NOT NULL DEFAULT 'USD',
            join_date       TEXT,
            status          TEXT    DEFAULT 'Active',
            photo_path      TEXT,
            father_name     TEXT,
            mother_name     TEXT,
            blood_group     TEXT,
            cnic            TEXT,
            religion        TEXT,
            nationality     TEXT,
            emergency_contact TEXT,
            qualification   TEXT,
            experience_years TEXT,
            created_at      TEXT    DEFAULT (datetime('now'))
        )
    """)

    _add_column_if_missing(cur, "staff", "photo_path", "TEXT")
    _add_column_if_missing(cur, "staff", "father_name", "TEXT")
    _add_column_if_missing(cur, "staff", "mother_name", "TEXT")
    _add_column_if_missing(cur, "staff", "blood_group", "TEXT")
    _add_column_if_missing(cur, "staff", "cnic", "TEXT")
    _add_column_if_missing(cur, "staff", "religion", "TEXT")
    _add_column_if_missing(cur, "staff", "nationality", "TEXT")
    _add_column_if_missing(cur, "staff", "emergency_contact", "TEXT")
    _add_column_if_missing(cur, "staff", "qualification", "TEXT")
    _add_column_if_missing(cur, "staff", "experience_years", "TEXT")

    # Salary payments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS salary_payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id    TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            currency    TEXT    NOT NULL DEFAULT 'USD',
            month       TEXT    NOT NULL,
            year        TEXT    NOT NULL,
            paid_date   TEXT,
            status      TEXT    DEFAULT 'Pending',
            notes       TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
        )
    """)

    # Invoices table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT    UNIQUE NOT NULL,
            invoice_type   TEXT    NOT NULL,
            reference_id   TEXT,
            recipient_name TEXT    NOT NULL,
            recipient_email TEXT,
            amount         REAL    NOT NULL,
            currency       TEXT    NOT NULL DEFAULT 'USD',
            issue_date     TEXT    NOT NULL,
            due_date       TEXT,
            status         TEXT    DEFAULT 'Unpaid',
            notes          TEXT,
            created_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Subjects table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT   UNIQUE NOT NULL,
            subject_name TEXT   NOT NULL,
            program      TEXT,
            semester     TEXT,
            credit_hours INTEGER DEFAULT 3,
            description  TEXT,
            created_at   TEXT   DEFAULT (datetime('now'))
        )
    """)

    # Teacher–Subject assignment table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teacher_subjects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id    TEXT    NOT NULL,
            subject_code TEXT   NOT NULL,
            academic_year TEXT,
            assigned_date TEXT  DEFAULT (date('now')),
            UNIQUE(staff_id, subject_code, academic_year),
            FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code)
        )
    """)

    # Student–Subject enrollment table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT    NOT NULL,
            subject_code TEXT    NOT NULL,
            academic_year TEXT,
            grade        TEXT,
            marks        REAL,
            enrolled_date TEXT   DEFAULT (date('now')),
            UNIQUE(student_id, subject_code, academic_year),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code)
        )
    """)

    # Attendance table (shared for students and staff)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            person_type   TEXT    NOT NULL CHECK(person_type IN ('student','staff')),
            person_id     TEXT    NOT NULL,
            attendance_date TEXT  NOT NULL,
            status        TEXT    NOT NULL DEFAULT 'Present'
                          CHECK(status IN ('Present','Absent','Late','Leave')),
            remarks       TEXT,
            recorded_by   TEXT,
            created_at    TEXT    DEFAULT (datetime('now')),
            UNIQUE(person_type, person_id, attendance_date)
        )
    """)

    # Notices / Announcements table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            content     TEXT    NOT NULL,
            category    TEXT    DEFAULT 'General',
            audience    TEXT    DEFAULT 'All',
            posted_by   TEXT,
            posted_date TEXT    DEFAULT (date('now')),
            expiry_date TEXT,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Seed default settings
    defaults = {
        "institution_name": "My College",
        "institution_address": "123 College Street",
        "institution_phone": "+1-000-000-0000",
        "institution_email": "admin@mycollege.edu",
        "default_currency": "USD",
        "currency_symbol": "$",
        "available_currencies": "USD,EUR,GBP,PKR,INR,AED,SAR,CAD,AUD,JPY",
        "theme": "default",
        "fee_types": "Tuition,Library,Laboratory,Sports,Transport,Exam,Hostel,Miscellaneous",
        "title_font": "Segoe UI",
        "title_font_size": "20",
        "title_bold": "1",
        "title_color": "#FFFFFF",
        "title_bg_color": "#2C3E50",
        "academic_year": str(datetime.now().year),
    }
    for key, value in defaults.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value)
        )

    conn.commit()
    conn.close()


def _add_column_if_missing(cur, table, column, col_type):
    """Add a column to a table if it does not already exist."""
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if column not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


# ─── Settings helpers ─────────────────────────────────────────────────────────

def get_setting(key):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


# ─── Student helpers ───────────────────────────────────────────────────────────

def add_student(data):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO students
                (student_id, first_name, last_name, date_of_birth, gender,
                 email, phone, address, program, semester, enrollment_date, status,
                 photo_path, father_name, mother_name, guardian_name, guardian_phone,
                 blood_group, cnic, religion, nationality, emergency_contact)
            VALUES
                (:student_id, :first_name, :last_name, :date_of_birth, :gender,
                 :email, :phone, :address, :program, :semester, :enrollment_date, :status,
                 :photo_path, :father_name, :mother_name, :guardian_name, :guardian_phone,
                 :blood_group, :cnic, :religion, :nationality, :emergency_contact)
        """, data)
        conn.commit()
        return True, "Student added successfully."
    except sqlite3.IntegrityError:
        return False, f"Student ID '{data['student_id']}' already exists."
    finally:
        conn.close()


def update_student(data):
    conn = get_connection()
    conn.execute("""
        UPDATE students SET
            first_name=:first_name, last_name=:last_name,
            date_of_birth=:date_of_birth, gender=:gender,
            email=:email, phone=:phone, address=:address,
            program=:program, semester=:semester,
            enrollment_date=:enrollment_date, status=:status,
            photo_path=:photo_path, father_name=:father_name,
            mother_name=:mother_name, guardian_name=:guardian_name,
            guardian_phone=:guardian_phone, blood_group=:blood_group,
            cnic=:cnic, religion=:religion, nationality=:nationality,
            emergency_contact=:emergency_contact
        WHERE student_id=:student_id
    """, data)
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY first_name, last_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_students(query):
    conn = get_connection()
    like = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM students
        WHERE student_id LIKE ? OR first_name LIKE ? OR last_name LIKE ?
              OR email LIKE ? OR program LIKE ?
        ORDER BY first_name, last_name
    """, (like, like, like, like, like)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student(student_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Fee helpers ───────────────────────────────────────────────────────────────

def add_fee(data):
    conn = get_connection()
    conn.execute("""
        INSERT INTO fees
            (student_id, fee_type, amount, currency, due_date, paid_date, status, description)
        VALUES
            (:student_id, :fee_type, :amount, :currency, :due_date, :paid_date, :status, :description)
    """, data)
    conn.commit()
    conn.close()


def update_fee(data):
    conn = get_connection()
    conn.execute("""
        UPDATE fees SET
            fee_type=:fee_type, amount=:amount, currency=:currency,
            due_date=:due_date, paid_date=:paid_date, status=:status,
            description=:description
        WHERE id=:id
    """, data)
    conn.commit()
    conn.close()


def delete_fee(fee_id):
    conn = get_connection()
    conn.execute("DELETE FROM fees WHERE id = ?", (fee_id,))
    conn.commit()
    conn.close()


def get_fees_for_student(student_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM fees WHERE student_id = ? ORDER BY due_date DESC", (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_fees():
    conn = get_connection()
    rows = conn.execute("""
        SELECT f.*, s.first_name, s.last_name
        FROM fees f
        LEFT JOIN students s ON f.student_id = s.student_id
        ORDER BY f.due_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Staff helpers ─────────────────────────────────────────────────────────────

def add_staff(data):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO staff
                (staff_id, first_name, last_name, department, designation,
                 email, phone, salary, currency, join_date, status,
                 photo_path, father_name, mother_name, blood_group, cnic,
                 religion, nationality, emergency_contact, qualification, experience_years)
            VALUES
                (:staff_id, :first_name, :last_name, :department, :designation,
                 :email, :phone, :salary, :currency, :join_date, :status,
                 :photo_path, :father_name, :mother_name, :blood_group, :cnic,
                 :religion, :nationality, :emergency_contact, :qualification, :experience_years)
        """, data)
        conn.commit()
        return True, "Staff member added successfully."
    except sqlite3.IntegrityError:
        return False, f"Staff ID '{data['staff_id']}' already exists."
    finally:
        conn.close()


def update_staff(data):
    conn = get_connection()
    conn.execute("""
        UPDATE staff SET
            first_name=:first_name, last_name=:last_name,
            department=:department, designation=:designation,
            email=:email, phone=:phone, salary=:salary, currency=:currency,
            join_date=:join_date, status=:status,
            photo_path=:photo_path, father_name=:father_name,
            mother_name=:mother_name, blood_group=:blood_group, cnic=:cnic,
            religion=:religion, nationality=:nationality,
            emergency_contact=:emergency_contact, qualification=:qualification,
            experience_years=:experience_years
        WHERE staff_id=:staff_id
    """, data)
    conn.commit()
    conn.close()


def delete_staff(staff_id):
    conn = get_connection()
    conn.execute("DELETE FROM staff WHERE staff_id = ?", (staff_id,))
    conn.commit()
    conn.close()


def get_all_staff():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM staff ORDER BY first_name, last_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_staff(staff_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM staff WHERE staff_id = ?", (staff_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def search_staff(query):
    conn = get_connection()
    like = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM staff
        WHERE staff_id LIKE ? OR first_name LIKE ? OR last_name LIKE ?
              OR department LIKE ? OR designation LIKE ?
        ORDER BY first_name, last_name
    """, (like, like, like, like, like)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Salary payment helpers ────────────────────────────────────────────────────

def add_salary_payment(data):
    conn = get_connection()
    conn.execute("""
        INSERT INTO salary_payments
            (staff_id, amount, currency, month, year, paid_date, status, notes)
        VALUES
            (:staff_id, :amount, :currency, :month, :year, :paid_date, :status, :notes)
    """, data)
    conn.commit()
    conn.close()


def update_salary_payment(data):
    conn = get_connection()
    conn.execute("""
        UPDATE salary_payments SET
            amount=:amount, currency=:currency, month=:month, year=:year,
            paid_date=:paid_date, status=:status, notes=:notes
        WHERE id=:id
    """, data)
    conn.commit()
    conn.close()


def delete_salary_payment(payment_id):
    conn = get_connection()
    conn.execute("DELETE FROM salary_payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()


def get_salary_payments_for_staff(staff_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM salary_payments WHERE staff_id = ? ORDER BY year DESC, month DESC",
        (staff_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_salary_payments():
    conn = get_connection()
    rows = conn.execute("""
        SELECT sp.*, s.first_name, s.last_name, s.designation
        FROM salary_payments sp
        LEFT JOIN staff s ON sp.staff_id = s.staff_id
        ORDER BY sp.year DESC, sp.month DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Invoice helpers ───────────────────────────────────────────────────────────

def _next_invoice_number():
    conn = get_connection()
    row = conn.execute(
        "SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row:
        try:
            num = int(row["invoice_number"].split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"INV-{num:05d}"


def add_invoice(data):
    data.setdefault("invoice_number", _next_invoice_number())
    conn = get_connection()
    conn.execute("""
        INSERT INTO invoices
            (invoice_number, invoice_type, reference_id, recipient_name,
             recipient_email, amount, currency, issue_date, due_date, status, notes)
        VALUES
            (:invoice_number, :invoice_type, :reference_id, :recipient_name,
             :recipient_email, :amount, :currency, :issue_date, :due_date, :status, :notes)
    """, data)
    conn.commit()
    conn.close()
    return data["invoice_number"]


def update_invoice(data):
    conn = get_connection()
    conn.execute("""
        UPDATE invoices SET
            invoice_type=:invoice_type, reference_id=:reference_id,
            recipient_name=:recipient_name, recipient_email=:recipient_email,
            amount=:amount, currency=:currency, issue_date=:issue_date,
            due_date=:due_date, status=:status, notes=:notes
        WHERE id=:id
    """, data)
    conn.commit()
    conn.close()


def delete_invoice(invoice_id):
    conn = get_connection()
    conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    conn.commit()
    conn.close()


def get_all_invoices():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM invoices ORDER BY issue_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice(invoice_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Subjects helpers ──────────────────────────────────────────────────────────

def add_subject(data):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO subjects
                (subject_code, subject_name, program, semester, credit_hours, description)
            VALUES
                (:subject_code, :subject_name, :program, :semester, :credit_hours, :description)
        """, data)
        conn.commit()
        return True, "Subject added successfully."
    except sqlite3.IntegrityError:
        return False, f"Subject code '{data['subject_code']}' already exists."
    finally:
        conn.close()


def update_subject(data):
    conn = get_connection()
    conn.execute("""
        UPDATE subjects SET
            subject_name=:subject_name, program=:program, semester=:semester,
            credit_hours=:credit_hours, description=:description
        WHERE subject_code=:subject_code
    """, data)
    conn.commit()
    conn.close()


def delete_subject(subject_code):
    conn = get_connection()
    conn.execute("DELETE FROM subjects WHERE subject_code = ?", (subject_code,))
    conn.commit()
    conn.close()


def get_all_subjects():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM subjects ORDER BY subject_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_subject(subject_code):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM subjects WHERE subject_code = ?", (subject_code,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Teacher–Subject helpers ───────────────────────────────────────────────────

def assign_teacher_subject(staff_id, subject_code, academic_year):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO teacher_subjects (staff_id, subject_code, academic_year)
            VALUES (?, ?, ?)
        """, (staff_id, subject_code, academic_year))
        conn.commit()
        return True, "Subject assigned to teacher."
    except sqlite3.IntegrityError:
        return False, "This subject is already assigned to the teacher for this year."
    finally:
        conn.close()


def remove_teacher_subject(record_id):
    conn = get_connection()
    conn.execute("DELETE FROM teacher_subjects WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def get_teacher_subjects(staff_id, academic_year=None):
    conn = get_connection()
    if academic_year:
        rows = conn.execute("""
            SELECT ts.*, s.subject_name, s.program, s.credit_hours
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_code = s.subject_code
            WHERE ts.staff_id = ? AND ts.academic_year = ?
        """, (staff_id, academic_year)).fetchall()
    else:
        rows = conn.execute("""
            SELECT ts.*, s.subject_name, s.program, s.credit_hours
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_code = s.subject_code
            WHERE ts.staff_id = ?
        """, (staff_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_teacher_subjects(academic_year=None):
    conn = get_connection()
    if academic_year:
        rows = conn.execute("""
            SELECT ts.*, s.subject_name, s.program,
                   st.first_name, st.last_name, st.department
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_code = s.subject_code
            JOIN staff st ON ts.staff_id = st.staff_id
            WHERE ts.academic_year = ?
            ORDER BY st.first_name, s.subject_name
        """, (academic_year,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT ts.*, s.subject_name, s.program,
                   st.first_name, st.last_name, st.department
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_code = s.subject_code
            JOIN staff st ON ts.staff_id = st.staff_id
            ORDER BY st.first_name, s.subject_name
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Student–Subject enrollment helpers ───────────────────────────────────────

def enroll_student_subject(data):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO student_subjects
                (student_id, subject_code, academic_year, grade, marks)
            VALUES
                (:student_id, :subject_code, :academic_year, :grade, :marks)
        """, data)
        conn.commit()
        return True, "Student enrolled in subject."
    except sqlite3.IntegrityError:
        return False, "Student is already enrolled in this subject for this year."
    finally:
        conn.close()


def update_student_subject(data):
    conn = get_connection()
    conn.execute("""
        UPDATE student_subjects SET grade=:grade, marks=:marks
        WHERE id=:id
    """, data)
    conn.commit()
    conn.close()


def remove_student_subject(record_id):
    conn = get_connection()
    conn.execute("DELETE FROM student_subjects WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def get_student_subjects(student_id, academic_year=None):
    conn = get_connection()
    if academic_year:
        rows = conn.execute("""
            SELECT ss.*, s.subject_name, s.program, s.credit_hours
            FROM student_subjects ss
            JOIN subjects s ON ss.subject_code = s.subject_code
            WHERE ss.student_id = ? AND ss.academic_year = ?
        """, (student_id, academic_year)).fetchall()
    else:
        rows = conn.execute("""
            SELECT ss.*, s.subject_name, s.program, s.credit_hours
            FROM student_subjects ss
            JOIN subjects s ON ss.subject_code = s.subject_code
            WHERE ss.student_id = ?
        """, (student_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Attendance helpers ────────────────────────────────────────────────────────

def mark_attendance(person_type, person_id, attendance_date, status, remarks="", recorded_by=""):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO attendance
                (person_type, person_id, attendance_date, status, remarks, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (person_type, person_id, attendance_date, status, remarks, recorded_by))
        conn.commit()
        return True, "Attendance marked."
    except sqlite3.IntegrityError:
        # Update existing record
        conn.execute("""
            UPDATE attendance SET status=?, remarks=?, recorded_by=?
            WHERE person_type=? AND person_id=? AND attendance_date=?
        """, (status, remarks, recorded_by, person_type, person_id, attendance_date))
        conn.commit()
        return True, "Attendance updated."
    finally:
        conn.close()


def get_attendance(person_type, person_id=None, from_date=None, to_date=None):
    conn = get_connection()
    query = "SELECT * FROM attendance WHERE person_type = ?"
    params = [person_type]
    if person_id:
        query += " AND person_id = ?"
        params.append(person_id)
    if from_date:
        query += " AND attendance_date >= ?"
        params.append(from_date)
    if to_date:
        query += " AND attendance_date <= ?"
        params.append(to_date)
    query += " ORDER BY attendance_date DESC, person_id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_attendance_for_date(person_type, attendance_date):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM attendance
        WHERE person_type = ? AND attendance_date = ?
        ORDER BY person_id
    """, (person_type, attendance_date)).fetchall()
    conn.close()
    return {r["person_id"]: dict(r) for r in rows}


def get_attendance_summary(person_type, person_id, from_date=None, to_date=None):
    """Return counts of each status for a person."""
    records = get_attendance(person_type, person_id, from_date, to_date)
    summary = {"Present": 0, "Absent": 0, "Late": 0, "Leave": 0, "total": len(records)}
    for r in records:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    return summary


def delete_attendance(attendance_id):
    conn = get_connection()
    conn.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    conn.commit()
    conn.close()


# ─── Notices helpers ───────────────────────────────────────────────────────────

def add_notice(data):
    conn = get_connection()
    conn.execute("""
        INSERT INTO notices
            (title, content, category, audience, posted_by, posted_date, expiry_date, is_active)
        VALUES
            (:title, :content, :category, :audience, :posted_by, :posted_date, :expiry_date, :is_active)
    """, data)
    conn.commit()
    conn.close()


def update_notice(data):
    conn = get_connection()
    conn.execute("""
        UPDATE notices SET
            title=:title, content=:content, category=:category,
            audience=:audience, posted_by=:posted_by, posted_date=:posted_date,
            expiry_date=:expiry_date, is_active=:is_active
        WHERE id=:id
    """, data)
    conn.commit()
    conn.close()


def delete_notice(notice_id):
    conn = get_connection()
    conn.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    conn.commit()
    conn.close()


def get_all_notices(active_only=False):
    conn = get_connection()
    if active_only:
        rows = conn.execute(
            "SELECT * FROM notices WHERE is_active = 1 ORDER BY posted_date DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notices ORDER BY posted_date DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_notice(notice_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notices WHERE id = ?", (notice_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Analytics helpers (AI insights) ──────────────────────────────────────────

def get_attendance_analytics():
    """Return institution-wide attendance statistics."""
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")

    # Overall student attendance this month
    rows = conn.execute("""
        SELECT status, COUNT(*) as cnt
        FROM attendance
        WHERE person_type='student' AND attendance_date LIKE ?
        GROUP BY status
    """, (f"{this_month}%",)).fetchall()
    student_att = {r["status"]: r["cnt"] for r in rows}

    # Overall staff attendance this month
    rows = conn.execute("""
        SELECT status, COUNT(*) as cnt
        FROM attendance
        WHERE person_type='staff' AND attendance_date LIKE ?
        GROUP BY status
    """, (f"{this_month}%",)).fetchall()
    staff_att = {r["status"]: r["cnt"] for r in rows}

    # Chronic absentees (>3 absences this month)
    rows = conn.execute("""
        SELECT person_id, COUNT(*) as absent_count
        FROM attendance
        WHERE person_type='student' AND status='Absent' AND attendance_date LIKE ?
        GROUP BY person_id
        HAVING absent_count >= 3
        ORDER BY absent_count DESC
        LIMIT 10
    """, (f"{this_month}%",)).fetchall()
    absentees = [dict(r) for r in rows]

    conn.close()
    return {
        "student_attendance": student_att,
        "staff_attendance": staff_att,
        "chronic_absentees": absentees,
        "month": this_month,
    }


def get_fee_analytics():
    """Return fee collection analytics."""
    conn = get_connection()
    this_month = datetime.now().strftime("%Y-%m")

    total_pending = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM fees WHERE status='Pending'"
    ).fetchone()["total"]

    total_collected = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM fees WHERE status='Paid'"
    ).fetchone()["total"]

    overdue = conn.execute("""
        SELECT COUNT(*) as cnt FROM fees
        WHERE status='Pending' AND due_date < date('now')
    """).fetchone()["cnt"]

    # Top defaulters
    rows = conn.execute("""
        SELECT student_id, SUM(amount) as total_due
        FROM fees WHERE status='Pending'
        GROUP BY student_id
        ORDER BY total_due DESC
        LIMIT 5
    """).fetchall()
    defaulters = [dict(r) for r in rows]

    conn.close()
    return {
        "total_pending": total_pending,
        "total_collected": total_collected,
        "overdue_count": overdue,
        "top_defaulters": defaulters,
    }

