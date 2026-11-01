import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from src import database, theme
from src.ui_kit import make_card, page_header, tag

class EventHistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_events)
        self.timer.start(5000)
        self.load_events()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(14)
        self.count_tag = tag("0 EVENTS")
        layout.addWidget(page_header("History", "Alerts and engine-lock events saved on this computer.", self.count_tag))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setContentsMargins(0, 0, 8, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

    def load_events(self):
        events = database.get_recent_events(50)
        
        # Clear existing
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not events:
            self.count_tag.setText("0 EVENTS")
            card, lay = make_card("NOTHING RECORDED YET")
            msg = QLabel("When a rider is seen without a helmet, the alert and a snapshot appear here.")
            msg.setProperty("class", "muted")
            msg.setWordWrap(True)
            lay.addWidget(msg)
            self.scroll_layout.addWidget(card)
            return
        self.count_tag.setText(f"{len(events)} EVENTS")
            
        for event in events:
            try:
                event_dict = dict(event)
                card = self.create_event_card(event_dict)
                self.scroll_layout.addWidget(card)
            except Exception as e:
                pass
            
    def create_event_card(self, event):
        text = event.get('event_type', 'Unknown event')
        bad = "Alert" in text or "Lock" in text
        card, lay = make_card(None, "bad" if bad else None)
        card.setFixedHeight(112)
        lay.setContentsMargins(14, 10, 18, 10)
        row = QHBoxLayout()
        row.setSpacing(16)
        lay.addLayout(row)

        thumb = QLabel()
        thumb.setFixedSize(160, 90)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet(f"background-color: {theme.DEVICE}; border-radius: 8px; color: {theme.FAINT};")
        path = event.get('screenshot_path')
        if path and os.path.exists(path):
            pix = QPixmap(path).scaled(160, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            thumb.setPixmap(pix)
        else:
            thumb.setText("no snapshot")
        row.addWidget(thumb)

        info = QVBoxLayout()
        info.setSpacing(3)
        head = QHBoxLayout()
        type_lbl = QLabel(text.upper())
        type_lbl.setStyleSheet(theme.css_semi(20, theme.BAD if bad else theme.ACCENT))
        time_lbl = QLabel(str(event.get('timestamp', '')))
        time_lbl.setProperty("class", "faint")
        head.addWidget(type_lbl)
        head.addStretch()
        head.addWidget(time_lbl)
        info.addLayout(head)
        details = QLabel(event.get('details', ''))
        details.setWordWrap(True)
        info.addWidget(details)
        conf = event.get('confidence')
        if conf is not None:
            c = QLabel(f"Confidence {conf:.0%}")
            c.setProperty("class", "muted")
            info.addWidget(c)
        info.addStretch()
        row.addLayout(info, stretch=1)
        return card
