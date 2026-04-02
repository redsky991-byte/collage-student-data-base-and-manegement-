"""
Fee management frame – track student fees with customizable currencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from utils import (
    COLORS, FONTS, apply_treeview_style, make_button,
    make_label_entry, make_label_combo, center_window,
    get_available_currencies, get_default_currency,
    currency_display, format_amount,
)


FEE_STATUSES = ["Pending", "Paid", "Overdue", "Waived", "Partial"]


def _get_fee_types():
    raw = db.get_setting("fee_types") or "Tuition"
    return [t.strip() for t in raw.split(",") if t.strip()]


class FeesFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["warning"], pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="💳  Fee Management", font=FONTS["title"],
                 bg=COLORS["warning"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS["light"], pady=8)
        toolbar.pack(fill=tk.X, padx=10)

        make_button(toolbar, "➕ Add Fee", self._add_dialog,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_dialog,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✅ Mark Paid", self._mark_paid,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self.refresh,
                    style="primary").pack(side=tk.LEFT, padx=4)

        # Filter by status
        tk.Label(toolbar, text="Filter:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(20, 4))
        self._filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            toolbar, textvariable=self._filter_var,
            values=["All"] + FEE_STATUSES, width=10, state="readonly",
            font=FONTS["body"]
        )
        filter_combo.pack(side=tk.LEFT)
        filter_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        self._stats_var = tk.StringVar()
        tk.Label(toolbar, textvariable=self._stats_var, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        # Treeview
        tree_frame = tk.Frame(self, bg=COLORS["light"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        cols = ("id", "student_id", "student_name", "fee_type", "amount",
                "currency", "due_date", "paid_date", "status")
        headings = ("#", "Student ID", "Student Name", "Fee Type", "Amount",
                    "Currency", "Due Date", "Paid Date", "Status")
        widths = (40, 90, 150, 120, 100, 70, 100, 100, 80)

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

    def refresh(self):
        fees = db.get_all_fees()
        status_filter = self._filter_var.get() if hasattr(self, "_filter_var") else "All"
        if status_filter != "All":
            fees = [f for f in fees if f["status"] == status_filter]
        self._load_fees(fees)

    def _load_fees(self, fees):
        self._tree.delete(*self._tree.get_children())
        total = 0.0
        for f in fees:
            name = f"{f.get('first_name', '')} {f.get('last_name', '')}".strip()
            try:
                total += float(f["amount"])
            except (TypeError, ValueError):
                pass
            tag = f["status"].lower().replace(" ", "_")
            self._tree.insert("", tk.END, values=(
                f["id"], f["student_id"], name, f["fee_type"],
                format_amount(f["amount"], f["currency"]),
                f["currency"], f["due_date"] or "", f["paid_date"] or "",
                f["status"],
            ), tags=(tag,))

        self._tree.tag_configure("paid", foreground=COLORS["success"])
        self._tree.tag_configure("overdue", foreground=COLORS["danger"])
        self._tree.tag_configure("pending", foreground=COLORS["warning"])
        self._stats_var.set(f"Records: {len(fees)}   |   Total: {total:,.2f}")

    def _selected_fee_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a fee record first.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _add_dialog(self):
        FeeDialog(self, title="Add Fee Record", on_save=self._save_new)

    def _edit_dialog(self):
        fid = self._selected_fee_id()
        if fid is None:
            return
        conn = db.get_connection()
        row = conn.execute("SELECT * FROM fees WHERE id = ?", (fid,)).fetchone()
        conn.close()
        if row:
            FeeDialog(self, title="Edit Fee Record",
                      data=dict(row), on_save=self._save_edit)

    def _save_new(self, data):
        db.add_fee(data)
        messagebox.showinfo("Success", "Fee record added.")
        self.refresh()

    def _save_edit(self, data):
        db.update_fee(data)
        messagebox.showinfo("Success", "Fee record updated.")
        self.refresh()

    def _delete(self):
        fid = self._selected_fee_id()
        if fid is None:
            return
        if messagebox.askyesno("Confirm", "Delete this fee record?"):
            db.delete_fee(fid)
            self.refresh()

    def _mark_paid(self):
        fid = self._selected_fee_id()
        if fid is None:
            return
        today = datetime.now().strftime("%Y-%m-%d")
        conn = db.get_connection()
        conn.execute(
            "UPDATE fees SET status='Paid', paid_date=? WHERE id=?", (today, fid)
        )
        conn.commit()
        conn.close()
        self.refresh()


# ─── Fee add/edit dialog ───────────────────────────────────────────────────────

class FeeDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._build()
        center_window(self, 500, 460)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg=COLORS["warning"], fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))

        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        d = self._data
        currencies = get_available_currencies()
        default_currency = d.get("currency", get_default_currency())

        self._fv = {}
        self._fv["student_id"] = make_label_entry(
            form, "Student ID *", 0, default=d.get("student_id", ""), width=28)
        self._fv["fee_type"] = make_label_combo(
            form, "Fee Type *", 1, _get_fee_types(),
            default=d.get("fee_type", _get_fee_types()[0]), width=28)
        self._fv["amount"] = make_label_entry(
            form, "Amount *", 2, default=str(d.get("amount", "")), width=28)
        self._fv["currency"] = make_label_combo(
            form, "Currency", 3, currencies,
            default=default_currency, width=28)
        self._fv["due_date"] = make_label_entry(
            form, "Due Date (YYYY-MM-DD)", 4,
            default=d.get("due_date", datetime.now().strftime("%Y-%m-%d")), width=28)
        self._fv["paid_date"] = make_label_entry(
            form, "Paid Date (YYYY-MM-DD)", 5, default=d.get("paid_date", ""), width=28)
        self._fv["status"] = make_label_combo(
            form, "Status", 6, FEE_STATUSES,
            default=d.get("status", "Pending"), width=28)
        self._fv["description"] = make_label_entry(
            form, "Description", 7, default=d.get("description", ""), width=28)

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        make_button(btn_frame, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(btn_frame, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        if not data["student_id"]:
            messagebox.showerror("Validation", "Student ID is required.", parent=self)
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
