"""Strawberry Timer - Theme Configuration.

Centralized theme colors and styling for the application.
"""

from tkinter import font
import tkinter as tk


class StrawberryTheme:
    """Strawberry-themed color scheme and styling."""

    # Strawberry colors
    STRAWBERRY_RED = "#E53935"
    STRAWBERRY_DARK = "#B71C1C"
    STRAWBERRY_LIGHT = "#FFCDD2"
    STRAWBERRY_PINK = "#F48FB1"

    # UI Colors
    BG_COLOR = "#FFF5F7"  # Light pinkish background
    FG_COLOR = "#4A2C2A"  # Dark brown text
    ACCENT_COLOR = STRAWBERRY_RED

    # Clock colors
    CLOCK_BG = "#E53935"
    CLOCK_FG = "#FFFFFF"

    @staticmethod
    def get_font(size: int, bold: bool = False) -> font.Font:
        """Get themed font.

        Args:
            size: Font size in points.
            bold: Whether font should be bold.

        Returns:
            Tkinter Font object.
        """
        family = "Segoe UI" if tk.TkVersion >= 8.6 else "Arial"
        weight = "bold" if bold else "normal"
        return font.Font(family=family, size=size, weight=weight)
