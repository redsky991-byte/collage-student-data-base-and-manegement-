"""
Dashboard / home frame showing summary statistics matching the MAXTECHFIX layout.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

import database as db
from utils import COLORS, FONTS, format_amount, get_default_currency, make_button
import print_utils


class DashboardFrame(tk.Frame):
    def __init__(self, parent, navigate_to=None, *args, **kwargs):
        self._navigate_to = navigate_to
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        # ── Header bar ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["white"], pady=8)
        hdr.pack(fill=tk.X)

        # "Dashboard" title
        self._page_title = tk.Label(
            hdr, text="Dashboard", font=FONTS["heading"],
            bg=COLORS["white"], fg=COLORS["text"]
        )
        self._page_title.pack(side=tk.LEFT, padx=20)

        # Date/time label
        self._dt_label = tk.Label(
            hdr, text="", font=FONTS["small"],
            bg=COLORS["white"], fg=COLORS["text_light"]
        )
        self._dt_label.pack(side=tk.LEFT, padx=16)
        self._update_clock()

        # Buttons on the right
        make_button(hdr, "+ New Student", self._new_student,
                    style="secondary").pack(side=tk.RIGHT, padx=8)
        make_button(hdr, "🖨️ Print Report", self._print_dashboard,
                    style="primary").pack(side=tk.RIGHT, padx=4)

        # Thin separator
        tk.Frame(self, bg="#DDE1E4", height=1).pack(fill=tk.X)

        # Scrollable content area
        canvas = tk.Canvas(self, bg=COLORS["light"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._scroll_frame = tk.Frame(canvas, bg=COLORS["light"])
        self._scroll_frame_id = canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(self._scroll_frame_id, width=e.width)

        self._scroll_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Stat cards area
        self._cards_frame = tk.Frame(self._scroll_frame, bg=COLORS["light"], pady=16)
        self._cards_frame.pack(fill=tk.X, padx=20)

        # Activity row: Recent Admissions + Students by Department
        act_frame = tk.Frame(self._scroll_frame, bg=COLORS["light"])
        act_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(4, 8))

        # Left: Recent Admissions
        left = tk.LabelFrame(act_frame, text="  🕐  Recent Admissions  ",
                              font=FONTS["subheading"], bg=COLORS["white"],
                              fg=COLORS["primary"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        # View All link in the labelframe header area
        view_all_btn = tk.Button(
            left, text="View All", font=FONTS["small"],
            bg=COLORS["white"], fg=COLORS["secondary"],
            relief=tk.FLAT, cursor="hand2", pady=0,
            command=lambda: self._navigate_to and self._navigate_to("students"),
        )
        view_all_btn.pack(anchor="ne", padx=4)

        self._student_tree = ttk.Treeview(left, columns=("id", "name", "program", "date"),
                                           show="headings", height=8)
        for col, hd, w in [("id", "ID", 80), ("name", "Name", 160),
                            ("program", "Program", 150), ("date", "Enrolled", 100)]:
            self._student_tree.heading(col, text=hd, anchor="w")
            self._student_tree.column(col, width=w, anchor="w")
        vsb1 = ttk.Scrollbar(left, orient="vertical", command=self._student_tree.yview)
        self._student_tree.configure(yscrollcommand=vsb1.set)
        self._student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0), pady=(0, 4))
        vsb1.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 4))

        # Right: Students by Department
        self._dept_frame = tk.LabelFrame(act_frame, text="  🎓  Students by Department  ",
                                          font=FONTS["subheading"], bg=COLORS["white"],
                                          fg=COLORS["secondary"])
        self._dept_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(8, 0), ipadx=8, ipady=4)
        self._dept_frame.config(width=260)

        # AI Insights section
        ai_lbl = tk.Label(self._scroll_frame, text="🤖  AI Insights & Alerts",
                          font=FONTS["heading"], bg=COLORS["light"],
                          fg=COLORS["primary"], anchor="w")
        ai_lbl.pack(fill=tk.X, padx=20, pady=(12, 4))

        self._ai_frame = tk.Frame(self._scroll_frame, bg=COLORS["light"])
        self._ai_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

    def refresh(self):
        institution = db.get_setting("institution_name") or "College Management System"
        self._page_title.config(text="Dashboard")

        self._build_cards()
        self._load_recent()
        self._build_dept_panel()
        self._build_ai_insights()

    def _build_cards(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()

        students = db.get_all_students()
        fees = db.get_all_fees()
        subjects = db.get_all_subjects()

        total_students = len(students)
        active_students = sum(1 for s in students if s["status"] == "Active")
        active_teachers = db.get_active_teachers_count()
        dept_count = db.get_departments_count()
        total_fees_collected = sum(f["amount"] for f in fees if f["status"] == "Paid")
        monthly_salary = db.get_monthly_salary_bill()
        subject_count = len(subjects)

        currency = get_default_currency()

        # Row 1 – 4 cards
        row1 = tk.Frame(self._cards_frame, bg=COLORS["light"])
        row1.pack(fill=tk.X, pady=(0, 10))

        self._make_stat_card(row1, "Total Students",
                             str(total_students), "👥",
                             "#3498DB", "students", "+ View All")
        self._make_stat_card(row1, "Active Students",
                             str(active_students), "🎓",
                             "#1ABC9C", "students", "+ Admissions")
        self._make_stat_card(row1, "Active Teachers",
                             str(active_teachers), "👨‍🏫",
                             "#27AE60", "salary", "+ Manage")
        self._make_stat_card(row1, "Departments",
                             str(dept_count), "🏢",
                             "#9B59B6", "subjects", "+ View")

        # Row 2 – 3 cards
        row2 = tk.Frame(self._cards_frame, bg=COLORS["light"])
        row2.pack(fill=tk.X)

        self._make_stat_card(row2, "Total Fees Collected",
                             format_amount(total_fees_collected, currency), "💰",
                             "#E67E22", "fees", "+ Fee Records")
        self._make_stat_card(row2, "Monthly Salary Bill",
                             format_amount(monthly_salary, currency), "📄",
                             "#E91E63", "salary", "+ Finance")
        self._make_stat_card(row2, "Subjects",
                             str(subject_count), "📚",
                             "#795548", "subjects", "+ View")

    def _make_stat_card(self, parent, title, value, icon, color, nav_key, link_text):
        """Create a full-colour stat card matching the dashboard image."""
        card = tk.Frame(parent, bg=color, padx=16, pady=12, cursor="hand2")
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Top row: value (left) + icon (right)
        top = tk.Frame(card, bg=color)
        top.pack(fill=tk.X)
        val_lbl = tk.Label(top, text=value, font=("Segoe UI", 22, "bold"),
                           bg=color, fg="white")
        val_lbl.pack(side=tk.LEFT)
        icon_lbl = tk.Label(top, text=icon, font=("Segoe UI", 22),
                            bg=color, fg="white")
        icon_lbl.pack(side=tk.RIGHT)

        # Title
        title_lbl = tk.Label(card, text=title, font=FONTS["small"],
                             bg=color, fg="white")
        title_lbl.pack(anchor="w", pady=(4, 0))

        # Link
        link_lbl = tk.Label(card, text=link_text, font=FONTS["small"],
                            bg=color, fg="white", cursor="hand2",
                            underline=0)
        link_lbl.pack(anchor="w")

        # Bind click events for navigation
        if self._navigate_to and nav_key:
            def _go(e, k=nav_key):
                self._navigate_to(k)
            for widget in (card, top, val_lbl, icon_lbl, title_lbl, link_lbl):
                widget.bind("<Button-1>", _go)

    def _load_recent(self):
        self._student_tree.delete(*self._student_tree.get_children())
        students = db.get_all_students()
        if not students:
            return
        for s in students[:10]:
            name = f"{s['first_name']} {s['last_name']}"
            self._student_tree.insert("", tk.END, values=(
                s["student_id"], name, s["program"] or "", s["enrollment_date"] or ""
            ))

    def _build_dept_panel(self):
        for w in self._dept_frame.winfo_children():
            w.destroy()

        dept_counts = db.get_students_by_program()

        if not dept_counts:
            # Fallback: show common departments with 0 students
            default_depts = [
                "Computer Science (CS)",
                "Commerce",
                "Arts & Humanities",
                "Engineering",
                "Business Administration",
            ]
            for dept in default_depts:
                self._dept_row(dept, 0)
        else:
            for dept, count in dept_counts.items():
                self._dept_row(dept, count)

    def _dept_row(self, dept_name, count):
        """Add a single department row to the department panel."""
        row = tk.Frame(self._dept_frame, bg=COLORS["white"])
        row.pack(fill=tk.X, padx=8, pady=1)
        tk.Label(row, text=dept_name, font=FONTS["body"],
                 bg=COLORS["white"], fg=COLORS["text"],
                 anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(row, text=str(count), font=("Segoe UI", 10, "bold"),
                 bg=COLORS["white"], fg=COLORS["secondary"],
                 anchor="e").pack(side=tk.RIGHT)
        tk.Frame(self._dept_frame, bg=COLORS["light"], height=1).pack(fill=tk.X, padx=4)

    def _build_ai_insights(self):
        for w in self._ai_frame.winfo_children():
            w.destroy()

        try:
            att_data = db.get_attendance_analytics()
            fee_data = db.get_fee_analytics()
        except Exception:
            tk.Label(self._ai_frame, text="Analytics not available.",
                     font=FONTS["body"], bg=COLORS["light"],
                     fg=COLORS["text_light"]).pack()
            return

        # Attendance insight card
        student_att = att_data.get("student_attendance", {})
        total_att = sum(student_att.values())
        present_att = student_att.get("Present", 0) + student_att.get("Late", 0)
        att_pct = round(present_att / total_att * 100, 1) if total_att else 0

        att_card = tk.LabelFrame(self._ai_frame, text="  📋 Attendance (This Month)  ",
                                  font=FONTS["subheading"], bg=COLORS["white"],
                                  fg=COLORS["primary"])
        att_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=4)

        att_color = COLORS["success"] if att_pct >= 75 else COLORS["danger"]
        tk.Label(att_card, text=f"Student Attendance: {att_pct}%",
                 font=FONTS["body"], bg=COLORS["white"], fg=att_color).pack(anchor="w", padx=8, pady=2)
        tk.Label(att_card, text=f"  Present: {student_att.get('Present', 0)}  "
                 f"Absent: {student_att.get('Absent', 0)}  "
                 f"Late: {student_att.get('Late', 0)}  "
                 f"Leave: {student_att.get('Leave', 0)}",
                 font=FONTS["small"], bg=COLORS["white"],
                 fg=COLORS["text_light"]).pack(anchor="w", padx=8, pady=2)

        absentees = att_data.get("chronic_absentees", [])
        if absentees:
            tk.Label(att_card,
                     text=f"⚠️ {len(absentees)} student(s) with 3+ absences this month:",
                     font=FONTS["small"], bg=COLORS["white"],
                     fg=COLORS["danger"]).pack(anchor="w", padx=8, pady=(4, 0))
            for a in absentees[:3]:
                tk.Label(att_card,
                         text=f"  • {a['person_id']} – {a['absent_count']} absences",
                         font=FONTS["small"], bg=COLORS["white"],
                         fg=COLORS["text"]).pack(anchor="w", padx=16)
        else:
            tk.Label(att_card, text="✅ No chronic absentees this month.",
                     font=FONTS["small"], bg=COLORS["white"],
                     fg=COLORS["success"]).pack(anchor="w", padx=8, pady=2)

        # Fee insight card
        fee_card = tk.LabelFrame(self._ai_frame, text="  💳 Fee Analytics  ",
                                  font=FONTS["subheading"], bg=COLORS["white"],
                                  fg=COLORS["primary"])
        fee_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=4)

        currency = get_default_currency()
        tk.Label(fee_card,
                 text=f"Total Collected: {format_amount(fee_data['total_collected'], currency)}",
                 font=FONTS["body"], bg=COLORS["white"],
                 fg=COLORS["success"]).pack(anchor="w", padx=8, pady=2)
        tk.Label(fee_card,
                 text=f"Total Pending: {format_amount(fee_data['total_pending'], currency)}",
                 font=FONTS["body"], bg=COLORS["white"],
                 fg=COLORS["warning"]).pack(anchor="w", padx=8, pady=2)

        overdue = fee_data.get("overdue_count", 0)
        overdue_color = COLORS["danger"] if overdue > 0 else COLORS["success"]
        tk.Label(fee_card,
                 text=f"⚠️ Overdue Payments: {overdue}" if overdue > 0
                 else "✅ No overdue payments",
                 font=FONTS["body"], bg=COLORS["white"],
                 fg=overdue_color).pack(anchor="w", padx=8, pady=2)

        defaulters = fee_data.get("top_defaulters", [])
        if defaulters:
            tk.Label(fee_card, text="Top Fee Defaulters:",
                     font=FONTS["small"], bg=COLORS["white"],
                     fg=COLORS["danger"]).pack(anchor="w", padx=8, pady=(4, 0))
            for d in defaulters[:3]:
                tk.Label(fee_card,
                         text=f"  • {d['student_id']} – {format_amount(d['total_due'], currency)} due",
                         font=FONTS["small"], bg=COLORS["white"],
                         fg=COLORS["text"]).pack(anchor="w", padx=16)

    # ── Clock ─────────────────────────────────────────────────────────────────

    def _update_clock(self):
        now = datetime.now().strftime("%a, %d %b %Y   %I:%M:%S %p")
        self._dt_label.config(text=now)
        self.after(1000, self._update_clock)

    # ── Quick Action ──────────────────────────────────────────────────────────

    def _new_student(self):
        """Navigate to Students frame and open the Add Student dialog."""
        if self._navigate_to:
            self._navigate_to("students")
        # Small delay to allow frame to be raised before opening dialog
        self.after(100, self._open_add_student_dialog)

    def _open_add_student_dialog(self):
        """Find StudentsFrame and call its _add_dialog method."""
        try:
            parent = self.master
            for widget in parent.winfo_children():
                if hasattr(widget, "_add_dialog") and callable(widget._add_dialog):
                    widget._add_dialog()
                    return
        except Exception:
            pass

    # ── Print ─────────────────────────────────────────────────────────────────

    def _print_dashboard(self):
        students = db.get_all_students()
        staff = db.get_all_staff()
        fees = db.get_all_fees()
        invoices = db.get_all_invoices()
        subjects = db.get_all_subjects()
        notices = db.get_all_notices(active_only=True)
        try:
            att_data = db.get_attendance_analytics()
            fee_data = db.get_fee_analytics()
        except Exception:
            att_data = {}
            fee_data = {"total_collected": 0, "total_pending": 0}
        print_utils.print_dashboard(
            students, staff, fees, invoices, subjects, notices, att_data, fee_data
        )
