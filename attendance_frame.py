"""
Attendance management frame – mark and view student & teacher attendance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

import database as db
from utils import COLORS, FONTS, apply_treeview_style, make_button, center_window


ATTENDANCE_STATUSES = ["Present", "Absent", "Late", "Leave"]
STATUS_COLORS = {
    "Present": COLORS["success"],
    "Absent": COLORS["danger"],
    "Late": COLORS["warning"],
    "Leave": COLORS["secondary"],
}


class AttendanceFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg="#8E44AD", pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📋  Attendance Management", font=FONTS["title"],
                 bg="#8E44AD", fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._student_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._staff_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._report_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._nb.add(self._student_tab, text="  Student Attendance  ")
        self._nb.add(self._staff_tab, text="  Teacher Attendance  ")
        self._nb.add(self._report_tab, text="  Reports  ")

        self._build_attendance_tab(self._student_tab, "student")
        self._build_attendance_tab(self._staff_tab, "staff")
        self._build_report_tab()

    # ── Generic attendance tab ────────────────────────────────────────────────

    def _build_attendance_tab(self, parent, person_type):
        top = tk.Frame(parent, bg=COLORS["light"], pady=6)
        top.pack(fill=tk.X, padx=4)

        # Date selector
        tk.Label(top, text="Date:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(4, 2))
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(top, textvariable=date_var, font=FONTS["body"],
                              width=14, relief=tk.SOLID, bd=1)
        date_entry.pack(side=tk.LEFT, padx=2)

        make_button(top, "⬅ Prev", lambda pt=person_type, dv=date_var: self._shift_date(dv, pt, -1),
                    style="secondary").pack(side=tk.LEFT, padx=2)
        make_button(top, "Today", lambda pt=person_type, dv=date_var: self._goto_today(dv, pt),
                    style="primary").pack(side=tk.LEFT, padx=2)
        make_button(top, "Next ➡", lambda pt=person_type, dv=date_var: self._shift_date(dv, pt, +1),
                    style="secondary").pack(side=tk.LEFT, padx=2)
        make_button(top, "📋 Load", lambda pt=person_type, dv=date_var: self._load_att_tab(pt, dv),
                    style="warning").pack(side=tk.LEFT, padx=8)
        make_button(top, "✅ Mark All Present",
                    lambda pt=person_type, dv=date_var: self._mark_all(pt, dv, "Present"),
                    style="success").pack(side=tk.LEFT, padx=2)
        make_button(top, "💾 Save Attendance",
                    lambda pt=person_type, dv=date_var: self._save_attendance(pt, dv),
                    style="success").pack(side=tk.LEFT, padx=8)

        stats_var = tk.StringVar()
        tk.Label(top, textvariable=stats_var, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        # Table frame
        tbl_frame = tk.Frame(parent, bg=COLORS["light"])
        tbl_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("id_col", "name", "info", "status")
        headings = ("ID", "Name", "Info", "Status")
        widths = (100, 200, 200, 100)
        tree = ttk.Treeview(tbl_frame, selectmode="browse")
        apply_treeview_style(tree, cols, headings, widths)
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tbl_frame.rowconfigure(0, weight=1)
        tbl_frame.columnconfigure(0, weight=1)

        # Double-click to cycle status
        tree.bind("<Double-1>", lambda e, pt=person_type, t=tree, dv=date_var, sv=stats_var:
                  self._cycle_status(pt, t, dv, sv))
        tree.bind("<Return>", lambda e, pt=person_type, t=tree, dv=date_var, sv=stats_var:
                  self._cycle_status(pt, t, dv, sv))

        # Store references
        if person_type == "student":
            self._student_tree = tree
            self._student_date_var = date_var
            self._student_stats_var = stats_var
            self._student_att_data = {}  # person_id -> status
        else:
            self._staff_tree = tree
            self._staff_date_var = date_var
            self._staff_stats_var = stats_var
            self._staff_att_data = {}

    def _build_report_tab(self):
        top = tk.Frame(self._report_tab, bg=COLORS["light"], pady=6)
        top.pack(fill=tk.X, padx=4)

        tk.Label(top, text="Person Type:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(4, 2))
        self._rpt_type_var = tk.StringVar(value="student")
        ttk.Combobox(top, textvariable=self._rpt_type_var,
                     values=["student", "staff"], width=10,
                     state="readonly", font=FONTS["body"]).pack(side=tk.LEFT, padx=2)

        tk.Label(top, text="ID:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(10, 2))
        self._rpt_id_var = tk.StringVar()
        tk.Entry(top, textvariable=self._rpt_id_var, font=FONTS["body"],
                 width=14, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=2)

        tk.Label(top, text="From:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(10, 2))
        self._rpt_from_var = tk.StringVar(
            value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        tk.Entry(top, textvariable=self._rpt_from_var, font=FONTS["body"],
                 width=12, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=2)

        tk.Label(top, text="To:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(6, 2))
        self._rpt_to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(top, textvariable=self._rpt_to_var, font=FONTS["body"],
                 width=12, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=2)

        make_button(top, "🔍 Generate Report", self._generate_report,
                    style="primary").pack(side=tk.LEFT, padx=10)

        # Summary cards
        self._rpt_summary_frame = tk.Frame(self._report_tab, bg=COLORS["light"])
        self._rpt_summary_frame.pack(fill=tk.X, padx=10, pady=4)

        # Report treeview
        rpt_frame = tk.Frame(self._report_tab, bg=COLORS["light"])
        rpt_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("date", "status", "remarks")
        headings = ("Date", "Status", "Remarks")
        widths = (120, 100, 300)
        self._rpt_tree = ttk.Treeview(rpt_frame, selectmode="browse")
        apply_treeview_style(self._rpt_tree, cols, headings, widths)
        vsb = ttk.Scrollbar(rpt_frame, orient="vertical", command=self._rpt_tree.yview)
        self._rpt_tree.configure(yscrollcommand=vsb.set)
        self._rpt_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        rpt_frame.rowconfigure(0, weight=1)
        rpt_frame.columnconfigure(0, weight=1)

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh(self):
        self._load_att_tab("student", self._student_date_var)
        self._load_att_tab("staff", self._staff_date_var)

    def _load_att_tab(self, person_type, date_var):
        date_str = date_var.get().strip()
        if not date_str:
            return

        if person_type == "student":
            tree = self._student_tree
            stats_var = self._student_stats_var
            people = db.get_all_students()
            id_key = "student_id"
            info_key = "program"
        else:
            tree = self._staff_tree
            stats_var = self._staff_stats_var
            people = db.get_all_staff()
            id_key = "staff_id"
            info_key = "designation"

        existing = db.get_attendance_for_date(person_type, date_str)

        tree.delete(*tree.get_children())
        for person in people:
            pid = person[id_key]
            name = f"{person['first_name']} {person['last_name']}"
            info = person.get(info_key) or ""
            status = existing.get(pid, {}).get("status", "Present")
            tag = status.lower()
            tree.insert("", tk.END, iid=pid, values=(pid, name, info, status), tags=(tag,))

        self._apply_status_colors(tree)
        self._update_stats(tree, stats_var, date_str, person_type)

    def _apply_status_colors(self, tree):
        tree.tag_configure("present", foreground=COLORS["success"])
        tree.tag_configure("absent", foreground=COLORS["danger"])
        tree.tag_configure("late", foreground=COLORS["warning"])
        tree.tag_configure("leave", foreground=COLORS["secondary"])

    def _update_stats(self, tree, stats_var, date_str, person_type):
        counts = {"Present": 0, "Absent": 0, "Late": 0, "Leave": 0}
        for item in tree.get_children():
            status = tree.item(item)["values"][3]
            counts[status] = counts.get(status, 0) + 1
        total = sum(counts.values())
        stats_var.set(
            f"{date_str}  |  Total: {total}  |  "
            f"✅ {counts['Present']}  ❌ {counts['Absent']}  "
            f"⏱ {counts['Late']}  🏖 {counts['Leave']}"
        )

    # ── Actions ───────────────────────────────────────────────────────────────

    def _shift_date(self, date_var, person_type, delta):
        try:
            d = datetime.strptime(date_var.get().strip(), "%Y-%m-%d")
            d += timedelta(days=delta)
            date_var.set(d.strftime("%Y-%m-%d"))
            self._load_att_tab(person_type, date_var)
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter date as YYYY-MM-DD.")

    def _goto_today(self, date_var, person_type):
        date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self._load_att_tab(person_type, date_var)

    def _mark_all(self, person_type, date_var, status):
        tree = self._student_tree if person_type == "student" else self._staff_tree
        stats_var = self._student_stats_var if person_type == "student" else self._staff_stats_var
        for item in tree.get_children():
            vals = list(tree.item(item)["values"])
            vals[3] = status
            tree.item(item, values=vals, tags=(status.lower(),))
        self._apply_status_colors(tree)
        self._update_stats(tree, stats_var, date_var.get(), person_type)

    def _cycle_status(self, person_type, tree, date_var, stats_var):
        sel = tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = list(tree.item(item)["values"])
        current = vals[3]
        idx = ATTENDANCE_STATUSES.index(current) if current in ATTENDANCE_STATUSES else 0
        next_status = ATTENDANCE_STATUSES[(idx + 1) % len(ATTENDANCE_STATUSES)]
        vals[3] = next_status
        tree.item(item, values=vals, tags=(next_status.lower(),))
        self._apply_status_colors(tree)
        self._update_stats(tree, stats_var, date_var.get(), person_type)

    def _save_attendance(self, person_type, date_var):
        date_str = date_var.get().strip()
        if not date_str:
            messagebox.showerror("Error", "Please enter a date.")
            return
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be YYYY-MM-DD format.")
            return

        tree = self._student_tree if person_type == "student" else self._staff_tree
        saved = 0
        for item in tree.get_children():
            pid, _name, _info, status = tree.item(item)["values"]
            db.mark_attendance(person_type, str(pid), date_str, status)
            saved += 1

        messagebox.showinfo("Saved", f"Attendance saved for {saved} person(s) on {date_str}.")

    def _generate_report(self):
        person_type = self._rpt_type_var.get()
        person_id = self._rpt_id_var.get().strip()
        from_date = self._rpt_from_var.get().strip()
        to_date = self._rpt_to_var.get().strip()

        records = db.get_attendance(person_type, person_id or None, from_date or None, to_date or None)

        # Summary
        for w in self._rpt_summary_frame.winfo_children():
            w.destroy()
        counts = {"Present": 0, "Absent": 0, "Late": 0, "Leave": 0}
        for r in records:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        total = len(records)
        attendance_pct = round((counts["Present"] + counts["Late"]) / total * 100, 1) if total else 0

        for label, val, color in [
            ("Total Days", str(total), COLORS["secondary"]),
            ("Present", str(counts["Present"]), COLORS["success"]),
            ("Absent", str(counts["Absent"]), COLORS["danger"]),
            ("Late", str(counts["Late"]), COLORS["warning"]),
            ("Leave", str(counts["Leave"]), COLORS["secondary"]),
            ("Attendance %", f"{attendance_pct}%", COLORS["success"] if attendance_pct >= 75 else COLORS["danger"]),
        ]:
            card = tk.Frame(self._rpt_summary_frame, bg=color, padx=12, pady=8)
            card.pack(side=tk.LEFT, padx=4, pady=4)
            tk.Label(card, text=label, font=FONTS["small"], bg=color, fg="white").pack()
            tk.Label(card, text=val, font=("Segoe UI", 16, "bold"),
                     bg=color, fg="white").pack()

        # Table
        self._rpt_tree.delete(*self._rpt_tree.get_children())
        for r in records:
            tag = r["status"].lower()
            self._rpt_tree.insert("", tk.END, values=(
                r["attendance_date"], r["status"], r.get("remarks", "")
            ), tags=(tag,))

        self._rpt_tree.tag_configure("present", foreground=COLORS["success"])
        self._rpt_tree.tag_configure("absent", foreground=COLORS["danger"])
        self._rpt_tree.tag_configure("late", foreground=COLORS["warning"])
        self._rpt_tree.tag_configure("leave", foreground=COLORS["secondary"])
