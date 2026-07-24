import time
from PyQt6.QtCore import QObject, pyqtSignal
from src import database
from src.audio_system import speaker

class AlertSystem(QObject):
    # Signals
    alert_triggered = pyqtSignal(str) # Emits alert message
    alert_cleared = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.no_helmet_start_time = None
        self.is_alert_active = False
        self.alert_delay = 5 # seconds, default
        self.safety_mode = "Monitor Only"
        self.last_logged_event_time = 0
        self.last_helmet_state = None
        
        # Load settings
        self.load_settings()

    def load_settings(self):
        settings = database.get_settings()
        if settings:
            self.alert_delay = settings.get('alert_delay', 5)
            self.safety_mode = settings.get('safety_mode', 'Monitor Only')

    def process_stats(self, stats):
        helmet_detected = stats.get("helmet_detected", False)
        confidence = stats.get("confidence", 0.0)
        
        current_time = time.time()

        # Handle speech on helmet state transition
        if self.last_helmet_state != helmet_detected:
            self.last_helmet_state = helmet_detected
            if helmet_detected:
                speaker.speak("Helmet detected. Now you can ride the bike.")
            else:
                speaker.speak("Please wear helmet.")
        
        if not helmet_detected:
            if self.no_helmet_start_time is None:
                # Started not detecting helmet
                self.no_helmet_start_time = current_time
                database.log_event("Helmet Removed", confidence, "Rider removed helmet or not detected.")
            else:
                elapsed = current_time - self.no_helmet_start_time
                if elapsed >= self.alert_delay and not self.is_alert_active:
                    self.trigger_alert(confidence)
        else:
            if self.no_helmet_start_time is not None:
                # Helmet restored
                self.no_helmet_start_time = None
                database.log_event("Helmet Restored", confidence, "Helmet detected again.")
                
            if self.is_alert_active:
                self.clear_alert()

    def trigger_alert(self, confidence, screenshot_path=None):
        self.is_alert_active = True
        
        # Save screenshot
        if self.main_window and hasattr(self.main_window, 'latest_image') and self.main_window.latest_image:
            import os
            from datetime import datetime
            captures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "captures"))
            os.makedirs(captures_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(captures_dir, f"alert_{timestamp}.jpg")
            self.main_window.latest_image.save(screenshot_path)
        
        alert_msg = f"NO HELMET DETECTED ({confidence:.1%})"
        
        # Log to DB
        database.log_event("Alert Triggered", confidence, "No helmet threshold exceeded.", screenshot_path)
        database.log_alert("No Helmet", alert_msg, screenshot_path)
        
        if self.safety_mode == "Smart Lock Mode":
            database.log_event("Smart Lock Activated", confidence, "Engine lock simulated.", screenshot_path)
            alert_msg += " - SMART LOCK ACTIVE"
            
        self.alert_triggered.emit(alert_msg)

    def clear_alert(self):
        self.is_alert_active = False
        self.alert_cleared.emit()

