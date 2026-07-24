import sys
from PyQt6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter

class RideShieldSplash(QSplashScreen):
    def __init__(self):
        super().__init__()
        
        pixmap = QPixmap(800, 450)
        pixmap.fill(QColor(5, 7, 10))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(0, 229, 255))
        painter.drawRect(0, 0, 799, 449)
        painter.end()
        
        self.setPixmap(pixmap)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("RideShield AI")
        title.setStyleSheet("color: white; font-size: 56px; font-weight: bold; font-family: 'Segoe UI';")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Ride Smarter. Ride Safer.")
        subtitle.setStyleSheet("color: #00E5FF; font-size: 24px; font-family: 'Segoe UI';")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        
        self.status_label = QLabel("Initializing System...")
        self.status_label.setStyleSheet("color: #888888; font-size: 14px; font-family: 'Segoe UI';")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #1A1A24; border: none; }
            QProgressBar::chunk { background-color: #00E5FF; }
        """)
        layout.addWidget(self.progress_bar)

    def set_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.status_label.setText(text)
        self.repaint()
