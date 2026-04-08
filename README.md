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

```bash
pip install -r requirements.txt
python main.py
```

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
