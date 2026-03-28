import os
import sys
import shutil
import json
import threading
import time
import webbrowser
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import or_

# ── Path detection (normal Python vs PyInstaller frozen exe) ─────────────────
# BUNDLE_DIR  – read-only assets bundled into the exe (templates, static CSS)
# APP_DIR     – writable directory next to the exe (database, uploads, backups)
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.abspath(os.path.dirname(__file__))
    APP_DIR = BUNDLE_DIR

UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
BACKUP_FOLDER = os.path.join(APP_DIR, 'backups')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(BUNDLE_DIR, 'templates'),
    static_folder=os.path.join(BUNDLE_DIR, 'static'),
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college-mgmt-secret-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(APP_DIR, 'college.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, default='')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    students = db.relationship('Student', backref='department', lazy=True)
    subjects = db.relationship('Subject', backref='department', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    description = db.Column(db.Text)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    father_name = db.Column(db.String(200))
    mother_name = db.Column(db.String(200))
    gender = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.String(20))
    cnic_number = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(200))
    address = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    class_name = db.Column(db.String(100))
    subjects = db.Column(db.Text)
    photo = db.Column(db.String(300), default='')
    admission_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_setting(key, default=''):
    s = Setting.query.filter_by(key=key).first()
    return s.value if s else default

def set_setting(key, value):
    s = Setting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        s = Setting(key=key, value=value)
        db.session.add(s)
    db.session.commit()

def seed_default_data():
    if Department.query.count() == 0:
        depts = [
            Department(name='Computer Science (CS)', type='college', description='Computer Science & IT programs'),
            Department(name='Commerce', type='college', description='Business and Commerce programs'),
            Department(name='Arts & Humanities', type='college', description='Arts, Literature and Humanities'),
            Department(name='Science (Pre-Medical)', type='college', description='Biology, Chemistry, Physics'),
            Department(name='Science (Pre-Engineering)', type='college', description='Math, Physics, Chemistry'),
        ]
        for c in range(1, 11):
            depts.append(Department(name=f'Class {c}', type='school', description=f'School Class {c}'))
        db.session.add_all(depts)
        db.session.commit()

        cs = Department.query.filter_by(name='Computer Science (CS)').first()
        cs_subjects = [
            Subject(name='Short Computer Courses', department_id=cs.id, description='Basic computer skills & MS Office'),
            Subject(name='Programming Languages (C++, Java, Python)', department_id=cs.id, description='Software development languages'),
            Subject(name='Graphic Design Courses (Adobe, CorelDRAW)', department_id=cs.id, description='Graphic design & multimedia'),
            Subject(name='Freelancing & Digital Marketing', department_id=cs.id, description='Online earning & digital skills'),
            Subject(name='Hardware & Networking Courses', department_id=cs.id, description='Computer hardware, A+ certification'),
            Subject(name='Web Development', department_id=cs.id, description='HTML, CSS, JavaScript, PHP'),
            Subject(name='Database Management', department_id=cs.id, description='SQL, MySQL, Oracle'),
            Subject(name='Artificial Intelligence & ML', department_id=cs.id, description='AI and Machine Learning basics'),
            Subject(name='Mobile App Development', department_id=cs.id, description='Android & iOS development'),
        ]
        db.session.add_all(cs_subjects)

        comm = Department.query.filter_by(name='Commerce').first()
        comm_subjects = [
            Subject(name='Accounting', department_id=comm.id),
            Subject(name='Business Studies', department_id=comm.id),
            Subject(name='Economics', department_id=comm.id),
            Subject(name='Statistics', department_id=comm.id),
            Subject(name='Urdu', department_id=comm.id),
            Subject(name='English', department_id=comm.id),
            Subject(name='Islamiyat', department_id=comm.id),
        ]
        db.session.add_all(comm_subjects)

        school_subjects_list = ['Mathematics', 'English', 'Urdu', 'Islamiyat (or Ethics)', 'General Science',
                                 'Social Studies', 'Computer Education', 'Drawing & Arts', 'Nazra Quran']
        for dept in Department.query.filter_by(type='school').all():
            for sname in school_subjects_list:
                db.session.add(Subject(name=sname, department_id=dept.id))

        pm = Department.query.filter_by(name='Science (Pre-Medical)').first()
        for sname in ['Biology', 'Chemistry', 'Physics', 'Mathematics', 'English', 'Urdu', 'Islamiyat', 'Pak Studies']:
            db.session.add(Subject(name=sname, department_id=pm.id))

        pe = Department.query.filter_by(name='Science (Pre-Engineering)').first()
        for sname in ['Mathematics', 'Physics', 'Chemistry', 'Computer Science', 'English', 'Urdu', 'Islamiyat', 'Pak Studies']:
            db.session.add(Subject(name=sname, department_id=pe.id))

        db.session.commit()

    if Setting.query.count() == 0:
        defaults = {
            'institute_name': 'MAXTECHFIX College & School',
            'institute_tagline': 'Excellence in Education',
            'institute_address': 'www.maxtechfix.com',
            'institute_phone': '',
            'institute_email': '',
            'primary_color': '#1a3a6b',
            'secondary_color': '#e8f0fe',
        }
        for k, v in defaults.items():
            db.session.add(Setting(key=k, value=v))
        db.session.commit()

@app.context_processor
def inject_settings():
    return {
        'institute_name': get_setting('institute_name', 'College Management System'),
        'institute_tagline': get_setting('institute_tagline', 'Excellence in Education'),
        'institute_address': get_setting('institute_address', ''),
        'primary_color': get_setting('primary_color', '#1a3a6b'),
        'secondary_color': get_setting('secondary_color', '#e8f0fe'),
    }

@app.route('/')
def dashboard():
    total_students = Student.query.count()
    active_students = Student.query.filter_by(status='Active').count()
    total_depts = Department.query.count()
    total_subjects = Subject.query.count()
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    college_depts = Department.query.filter_by(type='college').all()
    school_depts = Department.query.filter_by(type='school').all()
    dept_stats = []
    for d in Department.query.filter_by(type='college').all():
        dept_stats.append({'name': d.name, 'count': Student.query.filter_by(department_id=d.id).count()})
    return render_template('dashboard.html',
        total_students=total_students, active_students=active_students,
        total_depts=total_depts, total_subjects=total_subjects,
        recent_students=recent_students, college_depts=college_depts,
        school_depts=school_depts, dept_stats=dept_stats)

@app.route('/students')
def students():
    q = request.args.get('q', '')
    dept_id = request.args.get('dept_id', '')
    status = request.args.get('status', '')
    query = Student.query
    if q:
        query = query.filter(or_(Student.full_name.ilike(f'%{q}%'), Student.roll_number.ilike(f'%{q}%'), Student.phone.ilike(f'%{q}%')))
    if dept_id:
        query = query.filter_by(department_id=int(dept_id))
    if status:
        query = query.filter_by(status=status)
    students_list = query.order_by(Student.created_at.desc()).all()
    departments = Department.query.all()
    return render_template('students/list.html', students=students_list, departments=departments, q=q, dept_id=dept_id, status=status)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    departments = Department.query.all()
    if request.method == 'POST':
        roll = request.form.get('roll_number', '').strip()
        if Student.query.filter_by(roll_number=roll).first():
            flash('Roll number already exists!', 'danger')
            return render_template('students/add.html', departments=departments)

        photo_filename = ''
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename and allowed_file(photo.filename):
                filename = secure_filename(f"{roll}_{photo.filename}")
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_filename = filename

        subjects_selected = request.form.getlist('subjects')

        student = Student(
            roll_number=roll,
            full_name=request.form.get('full_name', '').strip(),
            father_name=request.form.get('father_name', '').strip(),
            mother_name=request.form.get('mother_name', '').strip(),
            gender=request.form.get('gender', ''),
            date_of_birth=request.form.get('date_of_birth', ''),
            cnic_number=request.form.get('cnic_number', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            address=request.form.get('address', ''),
            department_id=int(request.form.get('department_id')),
            class_name=request.form.get('class_name', ''),
            subjects=json.dumps(subjects_selected),
            photo=photo_filename,
            admission_date=request.form.get('admission_date', ''),
            status=request.form.get('status', 'Active'),
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students'))
    return render_template('students/add.html', departments=departments)

@app.route('/students/<int:sid>')
def view_student(sid):
    student = Student.query.get_or_404(sid)
    subject_ids = json.loads(student.subjects) if student.subjects else []
    subjects = Subject.query.filter(Subject.id.in_([int(x) for x in subject_ids if x])).all() if subject_ids else []
    return render_template('students/view.html', student=student, subjects=subjects)

@app.route('/students/<int:sid>/edit', methods=['GET', 'POST'])
def edit_student(sid):
    student = Student.query.get_or_404(sid)
    departments = Department.query.all()
    if request.method == 'POST':
        roll = request.form.get('roll_number', '').strip()
        existing = Student.query.filter_by(roll_number=roll).first()
        if existing and existing.id != sid:
            flash('Roll number already exists for another student!', 'danger')
        else:
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename and allowed_file(photo.filename):
                    if student.photo:
                        old = os.path.join(app.config['UPLOAD_FOLDER'], student.photo)
                        if os.path.exists(old):
                            os.remove(old)
                    filename = secure_filename(f"{roll}_{photo.filename}")
                    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    student.photo = filename

            student.roll_number = roll
            student.full_name = request.form.get('full_name', '').strip()
            student.father_name = request.form.get('father_name', '').strip()
            student.mother_name = request.form.get('mother_name', '').strip()
            student.gender = request.form.get('gender', '')
            student.date_of_birth = request.form.get('date_of_birth', '')
            student.cnic_number = request.form.get('cnic_number', '')
            student.phone = request.form.get('phone', '')
            student.email = request.form.get('email', '')
            student.address = request.form.get('address', '')
            student.department_id = int(request.form.get('department_id'))
            student.class_name = request.form.get('class_name', '')
            student.subjects = json.dumps(request.form.getlist('subjects'))
            student.admission_date = request.form.get('admission_date', '')
            student.status = request.form.get('status', 'Active')
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('view_student', sid=sid))
    subject_ids = json.loads(student.subjects) if student.subjects else []
    dept_subjects = Subject.query.filter_by(department_id=student.department_id).all()
    return render_template('students/edit.html', student=student, departments=departments, dept_subjects=dept_subjects, subject_ids=[str(x) for x in subject_ids])

@app.route('/students/<int:sid>/delete', methods=['POST'])
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    if student.photo:
        path = os.path.join(app.config['UPLOAD_FOLDER'], student.photo)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students'))

@app.route('/api/subjects/<int:dept_id>')
def get_subjects(dept_id):
    subjects = Subject.query.filter_by(department_id=dept_id).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in subjects])

@app.route('/departments')
def departments():
    college_depts = Department.query.filter_by(type='college').all()
    school_depts = Department.query.filter_by(type='school').all()
    return render_template('departments/list.html', college_depts=college_depts, school_depts=school_depts)

@app.route('/departments/add', methods=['POST'])
def add_department():
    name = request.form.get('name', '').strip()
    dtype = request.form.get('type', 'college')
    desc = request.form.get('description', '')
    if name:
        db.session.add(Department(name=name, type=dtype, description=desc))
        db.session.commit()
        flash('Department added!', 'success')
    return redirect(url_for('departments'))

@app.route('/departments/<int:did>/delete', methods=['POST'])
def delete_department(did):
    dept = Department.query.get_or_404(did)
    if Student.query.filter_by(department_id=did).count() > 0:
        flash('Cannot delete department with enrolled students!', 'danger')
    else:
        Subject.query.filter_by(department_id=did).delete()
        db.session.delete(dept)
        db.session.commit()
        flash('Department deleted!', 'success')
    return redirect(url_for('departments'))

@app.route('/subjects')
def subjects():
    departments = Department.query.all()
    dept_id = request.args.get('dept_id', '')
    if dept_id:
        subjects_list = Subject.query.filter_by(department_id=int(dept_id)).all()
    else:
        subjects_list = Subject.query.all()
    return render_template('subjects/list.html', subjects=subjects_list, departments=departments, selected_dept=dept_id)

@app.route('/subjects/add', methods=['POST'])
def add_subject():
    name = request.form.get('name', '').strip()
    dept_id = request.form.get('department_id', '')
    desc = request.form.get('description', '')
    if name and dept_id:
        db.session.add(Subject(name=name, department_id=int(dept_id), description=desc))
        db.session.commit()
        flash('Subject added!', 'success')
    return redirect(url_for('subjects'))

@app.route('/subjects/<int:sid>/delete', methods=['POST'])
def delete_subject(sid):
    subject = Subject.query.get_or_404(sid)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted!', 'success')
    return redirect(url_for('subjects'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        for key in ['institute_name', 'institute_tagline', 'institute_address', 'institute_phone', 'institute_email', 'primary_color', 'secondary_color']:
            val = request.form.get(key, '')
            set_setting(key, val)
        flash('Settings saved!', 'success')
        return redirect(url_for('settings'))
    all_settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('settings.html', s=all_settings)

@app.route('/backup')
def backup():
    return render_template('backup.html')

@app.route('/backup/download')
def backup_download():
    db_path = os.path.join(APP_DIR, 'college.db')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'college_backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)
    shutil.copy2(db_path, backup_path)
    return send_file(backup_path, as_attachment=True, download_name=backup_name)

@app.route('/backup/restore', methods=['POST'])
def backup_restore():
    if 'backup_file' not in request.files:
        flash('No file selected!', 'danger')
        return redirect(url_for('backup'))
    f = request.files['backup_file']
    if f and f.filename and f.filename.endswith('.db'):
        db_path = os.path.join(APP_DIR, 'college.db')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy2(db_path, os.path.join(BACKUP_FOLDER, f'pre_restore_{timestamp}.db'))
        f.save(db_path)
        flash('Database restored successfully! Please restart the application.', 'success')
    else:
        flash('Invalid backup file! Please upload a .db file.', 'danger')
    return redirect(url_for('backup'))

@app.route('/about')
def about():
    return render_template('about.html')

# Serve user-uploaded photos from the writable uploads directory.
# This works both in normal Python mode and when packaged as a frozen exe,
# where static/uploads inside the bundle is read-only.
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/students/<int:sid>/print')
def print_student(sid):
    student = Student.query.get_or_404(sid)
    subject_ids = json.loads(student.subjects) if student.subjects else []
    subjects = Subject.query.filter(Subject.id.in_([int(x) for x in subject_ids if x])).all() if subject_ids else []
    return render_template('students/print.html', student=student, subjects=subjects, now=datetime.now())

@app.route('/students/print-list')
def print_list():
    dept_id = request.args.get('dept_id', '')
    status = request.args.get('status', 'Active')
    query = Student.query
    if dept_id:
        query = query.filter_by(department_id=int(dept_id))
    if status:
        query = query.filter_by(status=status)
    students_list = query.order_by(Student.roll_number).all()
    departments = Department.query.all()
    dept_name = ''
    if dept_id:
        d = Department.query.get(int(dept_id))
        if d:
            dept_name = d.name
    return render_template('students/print_list.html', students=students_list, dept_name=dept_name, status=status)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    port = int(os.environ.get('PORT', 5000))
    url = f'http://127.0.0.1:{port}'

    def _open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    # Only auto-open browser when running as a packaged exe or when not in
    # development mode (so hot-reload doesn't open two browser tabs).
    if getattr(sys, 'frozen', False) or os.environ.get('FLASK_DEBUG', 'false').lower() != 'true':
        threading.Thread(target=_open_browser, daemon=True).start()

    debug_mode = not getattr(sys, 'frozen', False) and os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=port)
