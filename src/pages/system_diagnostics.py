from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QFrame
import psutil

class SystemDiagnosticsPage(QWidget):
    def __init__(self, ai_engine, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("System Diagnostics")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        diag_frame = QFrame()
        diag_frame.setProperty("class", "card")
        diag_layout = QFormLayout(diag_frame)
        
        # AI Engine Info
        model_path = self.ai_engine.model_path if self.ai_engine else "Unknown"
        diag_layout.addRow("AI Model Path:", QLabel(model_path))
        
        cam_id = str(self.ai_engine.camera_id) if self.ai_engine else "Unknown"
        diag_layout.addRow("Camera ID:", QLabel(cam_id))
        
        # System Info
        cpu_usage = f"{psutil.cpu_percent()}%"
        mem = psutil.virtual_memory()
        mem_usage = f"{mem.percent}% ({mem.used / (1024**3):.1f} GB / {mem.total / (1024**3):.1f} GB)"
        
        diag_layout.addRow("CPU Usage:", QLabel(cpu_usage))
        diag_layout.addRow("Memory Usage:", QLabel(mem_usage))
        
        layout.addWidget(diag_frame)
        layout.addStretch()
