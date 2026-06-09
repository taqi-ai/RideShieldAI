from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

class LiveMonitorPage(QWidget):
    def __init__(self, ai_engine, alert_system, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        self.init_ui()
        
        # Connect signals
        if self.ai_engine:
            self.ai_engine.image_update.connect(self.update_image)
            self.ai_engine.stats_update.connect(self.update_stats)
            
        if self.alert_system:
            self.alert_system.alert_triggered.connect(self.show_alert)
            self.alert_system.alert_cleared.connect(self.hide_alert)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Live AI Monitor")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Alert Banner
        self.alert_banner = QLabel("NO HELMET DETECTED - ALERT ACTIVE")
        self.alert_banner.setProperty("class", "alert-banner")
        self.alert_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alert_banner.setStyleSheet("background-color: #F44336; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.alert_banner.hide()
        layout.addWidget(self.alert_banner)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Video feed
        self.video_label = QLabel("Camera Feed Initializing...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #000; border-radius: 8px;")
        content_layout.addWidget(self.video_label, stretch=3)
        
        # Stats panel
        stats_panel = QFrame()
        stats_panel.setProperty("class", "card")
        stats_layout = QVBoxLayout(stats_panel)
        
        stats_title = QLabel("Real-time Analytics")
        stats_title.setProperty("class", "h3")
        stats_layout.addWidget(stats_title)
        
        self.helmet_status = QLabel("Helmet Status: Unknown")
        self.fps_label = QLabel("FPS: 0.0")
        self.inference_label = QLabel("Inference Time: 0.0 ms")
        self.confidence_label = QLabel("Confidence: 0.0%")
        
        stats_layout.addWidget(self.helmet_status)
        stats_layout.addWidget(self.fps_label)
        stats_layout.addWidget(self.inference_label)
        stats_layout.addWidget(self.confidence_label)
        stats_layout.addStretch()
        
        content_layout.addWidget(stats_panel, stretch=1)
        
        layout.addLayout(content_layout)

    @pyqtSlot(QImage)
    def update_image(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        # Scale pixmap to fit the label, keeping aspect ratio
        scaled_pixmap = pixmap.scaled(self.video_label.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    @pyqtSlot(dict)
    def update_stats(self, stats):
        helmet_detected = stats.get("helmet_detected", False)
        if helmet_detected:
            self.helmet_status.setText("Helmet Status: Detected")
            self.helmet_status.setStyleSheet("color: #4CAF50;") # Green
        else:
            self.helmet_status.setText("Helmet Status: Not Detected")
            self.helmet_status.setStyleSheet("color: #F44336;") # Red
            
        self.fps_label.setText(f"FPS: {stats.get('fps', 0):.1f}")
        self.inference_label.setText(f"Inference Time: {stats.get('inference_time', 0):.1f} ms")
        self.confidence_label.setText(f"Confidence: {stats.get('confidence', 0)*100:.1f}%")

    @pyqtSlot(str)
    def show_alert(self, msg):
        self.alert_banner.setText(msg)
        self.alert_banner.show()

    @pyqtSlot()
    def hide_alert(self):
        self.alert_banner.hide()
