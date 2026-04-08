"""Test cases for Timer Engine (business logic layer).

Following TDD principles, these tests define the expected behavior
of the timer before implementation.

Test categories:
- State management (idle, running, paused, completed)
- Time countdown functionality
- Timer completion and notification
- Pause/resume functionality
- Configuration and duration management
"""

import pytest
from datetime import timedelta
from unittest.mock import Mock, patch, call
import time


# ==================== Test: Timer State Management ====================

class TestTimerStateManagement:
    """Test timer state transitions."""

    def test_initial_state_is_idle(self, timer_engine):
        """Timer should start in IDLE state."""
        assert timer_engine.state == "IDLE"
        assert timer_engine.is_idle() is True
        assert timer_engine.is_running() is False

    def test_start_changes_state_to_running(self, timer_engine):
        """Starting timer should change state to RUNNING."""
        timer_engine.start()
        assert timer_engine.state == "RUNNING"
        assert timer_engine.is_running() is True
        assert timer_engine.is_idle() is False

    def test_pause_changes_state_to_paused(self, timer_engine):
        """Pausing running timer should change state to PAUSED."""
        timer_engine.start()
        timer_engine.pause()
        assert timer_engine.state == "PAUSED"
        assert timer_engine.is_paused() is True
        assert timer_engine.is_running() is False

    def test_resume_from_paused_returns_to_running(self, timer_engine):
        """Resuming from paused should return to RUNNING state."""
        timer_engine.start()
        timer_engine.pause()
        timer_engine.resume()
        assert timer_engine.state == "RUNNING"
        assert timer_engine.is_running() is True

    def test_stop_returns_to_idle(self, timer_engine):
        """Stopping timer should return to IDLE state."""
        timer_engine.start()
        timer_engine.stop()
        assert timer_engine.state == "IDLE"
        assert timer_engine.is_idle() is True

    def test_completion_changes_state_to_completed(self, timer_engine, mock_current_time):
        """Timer should transition to COMPLETED when time expires."""
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=25).total_seconds())
        assert timer_engine.state == "COMPLETED"
        assert timer_engine.is_completed() is True

    def test_cannot_start_when_already_running(self, timer_engine):
        """Starting an already running timer should be idempotent."""
        timer_engine.start()
        initial_remaining = timer_engine.remaining_time
        timer_engine.start()  # Should not reset
        assert timer_engine.state == "RUNNING"
        assert timer_engine.remaining_time == initial_remaining


# ==================== Test: Time Countdown ====================

class TestTimeCountdown:
    """Test timer countdown functionality."""

    def test_initial_remaining_time_matches_config(self, timer_engine, timer_config):
        """Initial remaining time should match configured work duration."""
        expected = timedelta(minutes=timer_config["work_duration_minutes"])
        assert timer_engine.remaining_time == expected

    def test_remaining_time_decreases_when_running(self, timer_engine):
        """Remaining time should decrease as timer runs."""
        timer_engine.start()
        initial = timer_engine.remaining_time
        time.sleep(0.1)  # Small delay
        assert timer_engine.remaining_time < initial

    def test_remaining_time_stops_decreasing_when_paused(self, timer_engine):
        """Remaining time should not decrease when paused."""
        timer_engine.start()
        timer_engine.pause()
        paused_time = timer_engine.remaining_time
        time.sleep(0.1)
        assert timer_engine.remaining_time == paused_time

    def test_remaining_time_continues_after_resume(self, timer_engine):
        """Remaining time should continue decreasing after resume."""
        timer_engine.start()
        timer_engine.pause()
        timer_engine.resume()
        resume_time = timer_engine.remaining_time
        time.sleep(0.1)
        assert timer_engine.remaining_time < resume_time

    def test_remaining_time_formatted_display(self, timer_engine):
        """Remaining time should be formatted as MM:SS."""
        # Mock exact remaining time
        timer_engine._remaining = timedelta(minutes=25, seconds=0)
        assert timer_engine.remaining_time_str == "25:00"

        timer_engine._remaining = timedelta(minutes=5, seconds=30)
        assert timer_engine.remaining_time_str == "05:30"

        timer_engine._remaining = timedelta(seconds=59)
        assert timer_engine.remaining_time_str == "00:59"


# ==================== Test: Timer Completion ====================

class TestTimerCompletion:
    """Test timer completion behavior."""

    def test_timer_triggers_completion_callback(self, timer_engine, mock_callback):
        """Completion callback should be triggered when timer ends."""
        timer_engine.on_complete(mock_callback)
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=25).total_seconds())
        mock_callback.assert_called_once()

    def test_completion_sound_played_when_enabled(self, timer_engine, mock_sound_player):
        """Sound should play on completion when enabled."""
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=25).total_seconds())
        mock_sound_player.play.assert_called_once()

    def test_completion_sound_not_played_when_disabled(self, timer_engine, mock_sound_player):
        """Sound should NOT play on completion when disabled."""
        timer_engine.config["sound_enabled"] = False
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=25).total_seconds())
        mock_sound_player.play.assert_not_called()

    def test_multiple_completion_callbacks_supported(self, timer_engine):
        """Multiple completion callbacks should all be triggered."""
        callback1 = Mock()
        callback2 = Mock()
        timer_engine.on_complete(callback1)
        timer_engine.on_complete(callback2)
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=25).total_seconds())
        callback1.assert_called_once()
        callback2.assert_called_once()


# ==================== Test: Pause/Resume ====================

class TestPauseResume:
    """Test pause and resume functionality."""

    def test_pause_freezes_remaining_time(self, timer_engine):
        """Pausing should freeze the remaining time."""
        timer_engine.start()
        paused_time = timer_engine.remaining_time
        timer_engine.pause()
        time.sleep(0.1)
        assert timer_engine.remaining_time == paused_time

    def test_resume_continues_from_paused_time(self, timer_engine):
        """Resuming should continue from paused remaining time."""
        timer_engine.start()
        timer_engine.pause()
        paused_remaining = timer_engine.remaining_time
        timer_engine.resume()
        assert timer_engine.remaining_time == paused_remaining

    def test_pause_when_idle_has_no_effect(self, timer_engine):
        """Pausing when idle should have no effect."""
        assert timer_engine.state == "IDLE"
        timer_engine.pause()
        assert timer_engine.state == "IDLE"

    def test_resume_when_idle_has_no_effect(self, timer_engine):
        """Resuming when idle should have no effect."""
        timer_engine.resume()
        assert timer_engine.state == "IDLE"


# ==================== Test: Configuration ====================

class TestTimerConfiguration:
    """Test timer configuration management."""

    def test_custom_work_duration(self, timer_config):
        """Timer should support custom work duration."""
        timer_config["work_duration_minutes"] = 20
        engine = TimerEngine(timer_config)
        assert engine.remaining_time == timedelta(minutes=20)

    def test_duration_in_seconds(self, timer_engine):
        """Timer should support duration in seconds for testing."""
        timer_engine.config["work_duration_minutes"] = 0.5  # 30 seconds
        assert timer_engine.remaining_time == timedelta(seconds=30)

    def test_invalid_duration_raises_error(self, timer_config):
        """Invalid duration should raise ValueError."""
        timer_config["work_duration_minutes"] = -5
        with pytest.raises(ValueError, match="Duration must be positive"):
            TimerEngine(timer_config)

    def test_config_update_after_creation(self, timer_engine):
        """Configuration should be updatable after creation."""
        timer_engine.update_config({"work_duration_minutes": 30})
        timer_engine.stop()  # Reset to apply new config
        timer_engine.start()
        assert timer_engine.remaining_time == timedelta(minutes=30)


# ==================== Test: Progress Tracking ====================

class TestProgressTracking:
    """Test progress percentage tracking."""

    def test_progress_at_start_is_100_percent(self, timer_engine):
        """Progress should be 100% at the start."""
        timer_engine.start()
        assert timer_engine.progress_percent == 100.0

    def test_progress_at_half_time(self, timer_engine):
        """Progress should be 50% at half time."""
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=12.5).total_seconds())
        assert timer_engine.progress_percent == 50.0

    def test_progress_at_completion_is_0_percent(self, timer_engine):
        """Progress should be 0% at completion."""
        timer_engine.start()
        timer_engine._advance_time(timedelta(minutes=25).total_seconds())
        assert timer_engine.progress_percent == 0.0


# ==================== Test: Event Hooks ====================

class TestEventHooks:
    """Test event hooks for extensibility."""

    def test_on_tick_callback_fired_periodically(self, timer_engine):
        """Tick callback should be fired periodically."""
        callback = Mock()
        timer_engine.on_tick(callback, interval_seconds=1)
        timer_engine.start()
        timer_engine._advance_time(5)
        assert callback.call_count >= 5

    def test_on_start_callback_fired(self, timer_engine):
        """Start callback should be fired when timer starts."""
        callback = Mock()
        timer_engine.on_start(callback)
        timer_engine.start()
        callback.assert_called_once()

    def test_on_pause_callback_fired(self, timer_engine):
        """Pause callback should be fired when timer pauses."""
        callback = Mock()
        timer_engine.on_pause(callback)
        timer_engine.start()
        timer_engine.pause()
        callback.assert_called_once()

    def test_on_resume_callback_fired(self, timer_engine):
        """Resume callback should be fired when timer resumes."""
        callback = Mock()
        timer_engine.on_resume(callback)
        timer_engine.start()
        timer_engine.pause()
        timer_engine.resume()
        callback.assert_called_once()


# ==================== Fixtures ====================

@pytest.fixture
def timer_engine(timer_config, mock_sound_player):
    """Create a TimerEngine instance for testing."""
    from src.timer.engine import TimerEngine
    return TimerEngine(timer_config)


@pytest.fixture
def mock_callback():
    """Mock callback for testing."""
    return Mock()
