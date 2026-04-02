"""
College Student Database and Management System
Main application entry point.

Run:
    python main.py

Build to .exe (Windows):
    pyinstaller app.spec
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Ensure the app directory is on the path so all modules resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from utils import COLORS, FONTS, center_window, make_button, load_saved_theme
from dashboard_frame import DashboardFrame
from students_frame import StudentsFrame
from fees_frame import FeesFrame
from salary_frame import SalaryFrame
from invoices_frame import InvoicesFrame
from settings_frame import SettingsFrame
from attendance_frame import AttendanceFrame
from subjects_frame import SubjectsFrame
from notices_frame import NoticesFrame


APP_VERSION = "v2.0.0"
DEVELOPER_NAME = "Zulfiqar Ali"
DEVELOPER_URL = "www.maxtechfix.com"


class CollegeApp(tk.Tk):
    """Main application window."""

    NAV_ITEMS = [
        ("🏠  Dashboard",       DashboardFrame,   "dashboard"),
        ("🎓  Students",        StudentsFrame,    "students"),
        ("📋  Attendance",      AttendanceFrame,  "attendance"),
        ("📚  Subjects",        SubjectsFrame,    "subjects"),
        ("💳  Fees",            FeesFrame,        "fees"),
        ("👥  Staff & Salary",  SalaryFrame,      "salary"),
        ("🧾  Invoices",        InvoicesFrame,    "invoices"),
        ("📣  Notices",         NoticesFrame,     "notices"),
        ("⚙️  Settings",        SettingsFrame,    "settings"),
    ]

    def __init__(self):
        super().__init__()
        db.initialize_db()
        load_saved_theme()       # Apply saved colour theme before building UI
        self._apply_title_style()
        self.state("zoomed")          # Start maximised on Windows
        self.minsize(1100, 660)
        self.configure(bg=COLORS["primary"])

        self._frames = {}
        self._active_key = None
        self._build_ui()
        self._show("dashboard")

    def _apply_title_style(self):
        institution = db.get_setting("institution_name") or "College Management System"
        self.title(institution)
        # Apply sidebar background from settings
        bg = db.get_setting("title_bg_color")
        if bg:
            COLORS["primary"] = bg
        fg = db.get_setting("title_color")
        if fg:
            COLORS["white"] = fg

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        institution = db.get_setting("institution_name") or "My College"
        title_font_name = db.get_setting("title_font") or "Segoe UI"
        try:
            title_font_size = int(db.get_setting("title_font_size") or "12")
        except (TypeError, ValueError):
            title_font_size = 12
        title_bold = db.get_setting("title_bold")
        title_font_weight = "bold" if title_bold != "0" else "normal"
        title_font = (title_font_name, title_font_size, title_font_weight)

        # Sidebar
        self._sidebar = tk.Frame(self, bg=COLORS["primary"], width=210)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        self._sidebar_title = tk.Label(
            self._sidebar, text=institution, font=title_font,
            bg=COLORS["primary"], fg=COLORS["white"],
            wraplength=195, justify="center", pady=18
        )
        self._sidebar_title.pack(fill=tk.X)

        tk.Frame(self._sidebar, bg=COLORS["secondary"], height=1).pack(fill=tk.X)

        self._nav_buttons = {}
        for label, _cls, key in self.NAV_ITEMS:
            btn = tk.Button(
                self._sidebar,
                text=label,
                font=FONTS["body"],
                bg=COLORS["primary"],
                fg=COLORS["white"],
                relief=tk.FLAT,
                anchor="w",
                padx=18,
                pady=10,
                cursor="hand2",
                activebackground=COLORS["secondary"],
                activeforeground=COLORS["white"],
                command=lambda k=key: self._show(k),
            )
            btn.pack(fill=tk.X)
            self._nav_buttons[key] = btn

        # About / Help button at bottom of sidebar
        tk.Button(
            self._sidebar,
            text="ℹ️  About / Help",
            font=FONTS["small"],
            bg=COLORS["primary"],
            fg=COLORS["text_light"],
            relief=tk.FLAT,
            anchor="w",
            padx=18,
            pady=6,
            cursor="hand2",
            activebackground=COLORS["secondary"],
            activeforeground=COLORS["white"],
            command=self._show_about,
        ).pack(side=tk.BOTTOM, fill=tk.X)

        # Version label at bottom of sidebar
        tk.Label(
            self._sidebar, text=APP_VERSION, font=FONTS["small"],
            bg=COLORS["primary"], fg=COLORS["text_light"]
        ).pack(side=tk.BOTTOM, pady=8)

        # Main content area
        self._content = tk.Frame(self, bg=COLORS["light"])
        self._content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Pre-build all frames
        for _label, frame_cls, key in self.NAV_ITEMS:
            frame = frame_cls(self._content)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._frames[key] = frame

    # ── Navigation ────────────────────────────────────────────────────────────

    def _show(self, key):
        if self._active_key == key:
            return

        # Deactivate old button
        if self._active_key:
            self._nav_buttons[self._active_key].config(bg=COLORS["primary"])

        # Activate new button
        self._nav_buttons[key].config(bg=COLORS["secondary"])
        self._active_key = key

        # Raise the frame
        frame = self._frames[key]
        frame.lift()

        # Refresh on show so data stays current
        if hasattr(frame, "refresh"):
            frame.refresh()

        # Update sidebar institution label when returning from settings
        if key == "dashboard":
            institution = db.get_setting("institution_name") or "My College"
            self._sidebar_title.config(text=institution)

    # ── About / Help ──────────────────────────────────────────────────────────

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title("About / Help")
        win.resizable(False, False)
        win.grab_set()
        win.configure(bg=COLORS["white"])
        center_window(win, 440, 360)

        # Header
        hdr = tk.Frame(win, bg=COLORS["primary"], pady=12)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="ℹ️  About / Help",
                 font=FONTS["heading"], bg=COLORS["primary"],
                 fg=COLORS["white"]).pack(padx=16)

        body = tk.Frame(win, bg=COLORS["white"], padx=30, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        lines = [
            ("College Management System", FONTS["heading"], COLORS["primary"]),
            (APP_VERSION, FONTS["body"], COLORS["text_light"]),
            ("", FONTS["small"], COLORS["white"]),
            ("Developer", FONTS["subheading"], COLORS["primary"]),
            (DEVELOPER_NAME, FONTS["body"], COLORS["text"]),
            (DEVELOPER_URL, FONTS["body"], COLORS["secondary"]),
            ("", FONTS["small"], COLORS["white"]),
            ("Features", FONTS["subheading"], COLORS["primary"]),
            ("• Student, Staff & Fee Management", FONTS["body"], COLORS["text"]),
            ("• Attendance, Subjects & Invoices", FONTS["body"], COLORS["text"]),
            ("• Offline – No internet required", FONTS["body"], COLORS["text"]),
            ("• Runs on any Windows PC", FONTS["body"], COLORS["text"]),
            ("", FONTS["small"], COLORS["white"]),
            (f"Support: {DEVELOPER_URL}", FONTS["small"], COLORS["text_light"]),
        ]
        for text, font, fg in lines:
            tk.Label(body, text=text, font=font, bg=COLORS["white"],
                     fg=fg, anchor="w").pack(anchor="w")

        make_button(win, "✖ Close", win.destroy, style="primary").pack(pady=10)


def main():
    try:
        app = CollegeApp()
        app.mainloop()
    except Exception as exc:  # pylint: disable=broad-except
        messagebox.showerror(
            "Fatal Error",
            f"The application encountered an unexpected error:\n\n{exc}\n\n"
            "Please contact support.",
        )
        raise


if __name__ == "__main__":
    main()
