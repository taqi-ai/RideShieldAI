import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QImage, QPixmap, QColor, QPainter, QFont

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
            
        self.blink_state = True
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_timer.start(500)

    def toggle_blink(self):
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.live_indicator.setStyleSheet("color: #FF3333; font-size: 24px; font-weight: bold; background-color: transparent;")
        else:
            self.live_indicator.setStyleSheet("color: rgba(255,51,51,0.5); font-size: 24px; font-weight: bold; background-color: transparent;")
        self.live_indicator.adjustSize()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)
        
        # --- Top Area: Video Feed (70%) ---
        self.video_container = QFrame()
        self.video_container.setStyleSheet("background-color: #0A0A0E; border: 2px solid #20202A; border-radius: 12px;")
        video_layout = QVBoxLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel("CAMERA FEED INITIALIZING...")
        self.video_label.setProperty("class", "h2")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_layout.addWidget(self.video_label)
        
        # Overlay LIVE indicator (using absolute positioning)
        self.live_indicator = QLabel("● LIVE")
        self.live_indicator.setStyleSheet("color: #FF3333; font-size: 24px; font-weight: bold; background-color: transparent;")
        self.live_indicator.setParent(self.video_container)
        self.live_indicator.adjustSize()
        self.live_indicator.move(20, 20)
        
        main_layout.addWidget(self.video_container, stretch=7)
        
        # --- Bottom Area: Live Cards (30%) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # 1. Helmet Status
        self.status_card = QFrame()
        self.status_card.setProperty("class", "glass-card safe-card-active")
        status_lay = QVBoxLayout(self.status_card)
        status_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl1 = QLabel("Helmet Status")
        lbl1.setProperty("class", "info-text")
        lbl1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_val = QLabel("DETECTED")
        self.status_val.setProperty("class", "safe-text")
        self.status_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lay.addWidget(lbl1)
        status_lay.addWidget(self.status_val)
        cards_layout.addWidget(self.status_card)
        
        def create_card(title, value_class):
            card = QFrame()
            card.setProperty("class", "glass-card")
            lay = QVBoxLayout(card)
            lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_title = QLabel(title)
            lbl_title.setProperty("class", "info-text")
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_val = QLabel("--")
            lbl_val.setProperty("class", value_class)
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl_title)
            lay.addWidget(lbl_val)
            cards_layout.addWidget(card)
            return lbl_val
            
        self.conf_val = create_card("Confidence", "h2")
        self.fps_val = create_card("FPS", "h2")
        self.infer_val = create_card("Inference Time", "h2")
        
        # Model Name Card
        model_name = "YOLO"
        if self.ai_engine and hasattr(self.ai_engine, 'model_path'):
            base = os.path.basename(self.ai_engine.model_path)
            model_name = os.path.splitext(base)[0].upper()
            
        self.model_val = create_card("Current Model", "h2")
        self.model_val.setText(model_name)
        
        main_layout.addLayout(cards_layout, stretch=2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep LIVE indicator at top-left
        self.live_indicator.move(20, 20)

    @pyqtSlot(QImage)
    def update_image(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        # Keep aspect ratio and fit inside the large container
        scaled_pixmap = pixmap.scaled(self.video_container.width() - 4, 
                                      self.video_container.height() - 4, 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    @pyqtSlot(dict)
    def update_stats(self, stats):
        helmet_detected = stats.get("helmet_detected", False)
        if helmet_detected:
            self.status_card.setProperty("class", "glass-card safe-card-active")
            self.status_val.setText("DETECTED")
            self.status_val.setProperty("class", "safe-text")
        else:
            self.status_card.setProperty("class", "glass-card alert-card-active")
            self.status_val.setText("NOT DETECTED")
            self.status_val.setProperty("class", "alert-text")
            
        # Ensure stylesheet refreshes dynamically
        self.status_card.style().unpolish(self.status_card)
        self.status_card.style().polish(self.status_card)
        self.status_val.style().unpolish(self.status_val)
        self.status_val.style().polish(self.status_val)
            
        self.fps_val.setText(f"{stats.get('fps', 0):.1f}")
        self.infer_val.setText(f"{stats.get('inference_time', 0):.1f} ms")
        self.conf_val.setText(f"{stats.get('confidence', 0)*100:.1f}%")
