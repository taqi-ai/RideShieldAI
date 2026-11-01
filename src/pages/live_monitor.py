import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QImage, QPixmap

from src import theme
from src.ui_kit import MetricTile, make_card, page_header, repolish, tag


class LiveMonitorPage(QWidget):
    def __init__(self, ai_engine, alert_system, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.alert_system = alert_system
        self.frames = 0
        self.helmet_frames = 0
        self.init_ui()

        if self.ai_engine:
            self.ai_engine.image_update.connect(self.update_image)
            self.ai_engine.stats_update.connect(self.update_stats)

        self.blink_state = True
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_timer.start(500)

    def toggle_blink(self):
        self.blink_state = not self.blink_state
        color = theme.BAD if self.blink_state else "rgba(255,102,116,0.35)"
        self.live_indicator.setStyleSheet(f"color: {color}; {theme.css_semi(18)} background: transparent;")

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 18)
        root.setSpacing(14)

        self.model_tag = tag("--")
        root.addWidget(page_header("Camera", "Live feed with helmet detection boxes drawn by the model.", self.model_tag))

        body = QHBoxLayout()
        body.setSpacing(14)

        # Video
        self.video_container = QFrame()
        self.video_container.setProperty("class", "device")
        vlay = QVBoxLayout(self.video_container)
        vlay.setContentsMargins(0, 0, 0, 0)
        self.video_label = QLabel("Starting camera...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setProperty("class", "muted")
        self.video_label.setMinimumSize(320, 240)
        vlay.addWidget(self.video_label)

        self.live_indicator = QLabel("● LIVE")
        self.live_indicator.setStyleSheet(f"color: {theme.BAD}; {theme.css_semi(18)} background: transparent;")
        self.live_indicator.setParent(self.video_container)
        self.live_indicator.adjustSize()
        self.live_indicator.move(18, 14)
        body.addWidget(self.video_container, stretch=1)

        # Side column
        side = QVBoxLayout()
        side.setSpacing(12)
        side.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.status_card, slay = make_card("HELMET STATUS", "ok")
        self.status_val = QLabel("DETECTED")
        self.status_val.setStyleSheet(theme.css_display(38, theme.OK))
        slay.addWidget(self.status_val)
        self.status_note = QLabel("Rider protected")
        self.status_note.setProperty("class", "muted")
        slay.addWidget(self.status_note)
        side.addWidget(self.status_card)

        self.t_conf = MetricTile("CONFIDENCE", "%")
        self.t_fps = MetricTile("FPS")
        self.t_inf = MetricTile("INFERENCE TIME", "ms")
        self.t_on = MetricTile("HELMET-ON FRAMES", "%")
        for t in (self.t_conf, self.t_fps, self.t_inf, self.t_on):
            side.addWidget(t)

        model_card, mlay = make_card("CURRENT MODEL")
        self.model_val = QLabel("YOLO")
        self.model_val.setStyleSheet(theme.css_semi(22, theme.ACCENT))
        mlay.addWidget(self.model_val)
        side.addWidget(model_card)
        side.addStretch()

        side_wrap = QWidget()
        side_wrap.setFixedWidth(300)
        side_wrap.setLayout(side)
        body.addWidget(side_wrap)
        root.addLayout(body, stretch=1)

        model_name = "YOLO"
        if self.ai_engine and hasattr(self.ai_engine, "model_path"):
            model_name = os.path.splitext(os.path.basename(self.ai_engine.model_path))[0].upper()
        self.model_val.setText(model_name)
        self.model_tag.setText(model_name)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.live_indicator.move(18, 14)

    @pyqtSlot(QImage)
    def update_image(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(self.video_container.width() - 4, self.video_container.height() - 4,
                               Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(scaled)
        self.live_indicator.raise_()

    @pyqtSlot(dict)
    def update_stats(self, stats):
        helmet = stats.get("helmet_detected", False)
        self.frames += 1
        if helmet:
            self.helmet_frames += 1
        state = "ok" if helmet else "bad"
        col = theme.OK if helmet else theme.BAD
        self.status_card.setProperty("state", state)
        repolish(self.status_card)
        self.status_val.setText("DETECTED" if helmet else "NOT DETECTED")
        self.status_val.setStyleSheet(theme.css_display(38, col))
        self.status_note.setText("Rider protected" if helmet else "Engine lock may engage")

        fps = stats.get("fps", 0)
        inf = stats.get("inference_time", 0)
        conf = stats.get("confidence", 0) * 100
        on = self.helmet_frames / max(1, self.frames) * 100
        self.t_conf.set(f"{conf:.0f}", conf / 100, theme.ACCENT)
        self.t_fps.set(f"{fps:.1f}", fps / 60, theme.OK)
        self.t_inf.set(f"{inf:.0f}", min(1.0, inf / 200), theme.WARN)
        self.t_on.set(f"{on:.0f}", on / 100, theme.OK if on >= 80 else theme.WARN)
