#!/usr/bin/env python3
"""Strawberry Timer - PyQt5 Version.

A simple, elegant desktop Pomodoro timer with:
- Real transparency support
- Custom strawberry-shaped widget
- Proper timer countdown
"""

import sys
from pathlib import Path
from datetime import timedelta, datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.timer.engine import TimerEngine
from src.config import ConfigManager

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                                  QVBoxLayout, QHBoxLayout, QWidget, QSystemTrayIcon,
                                  QMenu, QAction, QSlider)
    from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QRect
    from PyQt5.QtGui import (QIcon, QPixmap, QPainter, QColor, QPen, QBrush,
                             QFont, QPainterPath, QRegion)
except ImportError:
    print("PyQt5 not installed. Please install it with: pip install PyQt5")
    sys.exit(1)


class StrawberryWidget(QWidget):
    """Floating strawberry widget with TRUE strawberry SHAPE (not just drawing)."""

    def __init__(self, timer_engine=None):
        super().__init__()
        self.timer_engine = timer_engine

        # Widget size - larger to fit strawberry shape
        self.setFixedSize(80, 100)

        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        # Transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Mouse tracking for dragging
        self.setMouseTracking(True)
        self._drag_position = None

        # Create the strawberry shape mask
        self._create_shape_mask()

        # Update timer every second
        self.update_timer()

    def _create_shape_mask(self):
        """Create a mask that gives the widget a strawberry shape."""
        # Create an empty pixmap for the mask
        mask_pixmap = QPixmap(self.size())
        mask_pixmap.fill(Qt.transparent)

        # Draw the strawberry shape on the mask
        mask_painter = QPainter(mask_pixmap)
        mask_painter.setRenderHint(QPainter.Antialiasing)
        mask_painter.setPen(Qt.NoPen)
        mask_painter.setBrush(Qt.black)

        # Draw strawberry body (heart shape with rounded bottom)
        path = QPainterPath()
        path.moveTo(40, 95)  # Bottom tip
        path.cubicTo(40, 95, 5, 55, 5, 35)  # Left curve
        path.cubicTo(5, 15, 75, 15, 75, 35)  # Top curve
        path.cubicTo(75, 55, 40, 95, 40, 95)  # Right curve
        path.closeSubpath()

        mask_painter.drawPath(path)
        mask_painter.end()

        # Apply the mask to the widget
        mask = mask_pixmap.createMaskFromColor(Qt.transparent)
        self.setMask(QRegion(mask))

    def paintEvent(self, event):
        """Draw the strawberry widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get current timer state color
        if self.timer_engine:
            if self.timer_engine.is_running:
                color = QColor(229, 57, 53)  # Red
                glow_color = QColor(76, 175, 80, 80)  # Green glow
            elif self.timer_engine.is_paused:
                color = QColor(229, 57, 53)  # Red
                glow_color = QColor(255, 193, 7, 80)  # Yellow glow
            else:
                color = QColor(229, 57, 53)  # Red
                glow_color = None
        else:
            color = QColor(229, 57, 53)
            glow_color = None

        # Draw glow effect when running/paused
        if glow_color:
            glow_path = QPainterPath()
            glow_path.moveTo(40, 100)
            glow_path.cubicTo(40, 100, 0, 55, 0, 35)
            glow_path.cubicTo(0, 10, 80, 10, 80, 35)
            glow_path.cubicTo(80, 55, 40, 100, 40, 100)
            glow_path.closeSubpath()
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.NoPen)
            painter.drawPath(glow_path)

        # Draw strawberry body
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(183, 28, 28), 2))

        body_path = QPainterPath()
        body_path.moveTo(40, 95)  # Bottom tip
        body_path.cubicTo(40, 95, 5, 55, 5, 35)  # Left curve
        body_path.cubicTo(5, 15, 75, 15, 75, 35)  # Top curve
        body_path.cubicTo(75, 55, 40, 95, 40, 95)  # Right curve
        body_path.closeSubpath()
        painter.drawPath(body_path)

        # Draw seeds (yellow-orange dots)
        painter.setBrush(QBrush(QColor(255, 152, 0)))  # Orange-yellow
        painter.setPen(Qt.NoPen)
        seed_positions = [
            (25, 40), (55, 40),  # Top row
            (20, 55), (40, 50), (60, 55),  # Middle row
            (30, 70), (50, 70),  # Bottom row
            (35, 85), (45, 85),  # Near bottom
        ]
        for x, y in seed_positions:
            painter.drawEllipse(x, y, 4, 4)

        # Draw leaves (green calyx) at top
        painter.setBrush(QBrush(QColor(76, 175, 80)))  # Green
        painter.setPen(QPen(QColor(56, 142, 60), 1))

        # Center leaf
        leaf_path = QPainterPath()
        leaf_path.moveTo(40, 18)
        leaf_path.cubicTo(35, 5, 45, 5, 40, 18)
        painter.drawPath(leaf_path)

        # Left leaf
        left_leaf = QPainterPath()
        left_leaf.moveTo(38, 20)
        left_leaf.cubicTo(20, 10, 10, 25, 30, 28)
        painter.drawPath(left_leaf)

        # Right leaf
        right_leaf = QPainterPath()
        right_leaf.moveTo(42, 20)
        right_leaf.cubicTo(60, 10, 70, 25, 50, 28)
        painter.drawPath(right_leaf)

        # Draw small stems
        painter.setPen(QPen(QColor(76, 175, 80), 2))
        painter.drawLine(40, 18, 40, 25)
        painter.drawLine(32, 22, 38, 26)
        painter.drawLine(48, 22, 42, 26)

        # Draw timer text
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 18, QFont.Bold))

        if self.timer_engine:
            remaining = self.timer_engine.remaining
            minutes = int(remaining.total_seconds() // 60)
            text = str(minutes)
        else:
            text = "25"

        painter.drawText(self.rect(), Qt.AlignCenter, text)

        # Draw close button (small X in corner) - white circle
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(68, 2, 10, 10)
        painter.setPen(QPen(QColor(100, 100, 100), 1.5))
        painter.drawLine(70, 4, 76, 10)
        painter.drawLine(76, 4, 70, 10)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging and close."""
        if event.button() == Qt.LeftButton:
            # Check if close button clicked
            if 68 <= event.x() <= 78 and 2 <= event.y() <= 12:
                self.hide()
            else:
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self._drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self._drag_position = None

    def update_timer(self):
        """Update the timer display."""
        self.update()  # Trigger repaint


class MainWindow(QMainWindow):
    """Main timer window."""

    def __init__(self, timer_engine):
        super().__init__()
        self.timer_engine = timer_engine
        self.init_ui()
        self.init_strawberry_widget()

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("🍓 Strawberry Timer")
        self.setFixedSize(350, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        layout = QVBoxLayout(central)
        layout.setSpacing(15)

        # Title
        title = QLabel("🍓 Strawberry Timer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #E53935;")
        layout.addWidget(title)

        # Timer display
        self.timer_display = QLabel("25:00")
        self.timer_display.setAlignment(Qt.AlignCenter)
        self.timer_display.setFont(QFont("Arial", 48, QFont.Bold))
        self.timer_display.setStyleSheet("color: #E53935;")
        layout.addWidget(self.timer_display)

        # Progress bar (simple label for now)
        self.progress_label = QLabel("Ready to focus!")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self.on_start)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #EF9A9A;
            }
        """)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.on_pause)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet(self.start_btn.styleSheet())

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(self.start_btn.styleSheet())

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # Add stretch to push everything up
        layout.addStretch()

        # Background color
        central.setStyleSheet("background-color: #FFF5F7;")

    def init_strawberry_widget(self):
        """Initialize the floating strawberry widget."""
        self.strawberry = StrawberryWidget(self.timer_engine)
        self.strawberry.show()

        # Position in top-right
        screen = QApplication.desktop().screenGeometry()
        self.strawberry.move(screen.width() - 120, 50)

    # Timer update method
    def update_timer(self):
        """Update timer display."""
        remaining = self.timer_engine.remaining_time_str
        self.timer_display.setText(remaining)

        # Update strawberry widget
        self.strawberry.update_timer()

        # Update progress text
        if self.timer_engine.is_running:
            self.progress_label.setText("🍓 Focus time! Stay productive!")
        elif self.timer_engine.is_paused:
            self.progress_label.setText("⏸️ Timer paused.")
        else:
            self.progress_label.setText("Ready to focus!")

    # Button handlers
    def on_start(self):
        """Start the timer."""
        self.timer_engine.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.update_timer()

    def on_pause(self):
        """Pause/resume the timer."""
        if self.timer_engine.is_running:
            self.timer_engine.pause()
            self.pause_btn.setText("▶ Resume")
        else:
            self.timer_engine.resume()
            self.pause_btn.setText("⏸ Pause")
        self.update_timer()

    def on_stop(self):
        """Stop the timer."""
        self.timer_engine.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.stop_btn.setEnabled(False)
        self.update_timer()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit when strawberry closes

    # Load configuration
    config_manager = ConfigManager.load()

    # Create timer
    timer = TimerEngine(config_manager.all)

    # Create main window
    window = MainWindow(timer)
    window.show()

    # Set up update timer (refresh every 100ms)
    update_timer = QTimer()
    update_timer.timeout.connect(window.update_timer)
    update_timer.start(100)

    # Connect timer completion
    def on_complete():
        window.progress_label.setText("🎉 Time for a break!")
        window.start_btn.setEnabled(True)
        window.pause_btn.setEnabled(False)
        window.stop_btn.setEnabled(False)

    timer.on_complete(on_complete)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
