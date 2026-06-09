from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from src import database

class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Analytics & Reports")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        chart_frame = QFrame()
        chart_frame.setProperty("class", "card")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.addWidget(QLabel("Event Distribution (Coming Soon)"))
        
        placeholder = QLabel("Visual charts will be displayed here based on database events.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: gray;")
        chart_layout.addWidget(placeholder)
        
        layout.addWidget(chart_frame)
        layout.addStretch()
