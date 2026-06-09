import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer
from src.ai_engine import AIEngine
from src.alert_system import AlertSystem

from src.pages.dashboard import DashboardPage
from src.pages.live_monitor import LiveMonitorPage
from src.pages.analytics import AnalyticsPage
from src.pages.event_history import EventHistoryPage
from src.pages.settings_page import SettingsPage
from src.pages.system_diagnostics import SystemDiagnosticsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RideShield AI")
        self.setMinimumSize(1280, 720)
        
        # Core components
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "helmet_yolo26n.pt"))
        self.ai_engine = AIEngine(model_path)
        self.alert_system = AlertSystem()
        
        # Connect AI Engine to Alert System
        self.ai_engine.stats_update.connect(self.alert_system.process_stats)
        
        self.init_ui()
        self.apply_styles()
        
        # Start AI Engine
        self.ai_engine.start()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        title_label = QLabel("RideShield AI")
        title_label.setProperty("class", "h1")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addSpacing(30)
        
        self.nav_buttons = []
        pages_info = [
            ("Dashboard", 0),
            ("Live AI Monitor", 1),
            ("Analytics", 2),
            ("Event History", 3),
            ("Settings", 4),
            ("System Diagnostics", 5)
        ]
        
        self.stacked_widget = QStackedWidget()
        
        for name, index in pages_info:
            btn = QPushButton(name)
            btn.setProperty("class", "nav-button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)
        
        # Initialize pages
        self.dashboard_page = DashboardPage(main_window=self)
        self.live_monitor_page = LiveMonitorPage(ai_engine=self.ai_engine, alert_system=self.alert_system)
        self.analytics_page = AnalyticsPage()
        self.event_history_page = EventHistoryPage()
        self.settings_page = SettingsPage(alert_system=self.alert_system)
        self.system_diagnostics_page = SystemDiagnosticsPage(ai_engine=self.ai_engine)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.live_monitor_page)
        self.stacked_widget.addWidget(self.analytics_page)
        self.stacked_widget.addWidget(self.event_history_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.system_diagnostics_page)
            
        # Select first page
        self.switch_page(0)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def apply_styles(self):
        style_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "styles.qss"))
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load stylesheet: {e}")

    def closeEvent(self, event):
        self.ai_engine.stop()
        event.accept()
