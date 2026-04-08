# Desktop Floating Strawberry Widget - Architecture Design

## Requirements Analysis

### Functional Requirements
1. **Small strawberry icon**: 1/4 size of main window (100x125 pixels based on 400x500 main window)
2. **Transparent background**: Alpha channel transparency for floating effect
3. **Floats on desktop**: Topmost window, draggable, stays in screen bounds
4. **Can be closed**: Hide/show mechanism, survives main window close
5. **Timer display**: Shows remaining time and status

### Non-Functional Requirements
- **Performance**: Minimal CPU usage, efficient update loop
- **Platform**: Windows, macOS, Linux compatibility
- **Usability**: Easy to close/reopen, not intrusive

## Architecture Design

### Module Structure

```
src/ui/
├── main_window.py          # Main timer window (existing)
├── desktop_widget.py       # NEW: Desktop floating widget
└── theme.py                # Theme constants (existing, may extend)
```

### Class: `DesktopWidget`

```python
class DesktopWidget(tk.Toplevel):
    """Floating desktop widget with strawberry icon and timer display."""

    # Size: 1/4 of main window = 100x125 pixels
    WIDTH = 100
    HEIGHT = 125

    def __init__(self, master, timer_engine=None, config_manager=None):
        """Initialize desktop widget.

        Args:
            master: Parent window (for linking, but independent)
            timer_engine: Optional TimerEngine for time updates
            config_manager: Optional ConfigManager for settings
        """
```

### Key Components

#### 1. Window Properties
```python
# Frameless window (no title bar, borders)
self.overrideredirect(1)

# Transparent background
self.attributes("-alpha", 200)  # Semi-transparent (0-255)

# Always on top
self.attributes("-topmost", 1)
```

#### 2. Widget Content
```
┌──────────────┐
│   🍓         │  ← Strawberry icon (emoji or image)
│              │
│   25:00      │  ← Timer display
│              │
│   ● Running │  ← Status indicator
└──────────────┘
```

#### 3. Interaction Design

| User Action | System Response |
|-------------|-----------------|
| Drag widget | Move to new position (constrained to screen) |
| Right-click | Show context menu (Show/Hide, Settings, Close) |
| Double-click | Toggle main window visibility |
| Close button | Hide widget (can be reopened from main window) |

#### 4. Integration Points

```python
# TimerEngine → DesktopWidget
timer_engine.on_tick(desktop_widget.update_time)

# ConfigManager → DesktopWidget
config = {
    "widget_x": int,
    "widget_y": int,
    "widget_alpha": int,  # Transparency
    "widget_visible": bool
}
```

### Data Flow

```
TimerEngine (tick event)
    ↓
DesktopWidget.update_time()
    ↓
Display update (1-sec interval)

ConfigManager (settings)
    ↓
DesktopWidget.load_settings()
    ↓
Position, transparency restored

User (drag/close)
    ↓
DesktopWidget.handle_input()
    ↓
Save position to ConfigManager
```

### Extension Considerations

For future Todo integration:
```python
# Widget could show:
# - Current Todo item title (shortened)
# - Todo completion status
# - Click to open Todo details

desktop_widget.set_todo(todo_item)
```

### Implementation Priorities

**Phase 1 (MVP):**
- Basic frameless window
- Strawberry icon display
- Timer text display
- Close functionality
- Draggable

**Phase 2 (Enhancement):**
- Transparency control
- Position persistence
- Right-click context menu
- Status indicator

**Phase 3 (Polish):**
- Smooth animations
- Theme variations
- Double-click to toggle main window

## Testing Strategy

- **Unit tests**: Widget properties, size calculations, transparency
- **Integration tests**: Widget + TimerEngine interaction
- **GUI tests**: Draggability, close functionality, position bounds
