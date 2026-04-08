"""Strawberry Timer - Sound player module."""

import sys
import platform
from pathlib import Path
from typing import Optional
import subprocess
import threading


class SoundPlayer:
    """Cross-platform sound player for timer notifications.

    Supports:
    - Windows: winsound (built-in)
    - macOS: afplay (built-in)
    - Linux: aplay/paplay (system)
    - Fallback: playsound library
    """

    def __init__(self, volume: int = 80):
        """Initialize sound player.

        Args:
            volume: Volume level (0-100).
        """
        self._volume = max(0, min(100, volume))
        self._pre_mute_volume: int = self._volume
        self._current_process: Optional[subprocess.Popen] = None
        self._platform = platform.system()

    # ==================== Volume Control ====================

    @property
    def volume(self) -> int:
        """Get current volume level."""
        return self._volume

    def set_volume(self, volume: int) -> None:
        """Set volume level.

        Args:
            volume: Volume level (0-100), will be clamped to valid range.
        """
        self._volume = max(0, min(100, volume))

    def mute(self) -> None:
        """Mute sound (set volume to 0)."""
        self._pre_mute_volume = self._volume
        self._volume = 0

    def unmute(self) -> None:
        """Restore volume to pre-mute level."""
        self._volume = self._pre_mute_volume

    # ==================== Sound Playback ====================

    def play(self, sound_file: Optional[str] = None) -> None:
        """Play a sound file synchronously.

        Args:
            sound_file: Path to sound file. If None, uses default.

        Raises:
            FileNotFoundError: If sound file doesn't exist.
            ValueError: If audio format is not supported.
        """
        file_path = Path(sound_file or "assets/alarm.mp3")

        if not file_path.exists():
            raise FileNotFoundError(f"Sound file not found: {file_path}")

        self._validate_format(file_path)
        self._play_sync(file_path)

    def play_async(self, sound_file: Optional[str] = None,
                   on_complete: Optional[callable] = None) -> threading.Thread:
        """Play a sound file asynchronously.

        Args:
            sound_file: Path to sound file. If None, uses default.
            on_complete: Optional callback when playback completes.

        Returns:
            Thread object running the playback.

        Raises:
            FileNotFoundError: If sound file doesn't exist.
            ValueError: If audio format is not supported.
        """
        file_path = Path(sound_file or "assets/alarm.mp3")

        if not file_path.exists():
            raise FileNotFoundError(f"Sound file not found: {file_path}")

        self._validate_format(file_path)

        def playback_wrapper():
            self._play_sync(file_path)
            if on_complete:
                on_complete()

        thread = threading.Thread(target=playback_wrapper, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        """Stop any currently playing sound."""
        if self._current_process:
            self._current_process.terminate()
            self._current_process = None

    def beep(self) -> None:
        """Play a simple system beep."""
        if self._platform == "Windows":
            try:
                import winsound
                winsound.Beep(1000, 200)  # 1000Hz for 200ms
            except (ImportError, RuntimeError):
                print("\a")  # Fallback to terminal bell
        else:
            print("\a")

    # ==================== Internal Methods ====================

    def _validate_format(self, file_path: Path) -> None:
        """Validate audio file format.

        Args:
            file_path: Path to audio file.

        Raises:
            ValueError: If format is not supported.
        """
        supported_extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}
        if file_path.suffix.lower() not in supported_extensions:
            raise ValueError(
                f"Unsupported audio format: {file_path.suffix}. "
                f"Supported: {', '.join(supported_extensions)}"
            )

    def _play_sync(self, file_path: Path) -> None:
        """Play sound file synchronously based on platform.

        Args:
            file_path: Path to sound file.
        """
        if self._platform == "Windows":
            self._play_windows(file_path)
        elif self._platform == "Darwin":  # macOS
            self._play_macos(file_path)
        elif self._platform == "Linux":
            self._play_linux(file_path)
        else:
            self._play_fallback(file_path)

    def _play_windows(self, file_path: Path) -> None:
        """Play sound on Windows using winsound or playsound.

        Args:
            file_path: Path to sound file.
        """
        try:
            import winsound

            # For WAV files, use winsound directly
            if file_path.suffix.lower() == ".wav":
                winsound.PlaySound(str(file_path), winsound.SND_FILENAME)
            else:
                # For other formats, use playsound
                from playsound import playsound
                playsound(str(file_path))
        except ImportError:
            self._play_fallback(file_path)

    def _play_macos(self, file_path: Path) -> None:
        """Play sound on macOS using afplay.

        Args:
            file_path: Path to sound file.
        """
        cmd = ["afplay", str(file_path)]
        if self._volume < 100:
            # afplay volume is 0.0 to 1.0
            volume_arg = self._volume / 100.0
            cmd = ["afplay", "-v", str(volume_arg), str(file_path)]

        self._current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._current_process.wait()
        self._current_process = None

    def _play_linux(self, file_path: Path) -> None:
        """Play sound on Linux using paplay or aplay.

        Args:
            file_path: Path to sound file.
        """
        # Try paplay (PulseAudio) first
        commands = [
            ["paplay", "--volume", str(int(self._volume * 655)), str(file_path)],
            ["aplay", str(file_path)],  # Fallback to ALSA
        ]

        for cmd in commands:
            try:
                self._current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._current_process.wait()
                self._current_process = None
                return
            except FileNotFoundError:
                continue

        # If all fail, try fallback
        self._play_fallback(file_path)

    def _play_fallback(self, file_path: Path) -> None:
        """Fallback method using playsound library.

        Args:
            file_path: Path to sound file.
        """
        try:
            from playsound import playsound
            playsound(str(file_path))
        except ImportError:
            # Last resort - system beep
            self.beep()
