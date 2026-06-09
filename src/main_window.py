import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
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
        self.setMinimumSize(1920, 1080)
        self.showFullScreen() # Fullscreen for TFT dashboard feel
        
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
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, stretch=1)
        
        # Initialize pages
        self.dashboard_page = DashboardPage(self.ai_engine, self.alert_system, main_window=self)
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

        # Bottom Navigation Bar
        self.bottom_nav = QFrame()
        self.bottom_nav.setObjectName("bottom-nav")
        self.bottom_nav.setFixedHeight(80)
        nav_layout = QHBoxLayout(self.bottom_nav)
        nav_layout.setContentsMargins(50, 0, 50, 0)
        nav_layout.setSpacing(20)
        
        self.nav_buttons = []
        pages_info = [
            ("Dashboard", 0),
            ("AI Monitor", 1),
            ("Analytics", 2),
            ("History", 3),
            ("Settings", 4),
            ("Diagnostics", 5)
        ]
        
        nav_layout.addStretch()
        for name, index in pages_info:
            btn = QPushButton(name)
            btn.setProperty("class", "nav-button")
            btn.setCheckable(True)
            btn.setFixedWidth(150)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        nav_layout.addStretch()
        
        main_layout.addWidget(self.bottom_nav)
            
        # Select first page
        self.switch_page(0)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def set_alert_mode(self, is_alert):
        if is_alert:
            self.bottom_nav.setStyleSheet("border-top: 1px solid rgba(255, 51, 51, 0.5);")
            for btn in self.nav_buttons:
                btn.setProperty("alert_mode", "true")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        else:
            self.bottom_nav.setStyleSheet("")
            for btn in self.nav_buttons:
                btn.setProperty("alert_mode", "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)

