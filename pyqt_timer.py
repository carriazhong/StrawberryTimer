#!/usr/bin/env python3
"""Strawberry Timer - PyQt5 Version.

A simple, elegant desktop Pomodoro timer with:
- True strawberry-shaped widget
- Smaller size (half height)
- Real transparency
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.timer.engine import TimerEngine
from src.config import ConfigManager

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QPixmap, QRegion
except ImportError:
    print("PyQt5 not installed.")
    sys.exit(1)


class StrawberryWidget(QWidget):
    """Tiny strawberry-shaped widget."""

    def __init__(self, timer_engine=None):
        super().__init__()
        self.timer_engine = timer_engine

        # Smaller size - half height
        self.resize(50, 65)

        # Frameless + always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMouseTracking(True)
        self._drag_pos = None

        # Create strawberry shape
        self._create_strawberry_shape()

    def _create_strawberry_shape(self):
        """Create strawberry-shaped region."""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)

        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.black)

        # Strawberry body
        path = QPainterPath()
        path.moveTo(25, 62)  # Bottom tip
        path.cubicTo(25, 62, 3, 35, 3, 22)  # Left side
        path.cubicTo(3, 8, 47, 8, 47, 22)  # Top curve
        path.cubicTo(47, 35, 25, 62, 25, 62)  # Right side
        p.drawPath(path)
        p.end()

        # Apply as mask
        mask = pixmap.createMaskFromColor(Qt.transparent)
        self.setMask(QRegion(mask))

    def paintEvent(self, event):
        """Draw strawberry."""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Color based on state
        if self.timer_engine:
            if self.timer_engine.is_running:
                color = QColor(220, 50, 50)  # Brighter red when running
                glow = QColor(100, 200, 100, 60)  # Green glow
            elif self.timer_engine.is_paused:
                color = QColor(220, 50, 50)
                glow = QColor(255, 200, 50, 60)  # Yellow glow
            else:
                color = QColor(220, 50, 50)
                glow = None
        else:
            color = QColor(220, 50, 50)
            glow = None

        # Draw glow
        if glow:
            p.setBrush(QBrush(glow))
            p.setPen(Qt.NoPen)
            glow_path = QPainterPath()
            glow_path.moveTo(25, 65)
            glow_path.cubicTo(25, 65, 0, 35, 0, 20)
            glow_path.cubicTo(0, 5, 50, 5, 50, 20)
            glow_path.cubicTo(50, 35, 25, 65, 25, 65)
            p.drawPath(glow_path)

        # Draw body
        p.setBrush(QBrush(color))
        p.setPen(QPen(QColor(180, 30, 30), 1.5))
        body = QPainterPath()
        body.moveTo(25, 62)
        body.cubicTo(25, 62, 3, 35, 3, 22)
        body.cubicTo(3, 8, 47, 8, 47, 22)
        body.cubicTo(47, 35, 25, 62, 25, 62)
        p.drawPath(body)

        # Seeds
        p.setBrush(QBrush(QColor(255, 180, 0)))
        p.setPen(Qt.NoPen)
        for x, y in [(15, 25), (35, 25), (12, 38), (25, 32), (38, 38), (20, 50), (30, 50)]:
            p.drawEllipse(x, y, 3, 3)

        # Leaves
        p.setBrush(QBrush(QColor(80, 160, 80)))
        p.setPen(Qt.NoPen)
        # Center leaf
        p.drawEllipse(22, 5, 6, 8)
        # Left leaf
        p.drawEllipse(12, 8, 7, 6)
        # Right leaf
        p.drawEllipse(31, 8, 7, 6)

        # Timer text
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Arial", 12, QFont.Bold))
        mins = "25"
        if self.timer_engine:
            mins = str(int(self.timer_engine.remaining.total_seconds() // 60))
        p.drawText(self.rect(), Qt.AlignCenter, mins)

        # Close button (tiny white dot)
        p.setBrush(QBrush(QColor(255, 255, 255, 200)))
        p.drawEllipse(42, 2, 6, 6)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            if 42 <= ev.x() <= 48 and 2 <= ev.y() <= 8:
                self.hide()
            else:
                self._drag_pos = ev.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev):
        if self._drag_pos and ev.buttons() == Qt.LeftButton:
            self.move(ev.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, ev):
        self._drag_pos = None

    def update_timer(self):
        self.update()


class MainWindow(QMainWindow):
    def __init__(self, timer):
        super().__init__()
        self.timer = timer
        self.init_ui()
        self.init_strawberry()

    def init_ui(self):
        self.setWindowTitle("🍓 Strawberry Timer")
        self.setFixedSize(320, 380)

        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background-color: #FFF5F7;")

        layout = QVBoxLayout(central)
        layout.setSpacing(12)

        # Title
        title = QLabel("🍓 Strawberry Timer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #E53935;")
        layout.addWidget(title)

        # Timer
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 42, QFont.Bold))
        self.timer_label.setStyleSheet("color: #E53935;")
        layout.addWidget(self.timer_label)

        # Status
        self.status = QLabel("Ready to focus!")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)

        layout.addStretch()

        # Buttons
        btn_style = """
            QPushButton {
                background-color: #E53935; color: white; font-size: 13px;
                font-weight: bold; padding: 8px 18px; border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #C62828; }
            QPushButton:disabled { background-color: #EF9A9A; }
        """

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setStyleSheet(btn_style)
        self.start_btn.clicked.connect(self.on_start)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setStyleSheet(btn_style)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.on_pause)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet(btn_style)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

    def init_strawberry(self):
        self.strawberry = StrawberryWidget(self.timer)
        self.strawberry.show()
        screen = QApplication.desktop().screenGeometry()
        self.strawberry.move(screen.width() - 80, 50)

    def update_timer(self):
        self.timer_label.setText(self.timer.remaining_time_str)
        self.strawberry.update_timer()

        if self.timer.is_running:
            self.status.setText("🍓 Focus time!")
        elif self.timer.is_paused:
            self.status.setText("⏸️ Paused")
        else:
            self.status.setText("Ready to focus!")

    def on_start(self):
        self.timer.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.update_timer()

    def on_pause(self):
        if self.timer.is_running:
            self.timer.pause()
            self.pause_btn.setText("▶ Resume")
        else:
            self.timer.resume()
            self.pause_btn.setText("⏸ Pause")
        self.update_timer()

    def on_stop(self):
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.stop_btn.setEnabled(False)
        self.update_timer()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = ConfigManager.load()
    timer = TimerEngine(config.all)

    window = MainWindow(timer)
    window.show()

    # Update timer
    update_timer = QTimer()
    update_timer.timeout.connect(window.update_timer)
    update_timer.start(100)

    timer.on_complete(lambda: (
        window.status.setText("🎉 Break time!"),
        window.start_btn.setEnabled(True),
        window.pause_btn.setEnabled(False),
        window.stop_btn.setEnabled(False)
    ))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
