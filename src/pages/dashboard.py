import os
import psutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QPixmap, QRadialGradient, QLinearGradient, QImage, QPolygonF
import math

class AdvancedSpeedometer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 450)
        self.speed = 0
        self.fuel = 75

    def set_speed(self, speed):
        self.speed = max(0, min(240, speed))
        self.update()

    def set_fuel(self, fuel):
        self.fuel = max(0, min(100, fuel))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center = QPointF(width / 2, height / 2 - 20)
        radius = min(width, height) / 2 - 40
        
        # Draw Background Glow (Cyan)
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0, QColor(0, 229, 255, 40))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        # Outer Ring Tick Marks
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        start_angle = 225
        end_angle = -45
        total_range = 240
        
        for i in range(0, total_range + 1, 10):
            angle = start_angle - (i / total_range) * (start_angle - end_angle)
            rad_angle = math.radians(angle)
            
            is_major = (i % 20 == 0)
            length = 20 if is_major else 10
            
            x1 = center.x() + (radius - length) * math.cos(rad_angle)
            y1 = center.y() - (radius - length) * math.sin(rad_angle)
            x2 = center.x() + radius * math.cos(rad_angle)
            y2 = center.y() - radius * math.sin(rad_angle)
            
            if is_major:
                painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
            else:
                painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
                
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            if is_major:
                painter.setFont(QFont("Segoe UI", 12))
                painter.setPen(QColor(255, 255, 255, 200))
                tx = center.x() + (radius - 40) * math.cos(rad_angle)
                ty = center.y() - (radius - 40) * math.sin(rad_angle)
                rect = QRectF(tx - 15, ty - 10, 30, 20)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(i))

        # Cyan sweeping arc
        span_angle = int((start_angle - end_angle) * 16 * (self.speed / total_range))
        grad = QLinearGradient(0, height, width, 0)
        grad.setColorAt(0, QColor(0, 100, 255))
        grad.setColorAt(1, QColor(0, 229, 255))
        
        painter.setPen(QPen(grad, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2), start_angle * 16, -span_angle)

        # Digital Readout
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 80, QFont.Weight.Bold))
        text_rect = QRectF(center.x() - 100, center.y() - 50, 200, 100)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.speed)}")
        
        painter.setFont(QFont("Segoe UI", 14))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRectF(center.x() - 50, center.y() + 50, 100, 30), Qt.AlignmentFlag.AlignCenter, "km/h")
        
        # Cruise Indicator
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(57, 255, 20)) # Neon Green
        painter.drawText(QRectF(center.x() - 50, center.y() + 90, 100, 30), Qt.AlignmentFlag.AlignCenter, "CRUISE")

        # Fuel Gauge (Bottom arc)
        fuel_center = QPointF(center.x(), center.y() + radius + 10)
        fuel_radius = radius - 60
        painter.setPen(QPen(QColor(40, 45, 60), 4))
        painter.drawArc(QRectF(fuel_center.x() - fuel_radius, fuel_center.y() - fuel_radius, fuel_radius * 2, fuel_radius * 2), 220 * 16, -100 * 16)
        
        fuel_span = int(100 * 16 * (self.fuel / 100))
        fuel_grad = QLinearGradient(fuel_center.x() - fuel_radius, fuel_center.y(), fuel_center.x() + fuel_radius, fuel_center.y())
        fuel_grad.setColorAt(0, QColor(255, 51, 51))
        fuel_grad.setColorAt(1, QColor(57, 255, 20))
        painter.setPen(QPen(fuel_grad, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(QRectF(fuel_center.x() - fuel_radius, fuel_center.y() - fuel_radius, fuel_radius * 2, fuel_radius * 2), 220 * 16, -fuel_span)

        # Fuel markers
        painter.setPen(QColor(255, 51, 51))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(fuel_center.x() - fuel_radius - 20, fuel_center.y() - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, "E")
        
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(fuel_center.x() + fuel_radius, fuel_center.y() - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, "F")
        

class AdvancedTachometer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 450)
        self.rpm = 0

    def set_rpm(self, rpm):
        self.rpm = max(0, min(12000, rpm))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center = QPointF(width / 2, height / 2 - 20)
        radius = min(width, height) / 2 - 40
        
        # Draw Background Glow (Red)
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0, QColor(255, 51, 51, 40))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        start_angle = 225
        end_angle = -45
        total_range = 12
        
        for i in range(0, total_range + 1):
            angle = start_angle - (i / total_range) * (start_angle - end_angle)
            rad_angle = math.radians(angle)
            
            length = 20
            
            x1 = center.x() + (radius - length) * math.cos(rad_angle)
            y1 = center.y() - (radius - length) * math.sin(rad_angle)
            x2 = center.x() + radius * math.cos(rad_angle)
            y2 = center.y() - radius * math.sin(rad_angle)
            
            painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            painter.setFont(QFont("Segoe UI", 14))
            painter.setPen(QColor(255, 255, 255, 200))
            tx = center.x() + (radius - 40) * math.cos(rad_angle)
            ty = center.y() - (radius - 40) * math.sin(rad_angle)
            rect = QRectF(tx - 15, ty - 10, 30, 20)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(i))

        # Blue to Red sweeping arc
        span_angle = int((start_angle - end_angle) * 16 * (self.rpm / 12000))
        grad = QLinearGradient(0, height, width, 0)
        grad.setColorAt(0, QColor(0, 100, 255))
        grad.setColorAt(0.7, QColor(255, 51, 51))
        grad.setColorAt(1, QColor(255, 0, 0))
        
        painter.setPen(QPen(grad, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2), start_angle * 16, -span_angle)

        # Digital Readout
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 70, QFont.Weight.Bold))
        text_rect = QRectF(center.x() - 100, center.y() - 50, 200, 90)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.rpm)}")
        
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRectF(center.x() - 50, center.y() + 40, 100, 20), Qt.AlignmentFlag.AlignCenter, "RPM")
        
        # Ride Mode Indicator
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255, 150))
        painter.drawText(QRectF(center.x() - 50, center.y() + 90, 100, 20), Qt.AlignmentFlag.AlignCenter, "RIDE MODE")
        
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(255, 51, 51))
        painter.drawText(QRectF(center.x() - 50, center.y() + 110, 100, 20), Qt.AlignmentFlag.AlignCenter, "SPORT")


class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 180)
        self.is_alert = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Draw futuristic bracket
        path = QPainterPath()
        path.moveTo(w*0.1, 0)
        path.lineTo(0, h*0.3)
        path.lineTo(0, h*0.8)
        path.lineTo(w*0.05, h)
        path.lineTo(w*0.95, h)
        path.lineTo(w, h*0.8)
        path.lineTo(w*0.95, h*0.5)
        path.lineTo(w, h*0.2)
        path.lineTo(w*0.9, 0)
        path.lineTo(w*0.1, 0)
        
        if self.is_alert:
            painter.setPen(QPen(QColor(255, 51, 51, 200), 2))
            painter.setBrush(QColor(255, 51, 51, 20))
        else:
            painter.setPen(QPen(QColor(57, 255, 20, 150), 2))
            painter.setBrush(QColor(57, 255, 20, 10))
            
        painter.drawPath(path)

class DashboardPage(QWidget):
    def __init__(self, ai_engine, alert_system, main_window, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        self.main_window = main_window
        self.init_ui()
        
        self.dash_timer = QTimer(self)
        self.dash_timer.timeout.connect(self.update_telemetry)
        self.dash_timer.start(50)
        
        if self.ai_engine:
            self.ai_engine.image_update.connect(self.update_camera_feed)
            
        if self.alert_system:
            self.alert_system.alert_triggered.connect(self.trigger_adas_alert)
            self.alert_system.alert_cleared.connect(self.clear_adas_alert)
        
        self.speed = 0
        self.rpm = 0

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(10)
        
        # --- TOP HEADER ---
        top_header = QHBoxLayout()
        logo_lbl = QLabel("RIDESHIELD AI")
        logo_lbl.setStyleSheet("color: white; font-size: 28px; font-weight: 900; font-style: italic; letter-spacing: 2px;")
        
        self.top_ai_status = QLabel("YOLO11m | FPS: -- | INF: -- ms | DETECTING")
        self.top_ai_status.setStyleSheet("color: #00E5FF; font-weight: bold; font-size: 14px;")
        
        icons_lay = QHBoxLayout()
        icons_lay.setSpacing(20)
        for text, color in [("BT", "#00E5FF"), ("TEL", "white"), ("WIFI", "white"), ("CLOUD", "white")]:
            l = QLabel(text)
            l.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
            icons_lay.addWidget(l)
            
        time_lbl = QLabel("10:42 AM")
        time_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        weather_lbl = QLabel("23°C SUN")
        weather_lbl.setStyleSheet("color: white; font-size: 20px;")
        
        top_header.addWidget(logo_lbl)
        top_header.addSpacing(20)
        top_header.addWidget(self.top_ai_status)
        top_header.addStretch()
        top_header.addLayout(icons_lay)
        top_header.addSpacing(30)
        top_header.addWidget(time_lbl)
        top_header.addStretch()
        top_header.addWidget(weather_lbl)
        
        main_layout.addLayout(top_header)
        
        # --- CENTER DASHBOARD ---
        self.dash_content = QHBoxLayout()
        
        # Left Speedometer
        self.speedometer = AdvancedSpeedometer()
        self.dash_content.addWidget(self.speedometer, stretch=1)
        
        # Center Stack (Camera & Status)
        center_vert = QVBoxLayout()
        center_vert.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        gear_lbl = QLabel("GEAR\n4")
        gear_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gear_lbl.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 10px; border: 1px solid rgba(255, 51, 51, 0.5); border-radius: 8px;")
        center_vert.addWidget(gear_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.adas_stack = QStackedWidget()
        
        self.bike_view = QLabel()
        b_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Bike.png"))
        if os.path.exists(b_path):
            self.bike_view.setPixmap(QPixmap(b_path).scaled(500, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.bike_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bike_view.setStyleSheet("background-color: transparent;")
        
        self.adas_feed = QLabel()
        self.adas_feed.setFixedSize(500, 300)
        self.adas_feed.setStyleSheet("background-color: #111; border: 2px solid rgba(255, 51, 51, 0.8); border-radius: 12px;")
        self.adas_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.adas_stack.addWidget(self.bike_view)
        self.adas_stack.addWidget(self.adas_feed)
        
        center_vert.addWidget(self.adas_stack)
        
        self.status_panel = StatusPanel()
        status_lay = QHBoxLayout(self.status_panel)
        status_lay.setContentsMargins(40, 20, 40, 20)
        
        self.helmet_img = QLabel()
        h_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Helmet.png"))
        if os.path.exists(h_path):
            self.helmet_img.setPixmap(QPixmap(h_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.helmet_img.setText("[HELMET]")
            self.helmet_img.setStyleSheet("color: red;")
        
        status_text_lay = QVBoxLayout()
        self.alert_msg = QLabel("NO HELMET\nDETECTED")
        self.alert_msg.setStyleSheet("color: #FF3333; font-size: 24px; font-weight: 900;")
        
        self.conf_lbl = QLabel("CONFIDENCE 98.6%")
        self.conf_lbl.setStyleSheet("color: white; font-size: 14px;")
        
        self.mode_lbl = QLabel("MODE  SMART LOCK")
        self.mode_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        status_text_lay.addWidget(self.alert_msg)
        status_text_lay.addWidget(self.conf_lbl)
        status_text_lay.addWidget(self.mode_lbl)
        
        status_lay.addWidget(self.helmet_img)
        status_lay.addLayout(status_text_lay)
        
        center_vert.addWidget(self.status_panel)
        
        self.dash_content.addLayout(center_vert, stretch=1)
        
        # Right Tachometer
        self.tachometer = AdvancedTachometer()
        self.dash_content.addWidget(self.tachometer, stretch=1)
        
        main_layout.addLayout(self.dash_content, stretch=1)
        
        # --- BOTTOM TELEMETRY BAR ---
        bot_bar = QHBoxLayout()
        bot_bar.setSpacing(15)
        
        boxes = [
            ("FUEL", "75%"),
            ("GEAR", "4"),
            ("RANGE", "245 km"),
            ("TEMP", "68°C"),
            ("TRIP TIME", "01:24:36")
        ]
        
        for t, v in boxes:
            b = QFrame()
            b.setStyleSheet("background-color: rgba(15, 20, 25, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;")
            b.setFixedHeight(80)
            l = QVBoxLayout(b)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(QLabel(t))
            val = QLabel(v)
            val.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
            l.addWidget(val)
            bot_bar.addWidget(b)
            
        main_layout.addLayout(bot_bar)

    def update_telemetry(self):
        import random
        target_speed = 68
        target_rpm = 4200
        
        self.speed += (target_speed - self.speed) * 0.1 + random.uniform(-0.5, 0.5)
        self.rpm += (target_rpm - self.rpm) * 0.1 + random.uniform(-10, 10)
        
        self.speedometer.set_speed(self.speed)
        self.tachometer.set_rpm(self.rpm)

    @pyqtSlot(QImage)
    def update_camera_feed(self, qimg):
        pix = QPixmap.fromImage(qimg).scaled(self.adas_feed.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.adas_feed.setPixmap(pix)
        
    @pyqtSlot(dict)
    def update_live_stats(self, stats):
        fps = stats.get("fps", 0)
        inf = stats.get("inference_time", 0)
        model = stats.get("model_name", "YOLO11m")
        self.top_ai_status.setText(f"{model} | FPS: {fps:.1f} | INF: {inf:.1f} ms | DETECTING")
        if stats.get("helmet_detected", False) and not self.status_panel.is_alert:
            self.conf_lbl.setText(f"CONFIDENCE {stats.get('confidence', 0):.1%}")

    @pyqtSlot(str)
    def trigger_adas_alert(self, msg):
        self.alert_msg.setText(msg)
        self.status_panel.is_alert = True
        self.adas_stack.setCurrentIndex(1)
        self.status_panel.update()

    @pyqtSlot()
    def clear_adas_alert(self):
        self.alert_msg.setText("HELMET DETECTED")
        self.alert_msg.setStyleSheet("color: #39FF14; font-size: 24px; font-weight: 900;")
        self.status_panel.is_alert = False
        self.adas_stack.setCurrentIndex(0)
        self.status_panel.update()
