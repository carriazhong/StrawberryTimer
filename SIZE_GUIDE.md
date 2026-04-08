# 🍓 Strawberry Timer Size Guide

## Current Configuration

**Default Size**: MEDIUM (40×30 pixels, 14px font) ✅ **RECOMMENDED**

---

## Size Comparison

| Size | Dimensions | Font | Readability | Use Case |
|------|-----------|------|-------------|----------|
| **TINY** | 20×15 px | 6px | ❌ Very poor | Minimal background indicator |
| **SMALL** | 30×22 px | 10px | ⚠️ Fair | Compact with decent visibility |
| **MEDIUM** ✓ | 40×30 px | 14px | ✅ Excellent | Best balance - easy to read |
| **LARGE** | 50×38 px | 18px | ✅ Excellent | Very prominent, highly visible |

---

## Why 20×15 (TINY) is Too Small

### ❌ Problems:
1. **6px font is barely readable**
   - On 1080p: Hard to distinguish "25" from "20"
   - On 4K: Nearly invisible
   - On laptop: Lost in screen clutter

2. **Difficult interaction**
   - 20×15 is only 300 square pixels
   - Hard to click precisely
   - Dragging requires careful cursor placement

3. **Easy to lose**
   - Can hide behind other windows
   - Blends into background
   - Might be overlooked when glancing at desktop

4. **Limited information**
   - Only shows minutes (e.g., "25")
   - No seconds detail
   - Can't see status changes clearly

---

## Recommended: MEDIUM (40×30) ✅

### ✅ Advantages:
- **14px font is crisp and readable** at any resolution
- **Easy to click and drag** - comfortable interaction
- **Visible but not intrusive** - floats nicely on desktop
- **Shows time clearly** - "25" is easily distinguishable
- **Still minimal** - only 1200 square pixels (4× TINY size, much better UX)

---

## How to Change Size

### In `pyqt_timer.py`, find the `init_strawberry` method:

```python
def init_strawberry(self):
    # Line ~144 in pyqt_timer.py

    # TINY (not recommended - too small)
    self.strawberry = StrawberryWidget(self.timer, width=20, height=30, font_size=6)

    # SMALL (better)
    self.strawberry = StrawberryWidget(self.timer, width=30, height=22, font_size=10)

    # MEDIUM (recommended - current default)
    self.strawberry = StrawberryWidget(self.timer, width=40, height=30, font_size=14)

    # LARGE (very visible)
    self.strawberry = StrawberryWidget(self.timer, width=50, height=38, font_size=18)
```

### For Tkinter version (`src/ui/desktop_widget.py`):

```python
# Lines 29-30 in desktop_widget.py
WIDTH = 20   # Change to 40 for MEDIUM
HEIGHT = 15  # Change to 30 for MEDIUM

# Then update the drawing code (line ~120)
# Change font size from 6 to 14 for MEDIUM
```

---

## Test Different Sizes

Run the size comparison tool:

```bash
cd C:\03_SDV\Output\StawberryTimer
python test_sizes.py
```

This will show you visual previews of all sizes side by side!

---

## Quick Recommendation

**Start with MEDIUM (40×30, 14px font)** - this gives you the best balance:
- ✅ Easy to read
- ✅ Easy to interact with
- ✅ Minimal desktop footprint
- ✅ Professional appearance

If MEDIUM feels too large, try SMALL (30×22, 10px font).

**Avoid TINY (20×15)** unless you specifically want a nearly invisible background indicator.
