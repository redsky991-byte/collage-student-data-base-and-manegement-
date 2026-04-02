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
from utils import COLORS, FONTS, center_window
from dashboard_frame import DashboardFrame
from students_frame import StudentsFrame
from fees_frame import FeesFrame
from salary_frame import SalaryFrame
from invoices_frame import InvoicesFrame
from settings_frame import SettingsFrame


class CollegeApp(tk.Tk):
    """Main application window."""

    NAV_ITEMS = [
        ("🏠  Dashboard",    DashboardFrame,  "dashboard"),
        ("🎓  Students",     StudentsFrame,   "students"),
        ("💳  Fees",         FeesFrame,       "fees"),
        ("👥  Staff & Salary", SalaryFrame,   "salary"),
        ("🧾  Invoices",     InvoicesFrame,   "invoices"),
        ("⚙️  Settings",     SettingsFrame,   "settings"),
    ]

    def __init__(self):
        super().__init__()
        self.title("College Management System")
        self.state("zoomed")          # Start maximised on Windows
        self.minsize(1000, 620)
        self.configure(bg=COLORS["primary"])

        db.initialize_db()
        self._frames = {}
        self._active_key = None
        self._build_ui()
        self._show("dashboard")

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Sidebar
        self._sidebar = tk.Frame(self, bg=COLORS["primary"], width=200)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        institution = db.get_setting("institution_name") or "My College"
        tk.Label(
            self._sidebar, text=institution, font=("Segoe UI", 12, "bold"),
            bg=COLORS["primary"], fg=COLORS["white"],
            wraplength=180, justify="center", pady=18
        ).pack(fill=tk.X)

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

        # Version label at bottom of sidebar
        tk.Label(
            self._sidebar, text="v1.0.0", font=FONTS["small"],
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
            for widget in self._sidebar.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(text=institution)
                    break


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
