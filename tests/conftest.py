"""Pytest configuration and fixtures for Strawberry Timer tests."""

import pytest
from unittest.mock import Mock, patch
import time


# ==================== Timer Fixtures ====================

@pytest.fixture
def timer_config():
    """Default timer configuration."""
    return {
        "work_duration_minutes": 25,
        "sound_enabled": True,
        "sound_file": "assets/alarm.mp3",
    }


@pytest.fixture
def mock_sound_player():
    """Mock sound player for testing."""
    with patch("src.sound.player.SoundPlayer") as mock:
        yield mock


@pytest.fixture
def mock_current_time(monkeypatch):
    """Mock current time for deterministic testing."""
    fake_time = 0.0

    def mock_time():
        return fake_time

    def mock_sleep(seconds):
        nonlocal fake_time
        fake_time += seconds

    monkeypatch.setattr(time, "time", mock_time)
    monkeypatch.setattr(time, "sleep", mock_sleep)

    return fake_time


@pytest.fixture
def todo_integration_stub():
    """Mock Todo integration for future extension."""
    return Mock()


@pytest.fixture
def sample_todos():
    """Sample todo items for integration testing."""
    return [
        {"id": 1, "title": "Write documentation", "completed": False},
        {"id": 2, "title": "Fix bug in timer", "completed": False},
        {"id": 3, "title": "Review PR", "completed": False},
    ]
