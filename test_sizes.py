#!/usr/bin/env python3
"""Test different timer sizes to find the best one for your needs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import size presets
from src.ui.timer_sizes import TimerSize, get_config


class SizeTestWidget(QWidget):
    """Test widget showing different timer sizes."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🍓 Timer Size Comparison")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("🍓 Choose Your Timer Size")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Compare sizes and choose what works best for you")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)

        # Size comparison
        sizes_layout = QHBoxLayout()
        sizes_layout.setSpacing(30)

        for size_enum in [TimerSize.TINY, TimerSize.SMALL, TimerSize.MEDIUM, TimerSize.LARGE]:
            config = get_config(size_enum)

            size_widget = QWidget()
            size_layout = QVBoxLayout(size_widget)
            size_layout.setAlignment(Qt.AlignCenter)

            # Size label
            size_label = QLabel(f"{size_enum.value.upper()}\n{config.width}×{config.height}px\nFont: {config.font_size}px")
            size_label.setAlignment(Qt.AlignCenter)
            size_label.setFont(QFont("Arial", 10))
            size_layout.addWidget(size_label)

            # Preview box (simulated timer)
            from PyQt5.QtWidgets import QFrame
            preview = QFrame()
            preview.setFixedSize(config.width, config.height)
            preview.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(220, 50, 50, 0.9);
                    border-radius: {config.corner_radius}px;
                }}
            """)
            size_layout.addWidget(preview, alignment=Qt.AlignCenter)

            # Description
            desc_label = QLabel(config.description)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setFont(QFont("Arial", 8))
            desc_label.setMaximumWidth(120)
            size_layout.addWidget(desc_label)

            sizes_layout.addWidget(size_widget)

        layout.addLayout(sizes_layout)

        # Recommendation
        layout.addStretch()

        recommendation = QLabel("✓ Recommended: MEDIUM (40×30px, 14px font)")
        recommendation.setAlignment(Qt.AlignCenter)
        recommendation.setFont(QFont("Arial", 12, QFont.Bold))
        recommendation.setStyleSheet("color: #4CAF50; padding: 10px;")
        layout.addWidget(recommendation)

        # Note
        note = QLabel("TINY (20×15) is very small - may be hard to read on high-DPI displays")
        note.setAlignment(Qt.AlignCenter)
        note.setStyleSheet("color: #E53935; padding: 5px;")
        layout.addWidget(note)

        layout.addStretch()


def main():
    app = QApplication(sys.argv)
    window = SizeTestWidget()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
