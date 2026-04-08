# Strawberry Timer

A simple, elegant desktop Pomodoro timer application.

## Features

- **25-minute work sessions** (configurable)
- **Manual break control** - rest when you need to
- **Sound notification** when work time ends
- **Strawberry-themed UI** with desktop clock widget
- **Future Todo integration** - architecture ready for Todo list connectivity

## Technology Stack

- **Language**: Python 3.10+
- **GUI**: Tkinter (built-in)
- **Testing**: pytest
- **Sound**: Playsound / system beep

## Project Structure

```
StawberryTimer/
├── src/
│   ├── __init__.py
│   ├── timer/          # Timer business logic
│   ├── ui/             # GUI components
│   ├── sound/          # Sound notification
│   └── config/         # Configuration management
├── tests/              # Test suite
├── assets/             # Icons, sounds
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Installation

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python main.py
```

### Sound Support
The app uses built-in OS sound commands - no additional packages needed:
- **Windows**: Uses `winsound` (built-in with Python)
- **macOS**: Uses `afplay` (built-in with macOS)
- **Linux**: Uses `paplay` or `aplay` (install via `sudo apt install pulseaudio-utils` or `sudo apt install alsa-utils`)

## Usage

1. Click "Start" to begin a 25-minute work session
2. When the timer ends, a sound will play
3. Take a break for as long as you need
4. Click "Start" again when ready for the next session

## Future Features

- [ ] Todo list integration
- [ ] Statistics and session history
- [ ] Customizable work duration
- [ ] Different notification sounds
