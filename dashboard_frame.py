"""
Dashboard / home frame showing summary statistics and AI-powered insights.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

import database as db
from utils import COLORS, FONTS, format_amount, get_default_currency, make_button
import print_utils


class DashboardFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        # ── Header bar ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["primary"], pady=10)
        hdr.pack(fill=tk.X)

        self._institution_label = tk.Label(
            hdr, text="College Management System", font=FONTS["title"],
            bg=COLORS["primary"], fg=COLORS["white"]
        )
        self._institution_label.pack(side=tk.LEFT, padx=20)

        # Date/time label on the right side of header
        self._dt_label = tk.Label(
            hdr, text="", font=FONTS["small"],
            bg=COLORS["primary"], fg=COLORS["white"]
        )
        self._dt_label.pack(side=tk.RIGHT, padx=16)
        self._update_clock()

        # Print Dashboard button
        make_button(hdr, "🖨️ Print Report", self._print_dashboard,
                    style="secondary").pack(side=tk.RIGHT, padx=8)

        # Stats cards row
        self._cards_frame = tk.Frame(self, bg=COLORS["light"], pady=16)
        self._cards_frame.pack(fill=tk.X, padx=20)

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

        # Two-column activity row
        act_frame = tk.Frame(self._scroll_frame, bg=COLORS["light"])
        act_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(4, 8))

        left = tk.LabelFrame(act_frame, text="  Recent Students  ",
                              font=FONTS["subheading"], bg=COLORS["white"],
                              fg=COLORS["primary"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        right = tk.LabelFrame(act_frame, text="  Recent Fee Payments  ",
                               font=FONTS["subheading"], bg=COLORS["white"],
                               fg=COLORS["primary"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self._student_tree = ttk.Treeview(left, columns=("id", "name", "program", "date"),
                                           show="headings", height=7)
        for col, hd, w in [("id", "ID", 80), ("name", "Name", 150),
                            ("program", "Program", 130), ("date", "Enrolled", 100)]:
            self._student_tree.heading(col, text=hd, anchor="w")
            self._student_tree.column(col, width=w, anchor="w")
        vsb1 = ttk.Scrollbar(left, orient="vertical", command=self._student_tree.yview)
        self._student_tree.configure(yscrollcommand=vsb1.set)
        self._student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb1.pack(side=tk.RIGHT, fill=tk.Y)

        self._fee_tree = ttk.Treeview(right, columns=("sid", "type", "amount", "status"),
                                       show="headings", height=7)
        for col, hd, w in [("sid", "Student", 90), ("type", "Fee Type", 120),
                            ("amount", "Amount", 100), ("status", "Status", 80)]:
            self._fee_tree.heading(col, text=hd, anchor="w")
            self._fee_tree.column(col, width=w, anchor="w")
        vsb2 = ttk.Scrollbar(right, orient="vertical", command=self._fee_tree.yview)
        self._fee_tree.configure(yscrollcommand=vsb2.set)
        self._fee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)

        # AI Insights section
        ai_lbl = tk.Label(self._scroll_frame, text="🤖  AI Insights & Alerts",
                          font=FONTS["heading"], bg=COLORS["light"],
                          fg=COLORS["primary"], anchor="w")
        ai_lbl.pack(fill=tk.X, padx=20, pady=(12, 4))

        self._ai_frame = tk.Frame(self._scroll_frame, bg=COLORS["light"])
        self._ai_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

    def refresh(self):
        institution = db.get_setting("institution_name") or "College Management System"
        self._institution_label.config(text=f"🏫  {institution}  –  Dashboard")

        self._build_cards()
        self._load_recent()
        self._build_ai_insights()

    def _build_cards(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()

        students = db.get_all_students()
        staff = db.get_all_staff()
        fees = db.get_all_fees()
        invoices = db.get_all_invoices()
        subjects = db.get_all_subjects()
        notices = db.get_all_notices(active_only=True)

        active_students = sum(1 for s in students if s["status"] == "Active")
        active_staff = sum(1 for s in staff if s["status"] == "Active")
        pending_fees = sum(1 for f in fees if f["status"] == "Pending")
        total_fees_collected = sum(
            f["amount"] for f in fees if f["status"] == "Paid"
        )
        unpaid_invoices = sum(1 for i in invoices if i["status"] == "Unpaid")

        currency = get_default_currency()

        cards = [
            ("🎓 Students", str(active_students), f"{len(students)} total", COLORS["secondary"]),
            ("👥 Staff", str(active_staff), f"{len(staff)} total", COLORS["success"]),
            ("📚 Subjects", str(len(subjects)), "total subjects", "#16A085"),
            ("💳 Pending Fees", str(pending_fees), "require attention", COLORS["warning"]),
            ("✅ Fees Collected",
             format_amount(total_fees_collected, currency), "this period", COLORS["success"]),
            ("🧾 Unpaid Invoices", str(unpaid_invoices), "outstanding", COLORS["danger"]),
            ("📣 Active Notices", str(len(notices)), "announcements", "#D35400"),
        ]
        for title, value, subtitle, color in cards:
            # Outer wrapper gives a white card look with a colored left accent bar
            outer = tk.Frame(self._cards_frame, bg=COLORS["white"],
                             relief=tk.FLAT, bd=0, pady=0)
            outer.pack(side=tk.LEFT, padx=5, fill=tk.Y)

            # Coloured accent strip on the left
            tk.Frame(outer, bg=color, width=5).pack(side=tk.LEFT, fill=tk.Y)

            inner = tk.Frame(outer, bg=COLORS["white"], padx=12, pady=10)
            inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            tk.Label(inner, text=title, font=FONTS["small"],
                     bg=COLORS["white"], fg=COLORS["text_light"]).pack(anchor="w")
            tk.Label(inner, text=value, font=("Segoe UI", 17, "bold"),
                     bg=COLORS["white"], fg=color).pack(anchor="w")
            tk.Label(inner, text=subtitle, font=FONTS["small"],
                     bg=COLORS["white"], fg=COLORS["text_light"]).pack(anchor="w")

    def _load_recent(self):
        self._student_tree.delete(*self._student_tree.get_children())
        students = db.get_all_students()
        for s in students[:10]:
            name = f"{s['first_name']} {s['last_name']}"
            self._student_tree.insert("", tk.END, values=(
                s["student_id"], name, s["program"] or "", s["enrollment_date"] or ""
            ))

        self._fee_tree.delete(*self._fee_tree.get_children())
        fees = db.get_all_fees()
        for f in fees[:10]:
            self._fee_tree.insert("", tk.END, values=(
                f["student_id"], f["fee_type"],
                format_amount(f["amount"], f["currency"]), f["status"],
            ))

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
