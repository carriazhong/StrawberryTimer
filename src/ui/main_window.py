"""Strawberry Timer - Main GUI Application.

Built with Tkinter for cross-platform desktop support.
Features strawberry-themed UI with desktop clock widget.
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Optional, Callable
from datetime import timedelta

from src.ui.desktop_widget import DesktopWidget
from src.ui.theme import StrawberryTheme


class DigitalClock(tk.Label):
    """Digital clock widget with strawberry theme."""

    def __init__(self, parent, **kwargs):
        """Initialize digital clock.

        Args:
            parent: Parent widget.
            **kwargs: Additional Label arguments.
        """
        kwargs.setdefault("text", "00:00:00")
        kwargs.setdefault("font", StrawberryTheme.get_font(24, bold=True))
        kwargs.setdefault("bg", StrawberryTheme.CLOCK_BG)
        kwargs.setdefault("fg", StrawberryTheme.CLOCK_FG)
        kwargs.setdefault("padx", 15)
        kwargs.setdefault("pady", 8)
        kwargs.setdefault("anchor", "center")

        super().__init__(parent, **kwargs)
        self._update_time()

    def _update_time(self) -> None:
        """Update clock display."""
        current_time = time.strftime("%H:%M:%S")
        self.config(text=current_time)
        self.after(1000, self._update_time)


class TimerDisplay(tk.Label):
    """Large timer display with progress indication."""

    def __init__(self, parent, **kwargs):
        """Initialize timer display.

        Args:
            parent: Parent widget.
            **kwargs: Additional Label arguments.
        """
        kwargs.setdefault("text", "25:00")
        kwargs.setdefault("font", StrawberryTheme.get_font(72, bold=True))
        kwargs.setdefault("bg", StrawberryTheme.BG_COLOR)
        kwargs.setdefault("fg", StrawberryTheme.STRAWBERRY_RED)
        kwargs.setdefault("anchor", "center")

        super().__init__(parent, **kwargs)
        self._remaining_time: timedelta = timedelta(minutes=25)

    def update_time(self, remaining: timedelta) -> None:
        """Update displayed time.

        Args:
            remaining: Remaining time to display.
        """
        self._remaining_time = remaining
        total_seconds = int(remaining.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.config(text=f"{minutes:02d}:{seconds:02d}")

        # Color changes based on remaining time
        if remaining <= timedelta(minutes=5):
            self.config(fg=StrawberryTheme.STRAWBERRY_DARK)
        elif remaining <= timedelta(minutes=10):
            self.config(fg=StrawberryTheme.STRAWBERRY_RED)
        else:
            self.config(fg=StrawberryTheme.ACCENT_COLOR)


class StrawberryButton(tk.Button):
    """Strawberry-themed button."""

    def __init__(self, parent, **kwargs):
        """Initialize strawberry button.

        Args:
            parent: Parent widget.
            **kwargs: Additional Button arguments.
        """
        kwargs.setdefault("font", StrawberryTheme.get_font(12, bold=True))
        kwargs.setdefault("bg", StrawberryTheme.STRAWBERRY_RED)
        kwargs.setdefault("fg", "white")
        kwargs.setdefault("activebackground", StrawberryTheme.STRAWBERRY_DARK)
        kwargs.setdefault("activeforeground", "white")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("padx", 20)
        kwargs.setdefault("pady", 10)
        kwargs.setdefault("cursor", "hand2")

        super().__init__(parent, **kwargs)


class ProgressBar(tk.Canvas):
    """Custom progress bar with strawberry theme."""

    def __init__(self, parent, width: int = 300, height: int = 10, **kwargs):
        """Initialize progress bar.

        Args:
            parent: Parent widget.
            width: Bar width in pixels.
            height: Bar height in pixels.
            **kwargs: Additional Canvas arguments.
        """
        super().__init__(parent, width=width, height=height, **kwargs)
        self._width = width
        self._height = height
        self._progress = 100.0
        self._draw()

    def set_progress(self, percent: float) -> None:
        """Set progress percentage.

        Args:
            percent: Progress (0-100).
        """
        self._progress = max(0, min(100, percent))
        self._draw()

    def _draw(self) -> None:
        """Draw progress bar."""
        self.delete("all")

        # Background
        self.create_rectangle(
            0, 0, self._width, self._height,
            fill=StrawberryTheme.STRAWBERRY_LIGHT,
            outline=""
        )

        # Progress
        fill_width = (self._progress / 100) * self._width
        self.create_rectangle(
            0, 0, fill_width, self._height,
            fill=StrawberryTheme.STRAWBERRY_RED,
            outline=""
        )


class TodoSelector(tk.Frame):
    """Todo selection dropdown for future integration."""

    def __init__(self, parent, **kwargs):
        """Initialize Todo selector.

        Args:
            parent: Parent widget.
            **kwargs: Additional Frame arguments.
        """
        super().__init__(parent, **kwargs)

        label = tk.Label(
            self,
            text="🍓 Working on:",
            font=StrawberryTheme.get_font(10),
            bg=StrawberryTheme.BG_COLOR,
            fg=StrawberryTheme.FG_COLOR,
        )
        label.pack(side="left", padx=(0, 10))

        self._combo = ttk.Combobox(
            self,
            values=["(No Todo selected)"],
            state="readonly",
            font=StrawberryTheme.get_font(10),
            width=30,
        )
        self._combo.current(0)
        self._combo.pack(side="left")

    def set_todos(self, todos: list) -> None:
        """Update Todo list.

        Args:
            todos: List of Todo items with 'title' field.
        """
        titles = [t.get("title", "Untitled") for t in todos]
        self._combo["values"] = ["(No Todo selected)"] + titles
        self._combo.current(0)

    def get_selected_todo(self) -> Optional[str]:
        """Get currently selected Todo title.

        Returns:
            Todo title or None if none selected.
        """
        selection = self._combo.get()
        if selection == "(No Todo selected)":
            return None
        return selection


class MainWindow(tk.Tk):
    """Main application window for Strawberry Timer."""

    def __init__(self, timer_engine=None, config_manager=None):
        """Initialize main window.

        Args:
            timer_engine: Optional TimerEngine instance.
            config_manager: Optional ConfigManager instance.
        """
        super().__init__()

        self._timer_engine = timer_engine
        self._config_manager = config_manager
        self._desktop_widget = None

        self.title("🍓 Strawberry Timer")
        self.geometry("400x500")
        self.resizable(False, False)
        self.configure(bg=StrawberryTheme.BG_COLOR)

        # Center window on screen
        self.center_window()

        # Build UI
        self._create_widgets()

        # Apply theme to ttk widgets
        self._apply_theme()

        # Create desktop widget
        self._create_desktop_widget()

        # Handle window close event - destroy desktop widget when main window closes
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def center_window(self) -> None:
        """Center window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Header with clock
        header = tk.Frame(self, bg=StrawberryTheme.CLOCK_BG)
        header.pack(fill="x")

        clock = DigitalClock(header)
        clock.pack(pady=10)

        # Title
        title = tk.Label(
            self,
            text="🍓 Strawberry Timer",
            font=StrawberryTheme.get_font(20, bold=True),
            bg=StrawberryTheme.BG_COLOR,
            fg=StrawberryTheme.FG_COLOR,
        )
        title.pack(pady=(20, 10))

        # Todo selector (for future integration)
        todo_frame = tk.Frame(self, bg=StrawberryTheme.BG_COLOR)
        todo_frame.pack(pady=10)
        self.todo_selector = TodoSelector(todo_frame)
        self.todo_selector.pack()

        # Timer display
        self.timer_display = TimerDisplay(self)
        self.timer_display.pack(pady=20)

        # Progress bar
        self.progress_bar = ProgressBar(self, width=300)
        self.progress_bar.pack(pady=10)

        # Control buttons
        button_frame = tk.Frame(self, bg=StrawberryTheme.BG_COLOR)
        button_frame.pack(pady=20)

        self.start_button = StrawberryButton(
            button_frame,
            text="▶ Start",
            command=self.on_start_click,
        )
        self.start_button.pack(side="left", padx=5)

        self.pause_button = StrawberryButton(
            button_frame,
            text="⏸ Pause",
            command=self.on_pause_click,
            state="disabled",
        )
        self.pause_button.pack(side="left", padx=5)

        self.stop_button = StrawberryButton(
            button_frame,
            text="⏹ Stop",
            command=self.on_stop_click,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        # Status label
        self.status_label = tk.Label(
            self,
            text="Ready to focus!",
            font=StrawberryTheme.get_font(11),
            bg=StrawberryTheme.BG_COLOR,
            fg=StrawberryTheme.FG_COLOR,
        )
        self.status_label.pack(pady=20)

        # Start the UI update loop (polling timer from main thread)
        self._start_ui_update_loop()

    def _apply_theme(self) -> None:
        """Apply strawberry theme to ttk widgets."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground="white",
            background=StrawberryTheme.BG_COLOR,
            borderwidth=0,
        )

    def _create_desktop_widget(self) -> None:
        """Create desktop floating widget."""
        self._desktop_widget = DesktopWidget(
            master=self,
            timer_engine=self._timer_engine,
            config_manager=self._config_manager
        )
        self._desktop_widget.show()

    def _start_ui_update_loop(self) -> None:
        """Start polling timer state from main thread (Tkinter requires this)."""
        if self._timer_engine:
            remaining = self._timer_engine.remaining
            progress = self._timer_engine.progress_percent

            # Update main window display
            self.timer_display.update_time(remaining)
            self.progress_bar.set_progress(progress)

            # Update desktop widget
            if hasattr(self, '_desktop_widget') and self._desktop_widget:
                self._desktop_widget.update_from_engine()

        # Schedule next update (every 100ms)
        self.after(100, self._start_ui_update_loop)

    # ==================== Event Handlers ====================

    def on_start_click(self) -> None:
        """Handle start button click."""
        if self._timer_engine:
            self._timer_engine.start()
        self.status_label.config(text="🍓 Focus time! Stay productive!")
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal", text="⏸ Pause")
        self.stop_button.config(state="normal")

    def on_pause_click(self) -> None:
        """Handle pause button click."""
        if self._timer_engine:
            if self._timer_engine.is_running:
                self._timer_engine.pause()
                self.status_label.config(text="⏸️ Timer paused. Take a breath!")
                self.pause_button.config(text="▶ Resume")
            else:
                self._timer_engine.resume()
                self.status_label.config(text="🍓 Focus time! Stay productive!")
                self.pause_button.config(text="⏸ Pause")
        else:
            self.status_label.config(text="⏸️ Timer paused. Take a breath!")
            self.pause_button.config(text="▶ Resume")

    def on_stop_click(self) -> None:
        """Handle stop button click."""
        if self._timer_engine:
            self._timer_engine.stop()
        self.status_label.config(text="Ready to focus!")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="⏸ Pause")
        self.stop_button.config(state="disabled")
        self.timer_display.update_time(timedelta(minutes=25))
        self.progress_bar.set_progress(100)

    # ==================== Public Methods ====================

    def update_timer(self, remaining: timedelta, progress: float) -> None:
        """Update timer display from engine.

        Args:
            remaining: Remaining time.
            progress: Progress percentage.
        """
        self.timer_display.update_time(remaining)
        self.progress_bar.set_progress(progress)

    def show_completion(self) -> None:
        """Show timer completion notification."""
        self.status_label.config(
            text="🎉 Great work! Time for a break!",
            fg=StrawberryTheme.STRAWBERRY_RED
        )
        # TODO: Play sound

    def set_todos(self, todos: list) -> None:
        """Update Todo list for selector.

        Args:
            todos: List of Todo items.
        """
        self.todo_selector.set_todos(todos)

    def _on_close(self) -> None:
        """Handle main window close event.

        Closes the desktop floating widget and destroys main window.
        """
        # Close/destroy desktop widget
        if self._desktop_widget:
            try:
                self._desktop_widget.destroy()
                self._desktop_widget = None
            except Exception:
                # Widget already destroyed or doesn't exist
                self._desktop_widget = None

        # Destroy main window and quit application
        self.destroy()


def run_application(timer_engine=None, config_manager=None) -> MainWindow:
    """Run the Strawberry Timer application.

    Args:
        timer_engine: Optional TimerEngine instance.
        config_manager: Optional ConfigManager instance.

    Returns:
        MainWindow instance.
    """
    app = MainWindow(timer_engine, config_manager)
    app.mainloop()
    return app


if __name__ == "__main__":
    run_application()
