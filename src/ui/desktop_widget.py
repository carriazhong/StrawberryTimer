"""Strawberry Timer - Desktop Floating Widget.

A small, transparent desktop widget that displays timer status
and can float above other windows.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from src.ui.theme import StrawberryTheme


class DesktopWidget(tk.Toplevel):
    """Floating desktop widget with strawberry icon and timer display.

    Features:
    - 1/4 size of main window (100x125 pixels)
    - Transparent background
    - Always on top (floats above other windows)
    - Draggable with mouse
    - Can be hidden/closed
    - Shows timer status and remaining time
    """

    # Size: 1/4 of main window (400x500 -> 100x125)
    WIDTH = 100
    HEIGHT = 125

    # Default transparency (alpha channel, 0-255)
    DEFAULT_ALPHA = 220

    # Minimum size for usability
    MIN_WIDTH = 80
    MIN_HEIGHT = 100

    def __init__(self, master=None, timer_engine=None, config_manager=None):
        """Initialize desktop widget.

        Args:
            master: Parent window (for linking, but widget is independent)
            timer_engine: Optional TimerEngine for time updates
            config_manager: Optional ConfigManager for settings persistence (or Path for testing)
        """
        # Create as independent Toplevel (None master makes it truly independent)
        super().__init__(None)

        self._master = master  # Keep reference for callbacks, but not as parent
        self._timer_engine = timer_engine

        # Handle config_manager - can be ConfigManager object, Path, or None
        from pathlib import Path
        if config_manager is not None and isinstance(config_manager, Path):
            # Create a ConfigManager and load from file if it exists
            from src.config.manager import ConfigManager
            self._config_manager = ConfigManager.load(config_manager)
        else:
            self._config_manager = config_manager

        # Position tracking
        self._start_x = 0
        self._start_y = 0
        self._visible = True

        # Setup window
        self._setup_window()
        self._create_content()

        # Load saved settings
        self._load_settings()

        # Register for timer updates if engine provided
        if self._timer_engine:
            self._timer_engine.on_tick(self._update_time, interval_seconds=1)

        # Ensure widget is visible at the end (after all setup)
        self.deiconify()
        self.update_idletasks()  # Force window to update
        self._visible = True

    def _setup_window(self) -> None:
        """Setup window properties for floating widget."""
        # Set size (1/4 of main window)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Frameless window (no title bar, borders)
        self.overrideredirect(1)

        # Transparent background
        self.attributes("-alpha", self.DEFAULT_ALPHA)

        # Always on top (floats above other windows)
        self.attributes("-topmost", 1)

        # Disable resizing
        self.resizable(False, False)

        # Setup drag behavior
        self._setup_drag()

        # Setup right-click menu
        self._setup_context_menu()

        # Position on screen (default: top-right corner)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        default_x = screen_width - self.WIDTH - 50
        default_y = 50
        self.geometry(f"+{default_x}+{default_y}")

        # Protocol for window close (X button)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_content(self) -> None:
        """Create widget content."""
        # Main container with transparent background effect
        container = tk.Frame(self, bd=0, highlightthickness=0)
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # Strawberry icon (larger size - 60 points to be 60% of 100px width)
        icon_label = tk.Label(
            container,
            text="🍓",
            font=("Segoe UI", 60),
            bd=0,
        )
        icon_label.pack(pady=(5, 2))

        # Timer display
        self._time_label = tk.Label(
            container,
            text="25:00",
            font=("Segoe UI", 12, "bold"),
            fg=StrawberryTheme.STRAWBERRY_RED,
            bd=0,
        )
        self._time_label.pack(pady=2)

        # Status indicator
        self._status_label = tk.Label(
            container,
            text="● Ready",
            font=("Segoe UI", 8),
            fg=StrawberryTheme.STRAWBERRY_RED,
            bd=0,
        )
        self._status_label.pack(pady=(2, 5))

        # Close button (small X in corner)
        close_btn = tk.Label(
            container,
            text="✕",
            font=("Segoe UI", 10),
            fg=StrawberryTheme.FG_COLOR,
            cursor="hand2",
            bd=0,
        )
        close_btn.place(relx=1.0, rely=0.0, x=-2, y=2)
        close_btn.bind("<Button-1>", lambda e: self._on_close_button())

    def _setup_drag(self) -> None:
        """Setup mouse drag behavior for widget."""
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._do_drag)
        self.bind("<ButtonRelease-1>", self._stop_drag)

    def _start_drag(self, event) -> None:
        """Start dragging widget.

        Args:
            event: Mouse event.
        """
        self._start_x = event.x
        self._start_y = event.y

    def _do_drag(self, event) -> None:
        """Drag widget to new position.

        Args:
            event: Mouse event.
        """
        x = self.winfo_x() + (event.x - self._start_x)
        y = self.winfo_y() + (event.y - self._start_y)

        # Constrain to screen bounds
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max(0, min(x, screen_width - self.WIDTH))
        y = max(0, min(y, screen_height - self.HEIGHT))

        self.geometry(f"+{x}+{y}")

    def _stop_drag(self, event) -> None:
        """Stop dragging and save position.

        Args:
            event: Mouse event.
        """
        self._save_settings()

    def _setup_context_menu(self) -> None:
        """Setup right-click context menu."""
        self._context_menu = tk.Menu(self, tearoff=0)

        self._context_menu.add_command(
            label="Hide Widget",
            command=self.hide
        )

        self._context_menu.add_separator()

        self._context_menu.add_command(
            label="Toggle Main Window",
            command=self._toggle_main_window
        )

        self._context_menu.add_separator()

        self._context_menu.add_command(
            label="Settings",
            command=self._open_settings
        )

        self._context_menu.add_command(
            label="Close",
            command=self._on_close
        )

        # Bind right-click
        self.bind("<Button-3>", self._show_context_menu)

        # For macOS (Control+Click)
        self.bind("<Control-Button-1>", self._show_context_menu)

    def _show_context_menu(self, event) -> None:
        """Show context menu at mouse position.

        Args:
            event: Mouse event.
        """
        try:
            self._context_menu.tk_popup(event.x_root, event.y_root)
        except AttributeError:
            # Menu not ready yet
            pass

    # ==================== Content Updates ====================

    def _update_time(self) -> None:
        """Update timer display from TimerEngine.

        Called periodically by timer tick callback.
        """
        if self._timer_engine and self._visible:
            remaining = self._timer_engine.remaining_time_str
            self._time_label.config(text=remaining)

            # Update status based on timer state
            if self._timer_engine.is_running:
                self._status_label.config(text="● Running", fg="#4CAF50")
            elif self._timer_engine.is_paused:
                self._status_label.config(text="● Paused", fg="#FFC107")
            elif self._timer_engine.is_completed:
                self._status_label.config(text="● Done!", fg=StrawberryTheme.STRAWBERRY_RED)
            else:
                self._status_label.config(text="● Ready", fg=StrawberryTheme.STRAWBERRY_RED)

    def set_status(self, status: str, color: str = None) -> None:
        """Set status text and color.

        Args:
            status: Status text to display.
            color: Optional color for status text.
        """
        self._status_label.config(text=f"● {status}")
        if color:
            self._status_label.config(fg=color)

    # ==================== Public API for Tests ====================

    def close(self) -> None:
        """Public method to close/hide the widget."""
        self.withdraw()
        self._visible = False
        self.update_idletasks()  # Ensure state is updated

    def show_context_menu(self) -> tk.Menu:
        """Show and return the context menu.

        Returns:
            The context menu instance.
        """
        return self._context_menu

    def move(self, x: int, y: int) -> None:
        """Move widget to specific position.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.geometry(f"+{x}+{y}")
        self._save_settings()

    def save_position(self) -> None:
        """Save widget position to config."""
        self._save_settings()

    def save_settings(self) -> None:
        """Save all widget settings to config."""
        self._save_settings()

    def set_icon(self, icon: str) -> None:
        """Set widget icon.

        Args:
            icon: Icon text (emoji or custom).
        """
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if hasattr(child, "cget") and child.cget("text") == "🍓":
                        child.config(text=icon)
                        break

    # ==================== Visibility Control ====================

    def show(self) -> None:
        """Show the widget."""
        self.deiconify()
        self._visible = True

    def hide(self) -> None:
        """Hide the widget."""
        self.withdraw()
        self._visible = False
        self.update_idletasks()  # Ensure state is updated

    def is_visible(self) -> bool:
        """Check if widget is visible.

        Returns:
            True if widget is visible, False otherwise.
        """
        return self._visible and self.winfo_ismapped()

    def toggle_visibility(self) -> None:
        """Toggle widget visibility."""
        if self._visible:
            self.hide()
        else:
            self.show()

    # ==================== Configuration ====================

    def _load_settings(self) -> None:
        """Load widget settings from config."""
        if self._config_manager:
            # Load transparency (can be int 0-255 or float 0.0-1.0)
            alpha = self._config_manager.get("widget_alpha", self.DEFAULT_ALPHA)
            if isinstance(alpha, int):
                # Convert int (0-255) to float (0.0-1.0) for Tkinter
                self.attributes("-alpha", alpha / 255.0)
            else:
                self.attributes("-alpha", alpha)

            # Load position (must come after window is fully set up)
            x = self._config_manager.get("widget_x", None)
            y = self._config_manager.get("widget_y", None)
            if x is not None and y is not None:
                self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
                self.update_idletasks()  # Ensure geometry is applied

    def _save_settings(self) -> None:
        """Save widget settings to config."""
        if self._config_manager:
            x = self.winfo_x()
            y = self.winfo_y()
            alpha_float = self.attributes("-alpha")
            alpha_int = int(alpha_float * 255)  # Save as int for consistency

            self._config_manager.set("widget_x", x)
            self._config_manager.set("widget_y", y)
            self._config_manager.set("widget_alpha", alpha_int)
            self._config_manager.save()

    def set_transparency(self, alpha: int) -> None:
        """Set widget transparency.

        Args:
            alpha: Transparency level (0=fully transparent, 255=opaque).
        """
        alpha = max(0, min(255, alpha))
        self.attributes("-alpha", alpha / 255.0)  # Tkinter uses 0.0-1.0 range
        self._save_settings()

    def get_transparency(self) -> int:
        """Get current transparency level.

        Returns:
            Alpha value (0-255).
        """
        alpha_float = self.attributes("-alpha")
        return int(alpha_float * 255)  # Convert from 0.0-1.0 to 0-255

    # ==================== Close Handlers ====================

    def _on_close(self) -> None:
        """Handle window close (X button or close command)."""
        self.hide()

    def _on_close_button(self) -> None:
        """Handle close button click."""
        self.hide()

    def _toggle_main_window(self) -> None:
        """Toggle main window visibility."""
        if self._master and self._master.winfo_exists():
            if self._master.state() == "withdrawn":
                self._master.deiconify()
            else:
                self._master.withdraw()

    def _open_settings(self) -> None:
        """Open settings dialog (placeholder for future)."""
        # TODO: Implement settings dialog
        pass

    # ==================== Public API ====================

    def get_time_text(self) -> str:
        """Get current timer display text.

        Returns:
            Time string (MM:SS format).
        """
        return self._time_label.cget("text")

    def get_status(self) -> str:
        """Get current status text.

        Returns:
            Status string (idle/running/paused/completed).
        """
        text = self._status_label.cget("text")
        status = text.replace("● ", "").strip().lower()
        # Map to expected status values
        if "running" in status:
            return "running"
        elif "paused" in status:
            return "paused"
        elif "done" in status or "complete" in status:
            return "completed"
        else:
            return "idle"

    def has_close_button(self) -> bool:
        """Check if widget has close button.

        Returns:
            True if close button is present.
        """
        return True  # Always has close button

    def get_close_button_tooltip(self) -> str:
        """Get close button tooltip.

        Returns:
            Tooltip text.
        """
        return "Hide widget"

    def get_context_menu_items(self) -> list:
        """Get context menu items.

        Returns:
            List of menu item labels.
        """
        items = []
        for i in range(self._context_menu.index("end")):
            try:
                items.append(self._context_menu.entrycget(i, "label"))
            except tk.TclError:
                pass
        return items

    def is_toplevel(self) -> bool:
        """Check if this is a Toplevel window.

        Returns:
            True (DesktopWidget is always a Toplevel).
        """
        return isinstance(self, tk.Toplevel)

    def get_icon(self) -> str:
        """Get widget icon.

        Returns:
            Icon text or path.
        """
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if hasattr(child, "cget") and "🍓" in child.cget("text"):
                        return child.cget("text")
        return "🍓"

    def get_icon_size(self) -> int:
        """Get icon font size.

        Returns:
            Font size in points.
        """
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if hasattr(child, "cget") and "🍓" in child.cget("text"):
                        font_spec = child.cget("font")
                        # Font spec can be a string or tuple
                        if isinstance(font_spec, str):
                            # Parse "Segoe UI 24" or "24"
                            parts = font_spec.split()
                            if len(parts) >= 2:
                                try:
                                    return int(parts[-1])
                                except ValueError:
                                    return 24
                        elif isinstance(font_spec, (list, tuple)):
                            # Font tuple: (family, size, ...)
                            if len(font_spec) >= 2:
                                try:
                                    return int(font_spec[1])
                                except (ValueError, IndexError):
                                    return 24
        return 24  # Default fallback

    def draggable(self) -> bool:
        """Check if widget is draggable.

        Returns:
            True (widget is always draggable).
        """
        return True


def create_desktop_widget(master=None, timer_engine=None, config_manager=None) -> DesktopWidget:
    """Convenience function to create and show desktop widget.

    Args:
        master: Parent window.
        timer_engine: Optional TimerEngine.
        config_manager: Optional ConfigManager.

    Returns:
        DesktopWidget instance.
    """
    widget = DesktopWidget(master, timer_engine, config_manager)
    return widget
