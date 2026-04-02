"""
Notices / Announcements board frame.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from utils import COLORS, FONTS, apply_treeview_style, make_button, center_window, make_label_entry, make_label_combo

NOTICE_CATEGORIES = ["General", "Academic", "Exam", "Holiday", "Sports", "Fee", "Urgent", "Event"]
NOTICE_AUDIENCES = ["All", "Students", "Staff", "Teachers", "Parents"]


class NoticesFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg="#D35400", pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📣  Notices & Announcements", font=FONTS["title"],
                 bg="#D35400", fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        toolbar = tk.Frame(self, bg=COLORS["light"], pady=6)
        toolbar.pack(fill=tk.X, padx=4)
        make_button(toolbar, "➕ Post Notice", self._add_notice,
                    style="success").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "✏️ Edit", self._edit_notice,
                    style="secondary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🗑️ Delete", self._delete_notice,
                    style="danger").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "👁 View", self._view_notice,
                    style="primary").pack(side=tk.LEFT, padx=4)
        make_button(toolbar, "🔄 Refresh", self.refresh,
                    style="primary").pack(side=tk.LEFT, padx=4)

        self._show_all_var = tk.BooleanVar(value=True)
        tk.Checkbutton(toolbar, text="Show All (incl. inactive)",
                       variable=self._show_all_var,
                       command=self.refresh,
                       bg=COLORS["light"], font=FONTS["body"]).pack(side=tk.LEFT, padx=8)

        self._notice_stats = tk.StringVar()
        tk.Label(toolbar, textvariable=self._notice_stats, font=FONTS["small"],
                 bg=COLORS["light"], fg=COLORS["text_light"]).pack(side=tk.RIGHT, padx=10)

        tf = tk.Frame(self, bg=COLORS["light"])
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("id", "title", "category", "audience", "posted_by", "posted_date",
                "expiry_date", "active")
        hdgs = ("#", "Title", "Category", "Audience", "Posted By", "Date",
                "Expiry", "Active")
        wids = (40, 280, 100, 90, 120, 100, 100, 60)
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
        self._tree.bind("<Double-1>", lambda e: self._view_notice())

    def refresh(self):
        active_only = not self._show_all_var.get()
        notices = db.get_all_notices(active_only=active_only)
        self._tree.delete(*self._tree.get_children())
        today = datetime.now().strftime("%Y-%m-%d")
        for n in notices:
            is_active = "Yes" if n["is_active"] else "No"
            tag = "active" if n["is_active"] else "inactive"
            # Highlight urgent
            if n.get("category") == "Urgent":
                tag = "urgent"
            self._tree.insert("", tk.END, values=(
                n["id"], n["title"], n.get("category", ""),
                n.get("audience", ""), n.get("posted_by", "") or "",
                n.get("posted_date", ""), n.get("expiry_date", "") or "",
                is_active,
            ), tags=(tag,))
        self._tree.tag_configure("active", foreground=COLORS["text"])
        self._tree.tag_configure("inactive", foreground=COLORS["text_light"])
        self._tree.tag_configure("urgent", foreground=COLORS["danger"])
        self._notice_stats.set(f"Total: {len(notices)} notice(s)")

    def _selected_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a notice.")
            return None
        return self._tree.item(sel[0])["values"][0]

    def _add_notice(self):
        NoticeDialog(self, title="Post New Notice", on_save=self._save_new)

    def _edit_notice(self):
        nid = self._selected_id()
        if not nid:
            return
        data = db.get_notice(nid)
        if data:
            NoticeDialog(self, title="Edit Notice", data=data, on_save=self._save_edit)

    def _save_new(self, data):
        db.add_notice(data)
        messagebox.showinfo("Success", "Notice posted successfully.")
        self.refresh()

    def _save_edit(self, data):
        db.update_notice(data)
        messagebox.showinfo("Success", "Notice updated.")
        self.refresh()

    def _delete_notice(self):
        nid = self._selected_id()
        if not nid:
            return
        if messagebox.askyesno("Confirm", "Delete this notice?"):
            db.delete_notice(nid)
            self.refresh()

    def _view_notice(self):
        nid = self._selected_id()
        if not nid:
            return
        data = db.get_notice(nid)
        if data:
            NoticeViewer(self, data)


# ─── Notice dialog ─────────────────────────────────────────────────────────────

class NoticeDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, data=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(True, True)
        self.grab_set()
        self._on_save = on_save
        self._data = data or {}
        self._build()
        center_window(self, 560, 500)

    def _build(self):
        self.configure(bg=COLORS["white"])
        tk.Label(self, text=self.title(), font=FONTS["heading"],
                 bg="#D35400", fg=COLORS["white"]).pack(fill=tk.X, pady=(0, 10))

        form = tk.Frame(self, bg=COLORS["white"], padx=20)
        form.pack(fill=tk.BOTH, expand=True, pady=10)
        form.columnconfigure(1, weight=1)

        d = self._data
        self._fv = {}

        self._fv["title"] = make_label_entry(form, "Title *", 0,
                                              default=d.get("title", ""), width=42)
        self._fv["category"] = make_label_combo(
            form, "Category", 1, NOTICE_CATEGORIES,
            default=d.get("category", "General"), width=40)
        self._fv["audience"] = make_label_combo(
            form, "Audience", 2, NOTICE_AUDIENCES,
            default=d.get("audience", "All"), width=40)
        self._fv["posted_by"] = make_label_entry(form, "Posted By", 3,
                                                  default=d.get("posted_by", "") or "", width=42)
        self._fv["posted_date"] = make_label_entry(
            form, "Post Date", 4,
            default=d.get("posted_date", datetime.now().strftime("%Y-%m-%d")), width=42)
        self._fv["expiry_date"] = make_label_entry(form, "Expiry Date", 5,
                                                    default=d.get("expiry_date", "") or "", width=42)

        # Active checkbox
        self._active_var = tk.BooleanVar(value=bool(d.get("is_active", 1)))
        tk.Label(form, text="Active:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e").grid(row=6, column=0, padx=4, pady=4, sticky="e")
        tk.Checkbutton(form, variable=self._active_var,
                       bg=COLORS["white"]).grid(row=6, column=1, padx=4, pady=4, sticky="w")

        # Content text area
        tk.Label(form, text="Content *", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e").grid(row=7, column=0, padx=4, pady=4, sticky="ne")
        self._content_text = tk.Text(form, font=FONTS["body"], width=42, height=10,
                                     relief=tk.SOLID, bd=1, wrap=tk.WORD)
        self._content_text.grid(row=7, column=1, padx=4, pady=4, sticky="nsew")
        if d.get("content"):
            self._content_text.insert("1.0", d["content"])
        form.rowconfigure(7, weight=1)

        bf = tk.Frame(self, bg=COLORS["white"])
        bf.pack(fill=tk.X, padx=20, pady=10)
        make_button(bf, "💾 Save", self._save, style="success").pack(side=tk.LEFT, padx=4)
        make_button(bf, "✖ Cancel", self.destroy, style="danger").pack(side=tk.LEFT, padx=4)

    def _save(self):
        data = {k: v.get().strip() for k, v in self._fv.items()}
        data["content"] = self._content_text.get("1.0", tk.END).strip()
        data["is_active"] = 1 if self._active_var.get() else 0
        if not data["title"]:
            messagebox.showerror("Validation", "Title is required.", parent=self)
            return
        if not data["content"]:
            messagebox.showerror("Validation", "Content is required.", parent=self)
            return
        if self._data.get("id"):
            data["id"] = self._data["id"]
        self._on_save(data)
        self.destroy()


# ─── Notice viewer ─────────────────────────────────────────────────────────────

class NoticeViewer(tk.Toplevel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title(f"Notice – {data.get('title', '')}")
        self.resizable(True, True)
        self.grab_set()
        self._build(data)
        center_window(self, 560, 420)

    def _build(self, d):
        self.configure(bg=COLORS["white"])

        hdr = tk.Frame(self, bg="#D35400", pady=8)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=d.get("title", ""), font=FONTS["heading"],
                 bg="#D35400", fg=COLORS["white"],
                 wraplength=520).pack(padx=16, pady=4)

        meta = tk.Frame(self, bg=COLORS["light"])
        meta.pack(fill=tk.X, padx=16, pady=6)
        meta_items = [
            ("Category", d.get("category", "")),
            ("Audience", d.get("audience", "")),
            ("Posted By", d.get("posted_by", "") or "—"),
            ("Date", d.get("posted_date", "")),
            ("Expiry", d.get("expiry_date", "") or "—"),
            ("Status", "Active" if d.get("is_active") else "Inactive"),
        ]
        for i, (label, val) in enumerate(meta_items):
            col = (i % 3) * 2
            row = i // 3
            tk.Label(meta, text=f"{label}:", font=FONTS["small"],
                     bg=COLORS["light"], fg=COLORS["text_light"]).grid(
                row=row, column=col, padx=4, pady=2, sticky="e")
            tk.Label(meta, text=val, font=FONTS["body"],
                     bg=COLORS["light"]).grid(
                row=row, column=col + 1, padx=4, pady=2, sticky="w")

        tk.Label(self, text="Content:", font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", padx=16, pady=(8, 2))

        txt_frame = tk.Frame(self, bg=COLORS["white"])
        txt_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        txt = tk.Text(txt_frame, font=FONTS["body"], wrap=tk.WORD, state=tk.DISABLED,
                      relief=tk.SOLID, bd=1)
        vsb = ttk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.configure(state=tk.NORMAL)
        txt.insert("1.0", d.get("content", ""))
        txt.configure(state=tk.DISABLED)

        make_button(self, "✖ Close", self.destroy, style="danger").pack(pady=8)
