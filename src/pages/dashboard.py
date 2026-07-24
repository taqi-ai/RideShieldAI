import os
import psutil
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QProgressBar, QPushButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QRadialGradient, QLinearGradient, QImage
from src.audio_system import speaker

class CircularHelmetWidget(QWidget):
    """Card 1: Helmet Status with large circular outline around helmet illustration."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 160)
        self.detected = True
        self.helmet_pixmap = None
        
        h_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Helmet.png"))
        if os.path.exists(h_path):
            self.helmet_pixmap = QPixmap(h_path)

    def set_detected(self, detected):
        self.detected = detected
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        center = QPointF(w / 2, h / 2)
        radius = min(w, h) / 2 - 12
        
        # Color based on state
        circle_color = QColor(57, 255, 20) if self.detected else QColor(255, 51, 51)
        
        # Background Glow
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0, QColor(circle_color.red(), circle_color.green(), circle_color.blue(), 30))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        # Large Circular Outline (Bright Green or Red)
        painter.setPen(QPen(circle_color, 4))
        painter.setBrush(QColor(10, 15, 25, 200))
        painter.drawEllipse(center, radius - 4, radius - 4)
        
        # Helmet Image or Fallback Icon
        if self.helmet_pixmap:
            scaled_pix = self.helmet_pixmap.scaled(int((radius - 15) * 1.6), int((radius - 15) * 1.6),
                                                   Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
            px = center.x() - scaled_pix.width() / 2
            py = center.y() - scaled_pix.height() / 2
            painter.drawPixmap(int(px), int(py), scaled_pix)
        else:
            painter.setFont(QFont("Segoe UI", 36))
            painter.setPen(circle_color)
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "🪖")


class CenterSpeedometer(QWidget):
    """Real Motorcycle Instrument Speedometer Dial with 0, 20, 40, 60... tick markers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.speed = 42.0
        self.rpm = 4500.0
        self.fuel = 75.0
        self.gear = "3"
        self.neutral = False
        self.ride_mode = "SPORT"

    def set_telemetry(self, speed, rpm, gear, fuel, neutral=False, ride_mode="SPORT"):
        self.speed = max(0.0, min(240.0, speed))
        self.rpm = max(0.0, min(12000.0, rpm))
        self.gear = str(gear)
        self.fuel = max(0.0, min(100.0, fuel))
        self.neutral = (self.gear == "N" or speed == 0)
        self.ride_mode = ride_mode
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        center = QPointF(w / 2, h / 2 - 5)
        radius = min(w, h) / 2 - 22
        
        # Outer Ring Background
        painter.setPen(QPen(QColor(255, 255, 255, 30), 4))
        painter.setBrush(QColor(10, 14, 22, 230))
        painter.drawEllipse(center, radius, radius)
        
        start_angle = 225
        end_angle = -45
        total_range = 240.0

        # Authentic Motorcycle Speed Tick Marks (White lines & 0, 20, 40, 60... markers)
        for i in range(0, 241, 10):
            angle = start_angle - (i / total_range) * (start_angle - end_angle)
            rad = math.radians(angle)
            is_major = (i % 20 == 0)
            length = 14 if is_major else 7
            
            x1 = center.x() + (radius - length) * math.cos(rad)
            y1 = center.y() - (radius - length) * math.sin(rad)
            x2 = center.x() + radius * math.cos(rad)
            y2 = center.y() - radius * math.sin(rad)
            
            if is_major:
                painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                
                # Numeric Speed Tick Label (0, 20, 40, 60, 80, 100, 120...)
                painter.setFont(QFont("SF Pro Display", 9, QFont.Weight.Bold))
                painter.setPen(QColor(255, 255, 255, 210))
                tx = center.x() + (radius - 26) * math.cos(rad)
                ty = center.y() - (radius - 26) * math.sin(rad)
                painter.drawText(QRectF(tx - 15, ty - 9, 30, 18), Qt.AlignmentFlag.AlignCenter, str(i))
            else:
                painter.setPen(QPen(QColor(255, 255, 255, 90), 1))
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Sweeping Cyan Speed Arc
        span_angle = int((start_angle - end_angle) * 16 * (self.speed / total_range))
        grad = QLinearGradient(0, h, w, 0)
        grad.setColorAt(0, QColor(0, 120, 255))
        grad.setColorAt(1, QColor(0, 229, 255))
        
        painter.setPen(QPen(grad, 9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2), start_angle * 16, -span_angle)

        # Center Speed Readout
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("SF Pro Display", 64, QFont.Weight.Bold))
        painter.drawText(QRectF(center.x() - 100, center.y() - 60, 200, 70), Qt.AlignmentFlag.AlignCenter, f"{int(self.speed)}")
        
        painter.setFont(QFont("SF Pro Display", 13, QFont.Weight.Bold))
        painter.setPen(QColor(0, 229, 255))
        painter.drawText(QRectF(center.x() - 50, center.y() + 15, 100, 20), Qt.AlignmentFlag.AlignCenter, "km/h")

        # Gear Readout & Neutral Indicator
        gear_rect = QRectF(center.x() - 32, center.y() + 40, 64, 38)
        gear_color = QColor(57, 255, 20) if not self.neutral else QColor(0, 229, 255)
        
        painter.setPen(QPen(gear_color, 2))
        painter.setBrush(QColor(5, 6, 8, 220))
        painter.drawRoundedRect(gear_rect, 8, 8)
        
        painter.setFont(QFont("SF Pro Display", 22, QFont.Weight.Bold))
        painter.setPen(gear_color)
        painter.drawText(gear_rect, Qt.AlignmentFlag.AlignCenter, f"{self.gear}")

        # Neutral & Ride Mode Text
        painter.setFont(QFont("SF Pro Display", 10, QFont.Weight.Bold))
        if self.neutral:
            painter.setPen(QColor(0, 229, 255))
            painter.drawText(QRectF(center.x() - 70, center.y() + 84, 60, 18), Qt.AlignmentFlag.AlignCenter, "[N]")
        else:
            painter.setPen(QColor(150, 150, 160))
            painter.drawText(QRectF(center.x() - 70, center.y() + 84, 60, 18), Qt.AlignmentFlag.AlignCenter, "GEAR")

        painter.setPen(QColor(255, 51, 51))
        painter.drawText(QRectF(center.x() + 10, center.y() + 84, 60, 18), Qt.AlignmentFlag.AlignCenter, self.ride_mode)


class DashboardPage(QWidget):
    """Production Specification Dashboard for Ride Shield AI Motorcycle Cluster."""
    def __init__(self, ai_engine, alert_system, main_window, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        self.main_window = main_window
        
        # Telemetry & State
        self.speed = 42.0
        self.rpm = 4500.0
        self.gear = "3"
        self.fuel = 75.0
        self.ride_mode = "SPORT"
        self.throttle_input = 0.0
        self.is_braking = False
        
        # Helmet & Engine Control State: True = Helmet Detected, False = Helmet Missing
        self.helmet_detected = True
        self.engine_state = 1
        
        # Switchgear states
        self.headlight_state = "AUTO"
        self.indicators_state = "OFF"
        self.abs_state = "ON"
        self.cruise_active = False

        self.init_ui()
        
        # Main Telemetry Loop
        self.dash_timer = QTimer(self)
        self.dash_timer.timeout.connect(self.update_telemetry)
        self.dash_timer.start(50)

        if self.ai_engine:
            self.ai_engine.image_update.connect(self.update_camera_feed)
            
        if self.alert_system:
            self.alert_system.alert_triggered.connect(self.trigger_adas_alert)
            self.alert_system.alert_cleared.connect(self.clear_adas_alert)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 12, 18, 12)
        main_layout.setSpacing(14)
        
        # Common Card CSS with 20px rounded corners & subtle glass borders
        self.card_css = """
            QFrame {
                background-color: rgba(10, 14, 22, 0.9);
                border: 1px solid rgba(0, 229, 255, 0.2);
                border-radius: 20px;
            }
        """
        
        # ==========================================
        # TOP BAR (80px HEIGHT SPEC)
        # ==========================================
        top_bar_frame = QFrame()
        top_bar_frame.setFixedHeight(80)
        top_bar_frame.setStyleSheet("QFrame { background-color: #07090E; border-bottom: 1px solid rgba(255, 255, 255, 0.1); border-radius: 18px; }")
        top_bar = QHBoxLayout(top_bar_frame)
        top_bar.setContentsMargins(20, 0, 20, 0)
        
        # LEFT: Shield logo + "RIDE SHIELD" bold white + "AI" bright blue
        logo_lbl = QLabel("🛡️ <b style='color:#FFFFFF;'>RIDE SHIELD</b> <b style='color:#00E5FF;'>AI</b>")
        logo_lbl.setStyleSheet("font-size: 22px;")
        
        # CENTER: Wi-Fi, Bluetooth, Temp (23°C), Time (11:42 AM - largest item)
        center_top = QHBoxLayout()
        center_top.setSpacing(15)
        wifi_lbl = QLabel("📶 Wi-Fi")
        bt_lbl = QLabel("📡 BT")
        temp_lbl = QLabel("23°C")
        time_lbl = QLabel("11:42 AM")
        
        wifi_lbl.setStyleSheet("color: #00E5FF; font-size: 13px; font-weight: bold;")
        bt_lbl.setStyleSheet("color: #00E5FF; font-size: 13px; font-weight: bold;")
        temp_lbl.setStyleSheet("color: #A0A0B0; font-size: 16px; font-weight: 600;")
        time_lbl.setStyleSheet("color: #FFFFFF; font-size: 26px; font-weight: bold;")
        
        center_top.addWidget(wifi_lbl)
        center_top.addWidget(bt_lbl)
        center_top.addWidget(temp_lbl)
        center_top.addSpacing(10)
        center_top.addWidget(time_lbl)
        
        # RIGHT: Fuel indicator, Battery, Engine Temp
        right_top = QHBoxLayout()
        right_top.setSpacing(18)
        fuel_lbl = QLabel("⛽ FUEL <b style='color:#39FF14;'>75%</b>")
        bat_lbl = QLabel("🔋 BAT <b style='color:#FFFFFF;'>14.2V</b>")
        eng_temp_lbl = QLabel("🌡️ ENG <b style='color:#FFFFFF;'>88°C</b>")
        
        for l in (fuel_lbl, bat_lbl, eng_temp_lbl):
            l.setStyleSheet("color: #A0A0B0; font-size: 14px;")
            right_top.addWidget(l)
            
        top_bar.addWidget(logo_lbl)
        top_bar.addStretch()
        top_bar.addLayout(center_top)
        top_bar.addStretch()
        top_bar.addLayout(right_top)
        
        main_layout.addWidget(top_bar_frame)
        
        # ==========================================
        # THREE VERTICAL PANELS: SLIGHTLY WIDER SIDES (28% | 44% | 28%)
        # ==========================================
        body_layout = QHBoxLayout()
        body_layout.setSpacing(14)
        
        # ------------------------------------------
        # LEFT PANEL (28% WIDTH - SLIGHTLY WIDER)
        # ------------------------------------------
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)
        
        # CARD 1: Helmet Status
        self.card1 = QFrame()
        self.card1.setStyleSheet(self.card_css)
        c1_lay = QVBoxLayout(self.card1)
        c1_lay.setContentsMargins(15, 12, 15, 12)
        c1_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        c1_hdr = QLabel("HELMET STATUS")
        c1_hdr.setStyleSheet("color: #A0A0B0; font-size: 11px; font-weight: bold; border: none;")
        c1_lay.addWidget(c1_hdr, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.helmet_circle_widget = CircularHelmetWidget()
        c1_lay.addWidget(self.helmet_circle_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.h_status_lbl = QLabel("HELMET DETECTED")
        self.h_status_lbl.setStyleSheet("color: #39FF14; font-size: 16px; font-weight: 900; border: none;")
        c1_lay.addWidget(self.h_status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        left_panel.addWidget(self.card1)
        
        # CARD 2: Engine Control
        self.card2 = QFrame()
        self.card2.setStyleSheet(self.card_css)
        c2_lay = QVBoxLayout(self.card2)
        c2_lay.setContentsMargins(15, 12, 15, 12)
        c2_lay.setSpacing(8)
        
        c2_hdr = QLabel("ENGINE CONTROL")
        c2_hdr.setStyleSheet("color: #A0A0B0; font-size: 11px; font-weight: bold; border: none;")
        c2_lay.addWidget(c2_hdr)
        
        self.btn_engine_start = QPushButton("⚡ ENGINE START ENABLED")
        self.btn_engine_start.setStyleSheet("""
            QPushButton {
                background-color: rgba(57, 255, 20, 0.15);
                color: #39FF14;
                border: 2px solid #39FF14;
                border-radius: 14px;
                padding: 12px;
                font-size: 15px;
                font-weight: 900;
            }
            QPushButton:hover { background-color: #39FF14; color: #000; }
        """)
        c2_lay.addWidget(self.btn_engine_start)
        
        self.c2_subtext = QLabel("Ignition active. Press start button.")
        self.c2_subtext.setStyleSheet("color: #A0A0B0; font-size: 11px; border: none;")
        self.c2_subtext.setWordWrap(True)
        c2_lay.addWidget(self.c2_subtext)
        
        left_panel.addWidget(self.card2)
        
        # CARD 3: Alerts
        self.card3 = QFrame()
        self.card3.setStyleSheet(self.card_css)
        c3_lay = QVBoxLayout(self.card3)
        c3_lay.setContentsMargins(15, 10, 15, 10)
        c3_lay.setSpacing(6)
        
        c3_hdr = QLabel("SYSTEM ALERTS")
        c3_hdr.setStyleSheet("color: #A0A0B0; font-size: 11px; font-weight: bold; border: none;")
        c3_lay.addWidget(c3_hdr)
        
        self.alert_box_list = QVBoxLayout()
        alerts_sample = [("🟢", "No Critical Alerts"), ("📷", "Camera Active"), ("🛑", "ABS Ready")]
        for icon, txt in alerts_sample:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{icon} <span style='color:#FFF; font-size:11px;'>{txt}</span>"))
            self.alert_box_list.addLayout(row)
            
        c3_lay.addLayout(self.alert_box_list)
        left_panel.addWidget(self.card3)
        
        # CARD 4: Ride Information
        self.card4 = QFrame()
        self.card4.setStyleSheet(self.card_css)
        c4_lay = QVBoxLayout(self.card4)
        c4_lay.setContentsMargins(15, 10, 15, 10)
        c4_lay.setSpacing(4)
        
        c4_hdr = QLabel("RIDE INFORMATION")
        c4_hdr.setStyleSheet("color: #A0A0B0; font-size: 11px; font-weight: bold; border: none;")
        c4_lay.addWidget(c4_hdr)
        
        for k, v in [("Trip Distance", "142.8 km"), ("Ride Time", "01:24:36"), ("Average Speed", "54 km/h")]:
            r = QHBoxLayout()
            l_k = QLabel(k); l_k.setStyleSheet("color:#A0A0B0; font-size:11px; border:none;")
            l_v = QLabel(v); l_v.setStyleSheet("color:#FFFFFF; font-size:12px; font-weight:bold; border:none;")
            r.addWidget(l_k); r.addStretch(); r.addWidget(l_v)
            c4_lay.addLayout(r)
            
        route_lbl = QLabel("🗺️ Route: City Expressway → Highway 1")
        route_lbl.setStyleSheet("color: #00E5FF; font-size: 10px; border: none; margin-top: 4px;")
        c4_lay.addWidget(route_lbl)
        
        left_panel.addWidget(self.card4)
        
        body_layout.addLayout(left_panel, stretch=28)
        
        # ------------------------------------------
        # CENTER PANEL (44% WIDTH, CAMERA = 60%, METER = 40% HEIGHT SPEC)
        # ------------------------------------------
        center_panel = QVBoxLayout()
        center_panel.setSpacing(14)
        
        # CAMERA PORTION = 60% HEIGHT SPEC
        self.cam_card = QFrame()
        self.cam_card.setStyleSheet(self.card_css)
        cam_lay = QVBoxLayout(self.cam_card)
        cam_lay.setContentsMargins(0, 0, 0, 0)
        
        self.cam_label = QLabel("CAMERA FEED INITIALIZING...")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_label.setStyleSheet("color: #A0A0B0; font-size: 14px; font-weight: bold; border: none;")
        cam_lay.addWidget(self.cam_label)
        
        # Overlays: ONLY LIVE, FPS, Helmet Confidence
        self.cam_live_overlay = QLabel("● LIVE", self.cam_card)
        self.cam_live_overlay.setStyleSheet("color: #FF3333; font-weight: bold; font-size: 12px; background: rgba(0,0,0,0.7); padding: 4px 10px; border-bottom-right-radius: 10px;")
        self.cam_live_overlay.move(0, 0)
        
        self.cam_fps_overlay = QLabel("FPS 30", self.cam_card)
        self.cam_fps_overlay.setStyleSheet("color: #00E5FF; font-weight: bold; font-size: 12px; background: rgba(0,0,0,0.7); padding: 4px 10px; border-bottom-left-radius: 10px;")
        
        self.cam_conf_overlay = QLabel("Helmet Confidence 99.8%", self.cam_card)
        self.cam_conf_overlay.setStyleSheet("color: #39FF14; font-weight: 900; font-size: 13px; background: rgba(0,0,0,0.8); padding: 4px 12px; border-top-left-radius: 10px;")
        self.cam_conf_overlay.adjustSize()
        
        center_panel.addWidget(self.cam_card, stretch=60)
        
        # METER PORTION = 40% HEIGHT SPEC
        center_bot_card = QFrame()
        center_bot_card.setStyleSheet(self.card_css)
        cb_lay = QVBoxLayout(center_bot_card)
        cb_lay.setContentsMargins(12, 8, 12, 8)
        cb_lay.setSpacing(6)
        
        # Speedometer & Vertical Switchgear Side Layout
        speed_switch_row = QHBoxLayout()
        speed_switch_row.setSpacing(8)
        
        # LEFT SWITCHGEAR
        left_sw = QVBoxLayout()
        left_sw.setSpacing(4)
        sw_css = "QPushButton { background-color: #121624; color: #FFF; border: 1px solid rgba(0,229,255,0.4); border-radius: 8px; padding: 6px 10px; font-size: 10px; font-weight: bold; } QPushButton:hover { border-color: #00E5FF; color: #00E5FF; }"
        
        self.btn_hl = QPushButton("💡 Headlight")
        self.btn_ind = QPushButton("🔀 Indicators")
        self.btn_abs = QPushButton("🛑 ABS")
        self.btn_hrn = QPushButton("📢 Horn")
        self.btn_cr = QPushButton("🏎️ Cruise")
        
        for b in (self.btn_hl, self.btn_ind, self.btn_abs, self.btn_hrn, self.btn_cr):
            b.setStyleSheet(sw_css)
            left_sw.addWidget(b)
            
        self.btn_hl.clicked.connect(self.toggle_headlight)
        self.btn_ind.clicked.connect(self.toggle_indicators)
        self.btn_abs.clicked.connect(self.toggle_abs)
        self.btn_hrn.clicked.connect(lambda: speaker.speak("Beep beep", force=True))
        self.btn_cr.clicked.connect(self.toggle_cruise)
        
        speed_switch_row.addLayout(left_sw)
        
        # CENTER SPEEDOMETER DIAL WITH 20, 40, 60 MARKERS
        self.speedometer = CenterSpeedometer()
        speed_switch_row.addWidget(self.speedometer, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # RIGHT SWITCHGEAR
        right_sw = QVBoxLayout()
        right_sw.setSpacing(4)
        
        self.btn_g_up = QPushButton("⬆️ Gear +")
        self.btn_g_down = QPushButton("⬇️ Gear -")
        self.btn_m_sport = QPushButton("🏎️ Sport Mode")
        self.btn_m_eco = QPushButton("🌱 Eco Mode")
        self.btn_m_pwr = QPushButton("⚡ Power Mode")
        
        for b in (self.btn_g_up, self.btn_g_down, self.btn_m_sport, self.btn_m_eco, self.btn_m_pwr):
            b.setStyleSheet(sw_css)
            right_sw.addWidget(b)
            
        self.btn_g_up.clicked.connect(self.manual_gear_up)
        self.btn_g_down.clicked.connect(self.manual_gear_down)
        self.btn_m_sport.clicked.connect(lambda: self.set_ride_mode("SPORT"))
        self.btn_m_eco.clicked.connect(lambda: self.set_ride_mode("ECO"))
        self.btn_m_pwr.clicked.connect(lambda: self.set_ride_mode("POWER"))
        
        speed_switch_row.addLayout(right_sw)
        cb_lay.addLayout(speed_switch_row)
        
        # BELOW SPEEDOMETER: 4 EQUAL-WIDTH ACTION BUTTONS SPEC
        act_row = QHBoxLayout()
        act_row.setSpacing(8)
        
        act_css = "QPushButton { background-color: #121626; color: #FFF; border: 1.5px solid #00E5FF; border-radius: 10px; padding: 8px; font-size: 12px; font-weight: 900; } QPushButton:hover { background-color: #00E5FF; color: #000; }"
        
        self.btn_e_start = QPushButton("⚡ Engine Start")
        self.btn_brake = QPushButton("🛑 Brake")
        self.btn_release = QPushButton("🔄 Release")
        self.btn_emg = QPushButton("🚨 Emergency Stop")
        self.btn_emg.setStyleSheet("QPushButton { background-color: rgba(255,51,51,0.15); color: #FF3333; border: 1.5px solid #FF3333; border-radius: 10px; padding: 8px; font-size: 12px; font-weight: 900; } QPushButton:hover { background-color: #FF3333; color: #FFF; }")
        
        for b in (self.btn_e_start, self.btn_brake, self.btn_release):
            b.setStyleSheet(act_css)
            
        act_row.addWidget(self.btn_e_start, stretch=1)
        act_row.addWidget(self.btn_brake, stretch=1)
        act_row.addWidget(self.btn_release, stretch=1)
        act_row.addWidget(self.btn_emg, stretch=1)
        
        self.btn_e_start.clicked.connect(self.manual_accelerate)
        self.btn_brake.clicked.connect(self.manual_brake)
        self.btn_release.clicked.connect(self.manual_idle)
        self.btn_emg.clicked.connect(self.toggle_helmet_simulation)
        
        cb_lay.addLayout(act_row)
        center_panel.addWidget(center_bot_card, stretch=40)
        
        body_layout.addLayout(center_panel, stretch=44)
        
        # ------------------------------------------
        # RIGHT PANEL (28% WIDTH - SLIGHTLY WIDER)
        # ------------------------------------------
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)
        
        # TOP CARD: AI Analytics (Horizontal progress bars)
        self.right_top_card = QFrame()
        self.right_top_card.setStyleSheet(self.card_css)
        rt_lay = QVBoxLayout(self.right_top_card)
        rt_lay.setContentsMargins(15, 12, 15, 12)
        rt_lay.setSpacing(10)
        
        rt_hdr = QLabel("AI ANALYTICS")
        rt_hdr.setStyleSheet("color: #A0A0B0; font-size: 11px; font-weight: bold; border: none;")
        rt_lay.addWidget(rt_hdr)
        
        # 1. Helmet Confidence
        rt_lay.addWidget(QLabel("<span style='color:#FFF; font-size:11px;'>Helmet Detection Confidence</span> <b style='color:#39FF14;'>99.8%</b>"))
        p1 = QProgressBar()
        p1.setValue(99)
        p1.setStyleSheet("QProgressBar { background: #121520; border-radius: 4px; height: 8px; border: none; } QProgressBar::chunk { background-color: #39FF14; border-radius: 4px; }")
        p1.setTextVisible(False)
        rt_lay.addWidget(p1)
        
        # 2. Current Status
        rt_lay.addWidget(QLabel("<span style='color:#FFF; font-size:11px;'>Current Detection Status</span> <b style='color:#00E5FF;'>ACTIVE</b>"))
        
        # 3. Camera FPS
        rt_lay.addWidget(QLabel("<span style='color:#FFF; font-size:11px;'>Camera FPS</span> <b style='color:#00E5FF;'>30 FPS</b>"))
        p2 = QProgressBar()
        p2.setValue(100)
        p2.setStyleSheet("QProgressBar { background: #121520; border-radius: 4px; height: 8px; border: none; } QProgressBar::chunk { background-color: #00E5FF; border-radius: 4px; }")
        p2.setTextVisible(False)
        rt_lay.addWidget(p2)
        
        # 4. Latency
        rt_lay.addWidget(QLabel("<span style='color:#FFF; font-size:11px;'>Detection Latency</span> <b style='color:#FFFFFF;'>12 ms</b>"))
        p3 = QProgressBar()
        p3.setValue(20)
        p3.setStyleSheet("QProgressBar { background: #121520; border-radius: 4px; height: 8px; border: none; } QProgressBar::chunk { background-color: #00E5FF; border-radius: 4px; }")
        p3.setTextVisible(False)
        rt_lay.addWidget(p3)
        
        right_panel.addWidget(self.right_top_card, stretch=45)
        
        # BOTTOM CARD: Settings (Status Rows with Icons & Toggles)
        self.right_bot_card = QFrame()
        self.right_bot_card.setStyleSheet(self.card_css)
        rb_lay = QVBoxLayout(self.right_bot_card)
        rb_lay.setContentsMargins(15, 12, 15, 12)
        rb_lay.setSpacing(6)
        
        rb_hdr = QLabel("SYSTEM SETTINGS")
        rb_hdr.setStyleSheet("color: #A0A0B0; font-size: 11px; font-weight: bold; border: none;")
        rb_lay.addWidget(rb_hdr)
        
        settings_rows = [
            ("📷 Camera Status", "ONLINE", "#39FF14"),
            ("🎯 Sensitivity", "HIGH (0.75)", "#00E5FF"),
            ("🔒 Engine Lock", "ENABLED", "#39FF14"),
            ("🔊 Alert Sound", "ACTIVE", "#39FF14"),
            ("🤖 AI Detection", "RUNNING", "#00E5FF"),
            ("📶 Wi-Fi Status", "CONNECTED", "#00E5FF"),
            ("📡 Bluetooth", "PAIRED", "#FFFFFF"),
            ("🛰️ GPS Signal", "12 SATS", "#FFFFFF")
        ]
        
        for name, val, col in settings_rows:
            r = QHBoxLayout()
            l_n = QLabel(name); l_n.setStyleSheet("color:#FFF; font-size:11px; border:none;")
            l_v = QLabel(val); l_v.setStyleSheet(f"color:{col}; font-size:10px; font-weight:bold; border:none;")
            r.addWidget(l_n); r.addStretch(); r.addWidget(l_v)
            rb_lay.addLayout(r)
            
        right_panel.addWidget(self.right_bot_card, stretch=55)
        body_layout.addLayout(right_panel, stretch=28)
        
        main_layout.addLayout(body_layout, stretch=1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'cam_card') and hasattr(self, 'cam_fps_overlay'):
            self.cam_fps_overlay.move(self.cam_card.width() - self.cam_fps_overlay.width(), 0)
            self.cam_conf_overlay.move(self.cam_card.width() - self.cam_conf_overlay.width(), self.cam_card.height() - self.cam_conf_overlay.height())

    def toggle_headlight(self):
        states = ["AUTO", "HIGH BEAM", "OFF"]
        idx = (states.index(self.headlight_state) + 1) % len(states)
        self.headlight_state = states[idx]
        self.btn_hl.setText(f"💡 {self.headlight_state}")

    def toggle_indicators(self):
        states = ["OFF", "LEFT ⬅️", "RIGHT ➡️", "HAZARD ⚠️"]
        idx = (states.index(self.indicators_state) + 1) % len(states)
        self.indicators_state = states[idx]
        self.btn_ind.setText(f"🔀 {self.indicators_state}")

    def toggle_abs(self):
        self.abs_state = "OFF" if self.abs_state == "ON" else "ON"
        self.btn_abs.setText(f"🛑 ABS: {self.abs_state}")

    def toggle_cruise(self):
        self.cruise_active = not self.cruise_active
        self.btn_cr.setText(f"🏎️ Cruise: {'ON' if self.cruise_active else 'OFF'}")

    def set_ride_mode(self, mode):
        self.ride_mode = mode
        speaker.speak(f"{mode} mode selected.")

    def manual_gear_up(self):
        gears = ["N", "1", "2", "3", "4", "5", "6"]
        if self.gear in gears:
            idx = min(len(gears) - 1, gears.index(self.gear) + 1)
            self.gear = gears[idx]

    def manual_gear_down(self):
        gears = ["N", "1", "2", "3", "4", "5", "6"]
        if self.gear in gears:
            idx = max(0, gears.index(self.gear) - 1)
            self.gear = gears[idx]

    def manual_accelerate(self):
        if not self.helmet_detected:
            speaker.speak("Engine locked. Helmet required.")
            return
        self.is_braking = False
        self.throttle_input = min(1.0, self.throttle_input + 0.25)
        self.speed += 8.0

    def manual_brake(self):
        self.throttle_input = 0.0
        self.is_braking = True
        self.speed = max(0.0, self.speed - 16.0)

    def manual_idle(self):
        self.throttle_input = 0.0
        self.is_braking = False

    def toggle_helmet_simulation(self):
        """Toggle between Helmet Detected (Green) and Helmet Missing (Red Locked)."""
        self.helmet_detected = not self.helmet_detected
        
        if self.helmet_detected:
            self.helmet_circle_widget.set_detected(True)
            self.h_status_lbl.setText("HELMET DETECTED")
            self.h_status_lbl.setStyleSheet("color: #39FF14; font-size: 16px; font-weight: 900; border: none;")
            
            self.card2.setStyleSheet(self.card_css)
            self.btn_engine_start.setText("⚡ ENGINE START ENABLED")
            self.btn_engine_start.setStyleSheet("""
                QPushButton {
                    background-color: rgba(57, 255, 20, 0.15);
                    color: #39FF14;
                    border: 2px solid #39FF14;
                    border-radius: 14px;
                    padding: 12px;
                    font-size: 15px;
                    font-weight: 900;
                }
                QPushButton:hover { background-color: #39FF14; color: #000; }
            """)
            self.c2_subtext.setText("Ignition active. Press start button.")
            speaker.speak("Helmet detected. Now you can ride the bike.")
        else:
            self.helmet_circle_widget.set_detected(False)
            self.h_status_lbl.setText("HELMET NOT DETECTED")
            self.h_status_lbl.setStyleSheet("color: #FF3333; font-size: 16px; font-weight: 900; border: none;")
            
            self.card2.setStyleSheet("QFrame { background-color: rgba(40, 10, 15, 0.95); border: 2px solid #FF3333; border-radius: 20px; }")
            self.btn_engine_start.setText("🚫 ENGINE LOCKED")
            self.btn_engine_start.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 51, 51, 0.2);
                    color: #FF3333;
                    border: 2px solid #FF3333;
                    border-radius: 14px;
                    padding: 12px;
                    font-size: 15px;
                    font-weight: 900;
                }
            """)
            self.c2_subtext.setText("Motorcycle cannot start without helmet verification.")
            self.speed = 0.0
            self.throttle_input = 0.0
            speaker.speak("Engine locked. Please wear helmet.")

    def calculate_auto_gear_and_rpm(self):
        """Auto transmission gear shift logic."""
        if self.speed < 0.5:
            if self.throttle_input > 0:
                gear = "1"; rpm = 1200.0 + self.throttle_input * 1500.0
            else:
                gear = "N"; rpm = 1000.0
            return gear, rpm

        if self.speed <= 25.0:
            gear = "1"; ratio = self.speed / 25.0; rpm = 1500.0 + ratio * 5000.0
        elif self.speed <= 45.0:
            gear = "2"; ratio = (self.speed - 25.0) / 20.0; rpm = 2500.0 + ratio * 4500.0
        elif self.speed <= 70.0:
            gear = "3"; ratio = (self.speed - 45.0) / 25.0; rpm = 3000.0 + ratio * 4200.0
        elif self.speed <= 95.0:
            gear = "4"; ratio = (self.speed - 70.0) / 25.0; rpm = 3400.0 + ratio * 4000.0
        elif self.speed <= 125.0:
            gear = "5"; ratio = (self.speed - 95.0) / 30.0; rpm = 3800.0 + ratio * 3800.0
        else:
            gear = "6"; ratio = min(1.0, (self.speed - 125.0) / 75.0); rpm = 4000.0 + ratio * 6500.0

        rpm += self.throttle_input * 600.0
        return gear, min(12000.0, rpm)

    def update_telemetry(self):
        if not self.helmet_detected:
            self.throttle_input = 0.0
            self.speed = max(0.0, self.speed - 3.5)

        if self.throttle_input > 0:
            self.speed += 1.8 * self.throttle_input
            self.throttle_input = max(0.0, self.throttle_input - 0.02)
        elif self.is_braking:
            self.speed = max(0.0, self.speed - 3.5)
            if self.speed == 0: self.is_braking = False
        else:
            self.speed = max(0.0, self.speed - 0.7)

        if self.speed > 0:
            self.fuel = max(0.0, self.fuel - 0.003)

        auto_gear, rpm = self.calculate_auto_gear_and_rpm()
        if self.speed == 0 or auto_gear != "N":
            self.gear = auto_gear
        self.rpm = rpm

        # Update Speedometer
        self.speedometer.set_telemetry(self.speed, self.rpm, self.gear, self.fuel, (self.gear == "N"), self.ride_mode)

    @pyqtSlot(QImage)
    def update_camera_feed(self, qimg):
        pix = QPixmap.fromImage(qimg).scaled(self.cam_card.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.cam_label.setPixmap(pix)

    @pyqtSlot(dict)
    def update_live_stats(self, stats):
        conf = stats.get("confidence", 0.998) * 100.0
        fps = stats.get("fps", 30)
        self.cam_fps_overlay.setText(f"FPS {fps:.0f}")
        self.cam_conf_overlay.setText(f"Helmet Confidence {conf:.1f}%")

    @pyqtSlot(str)
    def trigger_adas_alert(self, msg):
        if self.helmet_detected:
            self.toggle_helmet_simulation()

    @pyqtSlot()
    def clear_adas_alert(self):
        if not self.helmet_detected:
            self.toggle_helmet_simulation()
