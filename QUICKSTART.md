# 🍓 Strawberry Timer - Quick Guide

## ✅ What's New

1. **Widget Size**: 80×30 pixels (shows full MM:SS format)
2. **Full Timer Display**: Shows "25:00" instead of just "25"
3. **Standalone EXE**: Double-click to run, no Python needed
4. **Close Together**: Both windows close simultaneously

---

## 🚀 Quick Start

### Build EXE (Windows)
```bash
cd C:\03_SDV\Output\StawberryTimer
build_exe.bat
```
The EXE will be in: `dist\StrawberryTimer.exe`

### Run from Source
```bash
cd C:\03_SDV\Output\StawberryTimer
python pyqt_timer.py
```

---

## 📊 Widget Display

**Floating Widget** (80×30px):
- Shows: **MM:SS** format (e.g., "25:00")
- Transparency: 85%
- Always on top
- Draggable
- Color states:
  - 🔴 Red = Ready/Stopped
  - 🟡 Yellow = Paused
  - 🟢 Green = Running

---

## 🔧 Building EXE

### Prerequisites
```bash
pip install PyQt5 pyinstaller
```

### Quick Build
1. Double-click `build_exe.bat`
2. Wait for build to complete
3. EXE is ready in `dist\` folder

### Manual Build
```bash
pyinstaller pyqt_timer.spec
```

---

## 📦 Distribution

The EXE file is standalone:
- No Python installation required
- Can copy to any Windows PC
- Just double-click to run
- Size: ~15-20 MB

---

## 🎨 Customization

### Change Widget Size

Edit `pyqt_timer.py`, line ~166:

```python
# Compact: 60×25
self.strawberry = StrawberryWidget(self.timer, width=60, height=25, font_size=12)

# Default: 80×30
self.strawberry = StrawberryWidget(self.timer, width=80, height=30, font_size=14)

# Large: 100×35
self.strawberry = StrawberryWidget(self.timer, width=100, height=35, font_size=16)
```

Rebuild after changing size:
```bash
build_exe.bat
```

---

## 📝 Files

- `pyqt_timer.py` - Main PyQt5 application
- `main.py` - Tkinter version
- `build_exe.bat` - Build script
- `pyqt_timer.spec` - PyInstaller configuration
- `dist/StrawberryTimer.exe` - Generated executable

---

## ⚠️ Troubleshooting

### EXE won't start
- Run as Administrator
- Check Windows Defender
- Run from Command Prompt to see errors

### Widget stays open
✅ **Fixed** - Both windows now close together

### Multiple instances
```bash
kill_timers.bat
```

---

🍓 **Stay focused, stay productive!**
