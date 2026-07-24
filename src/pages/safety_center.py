from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
import time

class SafetyCenterPage(QWidget):
    def __init__(self, ai_engine=None, alert_system=None, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        
        self.total_frames = 0
        self.helmet_frames = 0
        self.total_alerts = 0
        self.start_time = time.time()
        
        self.init_ui()
        
        if self.ai_engine:
            self.ai_engine.stats_update.connect(self.update_stats)
        if self.alert_system:
            self.alert_system.alert_triggered.connect(self.add_alert)
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)
        
        title = QLabel("Rider Safety Center")
        title.setProperty("class", "h1")
        main_layout.addWidget(title)
        
        # Top Grade Section
        grade_lay = QHBoxLayout()
        
        grade_card = QFrame()
        grade_card.setProperty("class", "glass-card")
        grade_card.setMinimumWidth(300)
        gc_lay = QVBoxLayout(grade_card)
        gc_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        gc_lay.addWidget(self.lbl("OVERALL RIDER GRADE"))
        self.grade_val = QLabel("A+")
        self.grade_val.setStyleSheet("color: #39FF14; font-size: 160px; font-weight: bold; font-family: 'Segoe UI';")
        self.grade_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gc_lay.addWidget(self.grade_val)
        
        grade_lay.addWidget(grade_card)
        
        # Stats Section
        stats_card = QFrame()
        stats_card.setProperty("class", "glass-card")
        sc_lay = QGridLayout(stats_card)
        sc_lay.setSpacing(20)
        
        self.kpi_score = self.create_kpi("Safety Score", "100")
        self.kpi_comp = self.create_kpi("Helmet Compliance", "100%")
        self.kpi_alerts = self.create_kpi("Session Alerts", "0")
        self.kpi_dur = self.create_kpi("Ride Duration", "00:00")
        self.kpi_health = self.create_kpi("System Health", "OPTIMAL")
        self.kpi_risk = self.create_kpi("Risk Level", "LOW")
        
        self.kpi_score[1].setStyleSheet("color: #00E5FF; font-size: 48px; font-weight: bold;")
        self.kpi_alerts[1].setStyleSheet("color: #FF3333; font-size: 48px; font-weight: bold;")
        self.kpi_health[1].setStyleSheet("color: #39FF14; font-size: 48px; font-weight: bold;")
        
        sc_lay.addWidget(self.kpi_score[0], 0, 0)
        sc_lay.addWidget(self.kpi_comp[0], 0, 1)
        sc_lay.addWidget(self.kpi_alerts[0], 0, 2)
        sc_lay.addWidget(self.kpi_dur[0], 1, 0)
        sc_lay.addWidget(self.kpi_health[0], 1, 1)
        sc_lay.addWidget(self.kpi_risk[0], 1, 2)
        
        grade_lay.addWidget(stats_card, stretch=1)
        
        main_layout.addLayout(grade_lay)
        main_layout.addStretch()

    def create_kpi(self, title, val):
        card = QFrame()
        card.setStyleSheet("background-color: rgba(0,0,0,0.3); border: 1px solid rgba(0,229,255,0.2); border-radius: 12px;")
        lay = QVBoxLayout(card)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l1 = self.lbl(title)
        l2 = QLabel(val)
        l2.setProperty("class", "value-medium")
        l2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(l1)
        lay.addWidget(l2)
        return card, l2

    def lbl(self, text):
        l = QLabel(text)
        l.setProperty("class", "info-text")
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return l
        
    @pyqtSlot(dict)
    def update_stats(self, stats):
        self.total_frames += 1
        if stats.get("helmet_detected", False):
            self.helmet_frames += 1

    @pyqtSlot(str)
    def add_alert(self, msg):
        self.total_alerts += 1

    def update_ui(self):
        dur = int(time.time() - self.start_time)
        mins, secs = divmod(dur, 60)
        self.kpi_dur[1].setText(f"{mins:02d}:{secs:02d}")
        
        if self.total_frames == 0:
            return
            
        comp = (self.helmet_frames / self.total_frames) * 100
        score = (comp * 0.8) + (20) - (self.total_alerts * 5)
        score = max(0, min(100, score))
        
        self.kpi_score[1].setText(f"{score:.0f}")
        self.kpi_comp[1].setText(f"{comp:.1f}%")
        self.kpi_alerts[1].setText(f"{self.total_alerts}")
        
        grade = "A+"
        color = "#39FF14"
        risk = "LOW"
        if score < 50:
            grade = "D"
            color = "#FF3333"
            risk = "CRITICAL"
        elif score < 70:
            grade = "C"
            color = "#FF8C00"
            risk = "MODERATE"
        elif score < 85:
            grade = "B"
            color = "#FFA500"
            risk = "ELEVATED"
        elif score < 95:
            grade = "A"
            color = "#00E5FF"
            
        self.grade_val.setText(grade)
        self.grade_val.setStyleSheet(f"color: {color}; font-size: 160px; font-weight: bold; font-family: 'Segoe UI';")
        self.kpi_risk[1].setText(risk)
        self.kpi_risk[1].setStyleSheet(f"color: {color}; font-size: 48px; font-weight: bold;")
