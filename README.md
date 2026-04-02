# College Student Database & Management System

A professional, multi-feature desktop management system built with Python (Tkinter + SQLite).
Suitable for schools, colleges, computer colleges, technical/vocational colleges, and short-course institutions.

---

## ✨ Features

### Core Management
- **🎓 Student Management** – Add, edit, delete students with full biodata, photo upload, blood group, CNIC, guardian contacts, and more
- **👥 Staff & Teacher Management** – Complete staff/teacher records with photo, biodata, qualifications, salary and payment tracking
- **💳 Fee Management** – Track all fee types, mark payments, view pending/overdue fees
- **🧾 Invoices** – Generate and manage invoices for students and staff
- **⚙️ Settings** – Configure institution name, currencies, fee types, title style, and academic year

### New Features (v2.0)
- **📋 Attendance** – Mark and track student & teacher attendance daily (Present / Absent / Late / Leave), with date navigation and monthly reports
- **📚 Subjects & Enrollment** – Manage subjects, assign subjects to teachers, enroll students in subjects with grade/marks tracking
- **📣 Notices & Announcements** – Post, edit and view announcements for students, staff, or all audiences
- **🤖 AI Analytics Dashboard** – Smart insights: attendance percentage, chronic absentees alert, fee defaulter highlights, overdue payments
- **🖼 Photo Uploads** – Student and teacher profile photos stored locally
- **📇 Biodata Cards** – Detailed biodata viewer with photo for students and teachers
- **🎨 Customizable Title Style** – Change sidebar font, size, and colors from Settings

---

## 🚀 Getting Started

### Requirements
- Python 3.10+
- Pillow (for photo support)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

### Build Windows .exe
```bash
pyinstaller app.spec
```

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| `main.py` | Application entry point, navigation |
| `database.py` | SQLite database layer, all CRUD operations |
| `utils.py` | Shared colors, fonts, widget helpers |
| `dashboard_frame.py` | Dashboard with stats cards and AI insights |
| `students_frame.py` | Student management with photo & biodata |
| `salary_frame.py` | Staff management, salary payments |
| `attendance_frame.py` | Student & teacher attendance |
| `subjects_frame.py` | Subjects, teacher assignments, student enrollment |
| `notices_frame.py` | Announcements board |
| `fees_frame.py` | Fee management |
| `invoices_frame.py` | Invoice management |
| `settings_frame.py` | App configuration |

---

## 🏫 Suitable For
- Schools & Colleges
- Computer Colleges
- Technical & Vocational Colleges
- Short Course Institutions
