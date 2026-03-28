# College Management System

A complete **College & School Management Database** built with Python/Flask.  
Developer: **Zulfiqar Ali** — [www.maxtechfix.com](http://www.maxtechfix.com)

---

## Features

- Student bio-data (add / edit / delete / view) with photo upload
- Gender, CNIC, contact, address fields
- Departments: Computer Science, Commerce, Arts, Pre-Medical, Pre-Engineering
- Computer Science courses: short courses, programming, graphic design, freelancing, hardware & networking, web dev, AI/ML, mobile apps
- School classes 1–10 with standard subjects
- Print student profiles and class lists
- SQLite database backup (download) and restore (upload)
- Customisable institute name, tagline and colour theme (Settings page)
- Works **fully offline** on a local PC – no internet required after setup

---

## Option A – Run the pre-built EXE (end users)

> No Python or extra software needed.

1. Download the **`CollegeManagement`** folder from the [Releases](../../releases) page.
2. Double-click **`CollegeManagement.exe`** (Windows) or run **`./CollegeManagement`** (Linux/macOS).
3. Your default browser opens automatically at `http://127.0.0.1:5000`.
4. All data (database, uploaded photos, backups) is stored **next to the exe** in the same folder.

---

## Option B – Build the EXE yourself (developers)

### Prerequisites
- Python 3.10 or newer — [python.org](https://www.python.org/downloads/)
- Windows, Linux, or macOS

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/redsky991-byte/collage-student-data-base-and-manegement-.git
cd collage-student-data-base-and-manegement-

# 2. (Optional) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Run the one-command build script
python build.py
```

The finished application appears in **`dist/CollegeManagement/`**.  
Zip that folder and distribute it — recipients need no Python installed.

---

## Option C – Run from source (developers)

```bash
pip install -r requirements.txt
python app.py
# → open http://127.0.0.1:5000
```

---

## Project structure

```
app.py                  Flask application (models + routes)
college_mgmt.spec       PyInstaller build spec
build.py                One-command build helper
requirements.txt        Runtime dependencies
requirements-build.txt  Build-time dependency (PyInstaller)
templates/              Jinja2 HTML templates
static/                 Static assets (CSS embedded, uploads folder)
```
