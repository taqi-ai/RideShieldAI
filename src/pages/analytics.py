import os
import time
import psutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
from src import theme
from src.ui_kit import make_card, page_header, tag

class MultiLineChart(QWidget):
    def __init__(self, title, lines, max_val, parent=None):
        super().__init__(parent)
        self.title = title
        self.lines = lines # list of dicts: {'name': 'FPS', 'color': QColor, 'data': []}
        self.max_val = max_val
        self.max_data_points = 60
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(theme.DEVICE))
        painter.drawRoundedRect(0, 0, width, height, 14, 14)

        # Grid
        painter.setPen(QPen(QColor(255, 255, 255, 16), 1))
        for i in range(1, 4):
            y = int(height * i / 4)
            painter.drawLine(14, y, width - 14, y)

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
            
        # Title and legend
        painter.setPen(QColor(theme.TEXT))
        painter.setFont(theme.semi_font(16))
        painter.drawText(16, 26, self.title)
        painter.setFont(theme.body_font(12))
        x = 16
        for line in self.lines:
            painter.setPen(line['color'])
            painter.drawText(x, 46, "● " + line['name'])
            x += 24 + painter.fontMetrics().horizontalAdvance("● " + line['name'])

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
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(14)

        layout.addWidget(page_header("Analytics", "Helmet compliance and engine performance for this session.", tag("LIVE SESSION DATA")))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_lay = QVBoxLayout(scroll_content)
        scroll_lay.setContentsMargins(0, 0, 8, 0)
        scroll_lay.setSpacing(14)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(14)

        self.kpi_compliance = self.create_kpi_card("HELMET COMPLIANCE", "0%")
        self.kpi_confidence = self.create_kpi_card("AVERAGE CONFIDENCE", "0%")
        self.kpi_detect_count = self.create_kpi_card("FRAMES ANALYSED", "0")
        self.kpi_alerts = self.create_kpi_card("ALERTS", "0", theme.BAD)
        self.kpi_fps = self.create_kpi_card("AVERAGE FPS", "0")
        self.kpi_safety_score = self.create_kpi_card("SAFETY SCORE", "100", theme.OK, 96)

        self.grid_layout.addWidget(self.kpi_safety_score[0], 0, 0, 2, 1)
        self.grid_layout.addWidget(self.kpi_compliance[0], 0, 1)
        self.grid_layout.addWidget(self.kpi_confidence[0], 0, 2)
        self.grid_layout.addWidget(self.kpi_detect_count[0], 0, 3)
        self.grid_layout.addWidget(self.kpi_alerts[0], 1, 1)
        self.grid_layout.addWidget(self.kpi_fps[0], 1, 2)
        for c in range(4):
            self.grid_layout.setColumnStretch(c, 1)
        scroll_lay.addLayout(self.grid_layout)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(14)
        self.chart_safety = MultiLineChart("Safety and compliance", [
            {'name': 'Compliance %', 'color': QColor(theme.OK), 'data': self.history_comp},
            {'name': 'Confidence %', 'color': QColor(theme.ACCENT), 'data': self.history_conf}
        ], 100)
        self.chart_perf = MultiLineChart("Engine performance", [
            {'name': 'FPS', 'color': QColor(theme.WARN), 'data': self.history_fps}
        ], 60)
        self.chart_hw = MultiLineChart("Hardware utilisation", [
            {'name': 'GPU %', 'color': QColor(theme.BAD), 'data': self.history_gpu},
            {'name': 'VRAM %', 'color': QColor(theme.VIOLET), 'data': self.history_vram}
        ], 100)
        charts_grid.addWidget(self.chart_safety, 0, 0)
        charts_grid.addWidget(self.chart_perf, 0, 1)
        charts_grid.addWidget(self.chart_hw, 1, 0, 1, 2)
        scroll_lay.addLayout(charts_grid)
        scroll_lay.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def create_kpi_card(self, title, initial_value, color=None, px=52):
        card, lay = make_card(title)
        lbl_val = QLabel(initial_value)
        lbl_val.setStyleSheet(theme.css_display(px, color or theme.TEXT))
        lay.addWidget(lbl_val)
        lay.addStretch()
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
            self.kpi_safety_score[1].setStyleSheet(theme.css_display(96, theme.OK))
        elif score > 50:
            self.kpi_safety_score[1].setStyleSheet(theme.css_display(96, theme.WARN))
        else:
            self.kpi_safety_score[1].setStyleSheet(theme.css_display(96, theme.BAD))

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
