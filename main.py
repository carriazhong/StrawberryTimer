#!/usr/bin/env python3
"""Strawberry Timer - Main Entry Point.

A simple, elegant desktop Pomodoro timer with strawberry theme.

Usage:
    python main.py                    # Run with default settings
    python main.py --duration 20      # Custom work duration
    python main.py --no-sound          # Disable sound
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ui import run_application
from src.config import ConfigManager
from src.timer import TimerEngine
from src.sound import SoundPlayer
from src.todo import TodoIntegration


def parse_arguments():
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Strawberry Timer - A simple desktop Pomodoro timer"
    )

    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=25,
        help="Work duration in minutes (default: 25)",
    )

    parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Disable sound notifications",
    )

    parser.add_argument(
        "-t", "--theme",
        choices=["strawberry", "dark", "light"],
        default="strawberry",
        help="UI theme (default: strawberry)",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )

    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()

    # Load configuration
    config_manager = ConfigManager.load(args.config)

    # Apply command line overrides
    if args.duration:
        config_manager.set("work_duration_minutes", args.duration)
    if args.no_sound:
        config_manager.set("sound_enabled", False)
    if args.theme:
        config_manager.set("theme", args.theme)

    # Save configuration for next run
    config_manager.save()

    # Initialize components
    timer = TimerEngine(config_manager.all)
    sound = SoundPlayer(config_manager.get("volume"))
    todos = TodoIntegration()

    # Connect timer to sound
    def on_timer_complete():
        if config_manager.get("sound_enabled"):
            try:
                sound.play(config_manager.get("sound_file"))
            except Exception:
                # Fallback to system beep if sound fails
                sound.beep()

        # Update status in main window
        if app := _get_main_window_ref():
            app.show_completion()

    timer.on_complete(on_timer_complete)

    # Connect timer tick to update main window display
    def on_timer_tick():
        if app := _get_main_window_ref():
            app.update_timer(timer.remaining_time, timer.progress_percent)

    timer.on_tick(on_timer_tick, interval_seconds=0.5)

    # Run GUI application with timer and config
    app = run_application(timer, config_manager)

    # Store reference for callbacks (simple approach)
    _set_main_window_ref(app)


# Simple global reference for callbacks (consider using weakref for production)
_main_window_ref = None


def _get_main_window_ref():
    """Get reference to main window."""
    return _main_window_ref


def _set_main_window_ref(ref):
    """Set reference to main window."""
    global _main_window_ref
    _main_window_ref = ref


if __name__ == "__main__":
    main()
