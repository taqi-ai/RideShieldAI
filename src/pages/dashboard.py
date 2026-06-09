import os
import time
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGridLayout, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QImage
from datetime import datetime

class Speedometer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.speed = 68

    def set_speed(self, speed):
        self.speed = speed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(20, 20, self.width()-40, self.height()-40)
        
        # Draw background arc
        pen = QPen(QColor(30, 30, 40), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawArc(rect, 210 * 16, -240 * 16)
        
        # Draw active arc
        span_angle = -min(240, max(0, self.speed)) * 16
        if self.speed > 0:
            pen = QPen(QColor(0, 229, 255), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.drawArc(rect, 210 * 16, int(span_angle))
            
        # Draw Redline arc
        pen = QPen(QColor(255, 51, 51), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawArc(rect, -30 * 16, 40 * 16) # Approx 200-240 is red

        # Draw Speed text
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 60, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(int(self.speed)))
        
        # Draw km/h text
        font = QFont("Segoe UI", 16)
        painter.setFont(font)
        kmh_rect = QRectF(rect.x(), rect.y() + 80, rect.width(), rect.height())
        painter.drawText(kmh_rect, Qt.AlignmentFlag.AlignCenter, "km/h")
        
        # Draw CRUISE text
        painter.setPen(QColor(160, 160, 176))
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font)
        cruise_rect = QRectF(rect.x(), rect.y() + 140, rect.width(), rect.height())
        painter.drawText(cruise_rect, Qt.AlignmentFlag.AlignCenter, "CRUISE")


class RPMGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.rpm = 4200

    def set_rpm(self, rpm):
        self.rpm = rpm
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(20, 20, self.width()-40, self.height()-40)
        
        # Draw background arc
        pen = QPen(QColor(30, 30, 40), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawArc(rect, 210 * 16, -240 * 16) 
        
        # Draw active arc
        mapped_rpm = (self.rpm / 12000.0) * 240.0
        span_angle = -min(240, max(0, mapped_rpm)) * 16
        if self.rpm > 0:
            pen = QPen(QColor(0, 229, 255), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.drawArc(rect, 210 * 16, int(span_angle))
            
        # Draw Redline arc
        pen = QPen(QColor(255, 51, 51), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawArc(rect, -30 * 16, 40 * 16) # 10-12k is red

        # Draw RPM text
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(int(self.rpm)))
        
        # Draw RPM label
        font = QFont("Segoe UI", 16)
        painter.setFont(font)
        rpm_rect = QRectF(rect.x(), rect.y() + 80, rect.width(), rect.height())
        painter.drawText(rpm_rect, Qt.AlignmentFlag.AlignCenter, "RPM")
        
        # Draw SPORT text
        painter.setPen(QColor(0, 229, 255))
        font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        painter.setFont(font)
        sport_rect = QRectF(rect.x(), rect.y() + 140, rect.width(), rect.height())
        painter.drawText(sport_rect, Qt.AlignmentFlag.AlignCenter, "SPORT")


class DashboardPage(QWidget):
    def __init__(self, ai_engine, alert_system, main_window, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        self.main_window = main_window
        
        self.is_alert_state = False
        self.last_helmet_time = time.time()
        
        self.init_ui()
        
        # Connect AI Engine
        if self.ai_engine:
            self.ai_engine.stats_update.connect(self.on_stats_update)
            self.ai_engine.image_update.connect(self.on_image_update)
            
        # Clock Timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)

        # ---------------- TOP HEADER ----------------
        header_layout = QHBoxLayout()
        
        # Top Left
        top_left = QVBoxLayout()
        logo_lbl = QLabel("RIDESHIELD AI")
        logo_lbl.setProperty("class", "h1")
        tagline_lbl = QLabel("Ride Smarter. Ride Safer.")
        tagline_lbl.setProperty("class", "info-text")
        top_left.addWidget(logo_lbl)
        top_left.addWidget(tagline_lbl)
        header_layout.addLayout(top_left)
        
        header_layout.addStretch()
        
        # Top Center
        top_center = QHBoxLayout()
        top_center.setSpacing(20)
        icons_lbl = QLabel("[ BT ]  [ PHONE ]")
        icons_lbl.setProperty("class", "h2")
        self.time_lbl = QLabel(datetime.now().strftime("%I:%M %p"))
        self.time_lbl.setProperty("class", "h1")
        top_center.addWidget(icons_lbl)
        top_center.addWidget(self.time_lbl)
        header_layout.addLayout(top_center)
        
        header_layout.addStretch()
        
        # Top Right
        top_right = QHBoxLayout()
        top_right.setSpacing(20)
        cloud_lbl = QLabel("[ WIFI ]  [ CLOUD ]")
        cloud_lbl.setProperty("class", "h2")
        temp_lbl = QLabel("23°C")
        temp_lbl.setProperty("class", "h1")
        weather_lbl = QLabel("☀️")
        weather_lbl.setProperty("class", "h1")
        top_right.addWidget(cloud_lbl)
        top_right.addWidget(temp_lbl)
        top_right.addWidget(weather_lbl)
        header_layout.addLayout(top_right)
        
        main_layout.addLayout(header_layout)
        
        # ---------------- CENTER AREA (Dials + Status) ----------------
        dials_layout = QHBoxLayout()
        dials_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Left Dial
        self.speedometer = Speedometer()
        dials_layout.addWidget(self.speedometer, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        dials_layout.addSpacing(50)
        
        # Center Stack
        center_content = QVBoxLayout()
        center_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.gear_label = QLabel("[ 4 ]")
        self.gear_label.setProperty("class", "gear-text")
        self.gear_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_content.addWidget(self.gear_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.center_visual_stack = QStackedWidget()
        self.center_visual_stack.setFixedSize(500, 350)
        
        # Bike Image
        self.bike_img = QLabel()
        bike_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "Bike.png"))
        if os.path.exists(bike_path):
            self.bike_pixmap = QPixmap(bike_path)
            self.bike_img.setPixmap(self.bike_pixmap.scaled(450, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.bike_img.setText("[ BIKE ASSET MISSING ]")
        self.bike_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_visual_stack.addWidget(self.bike_img)
        
        # Camera Feed
        self.camera_frame = QLabel()
        self.camera_frame.setObjectName("camera-frame")
        self.camera_frame.setFixedSize(450, 350)
        self.camera_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_visual_stack.addWidget(self.camera_frame)
        
        center_content.addWidget(self.center_visual_stack, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # AI Safety Status Card
        self.status_card = QFrame()
        self.status_card.setProperty("class", "glass-card safe-card-active")
        self.status_card.setFixedSize(400, 120)
        status_layout = QHBoxLayout(self.status_card)
        
        self.helmet_icon = QLabel()
        helmet_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "Helmet.png"))
        if os.path.exists(helmet_path):
            self.helmet_icon.setPixmap(QPixmap(helmet_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        status_layout.addWidget(self.helmet_icon)
        
        status_text_layout = QVBoxLayout()
        self.status_title = QLabel("HELMET DETECTED")
        self.status_title.setProperty("class", "safe-text")
        status_text_layout.addWidget(self.status_title)
        
        self.confidence_lbl = QLabel("Confidence: --%")
        self.confidence_lbl.setProperty("class", "info-text")
        status_text_layout.addWidget(self.confidence_lbl)
        
        self.mode_lbl = QLabel("Mode: SMART LOCK")
        self.mode_lbl.setProperty("class", "info-text")
        status_text_layout.addWidget(self.mode_lbl)
        
        status_layout.addLayout(status_text_layout)
        center_content.addWidget(self.status_card, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dials_layout.addLayout(center_content)
        
        dials_layout.addSpacing(50)
        
        # Right Dial
        self.rpm_gauge = RPMGauge()
        dials_layout.addWidget(self.rpm_gauge, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        main_layout.addLayout(dials_layout)
        
        main_layout.addStretch()
        
        # ---------------- BOTTOM INFORMATION CARDS ----------------
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        def create_bottom_card(title, value):
            card = QFrame()
            card.setProperty("class", "glass-card")
            card.setFixedHeight(100)
            lay = QVBoxLayout(card)
            lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_title = QLabel(title)
            lbl_title.setProperty("class", "info-text")
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_val = QLabel(value)
            lbl_val.setProperty("class", "h2")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl_title)
            lay.addWidget(lbl_val)
            cards_layout.addWidget(card)
            return lbl_val
            
        self.fuel_val = create_bottom_card("Fuel", "75%")
        self.gear_val = create_bottom_card("Gear", "4")
        self.range_val = create_bottom_card("Range", "245 km")
        self.temp_val = create_bottom_card("Temperature", "68°C")
        self.trip_val = create_bottom_card("Trip Time", "01:24:36")
        
        main_layout.addLayout(cards_layout)

    def update_clock(self):
        self.time_lbl.setText(datetime.now().strftime("%I:%M %p"))

    def on_stats_update(self, stats):
        helmet_detected = stats.get("helmet_detected", False)
        conf = stats.get("confidence", 0.0) * 100
        
        if helmet_detected:
            self.last_helmet_time = time.time()
            if self.is_alert_state:
                self.set_alert_state(False)
            self.confidence_lbl.setText(f"Confidence: {conf:.1f}%")
        else:
            time_without_helmet = time.time() - self.last_helmet_time
            if time_without_helmet > 5.0 and not self.is_alert_state:
                self.set_alert_state(True)
            
            if self.is_alert_state:
                self.confidence_lbl.setText(f"Confidence: {conf:.1f}%")

    def set_alert_state(self, state):
        self.is_alert_state = state
        if state:
            self.center_visual_stack.setCurrentIndex(1) # Show camera
            self.status_card.setProperty("class", "glass-card alert-card-active")
            self.status_title.setText("NO HELMET DETECTED")
            self.status_title.setProperty("class", "alert-text")
            
            # Ensure styles are re-evaluated
            self.status_card.style().unpolish(self.status_card)
            self.status_card.style().polish(self.status_card)
            self.status_title.style().unpolish(self.status_title)
            self.status_title.style().polish(self.status_title)
            
            if hasattr(self.main_window, 'set_alert_mode'):
                self.main_window.set_alert_mode(True)
        else:
            self.center_visual_stack.setCurrentIndex(0) # Show bike
            self.status_card.setProperty("class", "glass-card safe-card-active")
            self.status_title.setText("HELMET DETECTED")
            self.status_title.setProperty("class", "safe-text")
            
            self.status_card.style().unpolish(self.status_card)
            self.status_card.style().polish(self.status_card)
            self.status_title.style().unpolish(self.status_title)
            self.status_title.style().polish(self.status_title)
            
            if hasattr(self.main_window, 'set_alert_mode'):
                self.main_window.set_alert_mode(False)

    def on_image_update(self, qimg):
        if self.is_alert_state:
            self.camera_frame.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.camera_frame.width(), self.camera_frame.height(), 
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
