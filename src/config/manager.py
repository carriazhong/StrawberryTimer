"""Strawberry Timer - Configuration management module."""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


class ConfigManager:
    """Configuration manager for Strawberry Timer.

    Handles loading, saving, and validating configuration.
    Supports change notifications for reactive updates.
    """

    # Default configuration (class attribute)
    DEFAULTS: Dict[str, Any] = {
        "work_duration_minutes": 25,
        "sound_enabled": True,
        "sound_file": "assets/alarm.mp3",
        "theme": "strawberry",
        "volume": 80,
        "always_on_top": True,
        "show_desktop_widget": True,
    }

    # Valid themes
    VALID_THEMES = ["strawberry", "dark", "light"]

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to config file. If None, uses default location.
        """
        self._config_path = config_path or self._default_config_path()
        self._config: Dict[str, Any] = self.DEFAULTS.copy()
        self._change_listeners: List[tuple] = []  # (callback, key_filter)

    @property
    def config_path(self) -> Path:
        """Get configuration file path."""
        return self._config_path

    # ==================== Configuration Access ====================

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation.

        Args:
            key: Configuration key.
            value: New value.

        Raises:
            ValueError: If value is invalid.
        """
        old_value = self._config.get(key)
        self._validate(key, value)

        self._config[key] = value

        # Notify listeners if value changed
        if old_value != value:
            self._notify_change(key, value)

    def update(self, config: Dict[str, Any]) -> None:
        """Update multiple configuration values.

        Args:
            config: Dictionary of configuration values to update.
        """
        for key, value in config.items():
            self.set(key, value)

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self._config.copy()

    # ==================== File I/O ====================

    @classmethod
    def load(cls, path: Optional[str] = None) -> "ConfigManager":
        """Load configuration from file.

        Args:
            path: Path to config file. If None, uses default location.

        Returns:
            ConfigManager instance with loaded configuration.

        Raises:
            ValueError: If config file is invalid JSON.
        """
        config_path = Path(path) if path else cls._default_config_path()
        manager = cls(config_path)

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                manager._config = {**manager.DEFAULTS, **loaded}
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid configuration file: {e}")

        return manager

    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file.

        Args:
            path: Path to save config. If None, uses current config_path.
        """
        save_path = Path(path) if path else self._config_path

        # Create parent directories if needed
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)

    # ==================== Validation ====================

    def _validate(self, key: str, value: Any) -> None:
        """Validate a configuration value.

        Args:
            key: Configuration key.
            value: Value to validate.

        Raises:
            ValueError: If value is invalid.
        """
        if key == "work_duration_minutes":
            if not isinstance(value, (int, float)):
                raise ValueError("Work duration must be a number")
            if value <= 0:
                raise ValueError("Duration must be positive")
            if value > 180:
                raise ValueError("Duration too large (max 180 minutes)")

        elif key == "volume":
            if not isinstance(value, (int, float)):
                raise ValueError("Volume must be a number")
            if not 0 <= value <= 100:
                raise ValueError("Volume must be between 0 and 100")

        elif key == "theme":
            if value not in self.VALID_THEMES:
                raise ValueError(
                    f"Invalid theme: {value}. "
                    f"Valid themes: {', '.join(self.VALID_THEMES)}"
                )

        elif key == "sound_file":
            # Just check it's a string, actual file existence checked at runtime
            if not isinstance(value, str):
                raise ValueError("Sound file must be a string path")

    # ==================== Change Notifications ====================

    def on_change(self, callback: Callable[[str, Any], None],
                  key_filter: Optional[str] = None) -> None:
        """Register callback for configuration changes.

        Args:
            callback: Function to call with (key, new_value).
            key_filter: Optional specific key to watch. If None, watches all keys.
        """
        self._change_listeners.append((callback, key_filter))

    def _notify_change(self, key: str, value: Any) -> None:
        """Notify listeners of configuration change.

        Args:
            key: Configuration key that changed.
            value: New value.
        """
        for callback, key_filter in self._change_listeners:
            if key_filter is None or key_filter == key:
                try:
                    callback(key, value)
                except Exception:
                    pass  # Don't let one bad callback break others

    # ==================== Utilities ====================

    @staticmethod
    def _default_config_path() -> Path:
        """Get default configuration file path.

        Returns:
            Path to default config location (platform-specific).
        """
        import os

        home = Path.home()
        if os.name == "nt":  # Windows
            config_dir = home / "AppData" / "Roaming" / "StrawberryTimer"
        else:  # macOS / Linux
            config_dir = home / ".config" / "strawberry_timer"

        return config_dir / "config.json"
