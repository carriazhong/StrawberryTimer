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
    from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal
    from PyQt5.QtGui import (QIcon, QPixmap, QPainter, QColor, QPen, QBrush,
                             QFont, QPainterPath)
except ImportError:
    print("PyQt5 not installed. Please install it with: pip install PyQt5")
    sys.exit(1)


class StrawberryWidget(QWidget):
    """Floating strawberry widget with transparency."""

    def __init__(self, timer_engine=None):
        super().__init__()
        self.timer_engine = timer_engine

        # Widget setup
        self.setFixedSize(60, 80)

        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        # Transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Mouse tracking for dragging
        self.setMouseTracking(True)
        self._drag_position = None

        # Update timer every second
        self.update_timer()

    def paintEvent(self, event):
        """Draw the strawberry widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get current timer state color
        if self.timer_engine:
            if self.timer_engine.is_running:
                color = QColor(76, 175, 80)  # Green
            elif self.timer_engine.is_paused:
                color = QColor(255, 193, 7)  # Yellow
            else:
                color = QColor(229, 57, 53)  # Red
        else:
            color = QColor(229, 57, 53)  # Red

        # Draw strawberry body (heart shape)
        body_color = color
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(183, 28, 28), 2))

        # Draw heart-shaped strawberry using bezier curves
        path = QPainterPath()
        path.moveTo(30, 75)  # Bottom tip
        path.cubicTo(30, 75, 5, 45, 5, 35)  # Left side to top
        path.cubicTo(5, 15, 55, 15, 55, 35)  # Top curve
        path.cubicTo(55, 45, 30, 75, 30, 75)  # Right side to bottom
        painter.drawPath(path)

        # Draw seeds
        painter.setBrush(QBrush(QColor(255, 235, 59)))
        painter.setPen(Qt.NoPen)
        seed_positions = [(20, 35), (40, 35), (25, 50), (35, 50), (30, 60)]
        for x, y in seed_positions:
            painter.drawEllipse(x, y, 3, 3)

        # Draw leaves (green calyx)
        painter.setBrush(QBrush(QColor(76, 175, 80)))
        painter.setPen(QPen(QColor(56, 142, 60), 1))

        # Center leaf
        painter.drawPie(25, 10, 10, 15, 0, 180)

        # Left leaf
        painter.drawPie(15, 15, 12, 12, -45, 90)

        # Right leaf
        painter.drawPie(33, 15, 12, 12, -45, 90)

        # Draw timer text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 16, QFont.Bold))

        if self.timer_engine:
            remaining = self.timer_engine.remaining
            minutes = int(remaining.total_seconds() // 60)
            text = str(minutes)
        else:
            text = "25"

        painter.drawText(self.rect(), Qt.AlignCenter, text)

        # Draw close button
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawRoundedRect(50, 2, 10, 10, 2, 2)
        painter.drawLine(52, 4, 58, 10)
        painter.drawLine(58, 4, 52, 10)

    def update_timer(self):
        """Update the timer display."""
        self.update()  # Trigger repaint

    def mousePressEvent(self, event):
        """Handle mouse press for dragging and close."""
        if event.button() == Qt.LeftButton:
            # Check if close button clicked
            if 50 <= event.x() <= 60 and 2 <= event.y() <= 12:
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
        self.strawberry.move(screen.width() - 100, 50)

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
