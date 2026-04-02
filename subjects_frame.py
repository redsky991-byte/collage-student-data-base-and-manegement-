"""
Subjects management frame – manage subjects, assign to teachers, enroll students.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from utils import (
    COLORS, FONTS, apply_treeview_style, make_button,
    make_label_entry, make_label_combo, center_window,
)

SEMESTERS = [""] + [str(i) for i in range(1, 13)]
GRADES = ["", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F", "Incomplete"]


class SubjectsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg="#16A085", pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📚  Subjects & Enrollment", font=FONTS["title"],
                 bg="#16A085", fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._subj_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._teacher_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._student_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._nb.add(self._subj_tab, text="  Subjects  ")
        self._nb.add(self._teacher_tab, text="  Teacher Assignments  ")
        self._nb.add(self._student_tab, text="  Student Enrollment  ")

        self._build_subjects_tab()
        self._build_teacher_tab()
        self._build_student_tab()

    # ── Subjects tab ──────────────────────────────────────────────────────────

    def _build_subjects_tab(self):
        toolbar = tk.Frame(self._subj_tab, bg=COLORS["light"], pady=6)
        toolbar.pack(fill=tk.X)
        make_button(toolbar, "➕ Add Subject", self._add_subject,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_subject,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete_subject,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self._load_subjects,
                    style="primary").pack(side=tk.LEFT, padx=4)

        self._subj_stats = tk.StringVar()
        tk.Label(toolbar, textvariable=self._subj_stats, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        tf = tk.Frame(self._subj_tab, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        cols = ("subject_code", "subject_name", "program", "semester", "credit_hours", "description")
        hdgs = ("Code", "Subject Name", "Program", "Semester", "Credits", "Description")
        wids = (100, 200, 150, 80, 70, 250)
        self._subj_tree = ttk.Treeview(tf, selectmode="browse")
        apply_treeview_style(self._subj_tree, cols, hdgs, wids)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._subj_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._subj_tree.xview)
        self._subj_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._subj_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self._subj_tree.bind("<Double-1>", lambda e: self._edit_subject())

    # ── Teacher assignment tab ─────────────────────────────────────────────────

    def _build_teacher_tab(self):
        top = tk.Frame(self._teacher_tab, bg=COLORS["light"], pady=6)
        top.pack(fill=tk.X)

        tk.Label(top, text="Academic Year:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=4)
        self._ta_year_var = tk.StringVar(value=db.get_setting("academic_year") or str(datetime.now().year))
        tk.Entry(top, textvariable=self._ta_year_var, font=FONTS["body"],
                 width=8, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=4)

        make_button(top, "➕ Assign Subject to Teacher", self._assign_teacher_subject,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(top, "🗑️ Remove Assignment", self._remove_teacher_subject,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(top, "🔄 Refresh", self._load_teacher_subjects,
                    style="primary").pack(side=tk.LEFT, padx=4)

        tf = tk.Frame(self._teacher_tab, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        cols = ("id", "staff_id", "teacher_name", "department", "subject_code", "subject_name", "program", "year")
        hdgs = ("#", "Staff ID", "Teacher Name", "Dept", "Code", "Subject", "Program", "Year")
        wids = (40, 90, 180, 130, 90, 200, 140, 70)
        self._ta_tree = ttk.Treeview(tf, selectmode="browse")
        apply_treeview_style(self._ta_tree, cols, hdgs, wids)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._ta_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._ta_tree.xview)
        self._ta_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._ta_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)

    # ── Student enrollment tab ─────────────────────────────────────────────────

    def _build_student_tab(self):
        top = tk.Frame(self._student_tab, bg=COLORS["light"], pady=6)
        top.pack(fill=tk.X)

        tk.Label(top, text="Academic Year:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=4)
        self._se_year_var = tk.StringVar(value=db.get_setting("academic_year") or str(datetime.now().year))
        tk.Entry(top, textvariable=self._se_year_var, font=FONTS["body"],
                 width=8, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=4)

        make_button(top, "➕ Enroll Student", self._enroll_student,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(top, "📝 Update Grade/Marks", self._update_grade,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(top, "🗑️ Remove Enrollment", self._remove_enrollment,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(top, "🔄 Refresh", self._load_student_subjects,
                    style="primary").pack(side=tk.LEFT, padx=4)

        tf = tk.Frame(self._student_tab, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        cols = ("id", "student_id", "name", "subject_code", "subject_name", "credit_hours",
                "grade", "marks", "year")
        hdgs = ("#", "Student ID", "Name", "Code", "Subject", "Credits", "Grade", "Marks", "Year")
        wids = (40, 100, 180, 90, 200, 70, 70, 70, 70)
        self._se_tree = ttk.Treeview(tf, selectmode="browse")
        apply_treeview_style(self._se_tree, cols, hdgs, wids)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._se_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._se_tree.xview)
        self._se_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._se_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh(self):
        self._load_subjects()
        self._load_teacher_subjects()
        self._load_student_subjects()

    def _load_subjects(self):
        subjects = db.get_all_subjects()
        self._subj_tree.delete(*self._subj_tree.get_children())
        for s in subjects:
            self._subj_tree.insert("", tk.END, values=(
                s["subject_code"], s["subject_name"], s.get("program", "") or "",
                s.get("semester", "") or "", s.get("credit_hours", ""),
                s.get("description", "") or "",
            ))
        self._subj_stats.set(f"Total subjects: {len(subjects)}")

    def _load_teacher_subjects(self):
        records = db.get_all_teacher_subjects()
        self._ta_tree.delete(*self._ta_tree.get_children())
        for r in records:
            name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip()
            self._ta_tree.insert("", tk.END, values=(
                r["id"], r["staff_id"], name,
                r.get("department", "") or "",
                r["subject_code"], r.get("subject_name", ""),
                r.get("program", "") or "", r.get("academic_year", "") or "",
            ))

    def _load_student_subjects(self):
        conn = db.get_connection()
        rows = conn.execute("""
            SELECT ss.*, s.subject_name, s.credit_hours,
                   st.first_name, st.last_name
            FROM student_subjects ss
            JOIN subjects s ON ss.subject_code = s.subject_code
            JOIN students st ON ss.student_id = st.student_id
            ORDER BY st.first_name, s.subject_name
        """).fetchall()
        conn.close()
        self._se_tree.delete(*self._se_tree.get_children())
        for r in [dict(row) for row in rows]:
            name = f"{r['first_name']} {r['last_name']}"
            self._se_tree.insert("", tk.END, values=(
                r["id"], r["student_id"], name,
                r["subject_code"], r["subject_name"],
                r.get("credit_hours", ""), r.get("grade", "") or "",
                r.get("marks", "") or "", r.get("academic_year", "") or "",
            ))

    # ── Subject actions ────────────────────────────────────────────────────────

    def _selected_subject_code(self):
        sel = self._subj_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a subject.")
            return None
        return self._subj_tree.item(sel[0])["values"][0]

    def _add_subject(self):
        SubjectDialog(self, title="Add Subject", on_save=self._save_new_subject)

    def _edit_subject(self):
        code = self._selected_subject_code()
        if not code:
            return
        data = db.get_subject(code)
        if data:
            SubjectDialog(self, title="Edit Subject", data=data,
                          on_save=self._save_edit_subject)

    def _save_new_subject(self, data):
        ok, msg = db.add_subject(data)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self._load_subjects()

    def _save_edit_subject(self, data):
        db.update_subject(data)
        messagebox.showinfo("Success", "Subject updated.")
        self._load_subjects()

    def _delete_subject(self):
        code = self._selected_subject_code()
        if not code:
            return
        if messagebox.askyesno("Confirm", f"Delete subject '{code}'?"):
            db.delete_subject(code)
            self._load_subjects()

    # ── Teacher assignment actions ─────────────────────────────────────────────

    def _assign_teacher_subject(self):
        AssignTeacherSubjectDialog(self, on_save=self._save_ta,
                                   default_year=self._ta_year_var.get())

    def _save_ta(self, staff_id, subject_code, year):
        ok, msg = db.assign_teacher_subject(staff_id, subject_code, year)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self._load_teacher_subjects()

    def _remove_teacher_subject(self):
        sel = self._ta_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an assignment to remove.")
            return
        rid = self._ta_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", "Remove this teacher-subject assignment?"):
            db.remove_teacher_subject(rid)
            self._load_teacher_subjects()

    # ── Student enrollment actions ─────────────────────────────────────────────

    def _enroll_student(self):
        EnrollStudentDialog(self, on_save=self._save_enrollment,
                            default_year=self._se_year_var.get())

    def _save_enrollment(self, data):
        ok, msg = db.enroll_student_subject(data)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self._load_student_subjects()

    def _update_grade(self):
        sel = self._se_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an enrollment to update.")
            return
        vals = self._se_tree.item(sel[0])["values"]
        record_id = vals[0]
        current_grade = vals[6]
        current_marks = vals[7]
        GradeUpdateDialog(self, record_id, current_grade, current_marks,
                          on_save=self._save_grade_update)

    def _save_grade_update(self, data):
        db.update_student_subject(data)
        messagebox.showinfo("Success", "Grade/marks updated.")
        self._load_student_subjects()

    def _remove_enrollment(self):
        sel = self._se_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an enrollment to remove.")
            return
        rid = self._se_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", "Remove this student enrollment?"):
            db.remove_student_subject(rid)
            self._load_student_subjects()


# ─── Subject dialog ────────────────────────────────────────────────────────────

class SubjectDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._build()
        center_window(self, 500, 380)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg="#16A085", fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))
        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10)

        d = self._data
        self._fv = {}
        code_var = tk.StringVar(value=d.get("subject_code", ""))
        self._fv["subject_code"] = code_var
        tk.Label(form, text="Subject Code *", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        code_entry = tk.Entry(form, textvariable=code_var, font=FONTS["body"],
                              width=28, relief=tk.SOLID, bd=1)
        code_entry.grid(row=0, column=1, padx=4, pady=4, sticky="w")
        if d.get("subject_code"):
            code_entry.configure(state="disabled")

        self._fv["subject_name"] = make_label_entry(form, "Subject Name *", 1,
                                                     default=d.get("subject_name", ""), width=28)
        self._fv["program"] = make_label_entry(form, "Program", 2,
                                               default=d.get("program", "") or "", width=28)
        self._fv["semester"] = make_label_combo(
            form, "Semester", 3, SEMESTERS,
            default=str(d.get("semester", "")) or "", width=26)
        self._fv["credit_hours"] = make_label_entry(form, "Credit Hours", 4,
                                                     default=str(d.get("credit_hours", "3")), width=28)
        self._fv["description"] = make_label_entry(form, "Description", 5,
                                                    default=d.get("description", "") or "", width=28)

        bf = tk.Frame(self, bg=COLORS["white"])
        bf.pack(fill=tk.X, padx=20, pady=10)
        make_button(bf, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(bf, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        if not data["subject_code"]:
            messagebox.showerror("Validation", "Subject code is required.", parent=self)
            return
        if not data["subject_name"]:
            messagebox.showerror("Validation", "Subject name is required.", parent=self)
            return
        try:
            data["credit_hours"] = int(data["credit_hours"]) if data["credit_hours"] else 3
        except ValueError:
            data["credit_hours"] = 3
        self._on_save(data)
        self.destroy()


# ─── Assign teacher subject dialog ─────────────────────────────────────────────

class AssignTeacherSubjectDialog(tk.Toplevel):
    def __init__(self, parent, on_save, default_year=""):
        super().__init__(parent)
        self.title("Assign Subject to Teacher")
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._default_year = default_year
        self._build()
        center_window(self, 440, 260)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text="Assign Subject to Teacher", font=FONTS["heading"],
                 bg="#16A085", fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))
        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10)

        staff = db.get_all_staff()
        staff_choices = [f"{s['staff_id']} – {s['first_name']} {s['last_name']}" for s in staff]
        subjects = db.get_all_subjects()
        subj_choices = [f"{s['subject_code']} – {s['subject_name']}" for s in subjects]

        self._staff_var = make_label_combo(form, "Teacher *", 0, staff_choices, width=34)
        self._subj_var = make_label_combo(form, "Subject *", 1, subj_choices, width=34)
        self._year_var = make_label_entry(form, "Academic Year", 2,
                                          default=self._default_year, width=34)

        bf = tk.Frame(self, bg=COLORS["white"])
        bf.pack(fill=tk.X, padx=20, pady=10)
        make_button(bf, "💾 Assign", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(bf, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        staff_val = self._staff_var.get()
        subj_val = self._subj_var.get()
        year = self._year_var.get().strip()
        if not staff_val or not subj_val:
            messagebox.showerror("Validation", "Please select both teacher and subject.", parent=self)
            return
        if " – " not in staff_val or " – " not in subj_val:
            messagebox.showerror("Validation", "Invalid selection. Please choose from the list.", parent=self)
            return
        staff_id = staff_val.split(" – ")[0]
        subject_code = subj_val.split(" – ")[0]
        self._on_save(staff_id, subject_code, year)
        self.destroy()


# ─── Enroll student dialog ─────────────────────────────────────────────────────

class EnrollStudentDialog(tk.Toplevel):
    def __init__(self, parent, on_save, default_year=""):
        super().__init__(parent)
        self.title("Enroll Student in Subject")
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._default_year = default_year
        self._build()
        center_window(self, 440, 260)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text="Enroll Student in Subject", font=FONTS["heading"],
                 bg="#16A085", fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))
        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10)

        students = db.get_all_students()
        student_choices = [f"{s['student_id']} – {s['first_name']} {s['last_name']}" for s in students]
        subjects = db.get_all_subjects()
        subj_choices = [f"{s['subject_code']} – {s['subject_name']}" for s in subjects]

        self._student_var = make_label_combo(form, "Student *", 0, student_choices, width=34)
        self._subj_var = make_label_combo(form, "Subject *", 1, subj_choices, width=34)
        self._year_var = make_label_entry(form, "Academic Year", 2,
                                          default=self._default_year, width=34)

        bf = tk.Frame(self, bg=COLORS["white"])
        bf.pack(fill=tk.X, padx=20, pady=10)
        make_button(bf, "💾 Enroll", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(bf, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        student_val = self._student_var.get()
        subj_val = self._subj_var.get()
        year = self._year_var.get().strip()
        if not student_val or not subj_val:
            messagebox.showerror("Validation", "Please select both student and subject.", parent=self)
            return
        if " – " not in student_val or " – " not in subj_val:
            messagebox.showerror("Validation", "Invalid selection. Please choose from the list.", parent=self)
            return
        student_id = student_val.split(" – ")[0]
        subject_code = subj_val.split(" – ")[0]
        self._on_save({
            "student_id": student_id,
            "subject_code": subject_code,
            "academic_year": year,
            "grade": "",
            "marks": None,
        })
        self.destroy()


# ─── Grade update dialog ───────────────────────────────────────────────────────

class GradeUpdateDialog(tk.Toplevel):
    def __init__(self, parent, record_id, current_grade, current_marks, on_save):
        super().__init__(parent)
        self.title("Update Grade & Marks")
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._record_id = record_id
        self._build(current_grade, current_marks)
        center_window(self, 380, 220)

    def _build(self, grade, marks):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text="Update Grade & Marks", font=FONTS["heading"],
                 bg="#16A085", fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))
        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10)

        self._grade_var = make_label_combo(form, "Grade", 0, GRADES,
                                           default=grade or "", width=20)
        self._marks_var = make_label_entry(form, "Marks (0-100)", 1,
                                           default=str(marks) if marks else "", width=20)

        bf = tk.Frame(self, bg=COLORS["white"])
        bf.pack(fill=tk.X, padx=20, pady=10)
        make_button(bf, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(bf, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        grade = self._grade_var.get().strip()
        marks_str = self._marks_var.get().strip()
        marks = None
        if marks_str:
            try:
                marks = float(marks_str)
            except ValueError:
                messagebox.showerror("Validation", "Marks must be a number.", parent=self)
                return
        self._on_save({"id": self._record_id, "grade": grade, "marks": marks})
        self.destroy()
