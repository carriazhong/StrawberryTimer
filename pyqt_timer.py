#!/usr/bin/env python3
"""Strawberry Timer - Simple emoji-based widget."""

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
    """Super simple strawberry widget using SVG emoji style."""

    def __init__(self, timer_engine=None):
        super().__init__()
        self.timer_engine = timer_engine

        # Super tiny - just big enough for strawberry
        self.resize(40, 50)

        # Make window transparent and frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

        self.setMouseTracking(True)
        self._drag_pos = None

        # Create shape mask
        self._make_round_mask()

    def _make_round_mask(self):
        """Create circular/strawberry mask."""
        size = min(self.width(), self.height())
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)

        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.black)

        # Draw strawberry shape (top rounded, bottom pointy)
        path = QPainterPath()
        # Start at bottom
        path.moveTo(20, 48)
        # Left curve going up
        path.cubicTo(5, 40, 2, 25, 2, 15)
        # Top rounded
        path.cubicTo(2, 5, 38, 5, 38, 15)
        # Right curve going down
        path.cubicTo(38, 25, 35, 40, 20, 48)

        p.drawPath(path)
        p.end()

        mask = pixmap.createMaskFromColor(Qt.transparent)
        self.setMask(QRegion(mask))

    def paintEvent(self, event):
        """Draw strawberry."""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Strawberry red color
        red = QColor(220, 50, 50)

        # Draw strawberry body
        path = QPainterPath()
        path.moveTo(20, 46)
        path.cubicTo(5, 38, 2, 25, 2, 15)
        path.cubicTo(2, 5, 38, 5, 38, 15)
        path.cubicTo(38, 25, 35, 38, 20, 46)

        p.setBrush(QBrush(red))
        p.setPen(QPen(QColor(180, 30, 30), 1))
        p.drawPath(path)

        # Green leaves at top
        p.setBrush(QBrush(QColor(80, 160, 80)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(16, 3, 8, 6)  # center
        p.drawEllipse(8, 5, 6, 5)    # left
        p.drawEllipse(26, 5, 6, 5)   # right

        # Seeds
        p.setBrush(QBrush(QColor(255, 180, 0)))
        p.drawEllipse(10, 18, 3, 3)
        p.drawEllipse(27, 18, 3, 3)
        p.drawEllipse(18, 25, 3, 3)
        p.drawEllipse(12, 32, 3, 3)
        p.drawEllipse(25, 32, 3, 3)

        # Number
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Arial", 10, QFont.Bold))
        mins = "25"
        if self.timer_engine:
            mins = str(int(self.timer_engine.remaining.total_seconds() // 60))
        p.drawText(self.rect(), Qt.AlignCenter, mins)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
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

        title = QLabel("🍓 Strawberry Timer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #E53935;")
        layout.addWidget(title)

        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 42, QFont.Bold))
        self.timer_label.setStyleSheet("color: #E53935;")
        layout.addWidget(self.timer_label)

        self.status = QLabel("Ready to focus!")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)

        layout.addStretch()

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
        self.strawberry.move(screen.width() - 70, 50)

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
