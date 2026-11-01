import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFormLayout, QSpinBox, QComboBox, QPushButton, QFrame, QMessageBox, QStackedWidget, QListWidget)
from PyQt6.QtCore import Qt
from src import database, theme
from src.ui_kit import make_card, page_header

class SettingsPage(QWidget):
    def __init__(self, alert_system, parent=None):
        super().__init__(parent)
        self.alert_system = alert_system
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Sidebar ---
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f"background-color: {theme.DEVICE}; border-right: 1px solid {theme.LINE};")
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(16, 28, 16, 16)
        side_lay.setSpacing(15)
        
        title = QLabel("Settings")
        title.setStyleSheet(theme.css_display(34, theme.TEXT))
        side_lay.addWidget(title)
        side_lay.addSpacing(8)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; outline: none; }}
            QListWidget::item {{ color: {theme.MUTED}; font-size: 15px; font-weight: 600; padding: 12px 14px; border-radius: 10px; margin-bottom: 2px; }}
            QListWidget::item:selected {{ background-color: rgba(183, 156, 255, 0.14); color: {theme.ACCENT}; }}
            QListWidget::item:hover {{ color: {theme.TEXT}; }}
        """)

        categories = ["Detection", "Camera", "Safety", "Performance", "Interface", "System"]
        self.list_widget.addItems(categories)
        self.list_widget.setCurrentRow(0)
        side_lay.addWidget(self.list_widget)
        
        main_layout.addWidget(sidebar)
        
        # --- Right Content Area ---
        content_area = QWidget()
        content_lay = QVBoxLayout(content_area)
        content_lay.setContentsMargins(28, 18, 28, 18)
        content_lay.setSpacing(14)
        content_lay.addWidget(page_header("Preferences", "Detection, camera, safety and interface options. Saved on this computer."))
        
        self.stack = QStackedWidget()
        
        # 1. Detection
        det_page = QWidget()
        det_lay = self.form_card(det_page, 'det')
        self.conf_combo = QComboBox()
        self.conf_combo.addItems(["Low (0.30)", "Medium (0.50)", "High (0.75)", "Strict (0.90)"])
        self.model_combo = QComboBox()
        
        from src.paths import resource
        models_dir = os.path.abspath(resource("models"))
        if os.path.exists(models_dir):
            models = [f for f in os.listdir(models_dir) if f.endswith(".pt")]
        else:
            models = ["yolo11m.pt", "best.pt"]
        
        self.model_combo.addItems(models)
        det_lay.addRow(self.create_lbl("Confidence Threshold:"), self.conf_combo)
        det_lay.addRow(self.create_lbl("Model Selection:"), self.model_combo)
        self.stack.addWidget(det_page)
        
        # 2. Camera
        cam_page = QWidget()
        cam_lay = self.form_card(cam_page, 'cam')
        self.cam_id_spin = QSpinBox()
        self.cam_id_spin.setRange(0, 10)
        self.res_combo = QComboBox()
        self.res_combo.addItems(["640x480", "1280x720", "1920x1080"])
        cam_lay.addRow(self.create_lbl("Camera ID:"), self.cam_id_spin)
        cam_lay.addRow(self.create_lbl("Resolution:"), self.res_combo)
        self.stack.addWidget(cam_page)
        
        # 3. Safety
        saf_page = QWidget()
        saf_lay = self.form_card(saf_page, 'saf')
        self.safety_mode_combo = QComboBox()
        self.safety_mode_combo.addItems(["Monitor Only", "Smart Lock Mode", "Strict Enforcement"])
        self.alert_delay_spin = QSpinBox()
        self.alert_delay_spin.setRange(1, 60)
        self.alert_delay_spin.setSuffix(" sec")
        saf_lay.addRow(self.create_lbl("Safety Mode:"), self.safety_mode_combo)
        saf_lay.addRow(self.create_lbl("Alert Delay:"), self.alert_delay_spin)
        self.stack.addWidget(saf_page)
        
        # 4. Performance
        perf_page = QWidget()
        perf_lay = self.form_card(perf_page, 'perf')
        self.gpu_accel_combo = QComboBox()
        self.gpu_accel_combo.addItems(["Enabled (TensorRT)", "Enabled (CUDA)", "Disabled (CPU Only)"])
        self.max_fps_spin = QSpinBox()
        self.max_fps_spin.setRange(10, 120)
        self.max_fps_spin.setValue(30)
        perf_lay.addRow(self.create_lbl("GPU Acceleration:"), self.gpu_accel_combo)
        perf_lay.addRow(self.create_lbl("Max Inference FPS:"), self.max_fps_spin)
        self.stack.addWidget(perf_page)
        
        # 5. Interface
        int_page = QWidget()
        int_lay = self.form_card(int_page, 'int')
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Futuristic", "High Contrast", "Day Mode"])
        self.anim_speed_combo = QComboBox()
        self.anim_speed_combo.addItems(["Buttery Smooth (120Hz)", "Standard (60Hz)", "Battery Saver (30Hz)"])
        int_lay.addRow(self.create_lbl("Dashboard Theme:"), self.theme_combo)
        int_lay.addRow(self.create_lbl("Animation Quality:"), self.anim_speed_combo)
        self.stack.addWidget(int_page)
        
        # 6. System
        sys_page = QWidget()
        sys_lay = self.form_card(sys_page, 'sys')
        self.telemetry_combo = QComboBox()
        self.telemetry_combo.addItems(["Upload Anonymized", "Local Only"])
        self.auto_update_combo = QComboBox()
        self.auto_update_combo.addItems(["On", "Off"])
        sys_lay.addRow(self.create_lbl("Telemetry Data:"), self.telemetry_combo)
        sys_lay.addRow(self.create_lbl("Auto Update Firmware:"), self.auto_update_combo)
        self.stack.addWidget(sys_page)
        
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            if isinstance(w, QLabel): w.setProperty("class", "h2")
            
        content_lay.addWidget(self.stack, stretch=1)
        
        # Actions
        actions_lay = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "primary-button")
        save_btn.clicked.connect(self.save_settings)
        actions_lay.addStretch()
        actions_lay.addWidget(save_btn)
        
        content_lay.addLayout(actions_lay)
        main_layout.addWidget(content_area, stretch=1)
        
        self.list_widget.currentRowChanged.connect(self.stack.setCurrentIndex)

    CARD_TITLES = {"det": "DETECTION", "cam": "CAMERA", "saf": "SAFETY", "perf": "PERFORMANCE", "int": "INTERFACE", "sys": "SYSTEM"}

    def form_card(self, page, key):
        """Put a form inside a titled card on the given page widget and return the form layout."""
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        card, lay = make_card(self.CARD_TITLES[key])
        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        lay.addLayout(form)
        outer.addWidget(card)
        outer.addStretch()
        return form

    def create_lbl(self, text):
        lbl = QLabel(text)
        lbl.setProperty("class", "muted")
        return lbl

    def load_settings(self):
        settings = database.get_settings()
        if settings:
            self.alert_delay_spin.setValue(settings.get('alert_delay', 5))
            self.safety_mode_combo.setCurrentText(settings.get('safety_mode', 'Monitor Only'))
            self.cam_id_spin.setValue(settings.get('camera_id', 0))
            
            conf = settings.get('confidence_threshold', 0.5)
            if conf <= 0.3: self.conf_combo.setCurrentIndex(0)
            elif conf <= 0.5: self.conf_combo.setCurrentIndex(1)
            elif conf <= 0.75: self.conf_combo.setCurrentIndex(2)
            else: self.conf_combo.setCurrentIndex(3)
            
            model_name = settings.get('model_name', 'yolo11m.pt')
            index = self.model_combo.findText(model_name)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

    def save_settings(self):
        delay = self.alert_delay_spin.value()
        mode = self.safety_mode_combo.currentText()
        cam_id = self.cam_id_spin.value()
        
        conf_idx = self.conf_combo.currentIndex()
        conf_val = 0.5
        if conf_idx == 0: conf_val = 0.3
        elif conf_idx == 1: conf_val = 0.5
        elif conf_idx == 2: conf_val = 0.75
        elif conf_idx == 3: conf_val = 0.90
        
        database.update_setting('alert_delay', delay)
        database.update_setting('safety_mode', mode)
        database.update_setting('camera_id', cam_id)
        database.update_setting('confidence_threshold', conf_val)
        
        new_model = self.model_combo.currentText()
        database.update_setting('model_name', new_model)
        
        if self.alert_system:
            self.alert_system.load_settings()
            
        QMessageBox.information(self, "Settings Saved", "Settings updated successfully.\nRestart the application to apply model changes.")
