import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame)
# QShortcut and QKeySequence are imported where used (they live in QtGui in Qt 6)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage
from src.ai_engine import DetectionManager
from src.alert_system import AlertSystem

from src.pages.dashboard import DashboardPage
from src.pages.live_monitor import LiveMonitorPage
from src.pages.analytics import AnalyticsPage
from src.pages.event_history import EventHistoryPage
from src.pages.settings_page import SettingsPage
from src.pages.system_diagnostics import SystemDiagnosticsPage
from src import database
from src.paths import resource

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RideShield AI")
        # A minimum size larger than the screen was the cause of the window coming back off-screen after
        # leaving full screen. Keep it small enough for any laptop, and restore to a sensible size.
        self.setMinimumSize(1100, 680)
        self.resize(1500, 900)
        icon_path = resource("assets", "brand", "icon-512.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        self.showFullScreen()  # full screen for the TFT dashboard feel; Esc or F11 leaves it
        
        # Core components
        settings = database.get_settings()
        model_filename = settings.get('model_name', 'yolo11m.pt')
        model_path = os.path.abspath(resource("models", model_filename))
        if not os.path.exists(model_path):
            from PyQt6.QtWidgets import QMessageBox, QFileDialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Model Not Found")
            msg.setText("The default YOLO11m model could not be found.\nPlease select a valid YOLO model file (.pt).")
            msg.exec()
            
            model_path, _ = QFileDialog.getOpenFileName(self, "Select YOLO Model", "", "PyTorch Models (*.pt)")
            if not model_path:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Fatal Error")
                msg.setText("No model selected. Application will now exit.")
                msg.exec()
                import sys
                sys.exit()

        self.ai_engine = DetectionManager(model_path)
        self.alert_system = AlertSystem(main_window=self)
        self.latest_image = None
        
        # Connect AI Engine to Alert System
        self.ai_engine.stats_update.connect(self.alert_system.process_stats)
        self.ai_engine.image_update.connect(self.cache_image)
        
        self.init_ui()
        self.apply_styles()

        # Application-wide shortcuts so a single press works whichever control has focus.
        from PyQt6.QtGui import QShortcut, QKeySequence
        for key in ("Esc", "F11"):
            sc = QShortcut(QKeySequence(key), self)
            sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
            sc.activated.connect(self.toggle_fullscreen)
        
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
        self.analytics_page = AnalyticsPage(ai_engine=self.ai_engine, alert_system=self.alert_system)
        self.event_history_page = EventHistoryPage()
        self.settings_page = SettingsPage(alert_system=self.alert_system)
        self.system_diagnostics_page = SystemDiagnosticsPage(ai_engine=self.ai_engine)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.live_monitor_page)
        self.stacked_widget.addWidget(self.analytics_page)
        self.stacked_widget.addWidget(self.event_history_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.system_diagnostics_page)

        # Connect AI Engine to pages that need live data
        self.ai_engine.stats_update.connect(self.dashboard_page.update_live_stats)
        self.ai_engine.stats_update.connect(self.system_diagnostics_page.update_ai_stats)

        # Bottom Navigation Bar
        self.bottom_nav = QFrame()
        self.bottom_nav.setObjectName("bottom-nav")
        self.bottom_nav.setFixedHeight(76)
        nav_layout = QHBoxLayout(self.bottom_nav)
        nav_layout.setContentsMargins(40, 0, 40, 0)
        nav_layout.setSpacing(10)
        
        self.nav_buttons = []
        pages_info = [
            ("DASHBOARD", 0),
            ("CAMERA", 1),
            ("ANALYTICS", 2),
            ("HISTORY", 3),
            ("SETTINGS", 4),
            ("DIAGNOSTICS", 5)
        ]
        
        nav_layout.addStretch()
        for name, index in pages_info:
            btn = QPushButton(name)
            btn.setProperty("class", "nav-button")
            btn.setCheckable(True)
            btn.setFixedWidth(190 if name == "DIAGNOSTICS" else 160)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()
        hint = QLabel("Esc or F11: full screen")
        hint.setProperty("class", "faint")
        nav_layout.addWidget(hint)
        
        main_layout.addWidget(self.bottom_nav)
            
        # Select first page
        self.switch_page(0)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def set_alert_mode(self, is_alert):
        if is_alert:
            self.bottom_nav.setStyleSheet("#bottom-nav { border-top: 2px solid #FF6674; }")
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
        style_path = os.path.abspath(resource("assets", "styles.qss"))
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load stylesheet: {e}")

    def closeEvent(self, event):
        self.ai_engine.stop()
        event.accept()

    def toggle_fullscreen(self):
        """One key press switches between full screen and a maximised window (never an off-screen one)."""
        if self.isFullScreen():
            self.showNormal()
            self.showMaximized()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_W, Qt.Key.Key_Up):
            if hasattr(self, 'dashboard_page'):
                self.dashboard_page.manual_accelerate()
        elif event.key() in (Qt.Key.Key_S, Qt.Key.Key_Down):
            if hasattr(self, 'dashboard_page'):
                self.dashboard_page.manual_brake()
        elif event.key() == Qt.Key.Key_Space:
            if hasattr(self, 'dashboard_page'):
                self.dashboard_page.manual_idle()
        else:
            super().keyPressEvent(event)
            
    @pyqtSlot(QImage)
    def cache_image(self, qimg):
        self.latest_image = qimg


