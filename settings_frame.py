"""
Settings frame – institution info, currency configuration, fee types.
"""

import tkinter as tk
from tkinter import ttk, messagebox

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
        self._nb.add(self._inst_tab, text="  Institution  ")
        self._nb.add(self._curr_tab, text="  Currency  ")
        self._nb.add(self._fee_tab, text="  Fee Types  ")

        self._build_inst_tab()
        self._build_currency_tab()
        self._build_fee_tab()

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
