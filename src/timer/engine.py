"""Strawberry Timer - Core timer business logic."""

import time
import threading
from datetime import timedelta
from enum import Enum, auto
from typing import Callable, Optional, Dict, Any, List
from dataclasses import dataclass, field


class TimerState(Enum):
    """Timer state enumeration."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()


@dataclass
class TimerConfig:
    """Timer configuration."""
    work_duration_minutes: float = 25.0
    sound_enabled: bool = True
    sound_file: str = "assets/alarm.mp3"
    volume: int = 80
    theme: str = "strawberry"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.work_duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if self.work_duration_minutes > 180:  # 3 hours max
            raise ValueError("Duration too large (max 180 minutes)")
        if not 0 <= self.volume <= 100:
            raise ValueError("Volume must be between 0 and 100")


class TimerEngine:
    """Core timer engine implementing Pomodoro technique.

    Manages timer state, countdown, and event notifications.
    Designed for testability and extensibility.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize timer engine.

        Args:
            config: Configuration dictionary. If None, uses defaults.
        """
        self._config = self._parse_config(config or {})
        self._state = TimerState.IDLE
        self._remaining: timedelta = timedelta(minutes=self._config["work_duration_minutes"])
        self._initial_duration: timedelta = self._remaining
        self._active_todo: Optional[Dict[str, Any]] = None
        self._session_history: List[Dict[str, Any]] = []

        # Event callbacks
        self._on_complete_callbacks: List[Callable] = []
        self._on_tick_callbacks: List[tuple] = []  # (callback, interval)
        self._on_start_callbacks: List[Callable] = []
        self._on_pause_callbacks: List[Callable] = []
        self._on_resume_callbacks: List[Callable] = []

        # Thread control
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def _parse_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate configuration.

        Args:
            config: Raw configuration dictionary.

        Returns:
            Validated configuration with defaults applied.
        """
        defaults = {
            "work_duration_minutes": 25.0,
            "sound_enabled": True,
            "sound_file": "assets/alarm.mp3",
            "volume": 80,
            "theme": "strawberry",
        }
        defaults.update(config)
        return defaults

    # ==================== State Management ====================

    @property
    def state(self) -> str:
        """Get current timer state as string."""
        return self._state.name

    @property
    def is_idle(self) -> bool:
        """Check if timer is idle."""
        return self._state == TimerState.IDLE

    @property
    def is_running(self) -> bool:
        """Check if timer is running."""
        return self._state == TimerState.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if timer is paused."""
        return self._state == TimerState.PAUSED

    @property
    def is_completed(self) -> bool:
        """Check if timer is completed."""
        return self._state == TimerState.COMPLETED

    def start(self) -> None:
        """Start the timer.

        If already running, does nothing (idempotent).
        """
        with self._lock:
            if self._state == TimerState.RUNNING:
                return

            if self._state == TimerState.IDLE or self._state == TimerState.COMPLETED:
                self._remaining = timedelta(minutes=self._config["work_duration_minutes"])
                self._initial_duration = self._remaining

            self._state = TimerState.RUNNING
            self._stop_event.clear()

            # Start timer thread
            self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self._timer_thread.start()

            # Notify callbacks
            self._notify_callbacks(self._on_start_callbacks)

    def pause(self) -> None:
        """Pause the timer.

        If idle or already paused, does nothing.
        """
        with self._lock:
            if self._state != TimerState.RUNNING:
                return

            self._state = TimerState.PAUSED
            self._stop_event.set()
            self._notify_callbacks(self._on_pause_callbacks)

    def resume(self) -> None:
        """Resume from paused state.

        If not paused, does nothing.
        """
        with self._lock:
            if self._state != TimerState.PAUSED:
                return

            self._state = TimerState.RUNNING
            self._stop_event.clear()

            self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self._timer_thread.start()

            self._notify_callbacks(self._on_resume_callbacks)

    def stop(self) -> None:
        """Stop the timer and return to idle state.

        Stops any running timer thread and resets state.
        """
        with self._lock:
            self._stop_event.set()
            self._state = TimerState.IDLE
            if self._timer_thread and self._timer_thread.is_alive():
                self._timer_thread.join(timeout=1.0)

    # ==================== Time Management ====================

    @property
    def remaining_time(self) -> timedelta:
        """Get remaining time as timedelta."""
        return self._remaining

    @property
    def remaining_time_str(self) -> str:
        """Get remaining time formatted as MM:SS."""
        total_seconds = int(self._remaining.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def progress_percent(self) -> float:
        """Get progress percentage (100% at start, 0% at completion)."""
        if self._initial_duration.total_seconds() == 0:
            return 0.0
        return (self._remaining.total_seconds() / self._initial_duration.total_seconds()) * 100

    # ==================== Event Hooks ====================

    def on_complete(self, callback: Callable) -> None:
        """Register callback for timer completion.

        Args:
            callback: Function to call when timer completes.
        """
        self._on_complete_callbacks.append(callback)

    def on_tick(self, callback: Callable, interval_seconds: float = 1.0) -> None:
        """Register callback for periodic tick events.

        Args:
            callback: Function to call periodically.
            interval_seconds: Interval between callbacks.
        """
        self._on_tick_callbacks.append((callback, interval_seconds))

    def on_start(self, callback: Callable) -> None:
        """Register callback for timer start.

        Args:
            callback: Function to call when timer starts.
        """
        self._on_start_callbacks.append(callback)

    def on_pause(self, callback: Callable) -> None:
        """Register callback for timer pause.

        Args:
            callback: Function to call when timer pauses.
        """
        self._on_pause_callbacks.append(callback)

    def on_resume(self, callback: Callable) -> None:
        """Register callback for timer resume.

        Args:
            callback: Function to call when timer resumes.
        """
        self._on_resume_callbacks.append(callback)

    def _notify_callbacks(self, callbacks: List[Callable]) -> None:
        """Notify all registered callbacks.

        Args:
            callbacks: List of callback functions to notify.
        """
        for callback in callbacks:
            try:
                callback()
            except Exception:
                pass  # Don't let one bad callback break others

    # ==================== Todo Integration ====================

    def attach_todo(self, todo: Dict[str, Any]) -> None:
        """Attach a Todo item to the current timer session.

        Args:
            todo: Todo item dictionary with at least 'id' and 'title'.
        """
        self._active_todo = todo

    def detach_todo(self) -> None:
        """Detach any attached Todo item."""
        self._active_todo = None

    @property
    def active_todo(self) -> Optional[Dict[str, Any]]:
        """Get the currently attached Todo item."""
        return self._active_todo

    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get history of completed timer sessions.

        Returns:
            List of session dictionaries with duration, todo_id, timestamp.
        """
        return self._session_history.copy()

    # ==================== Configuration ====================

    def update_config(self, config: Dict[str, Any]) -> None:
        """Update timer configuration.

        Args:
            config: New configuration values to apply.
        """
        self._config.update(self._parse_config(config))

    @property
    def config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()

    # ==================== Internal Timer Loop ====================

    def _run_timer(self) -> None:
        """Internal timer running in separate thread."""
        tick_interval = 0.1  # 100ms precision
        last_tick = time.monotonic()

        while not self._stop_event.is_set():
            current_time = time.monotonic()
            elapsed = current_time - last_tick
            last_tick = current_time

            # Decrease remaining time
            self._remaining -= timedelta(seconds=elapsed)

            # Check for completion
            if self._remaining <= timedelta(0):
                self._remaining = timedelta(0)
                with self._lock:
                    if self._state == TimerState.RUNNING:
                        self._state = TimerState.COMPLETED
                self._complete_session()
                self._notify_callbacks(self._on_complete_callbacks)
                break

            # Notify tick callbacks
            self._notify_tick_callbacks(elapsed)

            # Sleep for tick interval
            self._stop_event.wait(tick_interval)

    def _notify_tick_callbacks(self, elapsed: float) -> None:
        """Notify tick callbacks based on their intervals.

        Args:
            elapsed: Time elapsed since last check.
        """
        # Simple implementation - in production, would track per-callback timers
        for callback, interval in self._on_tick_callbacks:
            if elapsed >= interval:
                try:
                    callback()
                except Exception:
                    pass

    def _complete_session(self) -> None:
        """Record session completion."""
        session = {
            "duration_seconds": self._initial_duration.total_seconds(),
            "completed_at": time.time(),
            "todo_id": self._active_todo["id"] if self._active_todo else None,
        }
        self._session_history.append(session)

    # ==================== Testing Utilities ====================

    def _advance_time(self, seconds: float) -> None:
        """Advance timer by specified seconds (testing only).

        This method allows fast-forwarding the timer for testing purposes.

        Args:
            seconds: Number of seconds to advance.
        """
        self._remaining -= timedelta(seconds=seconds)
        if self._remaining <= timedelta(0):
            self._remaining = timedelta(0)
            with self._lock:
                if self._state == TimerState.RUNNING:
                    self._state = TimerState.COMPLETED
            self._complete_session()
            self._notify_callbacks(self._on_complete_callbacks)

    @property
    def remaining(self) -> timedelta:
        """Get remaining time (for testing)."""
        return self._remaining
