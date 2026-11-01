import math
import time
from datetime import datetime

import psutil
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QImage, QFontMetrics, QPolygonF
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
                             QProgressBar, QPushButton, QSizePolicy)

from src import theme
from src.audio_system import speaker
from src.theme import qc
from src.ui_kit import repolish, make_card, tag, MetricTile


class HelmetRing(QWidget):
    """Large ring around the RideShield helmet mark. Green when a helmet is detected, coral when not."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 150)
        self.detected = True
        self.mark = theme.brand("mark-night.png")

    def set_detected(self, detected):
        self.detected = detected
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        c = QPointF(w / 2, h / 2)
        r = min(w, h) / 2 - 8
        col = qc(theme.OK) if self.detected else qc(theme.BAD)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qc(theme.DEVICE))
        p.drawEllipse(c, r, r)
        p.setPen(QPen(col, 5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(c, r - 3, r - 3)
        if not self.mark.isNull():
            size = int(r * 1.15)
            pix = self.mark.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap(int(c.x() - pix.width() / 2), int(c.y() - pix.height() / 2), pix)
        if not self.detected:
            p.setPen(QPen(col, 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            d = r * 0.72
            p.drawLine(QPointF(c.x() - d * 0.7, c.y() + d * 0.7), QPointF(c.x() + d * 0.7, c.y() - d * 0.7))


class ClusterDial(QWidget):
    """The bike cluster: segmented speed ring, inner RPM ring, gear, ride mode and telltale lights."""

    SPEED_MAX = 240.0
    RPM_MAX = 12000.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(560, 430)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.speed = 0.0
        self.rpm = 1000.0
        self.gear = "N"
        self.ride_mode = "SPORT"
        self.helmet_ok = True
        self.engine_locked = False
        self.indicators = "OFF"
        self.headlight = "AUTO"
        self.abs_on = True
        self.cruise = False
        self.blink = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(450)

    def _tick(self):
        self.blink = not self.blink
        if self.indicators != "OFF":
            self.update()

    def set_telemetry(self, speed, rpm, gear, ride_mode):
        self.speed = max(0.0, min(self.SPEED_MAX, speed))
        self.rpm = max(0.0, min(self.RPM_MAX, rpm))
        self.gear = str(gear)
        self.ride_mode = ride_mode
        self.update()

    def set_switches(self, helmet_ok, engine_locked, indicators, headlight, abs_on, cruise):
        self.helmet_ok = helmet_ok
        self.engine_locked = engine_locked
        self.indicators = indicators
        self.headlight = headlight
        self.abs_on = abs_on
        self.cruise = cruise
        self.update()

    # ---- drawing helpers ----
    def _pt(self, cx, cy, r, ang_deg):
        a = math.radians(ang_deg)
        return QPointF(cx + r * math.cos(a), cy - r * math.sin(a))

    def _ring(self, p, cx, cy, r_in, r_out, count, lit, lit_col, redline_from=None, dim=None):
        dim = dim or qc(theme.LINE2)
        for i in range(count):
            frac = i / (count - 1)
            ang = 225 - 270 * frac
            on = i < lit
            col = dim
            if on:
                col = qc(theme.BAD) if (redline_from is not None and frac >= redline_from) else lit_col
            pen = QPen(col, max(2.0, (r_out - r_in) * 0.32), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(self._pt(cx, cy, r_in, ang), self._pt(cx, cy, r_out, ang))

    def _chip(self, p, x, y, text, color, align_right=False):
        p.setFont(theme.body_font(13, True))
        fm = QFontMetrics(p.font())
        w = fm.horizontalAdvance(text) + 26
        h = 30
        rx = x - w if align_right else x
        rect = QRectF(rx, y, w, h)
        p.setPen(Qt.PenStyle.NoPen)
        fill = QColor(color)
        fill.setAlpha(40)
        p.setBrush(fill)
        p.drawRoundedRect(rect, 15, 15)
        p.setPen(QColor(color))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        return h + 8

    def _arrow(self, p, x, y, left, color):
        s = 12
        poly = QPolygonF()
        if left:
            poly << QPointF(x, y + s) << QPointF(x + 2 * s, y) << QPointF(x + 2 * s, y + 2 * s)
        else:
            poly << QPointF(x + 2 * s, y + s) << QPointF(x, y) << QPointF(x, y + 2 * s)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon(poly)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Device surface
        p.setPen(QPen(qc(theme.LINE), 1))
        p.setBrush(qc(theme.DEVICE))
        p.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 22, 22)

        cx, cy = w / 2, h * 0.50
        R = min(w * 0.33, h * 0.40)

        # Speed ring (segments) and numerals
        lit = int(round(self.speed / self.SPEED_MAX * 60))
        self._ring(p, cx, cy, R * 0.90, R, 61, lit, qc(theme.ACCENT), redline_from=0.9)
        p.setFont(theme.body_font(max(11, int(R * 0.075)), True))
        p.setPen(qc(theme.FAINT))
        for v in range(0, 241, 40):
            ang = 225 - 270 * (v / self.SPEED_MAX)
            pt = self._pt(cx, cy, R * 0.79, ang)
            p.drawText(QRectF(pt.x() - 22, pt.y() - 10, 44, 20), Qt.AlignmentFlag.AlignCenter, str(v))

        # RPM ring (inside the speed ring; red from 82% of the range)
        rl = int(round(self.rpm / self.RPM_MAX * 48))
        self._ring(p, cx, cy, R * 0.60, R * 0.67, 49, rl, qc(theme.VIOLET, 235), redline_from=0.82)

        # Speed number
        p.setPen(qc(theme.TEXT))
        p.setFont(theme.display_font(int(R * 0.62)))
        p.drawText(QRectF(cx - R * 0.5, cy - R * 0.46, R, R * 0.62), Qt.AlignmentFlag.AlignCenter, f"{int(self.speed)}")
        p.setFont(theme.semi_font(int(R * 0.115)))
        p.setPen(qc(theme.ACCENT))
        p.drawText(QRectF(cx - 60, cy + R * 0.17, 120, R * 0.16), Qt.AlignmentFlag.AlignCenter, "KM/H")

        # Gear, ride mode and RPM readout sit in the open gap at the bottom of the dial
        neutral = self.gear == "N"
        gcol = qc(theme.ACCENT) if neutral else qc(theme.OK)
        gb = QRectF(cx - R * 0.15, cy + R * 0.40, R * 0.30, R * 0.20)
        p.setPen(QPen(gcol, 2))
        p.setBrush(qc(theme.SURFACE))
        p.drawRoundedRect(gb, 10, 10)
        p.setPen(gcol)
        p.setFont(theme.display_font(int(R * 0.17)))
        p.drawText(gb, Qt.AlignmentFlag.AlignCenter, self.gear)
        mode_col = {"SPORT": theme.BAD, "ECO": theme.OK, "POWER": theme.WARN}.get(self.ride_mode, theme.ACCENT)
        p.setFont(theme.semi_font(int(R * 0.10)))
        p.setPen(qc(mode_col))
        p.drawText(QRectF(cx - R * 0.4, cy + R * 0.64, R * 0.8, R * 0.14), Qt.AlignmentFlag.AlignCenter, self.ride_mode)
        p.setFont(theme.body_font(max(10, int(R * 0.058)), True))
        p.setPen(qc(theme.FAINT))
        p.drawText(QRectF(cx - R * 0.5, cy + R * 0.82, R, R * 0.12), Qt.AlignmentFlag.AlignCenter, f"{int(self.rpm):,} RPM")
        # Telltales, left stack
        x, y = 20, 20
        if self.helmet_ok:
            y += self._chip(p, x, y, "HELMET OK", theme.OK)
        else:
            y += self._chip(p, x, y, "NO HELMET", theme.BAD)
        if self.engine_locked:
            y += self._chip(p, x, y, "ENGINE LOCKED", theme.BAD)
        else:
            y += self._chip(p, x, y, "ENGINE READY", theme.OK)
        y += self._chip(p, x, y, "ABS ON" if self.abs_on else "ABS OFF", theme.OK if self.abs_on else theme.WARN)

        # Telltales, right stack
        xr, yr = w - 20, 20
        beam_col = theme.ACCENT if self.headlight == "HIGH BEAM" else (theme.MUTED if self.headlight == "OFF" else theme.OK)
        yr += self._chip(p, xr, yr, f"LIGHTS {self.headlight}", beam_col, align_right=True)
        if self.cruise:
            yr += self._chip(p, xr, yr, "CRUISE ON", theme.ACCENT, align_right=True)
        else:
            yr += self._chip(p, xr, yr, "CRUISE OFF", theme.FAINT, align_right=True)

        # Indicator arrows beside the dial top
        show_left = self.indicators in ("LEFT", "HAZARD") and self.blink
        show_right = self.indicators in ("RIGHT", "HAZARD") and self.blink
        if show_left:
            self._arrow(p, cx - R * 0.42, cy - R * 1.02, True, theme.OK)
        if show_right:
            self._arrow(p, cx + R * 0.42 - 24, cy - R * 1.02, False, theme.OK)


class DashboardPage(QWidget):
    """Main screen: a motorcycle cluster with live detection metrics, the camera view and the bike controls."""

    def __init__(self, ai_engine, alert_system, main_window, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        self.main_window = main_window

        # Simulated ride telemetry (there is no vehicle connected). Everything below is labelled as demo data.
        self.speed = 0.0
        self.rpm = 1000.0
        self.gear = "N"
        self.fuel = 75.0
        self.ride_mode = "SPORT"
        self.throttle_input = 0.0
        self.is_braking = False

        self.helmet_detected = True
        self.headlight_state = "AUTO"
        self.indicators_state = "OFF"
        self.abs_state = "ON"
        self.cruise_active = False

        # Real session metrics, filled from the detector
        self.started = time.monotonic()
        self.frames = 0
        self.frames_with_detection = 0
        self.frames_helmet = 0
        self.total_detections = 0
        self.fps = 0.0
        self.latency = 0.0
        self.confidence = 0.0
        self.last_frame_time = 0.0
        self.alert_log = []

        self.init_ui()
        mode = self.alert_system.safety_mode if self.alert_system else "Monitor Only"
        self.lock_mode_lbl.setText(f"Safety mode: {mode}. In Smart Lock mode the lock is simulated.")
        self.refresh_cluster_switches()

        self.dash_timer = QTimer(self)
        self.dash_timer.timeout.connect(self.update_telemetry)
        self.dash_timer.start(50)

        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.update_system)
        self.system_timer.start(1000)
        psutil.cpu_percent(None)
        self.update_system()

        if self.ai_engine:
            self.ai_engine.image_update.connect(self.update_camera_feed)
        if self.alert_system:
            self.alert_system.alert_triggered.connect(self.trigger_adas_alert)
            self.alert_system.alert_cleared.connect(self.clear_adas_alert)

    # ------------------------------------------------------------------ UI
    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 12)
        root.setSpacing(12)

        # ---- top bar
        bar = QFrame()
        bar.setProperty("class", "device")
        bar.setFixedHeight(76)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(22, 0, 22, 0)
        logo = QLabel()
        pix = theme.brand("lockup-night.png")
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(44, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("RIDESHIELD AI")
        bl.addWidget(logo)
        bl.addStretch()

        self.clock_lbl = QLabel("--:--")
        self.clock_lbl.setStyleSheet(theme.css_display(44))
        self.date_lbl = QLabel("")
        self.date_lbl.setProperty("class", "faint")
        clock_box = QVBoxLayout()
        clock_box.setSpacing(0)
        clock_box.addWidget(self.clock_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        clock_box.addWidget(self.date_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        bl.addLayout(clock_box)
        bl.addStretch()

        self.fuel_lbl = QLabel()
        self.bat_lbl = QLabel()
        self.temp_lbl = QLabel()
        for l in (self.fuel_lbl, self.bat_lbl, self.temp_lbl):
            l.setProperty("class", "muted")
            l.setTextFormat(Qt.TextFormat.RichText)
            bl.addWidget(l)
            bl.addSpacing(14)
        bl.addWidget(tag("DEMO RIDE DATA"))
        root.addWidget(bar)

        # ---- body
        body = QHBoxLayout()
        body.setSpacing(12)
        body.addLayout(self.build_left(), stretch=26)
        body.addLayout(self.build_center(), stretch=48)
        body.addLayout(self.build_right(), stretch=26)
        root.addLayout(body, stretch=1)

    def build_left(self):
        col = QVBoxLayout()
        col.setSpacing(12)

        # Helmet status
        self.card_helmet, hl = make_card("HELMET STATUS")
        self.helmet_ring = HelmetRing()
        hl.addWidget(self.helmet_ring, alignment=Qt.AlignmentFlag.AlignCenter, stretch=1)
        self.h_status_lbl = QLabel("HELMET DETECTED")
        self.h_status_lbl.setStyleSheet(theme.css_display(30, theme.OK))
        self.h_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(self.h_status_lbl)
        self.h_conf_lbl = QLabel("Waiting for the camera")
        self.h_conf_lbl.setProperty("class", "faint")
        self.h_conf_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(self.h_conf_lbl)
        col.addWidget(self.card_helmet, stretch=5)

        # Engine control
        self.card_engine, el = make_card("ENGINE CONTROL")
        self.btn_engine_start = QPushButton("ENGINE START ENABLED")
        self.btn_engine_start.setProperty("class", "engine")
        self.btn_engine_start.setProperty("state", "ok")
        el.addWidget(self.btn_engine_start)
        self.c2_subtext = QLabel("Ignition ready. Press start.")
        self.c2_subtext.setProperty("class", "muted")
        self.c2_subtext.setWordWrap(True)
        el.addWidget(self.c2_subtext)
        self.lock_mode_lbl = QLabel("")
        self.lock_mode_lbl.setProperty("class", "faint")
        el.addWidget(self.lock_mode_lbl)
        col.addWidget(self.card_engine, stretch=3)

        # System alerts (real events)
        self.card_alerts, al = make_card("SYSTEM ALERTS")
        self.alert_rows = QVBoxLayout()
        self.alert_rows.setSpacing(4)
        al.addLayout(self.alert_rows)
        col.addWidget(self.card_alerts, stretch=3)
        self.render_alerts()

        # Ride information (demo)
        card, rl = make_card("RIDE INFORMATION")
        rl.itemAt(0).widget().setText("RIDE INFORMATION  (demo)")
        self.ride_vals = {}
        for k, v in (("Trip distance", "0.0 km"), ("Ride time", "00:00:00"), ("Average speed", "0 km/h"), ("Odometer", "12,480 km")):
            row = QHBoxLayout()
            a = QLabel(k)
            a.setProperty("class", "muted")
            b = QLabel(v)
            b.setStyleSheet(theme.css_semi(20))
            self.ride_vals[k] = b
            row.addWidget(a)
            row.addStretch()
            row.addWidget(b)
            rl.addLayout(row)
        col.addWidget(card, stretch=3)
        return col

    def build_center(self):
        col = QVBoxLayout()
        col.setSpacing(12)

        self.cluster = ClusterDial()
        col.addWidget(self.cluster, stretch=7)

        # Live metrics (real values)
        grid = QGridLayout()
        grid.setSpacing(10)
        self.m_fps = MetricTile("AI FPS")
        self.m_lat = MetricTile("LATENCY", "ms")
        self.m_conf = MetricTile("HELMET CONFIDENCE", "%")
        self.m_det = MetricTile("DETECTIONS")
        self.m_cpu = MetricTile("CPU", "%")
        self.m_ram = MetricTile("MEMORY", "%")
        self.m_comp = MetricTile("HELMET-ON FRAMES", "%")
        self.m_up = MetricTile("SESSION")
        tiles = [self.m_fps, self.m_lat, self.m_conf, self.m_det, self.m_cpu, self.m_ram, self.m_comp, self.m_up]
        for i, t in enumerate(tiles):
            grid.addWidget(t, i // 4, i % 4)
        col.addLayout(grid, stretch=3)

        # Switchgear
        sw = QGridLayout()
        sw.setSpacing(8)
        self.btn_hl = QPushButton("Headlight: AUTO")
        self.btn_ind = QPushButton("Indicators: OFF")
        self.btn_abs = QPushButton("ABS: ON")
        self.btn_hrn = QPushButton("Horn")
        self.btn_cr = QPushButton("Cruise: OFF")
        self.btn_g_up = QPushButton("Gear +")
        self.btn_g_down = QPushButton("Gear -")
        self.btn_m_sport = QPushButton("Sport")
        self.btn_m_eco = QPushButton("Eco")
        self.btn_m_pwr = QPushButton("Power")
        buttons = [self.btn_hl, self.btn_ind, self.btn_abs, self.btn_hrn, self.btn_cr,
                   self.btn_g_up, self.btn_g_down, self.btn_m_sport, self.btn_m_eco, self.btn_m_pwr]
        for i, b in enumerate(buttons):
            b.setProperty("class", "switch")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            sw.addWidget(b, i // 5, i % 5)
        self.btn_hl.clicked.connect(self.toggle_headlight)
        self.btn_ind.clicked.connect(self.toggle_indicators)
        self.btn_abs.clicked.connect(self.toggle_abs)
        self.btn_hrn.clicked.connect(lambda: speaker.speak("Beep beep", force=True))
        self.btn_cr.clicked.connect(self.toggle_cruise)
        self.btn_g_up.clicked.connect(self.manual_gear_up)
        self.btn_g_down.clicked.connect(self.manual_gear_down)
        self.btn_m_sport.clicked.connect(lambda: self.set_ride_mode("SPORT"))
        self.btn_m_eco.clicked.connect(lambda: self.set_ride_mode("ECO"))
        self.btn_m_pwr.clicked.connect(lambda: self.set_ride_mode("POWER"))
        col.addLayout(sw)

        # Actions
        act = QHBoxLayout()
        act.setSpacing(10)
        self.btn_e_start = QPushButton("Engine start")
        self.btn_brake = QPushButton("Brake")
        self.btn_release = QPushButton("Release")
        self.btn_emg = QPushButton("Emergency stop")
        for b in (self.btn_e_start, self.btn_brake, self.btn_release):
            b.setProperty("class", "action")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_emg.setProperty("class", "danger")
        self.btn_emg.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_emg.setToolTip("Toggles the helmet-missing engine lock demonstration.")
        for b in (self.btn_e_start, self.btn_brake, self.btn_release, self.btn_emg):
            act.addWidget(b, stretch=1)
        self.btn_e_start.clicked.connect(self.manual_accelerate)
        self.btn_brake.clicked.connect(self.manual_brake)
        self.btn_release.clicked.connect(self.manual_idle)
        self.btn_emg.clicked.connect(self.toggle_helmet_simulation)
        col.addLayout(act)
        return col

    def build_right(self):
        col = QVBoxLayout()
        col.setSpacing(12)

        # Camera
        self.cam_card = QFrame()
        self.cam_card.setProperty("class", "device")
        cl = QVBoxLayout(self.cam_card)
        cl.setContentsMargins(0, 0, 0, 0)
        self.cam_label = QLabel("Camera starting")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_label.setProperty("class", "muted")
        self.cam_label.setMinimumSize(280, 200)
        self.cam_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        cl.addWidget(self.cam_label)
        chip_css = "background: rgba(7,7,12,0.82); font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 10px;"
        self.cam_live_overlay = QLabel("LIVE", self.cam_card)
        self.cam_live_overlay.setStyleSheet(f"color: {theme.BAD}; {chip_css}")
        self.cam_live_overlay.move(12, 12)
        self.cam_fps_overlay = QLabel("FPS --", self.cam_card)
        self.cam_fps_overlay.setStyleSheet(f"color: {theme.ACCENT}; {chip_css}")
        self.cam_conf_overlay = QLabel("No detection", self.cam_card)
        self.cam_conf_overlay.setStyleSheet(f"color: {theme.MUTED}; {chip_css}")
        self.cam_conf_overlay.adjustSize()
        col.addWidget(self.cam_card, stretch=5)

        # AI analytics (real)
        card, al = make_card("AI ANALYTICS  (live)")
        self.bars = {}
        for key, label, color in (("conf", "Helmet confidence", theme.OK), ("fps", "Camera FPS", theme.ACCENT), ("lat", "Detection latency", theme.VIOLET)):
            row = QHBoxLayout()
            name = QLabel(label)
            name.setProperty("class", "muted")
            val = QLabel("--")
            val.setStyleSheet(theme.css_semi(20))
            row.addWidget(name)
            row.addStretch()
            row.addWidget(val)
            bar = QProgressBar()
            bar.setTextVisible(False)
            bar.setFixedHeight(6)
            bar.setRange(0, 100)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}")
            al.addLayout(row)
            al.addWidget(bar)
            self.bars[key] = (val, bar)
        self.model_lbl = QLabel("")
        self.model_lbl.setProperty("class", "faint")
        al.addWidget(self.model_lbl)
        col.addWidget(card, stretch=3)

        # System status
        card, sl = make_card("SYSTEM")
        self.status_vals = {}
        rows = [
            ("Camera", "WAITING", "real"),
            ("AI detection", "STARTING", "real"),
            ("Safety mode", "--", "real"),
            ("Alert sound", "ACTIVE", "real"),
            ("Wi-Fi", "CONNECTED", "demo"),
            ("Bluetooth", "PAIRED", "demo"),
            ("GPS", "12 SATS", "demo"),
        ]
        for name, val, kind in rows:
            row = QHBoxLayout()
            a = QLabel(name + ("  (demo)" if kind == "demo" else ""))
            a.setProperty("class", "muted" if kind == "real" else "faint")
            b = QLabel(val)
            b.setStyleSheet(theme.css_semi(18))
            self.status_vals[name] = b
            row.addWidget(a)
            row.addStretch()
            row.addWidget(b)
            sl.addLayout(row)
        col.addWidget(card, stretch=3)
        self.apply_status("Camera", "WAITING", theme.WARN)
        self.apply_status("AI detection", "STARTING", theme.WARN)
        self.apply_status("Alert sound", "ACTIVE", theme.OK)
        for n, c in (("Wi-Fi", theme.FAINT), ("Bluetooth", theme.FAINT), ("GPS", theme.FAINT)):
            self.apply_status(n, self.status_vals[n].text(), c)
        mode = self.alert_system.safety_mode if self.alert_system else "Monitor Only"
        self.apply_status("Safety mode", mode.upper(), theme.ACCENT)
        return col

    def apply_status(self, name, text, color):
        lbl = self.status_vals[name]
        lbl.setText(text)
        lbl.setStyleSheet(theme.css_semi(18, color))

    def place_overlays(self):
        self.cam_fps_overlay.adjustSize()
        self.cam_conf_overlay.adjustSize()
        self.cam_fps_overlay.move(self.cam_card.width() - self.cam_fps_overlay.width() - 12, 12)
        self.cam_conf_overlay.move(12, self.cam_card.height() - self.cam_conf_overlay.height() - 12)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "cam_card"):
            self.place_overlays()

    def set_conf_overlay(self, text, color):
        self.cam_conf_overlay.setText(text)
        self.cam_conf_overlay.setStyleSheet(
            f"color: {color}; background: rgba(7,7,12,0.82); font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 10px;")

    # ---------------------------------------------------------- switchgear
    def refresh_cluster_switches(self):
        self.cluster.set_switches(self.helmet_detected, not self.helmet_detected, self.indicators_state,
                                  self.headlight_state, self.abs_state == "ON", self.cruise_active)
        for b, on in ((self.btn_hl, self.headlight_state != "OFF"), (self.btn_ind, self.indicators_state != "OFF"),
                      (self.btn_abs, self.abs_state == "ON"), (self.btn_cr, self.cruise_active),
                      (self.btn_m_sport, self.ride_mode == "SPORT"), (self.btn_m_eco, self.ride_mode == "ECO"),
                      (self.btn_m_pwr, self.ride_mode == "POWER")):
            b.setProperty("active", "true" if on else "false")
            repolish(b)

    def toggle_headlight(self):
        states = ["AUTO", "HIGH BEAM", "OFF"]
        self.headlight_state = states[(states.index(self.headlight_state) + 1) % len(states)]
        self.btn_hl.setText(f"Headlight: {self.headlight_state}")
        self.refresh_cluster_switches()

    def toggle_indicators(self):
        states = ["OFF", "LEFT", "RIGHT", "HAZARD"]
        self.indicators_state = states[(states.index(self.indicators_state) + 1) % len(states)]
        self.btn_ind.setText(f"Indicators: {self.indicators_state}")
        self.refresh_cluster_switches()

    def toggle_abs(self):
        self.abs_state = "OFF" if self.abs_state == "ON" else "ON"
        self.btn_abs.setText(f"ABS: {self.abs_state}")
        self.refresh_cluster_switches()

    def toggle_cruise(self):
        self.cruise_active = not self.cruise_active
        self.btn_cr.setText(f"Cruise: {'ON' if self.cruise_active else 'OFF'}")
        self.refresh_cluster_switches()

    def set_ride_mode(self, mode):
        self.ride_mode = mode
        speaker.speak(f"{mode} mode selected.")
        self.refresh_cluster_switches()

    def manual_gear_up(self):
        gears = ["N", "1", "2", "3", "4", "5", "6"]
        if self.gear in gears:
            self.gear = gears[min(len(gears) - 1, gears.index(self.gear) + 1)]

    def manual_gear_down(self):
        gears = ["N", "1", "2", "3", "4", "5", "6"]
        if self.gear in gears:
            self.gear = gears[max(0, gears.index(self.gear) - 1)]

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

    # ------------------------------------------------------- helmet / lock
    def set_helmet_state(self, detected, speak=True):
        """Single place that switches the helmet status, engine lock and cluster lights."""
        if detected == self.helmet_detected and self.btn_engine_start.property("state"):
            return
        self.helmet_detected = detected
        self.helmet_ring.set_detected(detected)
        if detected:
            self.h_status_lbl.setText("HELMET DETECTED")
            self.h_status_lbl.setStyleSheet(theme.css_display(30, theme.OK))
            self.card_engine.setProperty("state", "")
            self.btn_engine_start.setText("ENGINE START ENABLED")
            self.btn_engine_start.setProperty("state", "ok")
            self.c2_subtext.setText("Ignition ready. Press start.")
            if speak:
                speaker.speak("Helmet detected. Now you can ride the bike.")
        else:
            self.h_status_lbl.setText("HELMET NOT DETECTED")
            self.h_status_lbl.setStyleSheet(theme.css_display(30, theme.BAD))
            self.card_engine.setProperty("state", "bad")
            self.btn_engine_start.setText("ENGINE LOCKED")
            self.btn_engine_start.setProperty("state", "bad")
            self.c2_subtext.setText("Motorcycle cannot start without helmet verification.")
            self.speed = 0.0
            self.throttle_input = 0.0
            if speak:
                speaker.speak("Engine locked. Please wear helmet.")
        repolish(self.card_engine)
        repolish(self.btn_engine_start)
        self.refresh_cluster_switches()

    def toggle_helmet_simulation(self):
        """Toggle between helmet detected (green) and helmet missing (coral, engine locked)."""
        self.set_helmet_state(not self.helmet_detected)

    # ------------------------------------------------------- demo telemetry
    def calculate_auto_gear_and_rpm(self):
        if self.speed < 0.5:
            if self.throttle_input > 0:
                return "1", 1200.0 + self.throttle_input * 1500.0
            return "N", 1000.0
        if self.speed <= 25.0:
            gear, rpm = "1", 1500.0 + (self.speed / 25.0) * 5000.0
        elif self.speed <= 45.0:
            gear, rpm = "2", 2500.0 + ((self.speed - 25.0) / 20.0) * 4500.0
        elif self.speed <= 70.0:
            gear, rpm = "3", 3000.0 + ((self.speed - 45.0) / 25.0) * 4200.0
        elif self.speed <= 95.0:
            gear, rpm = "4", 3400.0 + ((self.speed - 70.0) / 25.0) * 4000.0
        elif self.speed <= 125.0:
            gear, rpm = "5", 3800.0 + ((self.speed - 95.0) / 30.0) * 3800.0
        else:
            gear, rpm = "6", 4000.0 + min(1.0, (self.speed - 125.0) / 75.0) * 6500.0
        return gear, min(12000.0, rpm + self.throttle_input * 600.0)

    def update_telemetry(self):
        if not self.helmet_detected:
            self.throttle_input = 0.0
            self.speed = max(0.0, self.speed - 3.5)
        if self.throttle_input > 0:
            self.speed += 1.8 * self.throttle_input
            self.throttle_input = max(0.0, self.throttle_input - 0.02)
        elif self.is_braking:
            self.speed = max(0.0, self.speed - 3.5)
            if self.speed == 0:
                self.is_braking = False
        else:
            self.speed = max(0.0, self.speed - 0.7)
        if self.speed > 0:
            self.fuel = max(0.0, self.fuel - 0.003)
        auto_gear, rpm = self.calculate_auto_gear_and_rpm()
        if self.speed == 0 or auto_gear != "N":
            self.gear = auto_gear
        self.rpm = rpm
        self.cluster.set_telemetry(self.speed, self.rpm, self.gear, self.ride_mode)

    # ------------------------------------------------------ real + clock data
    def update_system(self):
        now = datetime.now()
        self.clock_lbl.setText(now.strftime("%I:%M %p").lstrip("0"))
        self.date_lbl.setText(now.strftime("%a %d %b"))
        fuel_col = theme.OK if self.fuel > 20 else theme.BAD
        self.fuel_lbl.setText(f"FUEL <b style='color:{fuel_col};'>{self.fuel:.0f}%</b>")
        self.bat_lbl.setText(f"BAT <b style='color:{theme.TEXT};'>14.2V</b>")
        self.temp_lbl.setText(f"ENG <b style='color:{theme.TEXT};'>88°C</b>")

        cpu = psutil.cpu_percent(None)
        ram = psutil.virtual_memory().percent
        self.m_cpu.set(f"{cpu:.0f}", cpu / 100, theme.OK if cpu < 70 else theme.WARN)
        self.m_ram.set(f"{ram:.0f}", ram / 100, theme.OK if ram < 80 else theme.WARN)
        elapsed = int(time.monotonic() - self.started)
        self.m_up.set(f"{elapsed // 3600:02d}:{elapsed % 3600 // 60:02d}:{elapsed % 60:02d}")

        online = (time.monotonic() - self.last_frame_time) < 2.5 and self.last_frame_time > 0
        self.apply_status("Camera", "ONLINE" if online else "NO SIGNAL", theme.OK if online else theme.BAD)
        self.cam_live_overlay.setText("LIVE" if online else "NO SIGNAL")

        # Demo ride info follows the demo telemetry
        self.ride_vals["Ride time"].setText(f"{elapsed // 3600:02d}:{elapsed % 3600 // 60:02d}:{elapsed % 60:02d}")

    @pyqtSlot(QImage)
    def update_camera_feed(self, qimg):
        self.last_frame_time = time.monotonic()
        pix = QPixmap.fromImage(qimg).scaled(self.cam_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
        self.cam_label.setPixmap(pix)

    @pyqtSlot(dict)
    def update_live_stats(self, stats):
        self.frames += 1
        boxes = stats.get("bboxes", [])
        if boxes:
            self.frames_with_detection += 1
            if stats.get("helmet_detected"):
                self.frames_helmet += 1
        self.total_detections = stats.get("total_detections", self.total_detections)
        self.fps = stats.get("fps", self.fps)
        self.latency = stats.get("inference_time", self.latency)
        self.confidence = stats.get("confidence", 0.0) * 100.0

        self.cam_fps_overlay.setText(f"FPS {self.fps:.0f}")
        if stats.get("helmet_detected"):
            self.set_conf_overlay(f"Helmet {self.confidence:.0f}%", theme.OK)
        elif boxes:
            self.set_conf_overlay("No helmet in view", theme.BAD)
        else:
            self.set_conf_overlay("No detection", theme.MUTED)
        self.place_overlays()

        self.m_fps.set(f"{self.fps:.0f}", self.fps / 30.0, theme.ACCENT)
        self.m_lat.set(f"{self.latency:.0f}", self.latency / 200.0, theme.OK if self.latency < 100 else theme.WARN)
        if stats.get("helmet_detected"):
            self.m_conf.set(f"{self.confidence:.0f}", self.confidence / 100, theme.OK)
        else:
            self.m_conf.set("--", None)
        self.m_det.set(f"{self.total_detections:,}")
        if self.frames_with_detection:
            comp = self.frames_helmet / self.frames_with_detection * 100.0
            self.m_comp.set(f"{comp:.0f}", comp / 100, theme.OK if comp >= 80 else theme.WARN)

        val, bar = self.bars["conf"]
        val.setText(f"{self.confidence:.1f}%" if stats.get("helmet_detected") else "--")
        bar.setValue(int(self.confidence) if stats.get("helmet_detected") else 0)
        val, bar = self.bars["fps"]
        val.setText(f"{self.fps:.0f} FPS")
        bar.setValue(int(min(100, self.fps / 30.0 * 100)))
        val, bar = self.bars["lat"]
        val.setText(f"{self.latency:.0f} ms")
        bar.setValue(int(min(100, self.latency / 200.0 * 100)))
        self.model_lbl.setText(f"Model: {stats.get('model_name', '')}")
        self.apply_status("AI detection", "RUNNING", theme.OK)
        if stats.get("helmet_detected"):
            self.h_conf_lbl.setText(f"Confidence {self.confidence:.0f}%")
        else:
            self.h_conf_lbl.setText("No helmet seen right now" if boxes else "Nobody in view")

    # --------------------------------------------------------------- alerts
    def render_alerts(self):
        while self.alert_rows.count():
            item = self.alert_rows.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not self.alert_log:
            lbl = QLabel("No alerts this session")
            lbl.setProperty("class", "muted")
            self.alert_rows.addWidget(lbl)
            return
        for stamp, msg, bad in self.alert_log[-4:][::-1]:
            lbl = QLabel(f"<span style='color:{theme.FAINT};'>{stamp}</span>  "
                         f"<span style='color:{theme.BAD if bad else theme.OK};'>{msg}</span>")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setWordWrap(True)
            self.alert_rows.addWidget(lbl)

    @pyqtSlot(str)
    def trigger_adas_alert(self, msg):
        self.alert_log.append((datetime.now().strftime("%H:%M:%S"), msg or "No helmet detected", True))
        self.render_alerts()
        if self.helmet_detected:
            self.set_helmet_state(False)

    @pyqtSlot()
    def clear_adas_alert(self):
        self.alert_log.append((datetime.now().strftime("%H:%M:%S"), "Helmet detected, alert cleared", False))
        self.render_alerts()
        if not self.helmet_detected:
            self.set_helmet_state(True)
