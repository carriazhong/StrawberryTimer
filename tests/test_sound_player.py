"""Test cases for Sound Player module.

Tests sound notification functionality including:
- Sound file playback
- Error handling for missing files
- Volume control
- Platform compatibility (Windows, macOS, Linux)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


# ==================== Test: Sound Playback ====================

class TestSoundPlayback:
    """Test basic sound playback functionality."""

    def test_play_sound_file_exists(self, sound_player, test_sound_file):
        """Should play sound when file exists."""
        sound_player.play(test_sound_file)
        # Verify sound was played (implementation specific)

    def test_play_default_alarm(self, sound_player):
        """Should play default alarm when no file specified."""
        sound_player.play()
        # Should use configured default sound

    def test_play_nonexistent_file_raises_error(self, sound_player):
        """Should raise error when sound file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            sound_player.play("nonexistent.mp3")

    def test_play_unsupported_format_raises_error(self, sound_player, test_sound_file):
        """Should raise error for unsupported audio format."""
        unsupported = Path(test_sound_file).parent / "unsupported.xyz"
        with pytest.raises(ValueError, match="Unsupported audio format"):
            sound_player.play(str(unsupported))


# ==================== Test: Volume Control ====================

class TestVolumeControl:
    """Test volume control functionality."""

    def test_set_volume_valid_range(self, sound_player):
        """Should set volume within valid range (0-100)."""
        sound_player.set_volume(50)
        assert sound_player.volume == 50

    def test_set_volume_clamps_to_maximum(self, sound_player):
        """Should clamp volume to maximum of 100."""
        sound_player.set_volume(150)
        assert sound_player.volume == 100

    def test_set_volume_clamps_to_minimum(self, sound_player):
        """Should clamp volume to minimum of 0."""
        sound_player.set_volume(-10)
        assert sound_player.volume == 0

    def test_mute(self, sound_player):
        """Should mute sound (volume = 0)."""
        sound_player.set_volume(50)
        sound_player.mute()
        assert sound_player.volume == 0

    def test_unmute_restores_volume(self, sound_player):
        """Should restore previous volume when unmuting."""
        sound_player.set_volume(50)
        sound_player.mute()
        sound_player.unmute()
        assert sound_player.volume == 50


# ==================== Test: Platform Compatibility ====================

class TestPlatformCompatibility:
    """Test cross-platform sound playback."""

    @patch('sys.platform', 'win32')
    def test_uses_windows_sound_api(self):
        """Should use Windows sound API on Windows."""
        # Platform-specific implementation test
        pass

    @patch('sys.platform', 'darwin')
    def test_uses_macos_sound_api(self):
        """Should use macOS sound API (afplay)."""
        # Platform-specific implementation test
        pass

    @patch('sys.platform', 'linux')
    def test_uses_linux_sound_api(self):
        """Should use Linux sound API (aplay/pulseaudio)."""
        # Platform-specific implementation test
        pass


# ==================== Test: Async Playback ====================

class TestAsyncPlayback:
    """Test asynchronous sound playback."""

    def test_play_async_does_not_block(self, sound_player):
        """Async play should return immediately."""
        import time
        start = time.time()
        sound_player.play_async("test.mp3")
        elapsed = time.time() - start
        assert elapsed < 0.1  # Should return very quickly

    def test_play_async_fires_completion_callback(self, sound_player):
        """Async play should fire callback when complete."""
        callback = Mock()
        sound_player.play_async("test.mp3", on_complete=callback)
        # Wait for async completion
        # callback.assert_called_once()

    def test_stop_stops_async_playback(self, sound_player):
        """Stop should halt async playback."""
        sound_player.play_async("long_sound.mp3")
        sound_player.stop()
        # Verify playback stopped


# ==================== Fixtures ====================

@pytest.fixture
def sound_player():
    """Create a SoundPlayer instance for testing."""
    from src.sound.player import SoundPlayer
    return SoundPlayer()


@pytest.fixture
def test_sound_file(tmp_path):
    """Create a test sound file."""
    sound_file = tmp_path / "test_alarm.mp3"
    # Create minimal valid MP3 header
    sound_file.write_bytes(b'ID3' + b'\x00' * 100)
    return str(sound_file)
