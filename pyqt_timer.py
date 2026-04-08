#!/usr/bin/env python3
"""Strawberry Timer - Tiny widget version."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.timer.engine import TimerEngine
from src.config import ConfigManager

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QPainter, QColor, QFont
except ImportError:
    print("PyQt5 not installed.")
    sys.exit(1)


class StrawberryWidget(QWidget):
    """Tiny strawberry widget - just a small red rectangle."""

    def __init__(self, timer_engine=None):
        super().__init__()
        self.timer_engine = timer_engine

        # Super tiny: 20x15 pixels
        self.resize(20, 15)

        # Frameless + always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setMouseTracking(True)
        self._drag_pos = None

    def paintEvent(self, event):
        """Draw tiny strawberry indicator."""
        p = QPainter(self)

        # Red strawberry background
        p.setBrush(QColor(220, 50, 50))
        p.setPen(QColor(180, 30, 30))
        p.drawRect(0, 0, 20, 15)

        # Small number
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Arial", 8))
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
        self.strawberry.move(screen.width() - 40, 50)

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
