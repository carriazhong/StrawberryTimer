# 🍓 Strawberry Timer - Build Executable

## Overview

Create a standalone Windows EXE file that can run without Python installed.

---

## Prerequisites

1. **Python 3.8+** installed
2. **PyInstaller** installed (will auto-install if missing)
3. **PyQt5** installed (for timer GUI)

---

## Quick Build (Windows)

Double-click the build script:
```
build_exe.bat
```

Or manually:
```bash
# Install PyInstaller
pip install pyinstaller

# Build EXE
pyinstaller pyqt_timer.spec
```

The EXE will be created in: `dist\StrawberryTimer.exe`

---

## Build Options

### Option 1: Quick Build (Recommended)
```bash
build_exe.bat
```
- Cleans previous build
- Builds with PyInstaller
- Opens output folder when done

### Option 2: Manual Build
```bash
# Install dependencies
pip install pyinstaller

# Clean previous build
rmdir /s /q build
rmdir /s /q dist

# Build
pyinstaller --clean pyqt_timer.spec
```

### Option 3: One-File (Single EXE)
Create a single file EXE (no folder structure):

Edit `pyqt_timer.spec`, change to:
```python
exe = EXE(
    ...
    onefile=True,  # Add this line
    ...
)
```

Then run:
```bash
pyinstaller pyqt_timer.spec
```

**Pros**: Single EXE file
**Cons**: Slower startup, larger file

---

## Generated EXE Features

✅ **Standalone**: No Python installation required
✅ **All-in-One**: Includes all dependencies
✅ **No Console**: Clean GUI-only application
✅ **Small Size**: ~15-20 MB (with PyQt5)
✅ **Fast Startup**: Ready in 1-2 seconds

---

## Widget Configuration

**Current Settings**:
- **Size**: 80 × 30 pixels
- **Font**: 14 pixels (bold)
- **Display**: MM:SS format (e.g., "25:00")
- **Transparency**: 85%
- **Always on Top**: Yes
- **Draggable**: Yes

---

## Changing Widget Size

Edit `pyqt_timer.py`, line ~166:

```python
# Current: 80×30 (shows full MM:SS)
self.strawberry = StrawberryWidget(self.timer, width=80, height=30, font_size=14)

# Smaller: 60×25 (still shows MM:SS, tighter fit)
self.strawberry = StrawberryWidget(self.timer, width=60, height=25, font_size=12)

# Larger: 100×35 (more prominent)
self.strawberry = StrawberryWidget(self.timer, width=100, height=35, font_size=16)
```

Then rebuild EXE:
```bash
build_exe.bat
```

---

## Distribution

The EXE file is ready to share:
- 📁 `dist\StrawberryTimer.exe`
- 📦 Can be copied to any Windows PC
- 🚫 No Python or dependencies needed
- ✅ Just double-click to run

---

## Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install PyQt5
pip install pyinstaller
```

### EXE doesn't start
- Run as Administrator
- Check Windows Defender isn't blocking it
- Run from Command Prompt to see errors

---

## Size Comparison

| Configuration | Size | Display |
|-------------|-------|---------|
| **80×30** (default) | Best fit | 25:00 |
| **60×25** (compact) | Smaller | 25:00 |
| **100×35** (large) | More space | 25:00 |

---

## Quick Reference

**Build**:
```bash
build_exe.bat
```

**Run**:
```bash
dist\StrawberryTimer.exe
```

**Test**:
```bash
python pyqt_timer.py  # For development
```

---

The EXE is ready! 🎉
