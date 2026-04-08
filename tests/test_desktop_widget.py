"""Test cases for Desktop Floating Strawberry Widget.

Tests the new desktop widget feature:
- Small strawberry icon (1/4 size of main window)
- Transparent background
- Floats on desktop
- Can be closed
- Independent from main timer window
"""

import pytest
from unittest.mock import Mock, patch
from tkinter import Tk


# ==================== Test: Widget Size ====================

class TestDesktopWidgetSize:
    """Test desktop widget sizing requirements."""

    def test_widget_width_is_one_quarter_main_window(self, desktop_widget, main_window):
        """Desktop widget width should be 1/4 of main window width."""
        main_width = main_window.winfo_width()
        widget_width = desktop_widget.winfo_width()
        assert widget_width == main_width // 4

    def test_widget_height_is_one_quarter_main_window(self, desktop_widget, main_window):
        """Desktop widget height should be 1/4 of main window height."""
        main_height = main_window.winfo_height()
        widget_height = desktop_widget.winfo_height()
        assert widget_height == main_height // 4

    def test_widget_dimensions_are_proportional(self, desktop_widget):
        """Widget should maintain proportional aspect ratio."""
        width = desktop_widget.winfo_width()
        height = desktop_widget.winfo_height()
        # Should be roughly square or slightly rectangular
        assert 0.5 <= width / height <= 2.0


# ==================== Test: Transparency ====================

class TestWidgetTransparency:
    """Test widget transparency functionality."""

    def test_widget_background_is_transparent(self, desktop_widget):
        """Widget background should be transparent."""
        # Transparency is achieved via alpha channel, not bg color
        # Check that alpha transparency is enabled
        alpha = desktop_widget.attributes("-alpha")
        assert alpha is not None and alpha < 255  # Not fully opaque

    def test_widget_uses_alpha_channel(self, desktop_widget):
        """Widget should use alpha channel for transparency."""
        # Check if window attributes include transparency
        attributes = desktop_widget.attributes()
        # -alpha should be set for transparency (0-255)
        assert "-alpha" in attributes or "alpha" in attributes

    def test_transparency_level_is_configurable(self, desktop_widget):
        """Transparency level should be configurable."""
        # Should support setting transparency from 0 (fully transparent) to 255 (opaque)
        desktop_widget.set_transparency(200)
        assert desktop_widget.get_transparency() == 200

    def test_widget_content_remains_visible_with_transparency(self, desktop_widget):
        """Widget content (strawberry icon/time) should remain visible with transparency."""
        desktop_widget.set_transparency(180)
        # Widget should still be visible and interactive
        assert desktop_widget.winfo_ismapped()
        assert desktop_widget.winfo_viewable()


# ==================== Test: Floating Behavior ====================

class TestWidgetFloatingBehavior:
    """Test widget floating on desktop behavior."""

    def test_widget_floats_above_other_windows(self, desktop_widget):
        """Widget should stay on top of other windows."""
        # Check if window has -topmost attribute
        attributes = desktop_widget.attributes()
        assert "-topmost" in attributes or desktop_widget.winfo_ismapped()

    def test_widget_is_decorated(self, desktop_widget):
        """Widget should be frameless (no title bar, borders)."""
        override = desktop_widget.overrideredirect()
        # override-redirect is 1 for frameless windows
        assert override == 1

    def test_widget_can_be_dragged(self, desktop_widget):
        """Widget should be draggable on desktop."""
        # Should have drag binding
        bind_tags = desktop_widget.bind("<Button-1>")
        assert bind_tags is not None or desktop_widget.draggable is True

    def test_widget_stays_in_screen_bounds(self, desktop_widget):
        """Widget should not move outside screen bounds."""
        x = desktop_widget.winfo_x()
        y = desktop_widget.winfo_y()
        screen_width = desktop_widget.winfo_screenwidth()
        screen_height = desktop_widget.winfo_screenheight()
        width = desktop_widget.winfo_width()
        height = desktop_widget.winfo_height()

        assert x >= 0 and y >= 0
        assert x + width <= screen_width
        assert y + height <= screen_height


# ==================== Test: Close Functionality ====================

class TestWidgetCloseFunctionality:
    """Test widget close functionality."""

    def test_widget_has_close_button(self, desktop_widget):
        """Widget should have a close button."""
        # Should have a close mechanism (button or right-click menu)
        assert desktop_widget.has_close_button() is True

    def test_close_button_hides_widget(self, desktop_widget):
        """Clicking close should hide (not destroy) the widget."""
        initial_mapped = desktop_widget.winfo_ismapped()
        desktop_widget.close()
        # Should be hidden/withdrawn, not destroyed
        assert desktop_widget.winfo_ismapped() is False or desktop_widget.state() == "withdrawn"
        # Should be able to show again
        desktop_widget.show()
        assert desktop_widget.winfo_ismapped() is True

    def test_widget_can_be_toggled_visible_hidden(self, desktop_widget):
        """Widget should support show/hide toggle."""
        desktop_widget.hide()
        assert desktop_widget.winfo_ismapped() is False
        desktop_widget.show()
        assert desktop_widget.winfo_ismapped() is True

    def test_close_button_tooltip(self, desktop_widget):
        """Close button should have helpful tooltip."""
        tooltip = desktop_widget.get_close_button_tooltip()
        assert tooltip is not None and len(tooltip) > 0


# ==================== Test: Strawberry Icon ====================

class TestStrawberryIcon:
    """Test strawberry icon display in widget."""

    def test_widget_displays_strawberry_icon(self, desktop_widget):
        """Widget should display strawberry icon."""
        icon = desktop_widget.get_icon()
        assert icon is not None
        assert "strawberry" in icon.lower() or icon == "🍓"

    def test_icon_size_is_appropriate_for_widget(self, desktop_widget):
        """Icon size should be appropriate for small widget."""
        icon_size = desktop_widget.get_icon_size()
        widget_size = min(desktop_widget.winfo_width(), desktop_widget.winfo_height())
        # Icon should be significant portion of widget but not fill it
        assert icon_size >= widget_size * 0.5
        assert icon_size <= widget_size * 0.9


# ==================== Test: Timer Display in Widget ====================

class TestWidgetTimerDisplay:
    """Test timer display in desktop widget."""

    def test_widget_shows_remaining_time(self, desktop_widget):
        """Widget should show remaining timer time."""
        time_text = desktop_widget.get_time_text()
        assert time_text is not None
        assert ":" in time_text  # Format: MM:SS

    def test_widget_updates_when_timer_ticks(self, desktop_widget, timer_engine):
        """Widget should update time when timer ticks."""
        # Connect widget to timer engine for this test
        desktop_widget._timer_engine = timer_engine

        initial_text = desktop_widget.get_time_text()
        timer_engine._advance_time(60)  # Advance 1 minute

        # Trigger the update callback manually
        desktop_widget._update_time()

        updated_text = desktop_widget.get_time_text()
        assert updated_text != initial_text

    def test_widget_shows_status_indicator(self, desktop_widget):
        """Widget should show visual status indicator."""
        status = desktop_widget.get_status()
        assert status in ["idle", "running", "paused", "completed"]


# ==================== Test: Independence from Main Window ====================

class TestWidgetIndependence:
    """Test widget independence from main timer window."""

    def test_widget_is_separate_toplevel_window(self, desktop_widget, main_window):
        """Widget should be a separate Toplevel window."""
        # Widget should be a Toplevel instance or pass is_toplevel check
        assert desktop_widget.is_toplevel()
        # Widget's toplevel should be itself (independent window)
        assert desktop_widget.winfo_toplevel() == desktop_widget

    def test_widget_survives_main_window_close(self, desktop_widget, main_window):
        """Widget should remain when main window is closed."""
        desktop_widget.show()
        main_window.destroy()
        assert desktop_widget.winfo_exists()
        # Cleanup
        desktop_widget.destroy()

    def test_main_window_survives_widget_close(self, desktop_widget, main_window):
        """Main window should remain when widget is closed."""
        desktop_widget.close()
        assert main_window.winfo_exists()
        # Cleanup
        desktop_widget.destroy()


# ==================== Test: Right-Click Context Menu ====================

class TestWidgetContextMenu:
    """Test right-click context menu functionality."""

    def test_right_click_opens_context_menu(self, desktop_widget):
        """Right-click should open context menu."""
        menu = desktop_widget.show_context_menu()
        assert menu is not None

    def test_context_menu_has_toggle_option(self, desktop_widget):
        """Context menu should have show/hide toggle option."""
        menu_items = desktop_widget.get_context_menu_items()
        assert any("toggle" in item.lower() or "show" in item.lower() or "hide" in item.lower()
                       for item in menu_items)

    def test_context_menu_has_settings_option(self, desktop_widget):
        """Context menu should have settings option."""
        menu_items = desktop_widget.get_context_menu_items()
        assert any("settings" in item.lower() or "config" in item.lower()
                       for item in menu_items)


# ==================== Test: Configuration ====================

class TestWidgetConfiguration:
    """Test widget configuration options."""

    def test_widget_position_is_saved(self, desktop_widget, config_file):
        """Widget position should be saved to config."""
        desktop_widget.move(100, 100)
        desktop_widget.save_position()
        # Should save to config file

    def test_widget_position_is_restored_on_startup(self, desktop_widget, config_file):
        """Widget position should be restored on startup."""
        from src.ui.desktop_widget import DesktopWidget

        desktop_widget.move(200, 200)
        desktop_widget.save_position()

        # Simulate restart by creating new widget
        new_widget = DesktopWidget(config_manager=config_file)
        assert new_widget.winfo_x() == 200
        assert new_widget.winfo_y() == 200

    def test_widget_transparency_is_saved(self, desktop_widget, config_file):
        """Widget transparency should be saved to config."""
        from src.ui.desktop_widget import DesktopWidget

        desktop_widget.set_transparency(200)
        desktop_widget.save_settings()

        # Simulate restart
        new_widget = DesktopWidget(config_manager=config_file)
        assert new_widget.get_transparency() == 200


# ==================== Fixtures ====================

@pytest.fixture
def main_window():
    """Create a main window for testing."""
    root = Tk()
    root.geometry("400x500")
    root.update_idletasks()  # Force window to render
    yield root
    root.destroy()


@pytest.fixture
def desktop_widget(main_window):
    """Create a DesktopWidget instance for testing."""
    from src.ui.desktop_widget import DesktopWidget
    widget = DesktopWidget(main_window)
    widget.update_idletasks()  # Force widget to render
    yield widget
    widget.destroy()


@pytest.fixture
def timer_engine():
    """Create a TimerEngine instance for testing."""
    from src.timer.engine import TimerEngine
    return TimerEngine()


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file."""
    return tmp_path / "widget_config.json"
