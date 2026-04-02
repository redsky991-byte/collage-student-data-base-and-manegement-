"""
Utility helpers shared across all GUI frames.
"""

import tkinter as tk
from tkinter import ttk
import database as db

# ─── Currency data ────────────────────────────────────────────────────────────

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "PKR": "₨",
    "INR": "₹",
    "AED": "د.إ",
    "SAR": "﷼",
    "CAD": "CA$",
    "AUD": "A$",
    "JPY": "¥",
    "CNY": "¥",
    "CHF": "Fr",
    "MYR": "RM",
    "SGD": "S$",
    "BDT": "৳",
    "LKR": "Rs",
    "NPR": "Rs",
    "TRY": "₺",
    "ZAR": "R",
    "BRL": "R$",
}

CURRENCY_NAMES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "PKR": "Pakistani Rupee",
    "INR": "Indian Rupee",
    "AED": "UAE Dirham",
    "SAR": "Saudi Riyal",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
    "CHF": "Swiss Franc",
    "MYR": "Malaysian Ringgit",
    "SGD": "Singapore Dollar",
    "BDT": "Bangladeshi Taka",
    "LKR": "Sri Lankan Rupee",
    "NPR": "Nepalese Rupee",
    "TRY": "Turkish Lira",
    "ZAR": "South African Rand",
    "BRL": "Brazilian Real",
}


def get_available_currencies():
    """Return list of available currency codes from settings."""
    raw = db.get_setting("available_currencies") or "USD"
    return [c.strip() for c in raw.split(",") if c.strip()]


def get_default_currency():
    return db.get_setting("default_currency") or "USD"


def currency_display(code):
    """Return a display string like 'USD ($)'."""
    sym = CURRENCY_SYMBOLS.get(code, code)
    return f"{code} ({sym})"


def format_amount(amount, currency_code=None):
    """Format amount with currency symbol."""
    if currency_code is None:
        currency_code = get_default_currency()
    sym = CURRENCY_SYMBOLS.get(currency_code, currency_code)
    try:
        return f"{sym} {float(amount):,.2f}"
    except (TypeError, ValueError):
        return f"{sym} 0.00"


# ─── Widget helpers ───────────────────────────────────────────────────────────

COLORS = {
    "primary":    "#2C3E50",
    "secondary":  "#3498DB",
    "success":    "#27AE60",
    "warning":    "#F39C12",
    "danger":     "#E74C3C",
    "light":      "#ECF0F1",
    "white":      "#FFFFFF",
    "text":       "#2C3E50",
    "text_light": "#7F8C8D",
}

# ─── Dashboard Themes ─────────────────────────────────────────────────────────

THEMES = {
    "Default": {
        "primary":    "#2C3E50",
        "secondary":  "#3498DB",
        "success":    "#27AE60",
        "warning":    "#F39C12",
        "danger":     "#E74C3C",
        "light":      "#ECF0F1",
        "white":      "#FFFFFF",
        "text":       "#2C3E50",
        "text_light": "#7F8C8D",
        "description": "Dark navy sidebar with bright blue accents — the original look.",
    },
    "Classic": {
        "primary":    "#1A252F",
        "secondary":  "#2980B9",
        "success":    "#1E8449",
        "warning":    "#D4AC0D",
        "danger":     "#A93226",
        "light":      "#EBF5FB",
        "white":      "#FFFFFF",
        "text":       "#1A252F",
        "text_light": "#717D7E",
        "description": "Deep charcoal-blue sidebar — professional and timeless.",
    },
    "Stylish": {
        "primary":    "#4A235A",
        "secondary":  "#8E44AD",
        "success":    "#1E8449",
        "warning":    "#D4AC0D",
        "danger":     "#CB4335",
        "light":      "#F5EEF8",
        "white":      "#FFFFFF",
        "text":       "#2C2040",
        "text_light": "#8871A0",
        "description": "Rich purple sidebar — vibrant, modern and stylish.",
    },
    "Decent": {
        "primary":    "#1B4F72",
        "secondary":  "#2E86C1",
        "success":    "#1E8449",
        "warning":    "#CA6F1E",
        "danger":     "#CB4335",
        "light":      "#EBF5FB",
        "white":      "#FFFFFF",
        "text":       "#1B2631",
        "text_light": "#5D6D7E",
        "description": "Ocean-blue sidebar — neat, calm and decent.",
    },
    "Emerald": {
        "primary":    "#1D4E47",
        "secondary":  "#1ABC9C",
        "success":    "#17A589",
        "warning":    "#D4AC0D",
        "danger":     "#CB4335",
        "light":      "#E8F8F5",
        "white":      "#FFFFFF",
        "text":       "#1D3A35",
        "text_light": "#5D8A80",
        "description": "Forest-green sidebar — fresh, natural and refreshing.",
    },
}


def apply_theme(theme_name):
    """Apply a named theme's colors to the global COLORS dict."""
    theme = THEMES.get(theme_name, THEMES["Default"])
    for key, value in theme.items():
        if key != "description":
            COLORS[key] = value


def load_saved_theme():
    """Load the saved dashboard theme from the database and apply it to COLORS."""
    theme_name = db.get_setting("dashboard_theme") or "Default"
    apply_theme(theme_name)


# ─── Widget helpers ───────────────────────────────────────────────────────────

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "subheading": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "button": ("Segoe UI", 10, "bold"),
}


def apply_treeview_style(tree, columns, headings, col_widths=None):
    """Configure a ttk.Treeview with standard styling."""
    tree["columns"] = columns
    tree["show"] = "headings"
    for i, col in enumerate(columns):
        heading = headings[i] if i < len(headings) else col
        width = col_widths[i] if col_widths and i < len(col_widths) else 100
        tree.heading(col, text=heading, anchor="w")
        tree.column(col, width=width, anchor="w")


def make_button(parent, text, command, style="secondary", **kwargs):
    colors_map = {
        "primary": ("#2C3E50", "#FFFFFF"),
        "secondary": ("#3498DB", "#FFFFFF"),
        "success": ("#27AE60", "#FFFFFF"),
        "danger": ("#E74C3C", "#FFFFFF"),
        "warning": ("#F39C12", "#FFFFFF"),
    }
    bg, fg = colors_map.get(style, ("#3498DB", "#FFFFFF"))
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=FONTS["button"],
        relief=tk.FLAT,
        padx=14,
        pady=6,
        cursor="hand2",
        activebackground=bg,
        activeforeground=fg,
        **kwargs,
    )
    return btn


def make_label_entry(parent, label_text, row, col=0, default="", width=25):
    """Create a label + entry pair and return the Entry widget."""
    tk.Label(parent, text=label_text, font=FONTS["body"],
             bg=COLORS["white"], anchor="e").grid(
        row=row, column=col, padx=(10, 4), pady=4, sticky="e"
    )
    var = tk.StringVar(value=default)
    entry = tk.Entry(parent, textvariable=var, font=FONTS["body"], width=width,
                     relief=tk.SOLID, bd=1)
    entry.grid(row=row, column=col + 1, padx=(0, 10), pady=4, sticky="w")
    return var


def make_label_combo(parent, label_text, row, values, col=0, default="", width=23):
    """Create a label + combobox pair and return the StringVar."""
    tk.Label(parent, text=label_text, font=FONTS["body"],
             bg=COLORS["white"], anchor="e").grid(
        row=row, column=col, padx=(10, 4), pady=4, sticky="e"
    )
    var = tk.StringVar(value=default)
    combo = ttk.Combobox(parent, textvariable=var, values=values,
                         font=FONTS["body"], width=width - 2, state="readonly")
    combo.grid(row=row, column=col + 1, padx=(0, 10), pady=4, sticky="w")
    return var


def center_window(win, width, height):
    """Center a Toplevel or Tk window on screen."""
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")
