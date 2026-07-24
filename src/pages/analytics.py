import os
import time
import psutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath

class MultiLineChart(QWidget):
    def __init__(self, title, lines, max_val, parent=None):
        super().__init__(parent)
        self.title = title
        self.lines = lines # list of dicts: {'name': 'FPS', 'color': QColor, 'data': []}
        self.max_val = max_val
        self.max_data_points = 60
        self.setMinimumHeight(180)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background
        painter.fillRect(0, 0, width, height, QColor(10, 15, 25, 200))
        
        # Grid
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        for i in range(1, 4):
            y = int(height * i / 4)
            painter.drawLine(0, y, width, y)
            
        x_step = width / max(1, (self.max_data_points - 1))
        
        # Draw Lines
        for line in self.lines:
            data = line['data']
            if not data: continue
            
            path = QPainterPath()
            y_start = height - (min(self.max_val, data[0]) / self.max_val) * height
            path.moveTo(0, y_start)
            for i in range(1, len(data)):
                x0 = (i - 1) * x_step
                y0 = height - (min(self.max_val, data[i - 1]) / max(1, self.max_val)) * height
                x1 = i * x_step
                y1 = height - (min(self.max_val, data[i]) / max(1, self.max_val)) * height
                
                cx = (x0 + x1) / 2
                path.cubicTo(cx, y0, cx, y1, x1, y1)
                
            painter.setPen(QPen(line['color'], 2))
            painter.drawPath(path)
            
        # Title
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(10, 20, self.title)
        
        # Legend
        y_offset = 40
        painter.setFont(QFont("Segoe UI", 10))
        for line in self.lines:
            painter.setPen(line['color'])
            painter.drawText(10, y_offset, f"— {line['name']}")
            y_offset += 20

class AnalyticsPage(QWidget):
    def __init__(self, ai_engine=None, alert_system=None, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        
        self.total_frames = 0
        self.helmet_frames = 0
        self.no_helmet_frames = 0
        self.sum_confidence = 0.0
        self.sum_fps = 0.0
        self.total_alerts = 0
        
        self.current_compliance = 0.0
        self.current_fps = 0.0
        self.current_conf = 0.0
        
        self.max_points = 60
        self.history_comp = [0]*self.max_points
        self.history_fps = [0]*self.max_points
        self.history_conf = [0]*self.max_points
        self.history_alerts = [0]*self.max_points
        self.history_gpu = [0]*self.max_points
        self.history_vram = [0]*self.max_points
        
        self.init_ui()
        
        if self.ai_engine:
            self.ai_engine.stats_update.connect(self.accumulate_stats)
        if self.alert_system:
            self.alert_system.alert_triggered.connect(self.increment_alert)
            
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(1000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)
        
        title_layout = QHBoxLayout()
        title = QLabel("Fleet Analytics")
        title.setProperty("class", "h1")
        
        session_lbl = QLabel("LIVE SESSION DATA")
        session_lbl.setProperty("class", "h3")
        session_lbl.setStyleSheet("color: #39FF14;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(session_lbl)
        layout.addLayout(title_layout)
        
        # Scroll Area for massive dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_lay = QVBoxLayout(scroll_content)
        
        # KPI Grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        
        self.kpi_compliance = self.create_kpi_card("Helmet Compliance", "0%")
        self.kpi_confidence = self.create_kpi_card("Average Confidence", "0%")
        self.kpi_detect_count = self.create_kpi_card("Total Detections", "0")
        self.kpi_alerts = self.create_kpi_card("Alerts Today", "0")
        self.kpi_alerts[1].setStyleSheet("color: #FF3333; font-size: 32px; font-weight: bold;")
        self.kpi_fps = self.create_kpi_card("Average FPS", "0")
        
        self.kpi_safety_score = self.create_kpi_card("Safety Score", "100")
        self.kpi_safety_score[1].setStyleSheet("color: #39FF14; font-size: 64px; font-weight: bold;")
        
        self.grid_layout.addWidget(self.kpi_compliance[0], 0, 0)
        self.grid_layout.addWidget(self.kpi_confidence[0], 0, 1)
        self.grid_layout.addWidget(self.kpi_safety_score[0], 0, 2, 2, 1)
        self.grid_layout.addWidget(self.kpi_detect_count[0], 0, 3)
        self.grid_layout.addWidget(self.kpi_alerts[0], 1, 0)
        self.grid_layout.addWidget(self.kpi_fps[0], 1, 1)
        
        scroll_lay.addLayout(self.grid_layout)
        
        # Charts Grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(20)
        
        self.chart_safety = MultiLineChart("Safety & Compliance", [
            {'name': 'Compliance %', 'color': QColor(57, 255, 20), 'data': self.history_comp},
            {'name': 'Confidence %', 'color': QColor(0, 229, 255), 'data': self.history_conf}
        ], 100)
        
        self.chart_perf = MultiLineChart("Engine Performance", [
            {'name': 'FPS', 'color': QColor(255, 165, 0), 'data': self.history_fps}
        ], 60)
        
        self.chart_hw = MultiLineChart("Hardware Utilization", [
            {'name': 'GPU %', 'color': QColor(255, 51, 51), 'data': self.history_gpu},
            {'name': 'VRAM %', 'color': QColor(160, 32, 240), 'data': self.history_vram}
        ], 100)
        
        charts_grid.addWidget(self.chart_safety, 0, 0)
        charts_grid.addWidget(self.chart_perf, 0, 1)
        charts_grid.addWidget(self.chart_hw, 1, 0, 1, 2)
        
        scroll_lay.addLayout(charts_grid)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def create_kpi_card(self, title, initial_value):
        card = QFrame()
        card.setProperty("class", "glass-card")
        lay = QVBoxLayout(card)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "info-text")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_val = QLabel(initial_value)
        lbl_val.setProperty("class", "value-medium")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lay.addWidget(lbl_title)
        lay.addWidget(lbl_val)
        return card, lbl_val

    @pyqtSlot(dict)
    def accumulate_stats(self, stats):
        self.total_frames += 1
        self.sum_fps += stats.get("fps", 0)
        
        conf = stats.get("confidence", 0.0)
        self.sum_confidence += conf
        
        if stats.get("helmet_detected", False):
            self.helmet_frames += 1
        else:
            if conf > 0:
                self.no_helmet_frames += 1
                
        self.current_fps = stats.get("fps", 0)
        self.current_conf = conf * 100

    @pyqtSlot(str)
    def increment_alert(self, msg):
        self.total_alerts += 1

    def update_ui(self):
        if self.total_frames == 0:
            return
            
        compliance = (self.helmet_frames / self.total_frames) * 100
        self.current_compliance = compliance
        avg_conf = (self.sum_confidence / self.total_frames) * 100
        avg_fps = self.sum_fps / self.total_frames
        
        score = (compliance * 0.8) + (20) - (self.total_alerts * 5)
        score = max(0, min(100, score))
        
        self.kpi_compliance[1].setText(f"{compliance:.1f}%")
        self.kpi_confidence[1].setText(f"{avg_conf:.1f}%")
        self.kpi_detect_count[1].setText(f"{self.total_frames}")
        self.kpi_alerts[1].setText(f"{self.total_alerts}")
        self.kpi_fps[1].setText(f"{avg_fps:.1f}")
        self.kpi_safety_score[1].setText(f"{score:.0f}")
        
        if score > 80:
            self.kpi_safety_score[1].setStyleSheet("color: #39FF14; font-size: 64px; font-weight: bold;")
        elif score > 50:
            self.kpi_safety_score[1].setStyleSheet("color: #FFA500; font-size: 64px; font-weight: bold;")
        else:
            self.kpi_safety_score[1].setStyleSheet("color: #FF3333; font-size: 64px; font-weight: bold;")

        # Update History arrays
        self.history_comp.pop(0)
        self.history_comp.append(compliance)
        
        self.history_fps.pop(0)
        self.history_fps.append(self.current_fps)
        
        self.history_conf.pop(0)
        self.history_conf.append(self.current_conf)
        
        self.history_alerts.pop(0)
        self.history_alerts.append(self.total_alerts)
        
        gpu_util = 0
        vram_util = 0
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_util = gpus[0].load * 100
                vram_util = gpus[0].memoryUtil * 100
        except:
            pass
            
        self.history_gpu.pop(0)
        self.history_gpu.append(gpu_util)
        
        self.history_vram.pop(0)
        self.history_vram.append(vram_util)
        
        self.chart_safety.update()
        self.chart_perf.update()
        self.chart_hw.update()
