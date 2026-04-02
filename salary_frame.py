"""
Staff & Salary management frame with customizable currencies, photo and biodata.
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
    get_available_currencies, get_default_currency,
    format_amount,
)
from students_frame import BiodataViewer


MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
YEARS = [str(y) for y in range(2020, datetime.now().year + 3)]
PAYMENT_STATUSES = ["Pending", "Paid", "On Hold"]
STAFF_STATUSES = ["Active", "Inactive", "On Leave", "Resigned"]


class SalaryFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["success"], pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="👥  Staff & Salary Management", font=FONTS["title"],
                 bg=COLORS["success"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        # Notebook for Staff / Payments tabs
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._staff_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._pay_tab = tk.Frame(self._nb, bg=COLORS["light"])
        self._nb.add(self._staff_tab, text="  Staff Directory  ")
        self._nb.add(self._pay_tab, text="  Salary Payments  ")

        self._build_staff_tab()
        self._build_pay_tab()

    # ── Staff tab ─────────────────────────────────────────────────────────────

    def _build_staff_tab(self):
        toolbar = tk.Frame(self._staff_tab, bg=COLORS["light"], pady=6)
        toolbar.pack(fill=tk.X)
        make_button(toolbar, "➕ Add Staff", self._add_staff_dialog,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_staff_dialog,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete_staff,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "💰 Add Payment", self._add_payment_for_selected,
                    style="warning").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "👤 Biodata", self._view_staff_biodata,
                    style="primary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self.refresh,
                    style="primary").pack(side=tk.LEFT, padx=4)

        tk.Label(toolbar, text="Search:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(20, 4))
        self._staff_search = tk.StringVar()
        self._staff_search.trace_add("write", lambda *_: self._search_staff())
        tk.Entry(toolbar, textvariable=self._staff_search, font=FONTS["body"],
                 width=20, relief=tk.SOLID, bd=1).pack(side=tk.LEFT)

        self._staff_stats = tk.StringVar()
        tk.Label(toolbar, textvariable=self._staff_stats, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        tf = tk.Frame(self._staff_tab, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        cols = ("staff_id", "name", "department", "designation",
                "salary", "currency", "email", "phone", "status")
        hdgs = ("Staff ID", "Full Name", "Department", "Designation",
                "Salary", "Currency", "Email", "Phone", "Status")
        wids = (90, 160, 140, 130, 110, 70, 180, 110, 80)
        self._staff_tree = ttk.Treeview(tf, selectmode="browse")
        apply_treeview_style(self._staff_tree, cols, hdgs, wids)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._staff_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._staff_tree.xview)
        self._staff_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._staff_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self._staff_tree.bind("<Double-1>", lambda e: self._edit_staff_dialog())

    # ── Payments tab ──────────────────────────────────────────────────────────

    def _build_pay_tab(self):
        toolbar = tk.Frame(self._pay_tab, bg=COLORS["light"], pady=6)
        toolbar.pack(fill=tk.X)
        make_button(toolbar, "➕ Add Payment", self._add_payment_dialog,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_payment_dialog,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete_payment,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✅ Mark Paid", self._mark_payment_paid,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self._load_payments,
                    style="primary").pack(side=tk.LEFT, padx=4)

        self._pay_stats = tk.StringVar()
        tk.Label(toolbar, textvariable=self._pay_stats, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        tf = tk.Frame(self._pay_tab, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        cols = ("id", "staff_id", "name", "designation", "month", "year",
                "amount", "currency", "paid_date", "status")
        hdgs = ("#", "Staff ID", "Name", "Designation", "Month", "Year",
                "Amount", "Currency", "Paid Date", "Status")
        wids = (40, 90, 150, 130, 100, 60, 110, 70, 100, 80)
        self._pay_tree = ttk.Treeview(tf, selectmode="browse")
        apply_treeview_style(self._pay_tree, cols, hdgs, wids)
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._pay_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._pay_tree.xview)
        self._pay_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._pay_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self._pay_tree.bind("<Double-1>", lambda e: self._edit_payment_dialog())

    # ── Data ─────────────────────────────────────────────────────────────────

    def refresh(self):
        self._load_staff(db.get_all_staff())
        self._load_payments()

    def _load_staff(self, staff):
        self._staff_tree.delete(*self._staff_tree.get_children())
        for s in staff:
            name = f"{s['first_name']} {s['last_name']}"
            self._staff_tree.insert("", tk.END, values=(
                s["staff_id"], name, s["department"] or "",
                s["designation"] or "",
                format_amount(s["salary"], s["currency"]),
                s["currency"], s["email"] or "", s["phone"] or "", s["status"],
            ))
        self._staff_stats.set(f"Total staff: {len(staff)}")

    def _search_staff(self):
        q = self._staff_search.get().strip()
        self._load_staff(db.search_staff(q) if q else db.get_all_staff())

    def _load_payments(self):
        payments = db.get_all_salary_payments()
        self._pay_tree.delete(*self._pay_tree.get_children())
        total = 0.0
        for p in payments:
            try:
                total += float(p["amount"])
            except (TypeError, ValueError):
                pass
            name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
            tag = p["status"].lower().replace(" ", "_")
            self._pay_tree.insert("", tk.END, values=(
                p["id"], p["staff_id"], name, p.get("designation", "") or "",
                p["month"], p["year"],
                format_amount(p["amount"], p["currency"]),
                p["currency"], p["paid_date"] or "", p["status"],
            ), tags=(tag,))
        self._pay_tree.tag_configure("paid", foreground=COLORS["success"])
        self._pay_tree.tag_configure("pending", foreground=COLORS["warning"])
        self._pay_stats.set(f"Records: {len(payments)}   |   Total: {total:,.2f}")

    # ── Staff actions ─────────────────────────────────────────────────────────

    def _selected_staff_id(self):
        sel = self._staff_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a staff member.")
            return None
        return self._staff_tree.item(sel[0])["values"][0]

    def _add_staff_dialog(self):
        StaffDialog(self, title="Add Staff Member", on_save=self._save_new_staff)

    def _edit_staff_dialog(self):
        sid = self._selected_staff_id()
        if not sid:
            return
        data = db.get_staff(sid)
        if data:
            StaffDialog(self, title="Edit Staff Member",
                        data=data, on_save=self._save_edit_staff)

    def _save_new_staff(self, data):
        ok, msg = db.add_staff(data)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.refresh()

    def _save_edit_staff(self, data):
        db.update_staff(data)
        messagebox.showinfo("Success", "Staff record updated.")
        self.refresh()

    def _delete_staff(self):
        sid = self._selected_staff_id()
        if not sid:
            return
        if messagebox.askyesno("Confirm", f"Delete staff '{sid}'?"):
            db.delete_staff(sid)
            self.refresh()

    def _add_payment_for_selected(self):
        sid = self._selected_staff_id()
        if not sid:
            return
        staff = db.get_staff(sid)
        pre = {
            "staff_id": sid,
            "amount": staff["salary"],
            "currency": staff["currency"],
        }
        PaymentDialog(self, title="Add Salary Payment",
                      data=pre, on_save=self._save_new_payment)
        self._nb.select(self._pay_tab)

    def _view_staff_biodata(self):
        sid = self._selected_staff_id()
        if not sid:
            return
        staff = db.get_staff(sid)
        if staff:
            BiodataViewer(self, staff, person_type="staff")

    # ── Payment actions ───────────────────────────────────────────────────────

    def _selected_pay_id(self):
        sel = self._pay_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a payment record.")
            return None
        return self._pay_tree.item(sel[0])["values"][0]

    def _add_payment_dialog(self):
        PaymentDialog(self, title="Add Salary Payment", on_save=self._save_new_payment)

    def _edit_payment_dialog(self):
        pid = self._selected_pay_id()
        if pid is None:
            return
        conn = db.get_connection()
        row = conn.execute(
            "SELECT * FROM salary_payments WHERE id = ?", (pid,)
        ).fetchone()
        conn.close()
        if row:
            PaymentDialog(self, title="Edit Payment",
                          data=dict(row), on_save=self._save_edit_payment)

    def _save_new_payment(self, data):
        db.add_salary_payment(data)
        messagebox.showinfo("Success", "Payment record added.")
        self._load_payments()

    def _save_edit_payment(self, data):
        db.update_salary_payment(data)
        messagebox.showinfo("Success", "Payment record updated.")
        self._load_payments()

    def _delete_payment(self):
        pid = self._selected_pay_id()
        if pid is None:
            return
        if messagebox.askyesno("Confirm", "Delete this payment record?"):
            db.delete_salary_payment(pid)
            self._load_payments()

    def _mark_payment_paid(self):
        pid = self._selected_pay_id()
        if pid is None:
            return
        today = datetime.now().strftime("%Y-%m-%d")
        conn = db.get_connection()
        conn.execute(
            "UPDATE salary_payments SET status='Paid', paid_date=? WHERE id=?",
            (today, pid),
        )
        conn.commit()
        conn.close()
        self._load_payments()


# ─── Staff dialog ──────────────────────────────────────────────────────────────

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]


class StaffDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._photo_path = (data or {}).get("photo_path", "") or ""
        self._photo_img = None
        self._build()
        center_window(self, 700, 640)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg=COLORS["success"], fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 6))

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
        left = tk.Frame(parent, bg=COLORS["white"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right = tk.Frame(parent, bg=COLORS["white"], width=150)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right.pack_propagate(False)

        d = self._data
        currencies = get_available_currencies()
        self._fv["staff_id"] = make_label_entry(left, "Staff ID *", 0,
                                                 default=d.get("staff_id", ""), width=26)
        if d.get("staff_id"):
            # Get the actual Entry widget and disable it
            for widget in left.winfo_children():
                if isinstance(widget, tk.Entry):
                    widget.configure(state="disabled")
                    break

        self._fv["first_name"] = make_label_entry(left, "First Name *", 1,
                                                   default=d.get("first_name", ""), width=26)
        self._fv["last_name"] = make_label_entry(left, "Last Name *", 2,
                                                  default=d.get("last_name", ""), width=26)
        self._fv["department"] = make_label_entry(left, "Department", 3,
                                                   default=d.get("department", ""), width=26)
        self._fv["designation"] = make_label_entry(left, "Designation / Role", 4,
                                                    default=d.get("designation", ""), width=26)
        self._fv["email"] = make_label_entry(left, "Email", 5,
                                              default=d.get("email", ""), width=26)
        self._fv["phone"] = make_label_entry(left, "Phone *", 6,
                                              default=d.get("phone", ""), width=26)
        self._fv["salary"] = make_label_entry(left, "Base Salary *", 7,
                                               default=str(d.get("salary", "")), width=26)
        self._fv["currency"] = make_label_combo(
            left, "Currency", 8, currencies,
            default=d.get("currency", get_default_currency()), width=26)
        self._fv["join_date"] = make_label_entry(
            left, "Join Date (YYYY-MM-DD)", 9,
            default=d.get("join_date", datetime.now().strftime("%Y-%m-%d")), width=26)
        self._fv["status"] = make_label_combo(
            left, "Status", 10, STAFF_STATUSES,
            default=d.get("status", "Active"), width=26)

        # Photo panel
        tk.Label(right, text="Photo", font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(pady=(10, 4))
        self._photo_label = tk.Label(right, bg=COLORS["light"], relief=tk.SOLID,
                                     width=120, height=140)
        self._photo_label.pack(pady=4)
        self._refresh_photo()
        make_button(right, "📷 Browse", self._browse_photo, style="secondary").pack(pady=4, fill=tk.X)
        make_button(right, "✖ Remove", self._remove_photo, style="danger").pack(pady=2, fill=tk.X)

    def _build_bio_tab(self, parent):
        d = self._data
        frame = tk.Frame(parent, bg=COLORS["white"])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        bio_fields = [
            ("Father's Name", "father_name", 0),
            ("Mother's Name", "mother_name", 1),
            ("Emergency Contact", "emergency_contact", 2),
            ("CNIC / ID Number", "cnic", 3),
            ("Nationality", "nationality", 5),
            ("Religion", "religion", 6),
            ("Qualification", "qualification", 7),
            ("Experience (Years)", "experience_years", 8),
        ]
        for label, key, row in bio_fields:
            self._fv[key] = make_label_entry(frame, label, row,
                                             default=d.get(key, "") or "", width=30)
        self._fv["blood_group"] = make_label_combo(
            frame, "Blood Group", 4, BLOOD_GROUPS,
            default=d.get("blood_group", "Unknown") or "Unknown", width=28)

    def _browse_photo(self):
        path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
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
        if not data["staff_id"]:
            messagebox.showerror("Validation", "Staff ID is required.", parent=self)
            return
        if not data["first_name"] or not data["last_name"]:
            messagebox.showerror("Validation", "Name is required.", parent=self)
            return
        try:
            data["salary"] = float(data["salary"])
        except ValueError:
            messagebox.showerror("Validation", "Salary must be a number.", parent=self)
            return

        # Copy photo
        saved_path = ""
        if self._photo_path and os.path.isfile(self._photo_path):
            ext = os.path.splitext(self._photo_path)[1]
            dest = os.path.join(db.PHOTOS_DIR, f"staff_{data['staff_id']}{ext}")
            try:
                if os.path.abspath(self._photo_path) != os.path.abspath(dest):
                    shutil.copy2(self._photo_path, dest)
                saved_path = dest
            except Exception:
                saved_path = self._photo_path
        data["photo_path"] = saved_path

        for key in ("father_name", "mother_name", "blood_group", "cnic", "religion",
                    "nationality", "emergency_contact", "qualification", "experience_years"):
            data.setdefault(key, "")

        self._on_save(data)
        self.destroy()


# ─── Payment dialog ────────────────────────────────────────────────────────────

class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._build()
        center_window(self, 480, 400)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg=COLORS["success"], fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))

        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        d = self._data
        currencies = get_available_currencies()
        self._fv = {}

        self._fv["staff_id"] = make_label_entry(form, "Staff ID *", 0,
                                                 default=d.get("staff_id", ""), width=26)
        self._fv["amount"] = make_label_entry(form, "Amount *", 1,
                                               default=str(d.get("amount", "")), width=26)
        self._fv["currency"] = make_label_combo(
            form, "Currency", 2, currencies,
            default=d.get("currency", get_default_currency()), width=26)
        self._fv["month"] = make_label_combo(
            form, "Month", 3, MONTHS,
            default=d.get("month", MONTHS[datetime.now().month - 1]), width=26)
        self._fv["year"] = make_label_combo(
            form, "Year", 4, YEARS,
            default=d.get("year", str(datetime.now().year)), width=26)
        self._fv["paid_date"] = make_label_entry(
            form, "Paid Date (YYYY-MM-DD)", 5,
            default=d.get("paid_date", ""), width=26)
        self._fv["status"] = make_label_combo(
            form, "Status", 6, PAYMENT_STATUSES,
            default=d.get("status", "Pending"), width=26)
        self._fv["notes"] = make_label_entry(form, "Notes", 7,
                                              default=d.get("notes", ""), width=26)

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        make_button(btn_frame, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(btn_frame, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        if not data["staff_id"]:
            messagebox.showerror("Validation", "Staff ID is required.", parent=self)
            return
        try:
            data["amount"] = float(data["amount"])
        except ValueError:
            messagebox.showerror("Validation", "Amount must be a number.", parent=self)
            return
        if self._data.get("id"):
            data["id"] = self._data["id"]
        self._on_save(data)
        self.destroy()
