"""
Database module for College Student Management System.
Handles all SQLite database operations.
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "college.db")


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    """Create all tables if they do not exist and seed default settings."""
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
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id    TEXT    UNIQUE NOT NULL,
            first_name    TEXT    NOT NULL,
            last_name     TEXT    NOT NULL,
            date_of_birth TEXT,
            gender        TEXT,
            email         TEXT,
            phone         TEXT,
            address       TEXT,
            program       TEXT,
            semester      TEXT,
            enrollment_date TEXT,
            status        TEXT    DEFAULT 'Active',
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id    TEXT    UNIQUE NOT NULL,
            first_name  TEXT    NOT NULL,
            last_name   TEXT    NOT NULL,
            department  TEXT,
            designation TEXT,
            email       TEXT,
            phone       TEXT,
            salary      REAL    NOT NULL DEFAULT 0.0,
            currency    TEXT    NOT NULL DEFAULT 'USD',
            join_date   TEXT,
            status      TEXT    DEFAULT 'Active',
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

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
    }
    for key, value in defaults.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value)
        )

    conn.commit()
    conn.close()


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
                 email, phone, address, program, semester, enrollment_date, status)
            VALUES
                (:student_id, :first_name, :last_name, :date_of_birth, :gender,
                 :email, :phone, :address, :program, :semester, :enrollment_date, :status)
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
            enrollment_date=:enrollment_date, status=:status
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
                 email, phone, salary, currency, join_date, status)
            VALUES
                (:staff_id, :first_name, :last_name, :department, :designation,
                 :email, :phone, :salary, :currency, :join_date, :status)
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
            join_date=:join_date, status=:status
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
