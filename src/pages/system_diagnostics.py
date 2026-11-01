import os
import psutil
import platform
import cpuinfo
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFormLayout, QFrame, QProgressBar, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from src import theme
from src.ui_kit import MetricTile, make_card, page_header, tag, kv_row, value_label

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
        main_layout.setContentsMargins(28, 18, 28, 18)
        main_layout.setSpacing(14)
        main_layout.addWidget(page_header("Diagnostics", "Hardware and model health, refreshed every second.", tag("LIVE")))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(content)
        outer.setContentsMargins(0, 0, 8, 0)
        outer.setSpacing(14)

        tiles = QHBoxLayout()
        tiles.setSpacing(14)
        self.t_cpu = MetricTile("CPU LOAD", "%", 40)
        self.t_ram = MetricTile("MEMORY", "%", 40)
        self.t_gpu = MetricTile("GPU LOAD", "%", 40)
        self.t_fps = MetricTile("AI FPS", "", 40)
        for t in (self.t_cpu, self.t_ram, self.t_gpu, self.t_fps):
            tiles.addWidget(t)
        outer.addLayout(tiles)

        layout = QGridLayout()
        layout.setSpacing(14)

        cpu_card, cl = make_card("CPU")
        cl.addLayout(kv_row("Name", value_label(self.cpu_info.get('brand_raw', platform.processor()))))
        cl.addLayout(kv_row("Cores / threads", value_label(f"{psutil.cpu_count(logical=False)} / {psutil.cpu_count(logical=True)}")))
        self.cpu_usage_lbl = value_label("0%")
        cl.addLayout(kv_row("Usage", self.cpu_usage_lbl))
        cl.addStretch()

        ram_card, rl = make_card("MEMORY")
        mem = psutil.virtual_memory()
        rl.addLayout(kv_row("Total", value_label(f"{mem.total / (1024**3):.1f} GB")))
        self.ram_used_lbl = value_label("0 GB (0%)")
        rl.addLayout(kv_row("Used", self.ram_used_lbl))
        self.ram_avail_lbl = value_label("0 GB")
        rl.addLayout(kv_row("Available", self.ram_avail_lbl))
        rl.addStretch()

        gpu_card, gl = make_card("GPU")
        self.gpu_name = value_label("N/A")
        self.gpu_usage = value_label("N/A")
        self.gpu_temp = value_label("N/A")
        self.gpu_power = value_label("N/A")
        self.gpu_vram = value_label("N/A")
        for k, w in (("Name", self.gpu_name), ("Usage", self.gpu_usage), ("Temperature", self.gpu_temp),
                     ("Power draw", self.gpu_power), ("VRAM used", self.gpu_vram)):
            gl.addLayout(kv_row(k, w))
        gl.addStretch()

        ai_card, al = make_card("AI MODEL")
        model_name = os.path.basename(self.ai_engine.model_path) if self.ai_engine else "N/A"
        al.addLayout(kv_row("Model", value_label(model_name, theme.ACCENT)))
        self.ai_status_lbl = value_label("Loaded", theme.OK)
        self.ai_params_lbl = value_label("--")
        self.ai_fps_lbl = value_label("--")
        self.ai_inf_lbl = value_label("-- ms")
        self.ai_det_lbl = value_label("0")
        for k, w in (("Status", self.ai_status_lbl), ("Parameters", self.ai_params_lbl), ("FPS", self.ai_fps_lbl),
                     ("Inference time", self.ai_inf_lbl), ("Total detections", self.ai_det_lbl)):
            al.addLayout(kv_row(k, w))
        al.addStretch()

        layout.addWidget(cpu_card, 0, 0)
        layout.addWidget(ram_card, 0, 1)
        layout.addWidget(gpu_card, 1, 0)
        layout.addWidget(ai_card, 1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        outer.addLayout(layout)
        outer.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def lbl(self, text):
        l = QLabel(text)
        l.setProperty("class", "muted")
        return l

    def val(self, text):
        return value_label(text)

    @pyqtSlot(dict)
    def update_ai_stats(self, stats):
        model = stats.get("model_name", "YOLO11m")
        params = stats.get("params", "~20M")
        fps = stats.get("fps", 0)
        inf = stats.get("inference_time", 0)
        total = stats.get("total_detections", 0)
        
        self.ai_status_lbl.setText(f"Loaded ({model})")
        self.ai_params_lbl.setText(f"{params}")
        self.ai_fps_lbl.setText(f"{fps:.1f}")
        self.ai_inf_lbl.setText(f"{inf:.1f} ms")
        self.ai_det_lbl.setText(f"{total}")
        self.t_fps.set(f"{fps:.1f}", fps / 60, theme.OK)

    def update_diagnostics(self):
        # CPU
        cpu = psutil.cpu_percent()
        self.cpu_usage_lbl.setText(f"{cpu}%")
        self.t_cpu.set(f"{cpu:.0f}", cpu / 100, theme.ACCENT if cpu < 80 else theme.WARN)
        
        # RAM
        mem = psutil.virtual_memory()
        self.ram_used_lbl.setText(f"{mem.used / (1024**3):.1f} GB ({mem.percent}%)")
        self.ram_avail_lbl.setText(f"{mem.available / (1024**3):.1f} GB")
        self.t_ram.set(f"{mem.percent:.0f}", mem.percent / 100, theme.ACCENT if mem.percent < 85 else theme.WARN)
        
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
                self.t_gpu.set(f"{util.gpu}", util.gpu / 100, theme.ACCENT)
            except Exception as e:
                self.gpu_name.setText("Error reading NVML")
