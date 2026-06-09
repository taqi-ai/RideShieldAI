from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout, 
                             QSpinBox, QComboBox, QPushButton, QFrame, QMessageBox)
from src import database

class SettingsPage(QWidget):
    def __init__(self, alert_system, parent=None):
        super().__init__(parent)
        self.alert_system = alert_system
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("System Settings")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        form_layout = QFormLayout(form_frame)
        
        self.alert_delay_spin = QSpinBox()
        self.alert_delay_spin.setRange(1, 60)
        self.alert_delay_spin.setSuffix(" seconds")
        form_layout.addRow("Alert Delay:", self.alert_delay_spin)
        
        self.safety_mode_combo = QComboBox()
        self.safety_mode_combo.addItems(["Monitor Only", "Smart Lock Mode"])
        form_layout.addRow("Safety Mode:", self.safety_mode_combo)
        
        layout.addWidget(form_frame)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "primary-button")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()

    def load_settings(self):
        settings = database.get_settings()
        if settings:
            self.alert_delay_spin.setValue(settings.get('alert_delay', 5))
            self.safety_mode_combo.setCurrentText(settings.get('safety_mode', 'Monitor Only'))

    def save_settings(self):
        delay = self.alert_delay_spin.value()
        mode = self.safety_mode_combo.currentText()
        
        database.update_setting('alert_delay', delay)
        database.update_setting('safety_mode', mode)
        
        if self.alert_system:
            self.alert_system.load_settings()
            
        QMessageBox.information(self, "Settings Saved", "Settings have been successfully updated.")
