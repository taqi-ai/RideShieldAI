import os
import psutil
import platform
import cpuinfo
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFormLayout, QFrame, QProgressBar, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot

class SystemDiagnosticsPage(QWidget):
    def __init__(self, ai_engine, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        
        self.cpu_info = cpuinfo.get_cpu_info()
        self.has_gpu = False
        try:
            import pynvml
            pynvml.nvmlInit()
            self.has_gpu = True
        except:
            pass

        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_diagnostics)
        self.timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)
        
        title = QLabel("Engineering Console")
        title.setProperty("class", "h1")
        main_layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        layout = QGridLayout(scroll_content)
        layout.setSpacing(20)
        
        # --- CPU ---
        cpu_card = QFrame()
        cpu_card.setProperty("class", "glass-card")
        cpu_lay = QFormLayout(cpu_card)
        cpu_title = QLabel("CPU Diagnostics")
        cpu_title.setProperty("class", "h2")
        cpu_lay.addRow(cpu_title)
        
        cpu_lay.addRow(self.lbl("Name:"), self.val(self.cpu_info.get('brand_raw', platform.processor())))
        cpu_lay.addRow(self.lbl("Cores/Threads:"), self.val(f"{psutil.cpu_count(logical=False)} / {psutil.cpu_count(logical=True)}"))
        self.cpu_usage_lbl = self.val("0%")
        cpu_lay.addRow(self.lbl("Usage:"), self.cpu_usage_lbl)
        
        # --- RAM ---
        ram_card = QFrame()
        ram_card.setProperty("class", "glass-card")
        ram_lay = QFormLayout(ram_card)
        ram_title = QLabel("Memory Diagnostics")
        ram_title.setProperty("class", "h2")
        ram_lay.addRow(ram_title)
        
        mem = psutil.virtual_memory()
        ram_lay.addRow(self.lbl("Total:"), self.val(f"{mem.total / (1024**3):.1f} GB"))
        self.ram_used_lbl = self.val("0 GB (0%)")
        ram_lay.addRow(self.lbl("Used:"), self.ram_used_lbl)
        self.ram_avail_lbl = self.val("0 GB")
        ram_lay.addRow(self.lbl("Available:"), self.ram_avail_lbl)
        
        # --- GPU ---
        gpu_card = QFrame()
        gpu_card.setProperty("class", "glass-card")
        gpu_lay = QFormLayout(gpu_card)
        gpu_title = QLabel("GPU Diagnostics")
        gpu_title.setProperty("class", "h2")
        gpu_lay.addRow(gpu_title)
        
        self.gpu_name = self.val("N/A")
        self.gpu_usage = self.val("N/A")
        self.gpu_temp = self.val("N/A")
        self.gpu_power = self.val("N/A")
        self.gpu_vram = self.val("N/A")
        
        gpu_lay.addRow(self.lbl("Name:"), self.gpu_name)
        gpu_lay.addRow(self.lbl("Usage:"), self.gpu_usage)
        gpu_lay.addRow(self.lbl("Temperature:"), self.gpu_temp)
        gpu_lay.addRow(self.lbl("Power Draw:"), self.gpu_power)
        gpu_lay.addRow(self.lbl("VRAM Used:"), self.gpu_vram)
        
        # --- AI MODEL ---
        ai_card = QFrame()
        ai_card.setProperty("class", "glass-card")
        ai_lay = QFormLayout(ai_card)
        ai_title = QLabel("AI Model Status")
        ai_title.setProperty("class", "h2")
        ai_lay.addRow(ai_title)
        
        model_name = os.path.basename(self.ai_engine.model_path) if self.ai_engine else "N/A"
        ai_lay.addRow(self.lbl("Model:"), self.val(model_name))
        ai_lay.addWidget(ai_title)
        
        self.ai_status_lbl = QLabel("Model Status: Loaded")
        self.ai_params_lbl = QLabel("Parameters: ~20M")
        self.ai_fps_lbl = QLabel("FPS: --")
        self.ai_inf_lbl = QLabel("Inference Time: -- ms")
        self.ai_det_lbl = QLabel("Total Detections: 0")
        
        for lbl in [self.ai_status_lbl, self.ai_params_lbl, self.ai_fps_lbl, self.ai_inf_lbl, self.ai_det_lbl]:
            lbl.setStyleSheet("color: #FFFFFF; font-size: 16px;")
            ai_lay.addWidget(lbl)
        
        layout.addWidget(cpu_card, 0, 0)
        layout.addWidget(ram_card, 0, 1)
        layout.addWidget(gpu_card, 1, 0)
        layout.addWidget(ai_card, 1, 1)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def lbl(self, text):
        l = QLabel(text)
        l.setProperty("class", "info-text")
        return l
        
    def val(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px;")
        return l

    @pyqtSlot(dict)
    def update_ai_stats(self, stats):
        model = stats.get("model_name", "YOLO11m")
        params = stats.get("params", "~20M")
        fps = stats.get("fps", 0)
        inf = stats.get("inference_time", 0)
        total = stats.get("total_detections", 0)
        
        self.ai_status_lbl.setText(f"Model Status: Loaded ({model})")
        self.ai_params_lbl.setText(f"Parameters: {params}")
        self.ai_fps_lbl.setText(f"FPS: {fps:.1f}")
        self.ai_inf_lbl.setText(f"Inference Time: {inf:.1f} ms")
        self.ai_det_lbl.setText(f"Total Detections: {total}")

    def update_diagnostics(self):
        # CPU
        self.cpu_usage_lbl.setText(f"{psutil.cpu_percent()}%")
        
        # RAM
        mem = psutil.virtual_memory()
        self.ram_used_lbl.setText(f"{mem.used / (1024**3):.1f} GB ({mem.percent}%)")
        self.ram_avail_lbl.setText(f"{mem.available / (1024**3):.1f} GB")
        
        # GPU
        if self.has_gpu:
            try:
                import pynvml
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes): name = name.decode()
                
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                self.gpu_name.setText(name)
                self.gpu_usage.setText(f"{util.gpu}%")
                self.gpu_temp.setText(f"{temp} °C")
                self.gpu_power.setText(f"{power:.1f} W")
                self.gpu_vram.setText(f"{mem_info.used / (1024**2):.0f} MB / {mem_info.total / (1024**2):.0f} MB")
            except Exception as e:
                self.gpu_name.setText("Error reading NVML")
