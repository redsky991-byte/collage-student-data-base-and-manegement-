"""
Student management frame – list, add, edit, delete students.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from utils import (
    COLORS, FONTS, apply_treeview_style, make_button,
    make_label_entry, make_label_combo, center_window,
)


GENDERS = ["Male", "Female", "Other", "Prefer not to say"]
STATUSES = ["Active", "Inactive", "Graduated", "Suspended", "On Leave"]
SEMESTERS = [str(i) for i in range(1, 13)]


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
                "email", "phone", "enrollment_date", "status")
        headings = ("ID", "Full Name", "Program", "Sem", "Gender",
                    "Email", "Phone", "Enrolled", "Status")
        widths = (90, 160, 160, 50, 80, 180, 110, 100, 80)

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
                s["gender"] or "", s["email"] or "", s["phone"] or "",
                s["enrollment_date"] or "", s["status"],
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


# ─── Student add/edit dialog ──────────────────────────────────────────────────

class StudentDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._build()
        center_window(self, 560, 560)

    def _build(self):
        self.configure(bg=COLORS["white"])

        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg=COLORS["primary"], fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))

        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        d = self._data
        self._fv = {}

        fields = [
            ("Student ID *", "student_id", 0),
            ("First Name *", "first_name", 1),
            ("Last Name *", "last_name", 2),
            ("Date of Birth", "date_of_birth", 3),
            ("Email", "email", 4),
            ("Phone", "phone", 5),
            ("Program", "program", 6),
            ("Address", "address", 7),
            ("Enrollment Date", "enrollment_date", 8),
        ]
        for label, key, row in fields:
            self._fv[key] = make_label_entry(form, label, row,
                                             default=d.get(key, ""), width=30)

        # Read-only ID when editing
        if d.get("student_id"):
            # find the entry widget and disable it
            for widget in form.winfo_children():
                if isinstance(widget, tk.Entry) and widget.cget("textvariable") == str(self._fv["student_id"]):
                    widget.configure(state="disabled")
                    break

        self._fv["gender"] = make_label_combo(
            form, "Gender", 9, GENDERS,
            default=d.get("gender", GENDERS[0]), width=28
        )
        self._fv["semester"] = make_label_combo(
            form, "Semester", 10, SEMESTERS,
            default=d.get("semester", "1"), width=28
        )
        self._fv["status"] = make_label_combo(
            form, "Status", 11, STATUSES,
            default=d.get("status", "Active"), width=28
        )

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        make_button(btn_frame, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(btn_frame, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        if not data["student_id"]:
            messagebox.showerror("Validation Error", "Student ID is required.", parent=self)
            return
        if not data["first_name"] or not data["last_name"]:
            messagebox.showerror("Validation Error", "First and last name are required.", parent=self)
            return
        self._on_save(data)
        self.destroy()
