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
        description="🍓 Strawberry Timer - A simple desktop Pomodoro timer"
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
            sound.play(config_manager.get("sound_file"))

    timer.on_complete(on_timer_complete)

    # Run GUI application
    # TODO: Pass timer, todos to MainWindow for full integration
    run_application()


if __name__ == "__main__":
    main()
