"""
Settings frame – institution info, currency configuration, fee types,
and backup / restore.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import database as db
from utils import (
    COLORS, FONTS, make_button, center_window,
    CURRENCY_SYMBOLS, CURRENCY_NAMES,
    get_available_currencies,
)


ALL_CURRENCIES = sorted(CURRENCY_SYMBOLS.keys())


class SettingsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["primary"], pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⚙️  Settings", font=FONTS["title"],
                 bg=COLORS["primary"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=20)

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._inst_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._curr_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._fee_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._bkp_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._nb.add(self._inst_tab, text="  Institution  ")
        self._nb.add(self._curr_tab, text="  Currency  ")
        self._nb.add(self._fee_tab, text="  Fee Types  ")
        self._nb.add(self._bkp_tab, text="  Backup & Restore  ")

        self._build_inst_tab()
        self._build_currency_tab()
        self._build_fee_tab()
        self._build_backup_tab()

    # ── Institution tab ───────────────────────────────────────────────────────

    def _build_inst_tab(self):
        frame = tk.Frame(self._inst_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Institution Information", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).grid(
            row=0, column=0, columnspan=2, pady=(0, 16), sticky="w"
        )

        self._inst_fv = {}
        fields = [
            ("Institution Name", "institution_name", 1),
            ("Address", "institution_address", 2),
            ("Phone", "institution_phone", 3),
            ("Email", "institution_email", 4),
        ]
        for label, key, row in fields:
            tk.Label(frame, text=label + ":", font=FONTS["body"],
                     bg=COLORS["white"], anchor="e", width=22).grid(
                row=row, column=0, padx=(0, 8), pady=6, sticky="e"
            )
            var = tk.StringVar()
            tk.Entry(frame, textvariable=var, font=FONTS["body"],
                     width=36, relief=tk.SOLID, bd=1).grid(
                row=row, column=1, pady=6, sticky="w"
            )
            self._inst_fv[key] = var

        make_button(frame, "💾 Save Institution Info", self._save_inst,
                    style="success").grid(row=6, column=1, pady=16, sticky="w")

    # ── Currency tab ──────────────────────────────────────────────────────────

    def _build_currency_tab(self):
        frame = tk.Frame(self._curr_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Currency Settings", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).grid(
            row=0, column=0, columnspan=3, pady=(0, 16), sticky="w"
        )

        # Default currency
        tk.Label(frame, text="Default Currency:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=1, column=0, padx=(0, 8), pady=8, sticky="e"
        )
        self._default_currency_var = tk.StringVar()
        self._default_currency_combo = ttk.Combobox(
            frame, textvariable=self._default_currency_var,
            values=ALL_CURRENCIES, width=16, state="readonly", font=FONTS["body"]
        )
        self._default_currency_combo.grid(row=1, column=1, pady=8, sticky="w")
        self._default_currency_combo.bind("<<ComboboxSelected>>", self._on_currency_select)

        self._currency_preview = tk.StringVar()
        tk.Label(frame, textvariable=self._currency_preview, font=FONTS["body"],
                 bg=COLORS["white"], fg=COLORS["text_light"]).grid(
            row=1, column=2, padx=10, sticky="w"
        )

        # Available currencies checklist
        tk.Label(frame, text="Available Currencies:", font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).grid(
            row=2, column=0, columnspan=3, pady=(16, 4), sticky="w"
        )
        tk.Label(frame, text="Select which currencies will appear in dropdowns throughout the app:",
                 font=FONTS["small"], bg=COLORS["white"],
                 fg=COLORS["text_light"]).grid(
            row=3, column=0, columnspan=3, sticky="w"
        )

        check_frame = tk.Frame(frame, bg=COLORS["white"])
        check_frame.grid(row=4, column=0, columnspan=3, pady=8, sticky="w")

        self._currency_vars = {}
        cols = 5
        for idx, code in enumerate(ALL_CURRENCIES):
            var = tk.BooleanVar()
            self._currency_vars[code] = var
            sym = CURRENCY_SYMBOLS.get(code, "")
            name = CURRENCY_NAMES.get(code, code)
            cb = tk.Checkbutton(
                check_frame,
                text=f"{code} ({sym}) – {name}",
                variable=var,
                font=FONTS["small"],
                bg=COLORS["white"],
                anchor="w",
            )
            cb.grid(row=idx // cols, column=idx % cols, padx=4, pady=2, sticky="w")

        make_button(frame, "💾 Save Currency Settings", self._save_currencies,
                    style="success").grid(row=5, column=0, columnspan=3, pady=16, sticky="w")

    # ── Fee types tab ─────────────────────────────────────────────────────────

    def _build_fee_tab(self):
        frame = tk.Frame(self._fee_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Fee Type Configuration", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 8))
        tk.Label(
            frame,
            text="Enter fee types separated by commas.\n"
                 "Example: Tuition, Library, Laboratory, Sports, Exam",
            font=FONTS["small"], bg=COLORS["white"], fg=COLORS["text_light"],
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        self._fee_types_var = tk.StringVar()
        tk.Entry(frame, textvariable=self._fee_types_var, font=FONTS["body"],
                 width=60, relief=tk.SOLID, bd=1).pack(anchor="w", pady=4)

        make_button(frame, "💾 Save Fee Types", self._save_fee_types,
                    style="success").pack(anchor="w", pady=12)

        tk.Label(frame, text="Current fee types:", font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", pady=(16, 4))
        self._fee_types_display = tk.Label(frame, text="", font=FONTS["body"],
                                            bg=COLORS["white"], fg=COLORS["text"],
                                            wraplength=600, justify="left")
        self._fee_types_display.pack(anchor="w")

    # ── Load / Save ───────────────────────────────────────────────────────────

    def _load(self):
        settings = db.get_all_settings()

        # Institution
        for key, var in self._inst_fv.items():
            var.set(settings.get(key, ""))

        # Currencies
        default = settings.get("default_currency", "USD")
        self._default_currency_var.set(default)
        self._update_currency_preview(default)

        available = [c.strip() for c in
                     settings.get("available_currencies", "USD").split(",")]
        for code, var in self._currency_vars.items():
            var.set(code in available)

        # Fee types
        fee_types = settings.get("fee_types", "")
        self._fee_types_var.set(fee_types)
        self._fee_types_display.config(text=fee_types.replace(",", " | "))

        # Backup directory
        self._backup_dir_var.set(
            settings.get("backup_directory", db.get_backup_directory())
        )
        self._refresh_backup_list()

    def _on_currency_select(self, *_):
        code = self._default_currency_var.get()
        self._update_currency_preview(code)

    def _update_currency_preview(self, code):
        sym = CURRENCY_SYMBOLS.get(code, "")
        name = CURRENCY_NAMES.get(code, "")
        self._currency_preview.set(f"{sym}  –  {name}")

    def _save_inst(self):
        for key, var in self._inst_fv.items():
            db.set_setting(key, var.get().strip())
        messagebox.showinfo("Saved", "Institution information saved.")

    def _save_currencies(self):
        default = self._default_currency_var.get()
        if not default:
            messagebox.showerror("Error", "Please select a default currency.")
            return
        selected = [c for c, v in self._currency_vars.items() if v.get()]
        if not selected:
            messagebox.showerror("Error", "Please select at least one available currency.")
            return
        if default not in selected:
            selected.insert(0, default)
        db.set_setting("default_currency", default)
        sym = CURRENCY_SYMBOLS.get(default, default)
        db.set_setting("currency_symbol", sym)
        db.set_setting("available_currencies", ",".join(selected))
        messagebox.showinfo(
            "Saved",
            f"Currency settings saved.\n"
            f"Default: {default} ({sym})\n"
            f"Available: {', '.join(selected)}"
        )

    def _save_fee_types(self):
        raw = self._fee_types_var.get().strip()
        types = [t.strip() for t in raw.split(",") if t.strip()]
        if not types:
            messagebox.showerror("Error", "Please enter at least one fee type.")
            return
        value = ", ".join(types)
        db.set_setting("fee_types", value)
        self._fee_types_display.config(text=value.replace(",", " | "))
        messagebox.showinfo("Saved", "Fee types saved.")

    # ── Backup & Restore tab ──────────────────────────────────────────────────

    def _build_backup_tab(self):
        frame = tk.Frame(self._bkp_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Backup & Restore", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(
            frame,
            text="Create timestamped backups of your database and restore them at any time.",
            font=FONTS["small"], bg=COLORS["white"], fg=COLORS["text_light"],
        ).pack(anchor="w", pady=(0, 14))

        # ── Backup directory row ──────────────────────────────────────────────
        dir_row = tk.Frame(frame, bg=COLORS["white"])
        dir_row.pack(fill=tk.X, pady=(0, 4))

        tk.Label(dir_row, text="Backup Directory:", font=FONTS["body"],
                 bg=COLORS["white"], width=20, anchor="e").pack(side=tk.LEFT, padx=(0, 8))

        self._backup_dir_var = tk.StringVar()
        tk.Entry(dir_row, textvariable=self._backup_dir_var,
                 font=FONTS["body"], width=46,
                 relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=(0, 6))

        make_button(dir_row, "📂 Browse", self._browse_backup_dir,
                    style="secondary").pack(side=tk.LEFT, padx=(0, 6))
        make_button(dir_row, "💾 Save Path", self._save_backup_dir,
                    style="success").pack(side=tk.LEFT)

        # ── Action buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(frame, bg=COLORS["white"])
        btn_row.pack(fill=tk.X, pady=14)

        make_button(btn_row, "⬆️  Create Backup Now", self._create_backup,
                    style="primary").pack(side=tk.LEFT, padx=(0, 10))
        make_button(btn_row, "📁 Restore from File…", self._restore_from_file,
                    style="warning").pack(side=tk.LEFT)

        # ── Existing backups list ─────────────────────────────────────────────
        tk.Label(frame, text="Existing Backups  (double-click to restore)",
                 font=FONTS["subheading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", pady=(6, 4))

        list_frame = tk.Frame(frame, bg=COLORS["white"])
        list_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("filename", "size", "created")
        self._backup_tree = ttk.Treeview(list_frame, columns=cols,
                                          show="headings", height=10)
        self._backup_tree.heading("filename", text="File Name", anchor="w")
        self._backup_tree.heading("size",     text="Size (KB)", anchor="w")
        self._backup_tree.heading("created",  text="Created At", anchor="w")
        self._backup_tree.column("filename", width=310, anchor="w")
        self._backup_tree.column("size",     width=90,  anchor="w")
        self._backup_tree.column("created",  width=160, anchor="w")

        vsb = ttk.Scrollbar(list_frame, orient="vertical",
                             command=self._backup_tree.yview)
        self._backup_tree.configure(yscrollcommand=vsb.set)
        self._backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.LEFT, fill=tk.Y)

        self._backup_tree.bind("<Double-1>", self._restore_selected_backup)

        # Refresh / Delete row
        btn_row2 = tk.Frame(frame, bg=COLORS["white"])
        btn_row2.pack(fill=tk.X, pady=(6, 0))
        make_button(btn_row2, "🔄 Refresh List", self._refresh_backup_list,
                    style="secondary").pack(side=tk.LEFT, padx=(0, 10))
        make_button(btn_row2, "🗑️  Delete Selected", self._delete_selected_backup,
                    style="danger").pack(side=tk.LEFT)

    # ── Backup helpers ────────────────────────────────────────────────────────

    def _browse_backup_dir(self):
        path = filedialog.askdirectory(
            title="Select Backup Directory",
            initialdir=self._backup_dir_var.get() or os.path.expanduser("~"),
        )
        if path:
            self._backup_dir_var.set(path)

    def _save_backup_dir(self):
        path = self._backup_dir_var.get().strip()
        if not path:
            messagebox.showerror("Error", "Please enter or browse to a backup directory.")
            return
        if not os.path.isabs(path):
            messagebox.showerror("Error", "Please select an absolute directory path.")
            return
        db.set_setting("backup_directory", path)
        os.makedirs(path, exist_ok=True)
        messagebox.showinfo("Saved", f"Backup directory saved:\n{path}")
        self._refresh_backup_list()

    def _create_backup(self):
        backup_dir = self._backup_dir_var.get().strip() or None
        try:
            dest = db.create_backup(backup_dir)
            messagebox.showinfo(
                "Backup Created",
                f"Backup saved successfully:\n{dest}"
            )
            self._refresh_backup_list()
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Backup Failed", str(exc))

    def _restore_from_file(self):
        path = filedialog.askopenfilename(
            title="Select Backup File to Restore",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            initialdir=self._backup_dir_var.get() or os.path.expanduser("~"),
        )
        if not path:
            return
        self._do_restore(path)

    def _restore_selected_backup(self, _event=None):
        sel = self._backup_tree.selection()
        if not sel:
            return
        item = self._backup_tree.item(sel[0])
        full_path = item["values"][3]  # hidden column with full path
        self._do_restore(full_path)

    def _do_restore(self, path):
        if not messagebox.askyesno(
            "Confirm Restore",
            f"Restore database from:\n{path}\n\n"
            "A safety backup of your current data will be created first.\n\n"
            "The application will need to reload after restore. Continue?"
        ):
            return
        try:
            safety = db.restore_backup(path)
            messagebox.showinfo(
                "Restore Successful",
                f"Database restored successfully.\n\n"
                f"A safety backup of your previous data was saved to:\n{safety}\n\n"
                "Please restart the application for the changes to take full effect."
            )
            self._refresh_backup_list()
        except (ValueError, OSError, Exception) as exc:  # pylint: disable=broad-except
            messagebox.showerror("Restore Failed", str(exc))

    def _refresh_backup_list(self):
        for row in self._backup_tree.get_children():
            self._backup_tree.delete(row)
        backup_dir = self._backup_dir_var.get().strip() or None
        entries = db.list_backups(backup_dir)
        for fname, full, size_kb, mtime in entries:
            self._backup_tree.insert(
                "", "end",
                values=(fname, f"{size_kb:.1f}", mtime, full)
            )

    def _delete_selected_backup(self):
        sel = self._backup_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a backup to delete.")
            return
        item = self._backup_tree.item(sel[0])
        fname = item["values"][0]
        full_path = item["values"][3]
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Permanently delete backup:\n{fname}?"
        ):
            return
        try:
            os.remove(full_path)
            self._refresh_backup_list()
        except OSError as exc:
            messagebox.showerror("Delete Failed", str(exc))
