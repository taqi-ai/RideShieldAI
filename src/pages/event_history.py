from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt
from src import database

class EventHistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("Event History")
        title.setProperty("class", "h2")
        header_layout.addWidget(title)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "secondary-button")
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Event Type", "Confidence", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        events = database.get_recent_events(limit=50)
        self.table.setRowCount(len(events))
        
        for row, event in enumerate(events):
            # event = (id, timestamp, event_type, confidence, description)
            self.table.setItem(row, 0, QTableWidgetItem(str(event[1])))
            self.table.setItem(row, 1, QTableWidgetItem(str(event[2])))
            self.table.setItem(row, 2, QTableWidgetItem(f"{event[3]*100:.1f}%"))
            self.table.setItem(row, 3, QTableWidgetItem(str(event[4])))
