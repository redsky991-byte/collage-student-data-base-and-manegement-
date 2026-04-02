"""
Student management frame – list, add, edit, delete students with photo and biodata.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import shutil

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import database as db
from utils import (
    COLORS, FONTS, apply_treeview_style, make_button,
    make_label_entry, make_label_combo, center_window,
)


GENDERS = ["Male", "Female", "Other", "Prefer not to say"]
STATUSES = ["Active", "Inactive", "Graduated", "Suspended", "On Leave"]
SEMESTERS = [str(i) for i in range(1, 13)]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]


class StudentsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Header bar
        hdr = tk.Frame(self, bg=COLORS["primary"], pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="🎓  Student Management", font=FONTS["title"],
                 bg=COLORS["primary"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        # Action toolbar
        toolbar = tk.Frame(self, bg=COLORS["light"], pady=8)
        toolbar.pack(fill=tk.X, padx=10)

        make_button(toolbar, "➕ Add Student", self._add_dialog,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_dialog,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "👤 Biodata", self._view_biodata,
                    style="primary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self.refresh,
                    style="primary").pack(side=tk.LEFT, padx=4)

        # Search bar
        tk.Label(toolbar, text="Search:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(20, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._search())
        tk.Entry(toolbar, textvariable=self._search_var, font=FONTS["body"],
                 width=22, relief=tk.SOLID, bd=1).pack(side=tk.LEFT)

        # Stats bar
        self._stats_var = tk.StringVar()
        tk.Label(toolbar, textvariable=self._stats_var, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        # Treeview
        tree_frame = tk.Frame(self, bg=COLORS["light"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        cols = ("student_id", "name", "program", "semester", "gender",
                "phone", "blood_group", "enrollment_date", "status")
        headings = ("ID", "Full Name", "Program", "Sem", "Gender",
                    "Phone", "Blood Grp", "Enrolled", "Status")
        widths = (90, 160, 160, 50, 80, 110, 80, 100, 80)

        self._tree = ttk.Treeview(tree_frame, selectmode="browse")
        apply_treeview_style(self._tree, cols, headings, widths)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self._tree.bind("<Double-1>", lambda e: self._edit_dialog())

    # ── Data ─────────────────────────────────────────────────────────────────

    def refresh(self):
        self._search_var.set("")
        self._load_students(db.get_all_students())

    def _search(self):
        q = self._search_var.get().strip()
        if q:
            self._load_students(db.search_students(q))
        else:
            self._load_students(db.get_all_students())

    def _load_students(self, students):
        self._tree.delete(*self._tree.get_children())
        for s in students:
            name = f"{s['first_name']} {s['last_name']}"
            tag = "active" if s["status"] == "Active" else "inactive"
            self._tree.insert("", tk.END, values=(
                s["student_id"], name, s["program"] or "", s["semester"] or "",
                s["gender"] or "", s["phone"] or "",
                s.get("blood_group") or "", s["enrollment_date"] or "", s["status"],
            ), tags=(tag,))
        self._tree.tag_configure("active", foreground=COLORS["text"])
        self._tree.tag_configure("inactive", foreground=COLORS["text_light"])
        self._stats_var.set(f"Total: {len(students)} student(s)")

    def _selected_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a student first.")
            return None
        return self._tree.item(sel[0])["values"][0]

    # ── Dialogs ───────────────────────────────────────────────────────────────

    def _add_dialog(self):
        StudentDialog(self, title="Add New Student", on_save=self._save_new)

    def _edit_dialog(self):
        sid = self._selected_id()
        if not sid:
            return
        student = db.get_student(sid)
        if student:
            StudentDialog(self, title="Edit Student",
                          data=student, on_save=self._save_edit)

    def _save_new(self, data):
        ok, msg = db.add_student(data)
        if ok:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def _save_edit(self, data):
        db.update_student(data)
        messagebox.showinfo("Success", "Student updated successfully.")
        self.refresh()

    def _delete(self):
        sid = self._selected_id()
        if not sid:
            return
        if messagebox.askyesno("Confirm Delete",
                                f"Delete student '{sid}'? This cannot be undone."):
            db.delete_student(sid)
            self.refresh()

    def _view_biodata(self):
        sid = self._selected_id()
        if not sid:
            return
        student = db.get_student(sid)
        if student:
            BiodataViewer(self, student, person_type="student")


# ─── Student add/edit dialog ──────────────────────────────────────────────────

class StudentDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._photo_path = data.get("photo_path", "") if data else ""
        self._photo_img = None
        self._build()
        center_window(self, 700, 680)

    def _build(self):
        self.configure(bg=COLORS["white"])

        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg=COLORS["primary"], fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 6))

        # Notebook for tabs
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        tab_basic = tk.Frame(nb, bg=COLORS["white"])
        tab_bio = tk.Frame(nb, bg=COLORS["white"])
        nb.add(tab_basic, text="  Basic Info  ")
        nb.add(tab_bio, text="  Biodata & Contact  ")

        self._fv = {}
        self._build_basic_tab(tab_basic)
        self._build_bio_tab(tab_bio)

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        make_button(btn_frame, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(btn_frame, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _build_basic_tab(self, parent):
        # Left: form | Right: photo
        left = tk.Frame(parent, bg=COLORS["white"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right = tk.Frame(parent, bg=COLORS["white"], width=150)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right.pack_propagate(False)

        d = self._data

        # Student ID
        id_var = tk.StringVar(value=d.get("student_id", ""))
        self._fv["student_id"] = id_var
        tk.Label(left, text="Student ID *", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e").grid(row=0, column=0, padx=(10, 4), pady=4, sticky="e")
        id_entry = tk.Entry(left, textvariable=id_var, font=FONTS["body"],
                            width=28, relief=tk.SOLID, bd=1)
        id_entry.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")
        if d.get("student_id"):
            id_entry.configure(state="disabled")

        basic_fields = [
            ("First Name *", "first_name", 1),
            ("Last Name *", "last_name", 2),
            ("Date of Birth", "date_of_birth", 3),
            ("Email", "email", 4),
            ("Phone *", "phone", 5),
            ("Program / Course", "program", 6),
            ("Address", "address", 7),
            ("Enrollment Date", "enrollment_date", 8),
        ]
        for label, key, row in basic_fields:
            self._fv[key] = make_label_entry(left, label, row,
                                             default=d.get(key, ""), width=28)

        self._fv["gender"] = make_label_combo(
            left, "Gender", 9, GENDERS, default=d.get("gender", GENDERS[0]), width=26)
        self._fv["semester"] = make_label_combo(
            left, "Semester", 10, SEMESTERS, default=d.get("semester", "1"), width=26)
        self._fv["status"] = make_label_combo(
            left, "Status", 11, STATUSES, default=d.get("status", "Active"), width=26)

        # Photo section (right panel)
        tk.Label(right, text="Photo", font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(pady=(10, 4))
        self._photo_label = tk.Label(right, bg=COLORS["light"], relief=tk.SOLID,
                                     width=120, height=140)
        self._photo_label.pack(pady=4)
        self._refresh_photo()
        make_button(right, "📷 Browse", self._browse_photo,
                    style="secondary").pack(pady=4, fill=tk.X)
        make_button(right, "✖ Remove", self._remove_photo,
                    style="danger").pack(pady=2, fill=tk.X)

    def _build_bio_tab(self, parent):
        d = self._data
        frame = tk.Frame(parent, bg=COLORS["white"])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        bio_fields = [
            ("Father's Name", "father_name", 0),
            ("Mother's Name", "mother_name", 1),
            ("Guardian Name", "guardian_name", 2),
            ("Guardian Phone", "guardian_phone", 3),
            ("Emergency Contact", "emergency_contact", 4),
            ("CNIC / ID Number", "cnic", 5),
            ("Nationality", "nationality", 7),
            ("Religion", "religion", 8),
        ]
        for label, key, row in bio_fields:
            self._fv[key] = make_label_entry(frame, label, row,
                                             default=d.get(key, "") or "", width=30)

        self._fv["blood_group"] = make_label_combo(
            frame, "Blood Group", 6, BLOOD_GROUPS,
            default=d.get("blood_group", "Unknown") or "Unknown", width=28)

    def _browse_photo(self):
        path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if path:
            self._photo_path = path
            self._refresh_photo()

    def _remove_photo(self):
        self._photo_path = ""
        self._photo_img = None
        self._photo_label.configure(image="", text="No Photo", compound=tk.CENTER)

    def _refresh_photo(self):
        if self._photo_path and os.path.isfile(self._photo_path) and PIL_AVAILABLE:
            try:
                img = Image.open(self._photo_path).resize((120, 140))
                self._photo_img = ImageTk.PhotoImage(img)
                self._photo_label.configure(image=self._photo_img, text="")
                return
            except Exception:
                pass
        self._photo_label.configure(image="", text="No Photo", compound=tk.CENTER)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        if not data["student_id"]:
            messagebox.showerror("Validation Error", "Student ID is required.", parent=self)
            return
        if not data["first_name"] or not data["last_name"]:
            messagebox.showerror("Validation Error", "First and last name are required.", parent=self)
            return

        # Copy photo to app photos dir
        saved_path = ""
        if self._photo_path and os.path.isfile(self._photo_path):
            ext = os.path.splitext(self._photo_path)[1]
            dest = os.path.join(db.PHOTOS_DIR, f"student_{data['student_id']}{ext}")
            try:
                if os.path.abspath(self._photo_path) != os.path.abspath(dest):
                    shutil.copy2(self._photo_path, dest)
                saved_path = dest
            except Exception:
                saved_path = self._photo_path
        data["photo_path"] = saved_path

        # Fill in optional new fields with empty string defaults
        for key in ("father_name", "mother_name", "guardian_name", "guardian_phone",
                    "blood_group", "cnic", "religion", "nationality", "emergency_contact"):
            data.setdefault(key, "")

        self._on_save(data)
        self.destroy()


# ─── Biodata viewer ───────────────────────────────────────────────────────────

class BiodataViewer(tk.Toplevel):
    """Read-only biodata card for a student or staff member."""

    def __init__(self, parent, data, person_type="student"):
        super().__init__(parent)
        name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
        self.title(f"Biodata – {name}")
        self.resizable(False, False)
        self.grab_set()
        self._data = data
        self._person_type = person_type
        self._photo_img = None
        self._build()
        center_window(self, 580, 560)

    def _build(self):
        self.configure(bg=COLORS["white"])
        d = self._data

        # Header
        hdr = tk.Frame(self, bg=COLORS["primary"], pady=8)
        hdr.pack(fill=tk.X)
        name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
        pid = d.get("student_id") or d.get("staff_id", "")
        tk.Label(hdr, text=f"{'🎓' if self._person_type == 'student' else '👤'}  {name}",
                 font=FONTS["heading"], bg=COLORS["primary"],
                 fg=COLORS["white"]).pack(side=tk.LEFT, padx=16)
        tk.Label(hdr, text=f"ID: {pid}", font=FONTS["body"],
                 bg=COLORS["primary"], fg=COLORS["white"]).pack(side=tk.RIGHT, padx=16)

        body = tk.Frame(self, bg=COLORS["white"])
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Photo
        photo_frame = tk.Frame(body, bg=COLORS["light"], width=130, height=150,
                               relief=tk.SOLID, bd=1)
        photo_frame.pack(side=tk.RIGHT, padx=10)
        photo_frame.pack_propagate(False)
        photo_path = d.get("photo_path", "")
        if photo_path and os.path.isfile(photo_path) and PIL_AVAILABLE:
            try:
                img = Image.open(photo_path).resize((128, 148))
                self._photo_img = ImageTk.PhotoImage(img)
                tk.Label(photo_frame, image=self._photo_img, bg=COLORS["light"]).pack()
            except Exception:
                tk.Label(photo_frame, text="No Photo", bg=COLORS["light"],
                         font=FONTS["small"]).pack(expand=True)
        else:
            tk.Label(photo_frame, text="No Photo", bg=COLORS["light"],
                     font=FONTS["small"]).pack(expand=True)

        # Info grid
        info = tk.Frame(body, bg=COLORS["white"])
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if self._person_type == "student":
            rows = [
                ("Program", d.get("program", "")),
                ("Semester", d.get("semester", "")),
                ("Date of Birth", d.get("date_of_birth", "")),
                ("Gender", d.get("gender", "")),
                ("Blood Group", d.get("blood_group", "")),
                ("Phone", d.get("phone", "")),
                ("Email", d.get("email", "")),
                ("Father's Name", d.get("father_name", "")),
                ("Mother's Name", d.get("mother_name", "")),
                ("Guardian", d.get("guardian_name", "")),
                ("Guardian Phone", d.get("guardian_phone", "")),
                ("Emergency Contact", d.get("emergency_contact", "")),
                ("CNIC / ID", d.get("cnic", "")),
                ("Nationality", d.get("nationality", "")),
                ("Religion", d.get("religion", "")),
                ("Address", d.get("address", "")),
                ("Enrollment Date", d.get("enrollment_date", "")),
                ("Status", d.get("status", "")),
            ]
        else:
            rows = [
                ("Department", d.get("department", "")),
                ("Designation", d.get("designation", "")),
                ("Date of Birth", d.get("date_of_birth", d.get("join_date", ""))),
                ("Gender", d.get("gender", "")),
                ("Blood Group", d.get("blood_group", "")),
                ("Phone", d.get("phone", "")),
                ("Email", d.get("email", "")),
                ("Father's Name", d.get("father_name", "")),
                ("Mother's Name", d.get("mother_name", "")),
                ("Emergency Contact", d.get("emergency_contact", "")),
                ("CNIC / ID", d.get("cnic", "")),
                ("Nationality", d.get("nationality", "")),
                ("Religion", d.get("religion", "")),
                ("Qualification", d.get("qualification", "")),
                ("Experience (yrs)", d.get("experience_years", "")),
                ("Join Date", d.get("join_date", "")),
                ("Status", d.get("status", "")),
            ]

        for i, (label, value) in enumerate(rows):
            tk.Label(info, text=f"{label}:", font=FONTS["small"],
                     bg=COLORS["white"], fg=COLORS["text_light"],
                     anchor="e", width=18).grid(row=i, column=0, padx=4, pady=2, sticky="e")
            tk.Label(info, text=str(value) if value else "—", font=FONTS["body"],
                     bg=COLORS["white"], fg=COLORS["text"],
                     anchor="w").grid(row=i, column=1, padx=4, pady=2, sticky="w")

        make_button(self, "✖ Close", self.destroy, style="danger").pack(pady=8)

