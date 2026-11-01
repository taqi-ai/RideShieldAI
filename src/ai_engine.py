import os
import time
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from ultralytics import YOLO
from src import database

class DetectionManager(QThread):
    # Signals
    # image_update: Emits the processed frame (QImage)
    image_update = pyqtSignal(QImage)
    
    # stats_update: Emits a dictionary with detection stats
    # {
    #     "helmet_detected": bool,
    #     "confidence": float,
    #     "fps": float,
    #     "inference_time": float,
    #     "bboxes": list,
    #     "total_detections": int,
    #     "model_name": str,
    #     "params": str
    # }
    stats_update = pyqtSignal(dict)
    
    # error_signal: Emits error messages
    error_signal = pyqtSignal(str)

    def __init__(self, model_path, camera_id=0, parent=None):
        super().__init__(parent)
        self.model_path = model_path
        self.camera_id = camera_id
        self.running = False
        self.model = None
        self.helmet_class_id = None
        self.confidence_threshold = 0.5
        self.total_detections = 0
        self.model_name = os.path.basename(model_path)
        self.params = "Unknown"
        
    def load_model(self):
        try:
            self.model = YOLO(self.model_path)
            # Find the helmet class ID
            for class_id, class_name in self.model.names.items():
                if 'helmet' in class_name.lower() and 'no' not in class_name.lower():
                    self.helmet_class_id = class_id
                    break
            
            # If not found explicitly by name, assume class 0 is helmet for typical binary models
            if self.helmet_class_id is None:
                self.helmet_class_id = 0
                
            return True
        except Exception as e:
            self.error_signal.emit(f"Failed to load model: {str(e)}")
            return False

    def update_settings(self, camera_id, confidence_threshold):
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold

    def run(self):
        self.running = True
        
        if self.model is None:
            if not self.load_model():
                self.running = False
                return

        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            self.error_signal.emit(f"Failed to open camera {self.camera_id}")
            self.running = False
            return

        prev_time = time.time()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                self.error_signal.emit("Failed to grab frame")
                time.sleep(0.1)
                continue
                
            start_infer_time = time.time()
            
            # Run YOLO inference
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            
            inference_time = (time.time() - start_infer_time) * 1000  # ms
            
            # Process results
            helmet_detected = False
            max_confidence = 0.0
            bboxes = []
            
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    if cls == self.helmet_class_id:
                        helmet_detected = True
                        if conf > max_confidence:
                            max_confidence = conf
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (151, 220, 61), 2)
                        cv2.putText(frame, f"Helmet {conf:.2f}", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (151, 220, 61), 2)
                    else:
                        # Draw other detected objects (e.g., no_helmet) in red
                        label = self.model.names.get(cls, "Object")
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (116, 102, 255), 2)
                        cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (116, 102, 255), 2)
                        
                    bboxes.append({'class': cls, 'conf': conf, 'box': [x1, y1, x2, y2]})

            # Calculate FPS
            current_time = time.time()
            fps = 1.0 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
            prev_time = current_time

            self.total_detections += len(bboxes)

            # Log to DB
            detected_class = "Helmet" if helmet_detected else "No Helmet"
            # Only log if confident enough, or just log everything? The prompt says "Every detection event must be logged"
            if len(bboxes) > 0:
                database.log_detection(helmet_detected, max_confidence, fps, inference_time, detected_class)

            # Prepare stats
            stats = {
                "helmet_detected": helmet_detected,
                "confidence": max_confidence,
                "fps": fps,
                "inference_time": inference_time,
                "bboxes": bboxes,
                "total_detections": self.total_detections,
                "model_name": self.model_name,
                "params": self.params
            }
            
            self.stats_update.emit(stats)

            # Convert frame to QImage for PyQt
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Important: copy the image data so it doesn't get corrupted when the original numpy array changes
            self.image_update.emit(qimg.copy())

            # Yield control slightly to prevent 100% CPU usage if camera is too fast
            time.sleep(0.001)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()
