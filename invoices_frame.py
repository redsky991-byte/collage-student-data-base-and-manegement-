"""
Invoice management frame with customizable currencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from utils import (
    COLORS, FONTS, apply_treeview_style, make_button,
    make_label_entry, make_label_combo, center_window,
    get_available_currencies, get_default_currency,
    format_amount,
)


INVOICE_TYPES = ["Fee Invoice", "Salary Invoice", "Service Invoice",
                 "Library Fine", "Hostel Invoice", "Other"]
INVOICE_STATUSES = ["Unpaid", "Paid", "Overdue", "Cancelled", "Draft"]


class InvoicesFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["secondary"], pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="🧾  Invoice Management", font=FONTS["title"],
                 bg=COLORS["secondary"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        toolbar = tk.Frame(self, bg=COLORS["light"], pady=8)
        toolbar.pack(fill=tk.X, padx=10)

        make_button(toolbar, "➕ New Invoice", self._add_dialog,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_dialog,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✅ Mark Paid", self._mark_paid,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🖨️ Preview", self._preview,
                    style="primary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self.refresh,
                    style="primary").pack(side=tk.LEFT, padx=4)

        # Filter
        tk.Label(toolbar, text="Filter:", font=FONTS["body"],
                 bg=COLORS["light"]).pack(side=tk.LEFT, padx=(20, 4))
        self._filter_var = tk.StringVar(value="All")
        fc = ttk.Combobox(toolbar, textvariable=self._filter_var,
                          values=["All"] + INVOICE_STATUSES, width=10,
                          state="readonly", font=FONTS["body"])
        fc.pack(side=tk.LEFT)
        fc.bind("<<ComboboxSelected>>", lambda _: self.refresh())

        self._stats_var = tk.StringVar()
        tk.Label(toolbar, textvariable=self._stats_var, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        tf = tk.Frame(self, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        cols = ("id", "invoice_number", "invoice_type", "recipient_name",
                "amount", "currency", "issue_date", "due_date", "status")
        hdgs = ("#", "Invoice #", "Type", "Recipient",
                "Amount", "Currency", "Issue Date", "Due Date", "Status")
        wids = (40, 100, 130, 170, 110, 70, 100, 100, 80)

        self._tree = ttk.Treeview(tf, selectmode="browse")
        apply_treeview_style(self._tree, cols, hdgs, wids)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)

        self._tree.bind("<Double-1>", lambda e: self._edit_dialog())

    def refresh(self):
        invoices = db.get_all_invoices()
        status_filter = self._filter_var.get() if hasattr(self, "_filter_var") else "All"
        if status_filter != "All":
            invoices = [i for i in invoices if i["status"] == status_filter]
        self._load_invoices(invoices)

    def _load_invoices(self, invoices):
        self._tree.delete(*self._tree.get_children())
        total = 0.0
        for inv in invoices:
            try:
                total += float(inv["amount"])
            except (TypeError, ValueError):
                pass
            tag = inv["status"].lower()
            self._tree.insert("", tk.END, values=(
                inv["id"], inv["invoice_number"], inv["invoice_type"],
                inv["recipient_name"],
                format_amount(inv["amount"], inv["currency"]),
                inv["currency"], inv["issue_date"] or "",
                inv["due_date"] or "", inv["status"],
            ), tags=(tag,))
        self._tree.tag_configure("paid", foreground=COLORS["success"])
        self._tree.tag_configure("overdue", foreground=COLORS["danger"])
        self._tree.tag_configure("unpaid", foreground=COLORS["warning"])
        self._tree.tag_configure("cancelled", foreground=COLORS["text_light"])
        self._stats_var.set(f"Records: {len(invoices)}   |   Total: {total:,.2f}")

    def _selected_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an invoice.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _add_dialog(self):
        InvoiceDialog(self, title="New Invoice", on_save=self._save_new)

    def _edit_dialog(self):
        iid = self._selected_id()
        if iid is None:
            return
        data = db.get_invoice(iid)
        if data:
            InvoiceDialog(self, title="Edit Invoice",
                          data=data, on_save=self._save_edit)

    def _save_new(self, data):
        inv_no = db.add_invoice(data)
        messagebox.showinfo("Success", f"Invoice {inv_no} created.")
        self.refresh()

    def _save_edit(self, data):
        db.update_invoice(data)
        messagebox.showinfo("Success", "Invoice updated.")
        self.refresh()

    def _delete(self):
        iid = self._selected_id()
        if iid is None:
            return
        if messagebox.askyesno("Confirm", "Delete this invoice?"):
            db.delete_invoice(iid)
            self.refresh()

    def _mark_paid(self):
        iid = self._selected_id()
        if iid is None:
            return
        conn = db.get_connection()
        conn.execute("UPDATE invoices SET status='Paid' WHERE id=?", (iid,))
        conn.commit()
        conn.close()
        self.refresh()

    def _preview(self):
        iid = self._selected_id()
        if iid is None:
            return
        data = db.get_invoice(iid)
        if data:
            InvoicePreview(self, data)


# ─── Invoice dialog ────────────────────────────────────────────────────────────

class InvoiceDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._build()
        center_window(self, 520, 490)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg=COLORS["secondary"], fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))

        form = tk.Frame(self, bg=COLORS["white"])
        form.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        d = self._data
        currencies = get_available_currencies()
        today = datetime.now().strftime("%Y-%m-%d")

        self._fv = {}
        self._fv["invoice_type"] = make_label_combo(
            form, "Invoice Type *", 0, INVOICE_TYPES,
            default=d.get("invoice_type", INVOICE_TYPES[0]), width=28)
        self._fv["reference_id"] = make_label_entry(
            form, "Reference ID", 1, default=d.get("reference_id", ""), width=28)
        self._fv["recipient_name"] = make_label_entry(
            form, "Recipient Name *", 2, default=d.get("recipient_name", ""), width=28)
        self._fv["recipient_email"] = make_label_entry(
            form, "Recipient Email", 3, default=d.get("recipient_email", ""), width=28)
        self._fv["amount"] = make_label_entry(
            form, "Amount *", 4, default=str(d.get("amount", "")), width=28)
        self._fv["currency"] = make_label_combo(
            form, "Currency", 5, currencies,
            default=d.get("currency", get_default_currency()), width=28)
        self._fv["issue_date"] = make_label_entry(
            form, "Issue Date (YYYY-MM-DD)", 6, default=d.get("issue_date", today), width=28)
        self._fv["due_date"] = make_label_entry(
            form, "Due Date (YYYY-MM-DD)", 7, default=d.get("due_date", ""), width=28)
        self._fv["status"] = make_label_combo(
            form, "Status", 8, INVOICE_STATUSES,
            default=d.get("status", "Unpaid"), width=28)
        self._fv["notes"] = make_label_entry(
            form, "Notes", 9, default=d.get("notes", ""), width=28)

        btn_frame = tk.Frame(self, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        make_button(btn_frame, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(btn_frame, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        if not data["recipient_name"]:
            messagebox.showerror("Validation", "Recipient name is required.", parent=self)
            return
        try:
            data["amount"] = float(data["amount"])
        except ValueError:
            messagebox.showerror("Validation", "Amount must be a number.", parent=self)
            return
        if self._data.get("id"):
            data["id"] = self._data["id"]
        if self._data.get("invoice_number"):
            data["invoice_number"] = self._data["invoice_number"]
        self._on_save(data)
        self.destroy()


# ─── Invoice preview window ────────────────────────────────────────────────────

class InvoicePreview(tk.Toplevel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title(f"Invoice Preview – {data['invoice_number']}")
        self.resizable(True, True)
        self.grab_set()
        self._data = data
        self._build()
        center_window(self, 520, 600)

    def _build(self):
        self.configure(bg=COLORS["white"])

        institution = db.get_setting("institution_name") or "My College"
        address = db.get_setting("institution_address") or ""
        phone = db.get_setting("institution_phone") or ""

        d = self._data

        canvas = tk.Canvas(self, bg=COLORS["white"])
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=COLORS["white"], padx=40, pady=30)

        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Header
        tk.Label(frame, text=institution, font=("Segoe UI", 18, "bold"),
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="center")
        tk.Label(frame, text=address, font=FONTS["small"],
                 bg=COLORS["white"], fg=COLORS["text_light"]).pack(anchor="center")
        tk.Label(frame, text=phone, font=FONTS["small"],
                 bg=COLORS["white"], fg=COLORS["text_light"]).pack(anchor="center")

        tk.Frame(frame, bg=COLORS["primary"], height=2).pack(fill=tk.X, pady=10)

        tk.Label(frame, text="INVOICE", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["white"], fg=COLORS["secondary"]).pack()

        info_frame = tk.Frame(frame, bg=COLORS["white"])
        info_frame.pack(fill=tk.X, pady=10)

        def row(parent, label, value, r):
            tk.Label(parent, text=label, font=FONTS["subheading"],
                     bg=COLORS["white"], fg=COLORS["text_light"],
                     anchor="w", width=20).grid(row=r, column=0, sticky="w", pady=2)
            tk.Label(parent, text=str(value), font=FONTS["body"],
                     bg=COLORS["white"], fg=COLORS["text"],
                     anchor="w").grid(row=r, column=1, sticky="w", pady=2)

        row(info_frame, "Invoice Number:", d["invoice_number"], 0)
        row(info_frame, "Invoice Type:", d["invoice_type"], 1)
        row(info_frame, "Issue Date:", d["issue_date"] or "", 2)
        row(info_frame, "Due Date:", d["due_date"] or "N/A", 3)
        row(info_frame, "Status:", d["status"], 4)
        row(info_frame, "Recipient:", d["recipient_name"], 5)
        if d.get("recipient_email"):
            row(info_frame, "Email:", d["recipient_email"], 6)
        if d.get("reference_id"):
            row(info_frame, "Reference:", d["reference_id"], 7)

        tk.Frame(frame, bg=COLORS["light"], height=2).pack(fill=tk.X, pady=10)

        # Amount
        amount_frame = tk.Frame(frame, bg=COLORS["light"], padx=20, pady=10)
        amount_frame.pack(fill=tk.X)
        tk.Label(amount_frame, text="Total Amount:", font=FONTS["subheading"],
                 bg=COLORS["light"]).pack(side=tk.LEFT)
        tk.Label(amount_frame, text=format_amount(d["amount"], d["currency"]),
                 font=("Segoe UI", 16, "bold"),
                 bg=COLORS["light"], fg=COLORS["success"]).pack(side=tk.RIGHT)

        if d.get("notes"):
            tk.Frame(frame, bg=COLORS["light"], height=2).pack(fill=tk.X, pady=10)
            tk.Label(frame, text="Notes:", font=FONTS["subheading"],
                     bg=COLORS["white"], anchor="w").pack(anchor="w")
            tk.Label(frame, text=d["notes"], font=FONTS["body"],
                     bg=COLORS["white"], anchor="w",
                     wraplength=400, justify="left").pack(anchor="w")

        tk.Frame(frame, bg=COLORS["primary"], height=2).pack(fill=tk.X, pady=16)
        tk.Label(frame, text="Thank you!", font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["text_light"]).pack()

        make_button(self, "✖ Close", self.destroy, style="danger").pack(pady=10)
