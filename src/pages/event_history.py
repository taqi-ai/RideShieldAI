import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from src import database

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
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(30)
        
        title = QLabel("Event Stream")
        title.setProperty("class", "h1")
        layout.addWidget(title)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(15)
        
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
            empty_lbl = QLabel("No events recorded in this session.")
            empty_lbl.setProperty("class", "info-text")
            self.scroll_layout.addWidget(empty_lbl)
            return
            
        for event in events:
            try:
                event_dict = dict(event)
                card = self.create_event_card(event_dict)
                self.scroll_layout.addWidget(card)
            except Exception as e:
                pass
            
    def create_event_card(self, event):
        card = QFrame()
        card.setProperty("class", "glass-card")
        card.setFixedHeight(120)
        
        lay = QHBoxLayout(card)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(20)
        
        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(160, 90)
        thumb.setStyleSheet("background-color: #000000; border-radius: 6px;")
        path = event.get('screenshot_path')
        if path and os.path.exists(path):
            pix = QPixmap(path).scaled(160, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            thumb.setPixmap(pix)
        else:
            thumb.setText("NO MEDIA")
            thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb.setProperty("class", "info-text")
            
        lay.addWidget(thumb)
        
        # Details
        info_lay = QVBoxLayout()
        
        header_lay = QHBoxLayout()
        type_lbl = QLabel(event.get('event_type', 'Unknown Event').upper())
        type_lbl.setProperty("class", "h3")
        
        if "Alert" in type_lbl.text() or "Lock" in type_lbl.text():
            type_lbl.setStyleSheet("color: #FF3333; font-weight: bold;")
        else:
            type_lbl.setStyleSheet("color: #00E5FF; font-weight: bold;")
            
        time_lbl = QLabel(str(event.get('timestamp', '')))
        time_lbl.setProperty("class", "info-text")
        
        header_lay.addWidget(type_lbl)
        header_lay.addStretch()
        header_lay.addWidget(time_lbl)
        
        info_lay.addLayout(header_lay)
        
        details_lbl = QLabel(event.get('details', ''))
        details_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        info_lay.addWidget(details_lbl)
        
        conf = event.get('confidence')
        if conf is not None:
            conf_lbl = QLabel(f"Confidence: {conf:.1%}")
            conf_lbl.setProperty("class", "info-text")
            info_lay.addWidget(conf_lbl)
            
        lay.addLayout(info_lay)
        return card
