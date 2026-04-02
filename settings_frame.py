"""
Settings frame – institution info, currency configuration, fee types, backup/restore.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime

import database as db
from utils import (
    COLORS, FONTS, THEMES, apply_theme, make_button, center_window,
    CURRENCY_SYMBOLS, CURRENCY_NAMES,
    get_available_currencies,
)


ALL_CURRENCIES = sorted(CURRENCY_SYMBOLS.keys())


class SettingsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=COLORS["light"], *args, **kwargs)
        self._build()
        self._load()

    def refresh(self):
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
        self._title_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._acad_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._theme_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._backup_tab = tk.Frame(self._nb, bg=COLORS["white"])
        self._nb.add(self._inst_tab, text="  Institution  ")
        self._nb.add(self._curr_tab, text="  Currency  ")
        self._nb.add(self._fee_tab, text="  Fee Types  ")
        self._nb.add(self._title_tab, text="  Title Style  ")
        self._nb.add(self._acad_tab, text="  Academic  ")
        self._nb.add(self._theme_tab, text="  Dashboard Theme  ")
        self._nb.add(self._backup_tab, text="  Backup & Restore  ")

        self._build_inst_tab()
        self._build_currency_tab()
        self._build_fee_tab()
        self._build_title_tab()
        self._build_acad_tab()
        self._build_theme_tab()
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

    # ── Title style tab ────────────────────────────────────────────────────────

    def _build_title_tab(self):
        frame = tk.Frame(self._title_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Customize Title Style", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).grid(
            row=0, column=0, columnspan=3, pady=(0, 16), sticky="w")

        self._title_fv = {}
        tk.Label(frame, text="Title Font:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=1, column=0, padx=(0, 8), pady=6, sticky="e")
        font_choices = ["Segoe UI", "Arial", "Calibri", "Times New Roman",
                        "Courier New", "Verdana", "Georgia", "Tahoma", "Comic Sans MS"]
        self._title_fv["title_font"] = tk.StringVar()
        ttk.Combobox(frame, textvariable=self._title_fv["title_font"],
                     values=font_choices, width=24, font=FONTS["body"],
                     state="readonly").grid(row=1, column=1, pady=6, sticky="w")

        tk.Label(frame, text="Font Size:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=2, column=0, padx=(0, 8), pady=6, sticky="e")
        self._title_fv["title_font_size"] = tk.StringVar()
        size_choices = [str(i) for i in range(10, 40, 2)]
        ttk.Combobox(frame, textvariable=self._title_fv["title_font_size"],
                     values=size_choices, width=8, font=FONTS["body"],
                     state="readonly").grid(row=2, column=1, pady=6, sticky="w")

        tk.Label(frame, text="Bold:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=3, column=0, padx=(0, 8), pady=6, sticky="e")
        self._title_bold_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, variable=self._title_bold_var,
                       bg=COLORS["white"]).grid(row=3, column=1, pady=6, sticky="w")

        tk.Label(frame, text="Title Text Color:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=4, column=0, padx=(0, 8), pady=6, sticky="e")
        self._title_fv["title_color"] = tk.StringVar()
        color_entry = tk.Entry(frame, textvariable=self._title_fv["title_color"],
                               font=FONTS["body"], width=14, relief=tk.SOLID, bd=1)
        color_entry.grid(row=4, column=1, pady=6, sticky="w")
        self._title_color_preview = tk.Label(frame, text="  ████  ", font=FONTS["body"],
                                              bg=COLORS["white"])
        self._title_color_preview.grid(row=4, column=2, padx=4)
        self._title_fv["title_color"].trace_add(
            "write", lambda *_: self._update_title_preview())

        tk.Label(frame, text="Sidebar BG Color:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=5, column=0, padx=(0, 8), pady=6, sticky="e")
        self._title_fv["title_bg_color"] = tk.StringVar()
        bg_entry = tk.Entry(frame, textvariable=self._title_fv["title_bg_color"],
                            font=FONTS["body"], width=14, relief=tk.SOLID, bd=1)
        bg_entry.grid(row=5, column=1, pady=6, sticky="w")
        self._title_bg_preview = tk.Label(frame, text="  ████  ", font=FONTS["body"],
                                           bg=COLORS["white"])
        self._title_bg_preview.grid(row=5, column=2, padx=4)
        self._title_fv["title_bg_color"].trace_add(
            "write", lambda *_: self._update_title_preview())

        tk.Label(frame,
                 text="Note: Color values must be valid hex codes (e.g. #2C3E50). "
                      "Restart the app to see sidebar color changes.",
                 font=FONTS["small"], bg=COLORS["white"], fg=COLORS["text_light"],
                 wraplength=480, justify="left").grid(
            row=6, column=0, columnspan=3, pady=8, sticky="w")

        make_button(frame, "💾 Save Title Style", self._save_title_style,
                    style="success").grid(row=7, column=1, pady=16, sticky="w")

    # ── Academic settings tab ──────────────────────────────────────────────────

    def _build_acad_tab(self):
        frame = tk.Frame(self._acad_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Academic Settings", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).grid(
            row=0, column=0, columnspan=2, pady=(0, 16), sticky="w")

        tk.Label(frame, text="Academic Year:", font=FONTS["body"],
                 bg=COLORS["white"], anchor="e", width=22).grid(
            row=1, column=0, padx=(0, 8), pady=6, sticky="e")
        self._acad_year_var = tk.StringVar()
        tk.Entry(frame, textvariable=self._acad_year_var, font=FONTS["body"],
                 width=14, relief=tk.SOLID, bd=1).grid(
            row=1, column=1, pady=6, sticky="w")

        tk.Label(frame,
                 text="This year is used as the default in subject assignments and enrollments.",
                 font=FONTS["small"], bg=COLORS["white"], fg=COLORS["text_light"],
                 wraplength=480, justify="left").grid(
            row=2, column=0, columnspan=2, pady=6, sticky="w")

        make_button(frame, "💾 Save Academic Settings", self._save_acad,
                    style="success").grid(row=3, column=1, pady=16, sticky="w")

    # ── Dashboard Theme tab ────────────────────────────────────────────────────

    def _build_theme_tab(self):
        outer = tk.Frame(self._theme_tab, bg=COLORS["white"])
        outer.pack(fill=tk.BOTH, expand=True)

        # Scrollable container
        canvas = tk.Canvas(outer, bg=COLORS["white"], highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frame = tk.Frame(canvas, bg=COLORS["white"], padx=30, pady=20)
        frame_id = canvas.create_window((0, 0), window=frame, anchor="nw")

        def _on_frame_cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_cfg(e):
            canvas.itemconfig(frame_id, width=e.width)

        frame.bind("<Configure>", _on_frame_cfg)
        canvas.bind("<Configure>", _on_canvas_cfg)

        tk.Label(frame, text="🎨  Dashboard Themes", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(
            frame,
            text="Choose a theme to set the color palette for the entire application.\n"
                 "Click 'Apply Theme' then restart the app for all changes to take effect.",
            font=FONTS["small"], bg=COLORS["white"], fg=COLORS["text_light"],
            justify="left",
        ).pack(anchor="w", pady=(0, 14))

        self._theme_var = tk.StringVar(value="Default")

        # Build one card per theme
        self._theme_cards = {}
        for name, data in THEMES.items():
            card = tk.Frame(frame, bg=COLORS["light"], relief=tk.FLAT, bd=0)
            card.pack(fill=tk.X, pady=5)
            self._theme_cards[name] = card

            # Left: radio + name + description
            left = tk.Frame(card, bg=COLORS["light"])
            left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

            rb = tk.Radiobutton(
                left,
                text=f"  {name}",
                variable=self._theme_var,
                value=name,
                font=FONTS["subheading"],
                bg=COLORS["light"],
                fg=COLORS["text"],
                activebackground=COLORS["light"],
                selectcolor=COLORS["light"],
                command=self._on_theme_select,
            )
            rb.pack(anchor="w")

            tk.Label(
                left,
                text=data["description"],
                font=FONTS["small"],
                bg=COLORS["light"],
                fg=COLORS["text_light"],
                anchor="w",
            ).pack(anchor="w", padx=22)

            # Right: color swatches
            right = tk.Frame(card, bg=COLORS["light"])
            right.pack(side=tk.RIGHT, padx=14, pady=8)

            for swatch_key, label in [
                ("primary",   "Sidebar"),
                ("secondary", "Accent"),
                ("success",   "Success"),
                ("light",     "Background"),
            ]:
                swatch_col = tk.Frame(right, bg=COLORS["light"])
                swatch_col.pack(side=tk.LEFT, padx=5)
                tk.Frame(
                    swatch_col,
                    bg=data[swatch_key],
                    width=32, height=32,
                    relief=tk.SOLID, bd=1,
                ).pack()
                tk.Label(
                    swatch_col,
                    text=label,
                    font=("Segoe UI", 7),
                    bg=COLORS["light"],
                    fg=COLORS["text_light"],
                ).pack()

        # Buttons row
        btn_row = tk.Frame(frame, bg=COLORS["white"])
        btn_row.pack(anchor="w", pady=(14, 4))
        make_button(btn_row, "✅ Apply Theme", self._save_theme,
                    style="success").pack(side=tk.LEFT, padx=(0, 10))
        make_button(btn_row, "↩ Reset to Default", self._reset_theme,
                    style="primary").pack(side=tk.LEFT)

        self._theme_status = tk.Label(frame, text="", font=FONTS["small"],
                                      bg=COLORS["white"], fg=COLORS["success"])
        self._theme_status.pack(anchor="w", pady=(4, 0))

    def _on_theme_select(self):
        """Highlight the selected theme card."""
        selected = self._theme_var.get()
        for name, card in self._theme_cards.items():
            color = THEMES[name]["secondary"] if name == selected else COLORS["light"]
            card.configure(bg=color)
            for child in card.winfo_children():
                try:
                    child.configure(bg=color)
                except tk.TclError:
                    pass
                for grandchild in child.winfo_children():
                    try:
                        grandchild.configure(bg=color)
                    except tk.TclError:
                        pass

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

        # Title style
        for key, var in self._title_fv.items():
            var.set(settings.get(key, ""))
        self._title_bold_var.set(settings.get("title_bold", "1") == "1")
        self._update_title_preview()

        # Academic
        self._acad_year_var.set(settings.get("academic_year", ""))

        # Dashboard theme
        saved_theme = settings.get("dashboard_theme", "Default")
        if saved_theme not in THEMES:
            saved_theme = "Default"
        self._theme_var.set(saved_theme)
        self._on_theme_select()

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

    def _update_title_preview(self):
        try:
            color = self._title_fv["title_color"].get().strip() or COLORS["white"]
            self._title_color_preview.config(fg=color, text="  ████  ")
        except Exception:
            pass
        try:
            bg_color = self._title_fv["title_bg_color"].get().strip() or COLORS["primary"]
            self._title_bg_preview.config(fg=bg_color, text="  ████  ")
        except Exception:
            pass

    def _save_title_style(self):
        for key, var in self._title_fv.items():
            val = var.get().strip()
            if val:
                db.set_setting(key, val)
        db.set_setting("title_bold", "1" if self._title_bold_var.get() else "0")
        messagebox.showinfo("Saved",
                            "Title style saved. Restart the app to see all changes take effect.")

    def _save_acad(self):
        year = self._acad_year_var.get().strip()
        if not year:
            messagebox.showerror("Error", "Please enter an academic year.")
            return
        db.set_setting("academic_year", year)
        messagebox.showinfo("Saved", f"Academic year set to {year}.")

    def _save_theme(self):
        name = self._theme_var.get()
        db.set_setting("dashboard_theme", name)
        apply_theme(name)
        self._theme_status.config(
            text=f"✅  '{name}' theme applied. Restart the app to see all changes.",
            fg=COLORS["success"],
        )

    def _reset_theme(self):
        self._theme_var.set("Default")
        self._on_theme_select()
        self._save_theme()

    # ── Backup & Restore tab ──────────────────────────────────────────────────

    def _build_backup_tab(self):
        frame = tk.Frame(self._backup_tab, bg=COLORS["white"], padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="🗄️  Data Backup & Restore", font=FONTS["heading"],
                 bg=COLORS["white"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 4))
        tk.Label(
            frame,
            text="Create a backup of the entire database or restore from a previous backup.\n"
                 "Backups are saved as .db files that can be stored anywhere on your computer.",
            font=FONTS["small"], bg=COLORS["white"], fg=COLORS["text_light"],
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        # ── Backup section ────────────────────────────────────────────────────
        backup_box = tk.LabelFrame(frame, text="  💾  Create Backup  ",
                                   font=FONTS["subheading"], bg=COLORS["white"],
                                   fg=COLORS["primary"])
        backup_box.pack(fill=tk.X, pady=(0, 16))

        b_inner = tk.Frame(backup_box, bg=COLORS["white"], padx=16, pady=12)
        b_inner.pack(fill=tk.X)

        tk.Label(b_inner,
                 text="Backup Destination Folder:",
                 font=FONTS["body"], bg=COLORS["white"]).grid(
            row=0, column=0, sticky="e", padx=(0, 8), pady=4)
        self._backup_dir_var = tk.StringVar(
            value=os.path.expanduser("~")
        )
        tk.Entry(b_inner, textvariable=self._backup_dir_var,
                 font=FONTS["body"], width=44, relief=tk.SOLID, bd=1).grid(
            row=0, column=1, sticky="w", pady=4)
        make_button(b_inner, "📂 Browse", self._browse_backup_dir,
                    style="primary").grid(row=0, column=2, padx=6)

        tk.Label(b_inner,
                 text="Backup File Name (optional):",
                 font=FONTS["body"], bg=COLORS["white"]).grid(
            row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        self._backup_name_var = tk.StringVar(
            value=f"college_backup_{datetime.now().strftime('%Y%m%d')}.db"
        )
        tk.Entry(b_inner, textvariable=self._backup_name_var,
                 font=FONTS["body"], width=44, relief=tk.SOLID, bd=1).grid(
            row=1, column=1, sticky="w", pady=4)
        tk.Label(b_inner, text="(leave as is for auto-dated name)",
                 font=FONTS["small"], bg=COLORS["white"],
                 fg=COLORS["text_light"]).grid(row=1, column=2, padx=6, sticky="w")

        make_button(b_inner, "💾 Backup Now", self._do_backup,
                    style="success").grid(row=2, column=1, pady=12, sticky="w")

        self._backup_status = tk.Label(b_inner, text="", font=FONTS["small"],
                                       bg=COLORS["white"], fg=COLORS["success"],
                                       wraplength=480, justify="left")
        self._backup_status.grid(row=3, column=0, columnspan=3, sticky="w")

        # ── Restore section ───────────────────────────────────────────────────
        restore_box = tk.LabelFrame(frame, text="  🔄  Restore from Backup  ",
                                    font=FONTS["subheading"], bg=COLORS["white"],
                                    fg=COLORS["primary"])
        restore_box.pack(fill=tk.X, pady=(0, 16))

        r_inner = tk.Frame(restore_box, bg=COLORS["white"], padx=16, pady=12)
        r_inner.pack(fill=tk.X)

        tk.Label(r_inner,
                 text="⚠️  Warning: Restoring will overwrite ALL current data.",
                 font=("Segoe UI", 10, "bold"), bg=COLORS["white"],
                 fg=COLORS["danger"]).pack(anchor="w", pady=(0, 8))

        file_row = tk.Frame(r_inner, bg=COLORS["white"])
        file_row.pack(anchor="w")

        tk.Label(file_row, text="Backup File:", font=FONTS["body"],
                 bg=COLORS["white"]).pack(side=tk.LEFT, padx=(0, 8))
        self._restore_file_var = tk.StringVar()
        tk.Entry(file_row, textvariable=self._restore_file_var,
                 font=FONTS["body"], width=44, relief=tk.SOLID, bd=1).pack(side=tk.LEFT)
        make_button(file_row, "📂 Browse", self._browse_restore_file,
                    style="primary").pack(side=tk.LEFT, padx=6)

        make_button(r_inner, "🔄 Restore Now", self._do_restore,
                    style="danger").pack(anchor="w", pady=10)

        self._restore_status = tk.Label(r_inner, text="", font=FONTS["small"],
                                        bg=COLORS["white"], fg=COLORS["success"],
                                        wraplength=480, justify="left")
        self._restore_status.pack(anchor="w")

        # ── Tips section ──────────────────────────────────────────────────────
        tips_box = tk.LabelFrame(frame, text="  💡  Backup Tips  ",
                                 font=FONTS["subheading"], bg=COLORS["white"],
                                 fg=COLORS["primary"])
        tips_box.pack(fill=tk.X)

        tips = [
            "• Back up regularly – we recommend once a week.",
            "• Store backups on an external drive or cloud storage (e.g. Google Drive, OneDrive).",
            "• Keep multiple dated backup files in case a recent backup is also corrupted.",
            "• After restoring, restart the application for all changes to take effect.",
        ]
        for tip in tips:
            tk.Label(tips_box, text=tip, font=FONTS["small"], bg=COLORS["white"],
                     fg=COLORS["text_light"], anchor="w").pack(anchor="w", padx=12, pady=2)

    def _browse_backup_dir(self):
        folder = filedialog.askdirectory(
            title="Select Backup Destination Folder",
            initialdir=self._backup_dir_var.get() or os.path.expanduser("~"),
        )
        if folder:
            self._backup_dir_var.set(folder)

    def _browse_restore_file(self):
        path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            initialdir=self._backup_dir_var.get() or os.path.expanduser("~"),
        )
        if path:
            self._restore_file_var.set(path)

    def _do_backup(self):
        folder = self._backup_dir_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid destination folder.")
            return
        name = self._backup_name_var.get().strip()
        if not name:
            name = f"college_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if not name.endswith(".db"):
            name += ".db"
        dest = os.path.join(folder, name)
        ok, msg = db.backup_database(dest)
        if ok:
            self._backup_status.config(text=f"✅  {msg}", fg=COLORS["success"])
            messagebox.showinfo("Backup Successful", msg)
        else:
            self._backup_status.config(text=f"❌  {msg}", fg=COLORS["danger"])
            messagebox.showerror("Backup Failed", msg)

    def _do_restore(self):
        src = self._restore_file_var.get().strip()
        if not src or not os.path.isfile(src):
            messagebox.showerror("Error", "Please select a valid backup file.")
            return
        confirmed = messagebox.askyesno(
            "Confirm Restore",
            "⚠️  This will OVERWRITE all current data with the selected backup.\n\n"
            "Are you absolutely sure you want to continue?",
        )
        if not confirmed:
            return
        ok, msg = db.restore_database(src)
        if ok:
            self._restore_status.config(text=f"✅  {msg}", fg=COLORS["success"])
            messagebox.showinfo("Restore Successful", msg)
        else:
            self._restore_status.config(text=f"❌  {msg}", fg=COLORS["danger"])
            messagebox.showerror("Restore Failed", msg)

