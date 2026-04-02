"""
Dashboard / home frame showing summary statistics.
"""

import tkinter as tk
from tkinter import ttk

import database as db
from utils import COLORS, FONTS, format_amount, get_default_currency


class DashboardFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["primary"], pady=12)
        hdr.pack(fill=tk.X)
        self._institution_label = tk.Label(
            hdr, text="College Management System", font=FONTS["title"],
            bg=COLORS["primary"], fg=COLORS["white"]
        )
        self._institution_label.pack(side=tk.LEFT, padx=20)

        # Stats cards row
        self._cards_frame = tk.Frame(self, bg=COLORS["light"], pady=16)
        self._cards_frame.pack(fill=tk.X, padx=20)

        # Recent activity frame
        activity_lbl = tk.Label(self, text="Recent Activity", font=FONTS["heading"],
                                 bg=COLORS["light"], fg=COLORS["primary"], anchor="w")
        activity_lbl.pack(fill=tk.X, padx=20, pady=(8, 4))

        act_frame = tk.Frame(self, bg=COLORS["light"])
        act_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Two-column layout: recent students | recent fees
        left = tk.LabelFrame(act_frame, text="  Recent Students  ",
                              font=FONTS["subheading"], bg=COLORS["white"],
                              fg=COLORS["primary"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        right = tk.LabelFrame(act_frame, text="  Recent Fee Payments  ",
                               font=FONTS["subheading"], bg=COLORS["white"],
                               fg=COLORS["primary"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self._student_tree = ttk.Treeview(left, columns=("id", "name", "program", "date"),
                                           show="headings", height=8)
        for col, hd, w in [("id", "ID", 80), ("name", "Name", 150),
                            ("program", "Program", 130), ("date", "Enrolled", 100)]:
            self._student_tree.heading(col, text=hd, anchor="w")
            self._student_tree.column(col, width=w, anchor="w")
        vsb1 = ttk.Scrollbar(left, orient="vertical", command=self._student_tree.yview)
        self._student_tree.configure(yscrollcommand=vsb1.set)
        self._student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb1.pack(side=tk.RIGHT, fill=tk.Y)

        self._fee_tree = ttk.Treeview(right, columns=("sid", "type", "amount", "status"),
                                       show="headings", height=8)
        for col, hd, w in [("sid", "Student", 90), ("type", "Fee Type", 120),
                            ("amount", "Amount", 100), ("status", "Status", 80)]:
            self._fee_tree.heading(col, text=hd, anchor="w")
            self._fee_tree.column(col, width=w, anchor="w")
        vsb2 = ttk.Scrollbar(right, orient="vertical", command=self._fee_tree.yview)
        self._fee_tree.configure(yscrollcommand=vsb2.set)
        self._fee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        institution = db.get_setting("institution_name") or "College Management System"
        self._institution_label.config(text=f"🏫  {institution}  –  Dashboard")

        self._build_cards()
        self._load_recent()

    def _build_cards(self):
        for w in self._cards_frame.winfo_children():
            w.destroy()

        students = db.get_all_students()
        staff = db.get_all_staff()
        fees = db.get_all_fees()
        invoices = db.get_all_invoices()

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
            ("💳 Pending Fees", str(pending_fees), "require attention", COLORS["warning"]),
            ("✅ Fees Collected",
             format_amount(total_fees_collected, currency), "this period", COLORS["success"]),
            ("🧾 Unpaid Invoices", str(unpaid_invoices), "outstanding", COLORS["danger"]),
        ]
        for title, value, subtitle, color in cards:
            card = tk.Frame(self._cards_frame, bg=color,
                            padx=18, pady=14, relief=tk.RAISED, bd=0)
            card.pack(side=tk.LEFT, padx=8, fill=tk.Y)
            tk.Label(card, text=title, font=FONTS["small"],
                     bg=color, fg=COLORS["white"]).pack(anchor="w")
            tk.Label(card, text=value, font=("Segoe UI", 22, "bold"),
                     bg=color, fg=COLORS["white"]).pack(anchor="w")
            tk.Label(card, text=subtitle, font=FONTS["small"],
                     bg=color, fg=COLORS["white"]).pack(anchor="w")

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
