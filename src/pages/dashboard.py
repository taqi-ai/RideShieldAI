from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt

class DashboardPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window # To allow navigation to other pages
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Dashboard Overview")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Summary Cards
        cards_layout = QHBoxLayout()
        
        # System Status Card
        status_card = QFrame()
        status_card.setProperty("class", "card")
        status_layout = QVBoxLayout(status_card)
        status_layout.addWidget(QLabel("System Status"))
        status_val = QLabel("Active")
        status_val.setProperty("class", "h3")
        status_val.setStyleSheet("color: #4CAF50;")
        status_layout.addWidget(status_val)
        cards_layout.addWidget(status_card)
        
        # Total Events Card
        events_card = QFrame()
        events_card.setProperty("class", "card")
        events_layout = QVBoxLayout(events_card)
        events_layout.addWidget(QLabel("Total Events Today"))
        events_val = QLabel("0") # Could be fetched from database
        events_val.setProperty("class", "h3")
        events_layout.addWidget(events_val)
        cards_layout.addWidget(events_card)
        
        layout.addLayout(cards_layout)
        
        # Quick Actions
        actions_layout = QHBoxLayout()
        jump_to_monitor_btn = QPushButton("Open Live Monitor")
        jump_to_monitor_btn.setMinimumHeight(50)
        jump_to_monitor_btn.setProperty("class", "primary-button")
        jump_to_monitor_btn.clicked.connect(lambda: self.main_window.switch_page(1)) # Index 1 is Live Monitor
        
        actions_layout.addWidget(jump_to_monitor_btn)
        layout.addLayout(actions_layout)
        
        layout.addStretch()
