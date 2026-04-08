"""Test cases for Configuration module.

Tests configuration management:
- Default configuration values
- Loading from config file
- Saving to config file
- Validation of config values
"""

import pytest
from pathlib import Path
import json
import tempfile


# ==================== Test: Default Configuration ====================

class TestDefaultConfiguration:
    """Test default configuration values."""

    def test_default_work_duration(self, config):
        """Default work duration should be 25 minutes."""
        assert config.get("work_duration_minutes") == 25

    def test_default_sound_enabled(self, config):
        """Sound should be enabled by default."""
        assert config.get("sound_enabled") is True

    def test_default_sound_file(self, config):
        """Default sound file path."""
        assert "alarm" in config.get("sound_file", "").lower()

    def test_default_theme(self, config):
        """Default theme should be 'strawberry'."""
        assert config.get("theme") == "strawberry"

    def test_all_required_keys_present(self, config):
        """All required configuration keys should be present."""
        required_keys = [
            "work_duration_minutes",
            "sound_enabled",
            "sound_file",
            "theme",
        ]
        for key in required_keys:
            assert key in config


# ==================== Test: Configuration Loading ====================

class TestConfigurationLoading:
    """Test loading configuration from file."""

    def test_load_from_json_file(self, config_file, custom_config):
        """Should load configuration from JSON file."""
        config_file.write_text(json.dumps(custom_config))
        from src.config.manager import ConfigManager
        config = ConfigManager.load(str(config_file))
        assert config.get("work_duration_minutes") == 20

    def test_load_nonexistent_file_creates_default(self, config_file):
        """Loading non-existent file should create default config."""
        from src.config.manager import ConfigManager
        config = ConfigManager.load(str(config_file))
        assert config.get("work_duration_minutes") == 25

    def test_invalid_json_raises_error(self, config_file):
        """Invalid JSON should raise error."""
        config_file.write_text("{invalid json}")
        from src.config.manager import ConfigManager
        with pytest.raises(ValueError, match="Invalid configuration file"):
            ConfigManager.load(str(config_file))


# ==================== Test: Configuration Saving ====================

class TestConfigurationSaving:
    """Test saving configuration to file."""

    def test_save_to_json_file(self, config, config_file):
        """Should save configuration to JSON file."""
        config.set("work_duration_minutes", 30)
        config.save(str(config_file))
        assert config_file.exists()

        # Verify saved content
        saved = json.loads(config_file.read_text())
        assert saved["work_duration_minutes"] == 30

    def test_save_creates_parent_directories(self, config):
        """Save should create parent directories if they don't exist."""
        nested_path = Path("/tmp/nested/path/config.json")
        config.set("work_duration_minutes", 20)
        config.save(str(nested_path))
        assert nested_path.exists()

    def test_save_preserves_all_settings(self, config, config_file):
        """Save should preserve all configuration settings."""
        config.set("work_duration_minutes", 20)
        config.set("sound_enabled", False)
        config.set("theme", "dark")
        config.save(str(config_file))

        # Reload and verify
        from src.config.manager import ConfigManager
        reloaded = ConfigManager.load(str(config_file))
        assert reloaded.get("work_duration_minutes") == 20
        assert reloaded.get("sound_enabled") is False
        assert reloaded.get("theme") == "dark"


# ==================== Test: Configuration Validation ====================

class TestConfigurationValidation:
    """Test configuration value validation."""

    def test_work_duration_must_be_positive(self, config):
        """Work duration must be positive number."""
        with pytest.raises(ValueError, match="must be positive"):
            config.set("work_duration_minutes", -5)

    def test_work_duration_max_value(self, config):
        """Work duration should have reasonable maximum."""
        with pytest.raises(ValueError, match="too large"):
            config.set("work_duration_minutes", 180)  # 3 hours

    def test_volume_must_be_between_0_and_100(self, config):
        """Volume must be in valid range."""
        with pytest.raises(ValueError, match="Volume"):
            config.set("volume", 150)

    def test_theme_must_be_valid(self, config):
        """Theme must be one of the available themes."""
        with pytest.raises(ValueError, match="Invalid theme"):
            config.set("theme", "nonexistent_theme")


# ==================== Test: Configuration Watcher ====================

class TestConfigurationWatcher:
    """Test watching for configuration changes."""

    def test_notify_on_config_change(self, config):
        """Should notify listeners when config changes."""
        callback = Mock()
        config.on_change(callback)
        config.set("work_duration_minutes", 30)
        callback.assert_called_once_with("work_duration_minutes", 30)

    def test_multiple_change_listeners(self, config):
        """Should notify all registered listeners."""
        callback1 = Mock()
        callback2 = Mock()
        config.on_change(callback1)
        config.on_change(callback2)
        config.set("sound_enabled", False)
        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_no_notification_for_same_value(self, config):
        """Should not notify when setting same value."""
        callback = Mock()
        config.on_change(callback)
        config.set("work_duration_minutes", 25)  # Same as default
        callback.assert_not_called()


# ==================== Fixtures ====================

@pytest.fixture
def config():
    """Create a default ConfigManager instance."""
    from src.config.manager import ConfigManager
    return ConfigManager()


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file path."""
    return tmp_path / "config.json"


@pytest.fixture
def custom_config():
    """Custom configuration for testing."""
    return {
        "work_duration_minutes": 20,
        "sound_enabled": False,
        "sound_file": "custom_alarm.mp3",
        "theme": "dark",
        "volume": 50,
    }
