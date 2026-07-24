import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "rideshield.db"))
SESSION_ID = str(uuid.uuid4())

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Detections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            detected_class TEXT,
            helmet_status BOOLEAN,
            confidence REAL,
            fps REAL,
            inference_time REAL
        )
    ''')
    
    # Try adding new columns to existing table
    try:
        cursor.execute("ALTER TABLE detections ADD COLUMN session_id TEXT")
        cursor.execute("ALTER TABLE detections ADD COLUMN detected_class TEXT")
    except:
        pass
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            confidence REAL,
            details TEXT,
            screenshot_path TEXT
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT,
            description TEXT,
            screenshot_path TEXT
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            safety_mode TEXT DEFAULT 'Monitor Only',
            alert_delay INTEGER DEFAULT 5,
            confidence_threshold REAL DEFAULT 0.5,
            camera_id INTEGER DEFAULT 0,
            resolution TEXT DEFAULT '640x480',
            model_name TEXT DEFAULT 'yolo11m.pt'
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN model_name TEXT DEFAULT 'yolo11m.pt'")
    except:
        pass

    
    # Insert default settings if not exists
    cursor.execute('INSERT OR IGNORE INTO settings (id) VALUES (1)')
    
    conn.commit()
    conn.close()

def log_detection(helmet_status, confidence, fps, inference_time, detected_class="Helmet"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detections (session_id, detected_class, helmet_status, confidence, fps, inference_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (SESSION_ID, detected_class, helmet_status, confidence, fps, inference_time))
    conn.commit()
    conn.close()

def log_event(event_type, confidence=None, details="", screenshot_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try adding columns if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE events ADD COLUMN screenshot_path TEXT')
    except:
        pass
        
    cursor.execute('''
        INSERT INTO events (event_type, confidence, details, screenshot_path)
        VALUES (?, ?, ?, ?)
    ''', (event_type, confidence, details, screenshot_path))
    conn.commit()
    conn.close()

def log_alert(alert_type, description="", screenshot_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('ALTER TABLE alerts ADD COLUMN screenshot_path TEXT')
    except:
        pass
        
    cursor.execute('''
        INSERT INTO alerts (type, description, screenshot_path)
        VALUES (?, ?, ?)
    ''', (alert_type, description, screenshot_path))
    conn.commit()
    conn.close()

def get_settings():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_settings(safety_mode, alert_delay, confidence_threshold, camera_id, resolution):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE settings
        SET safety_mode = ?, alert_delay = ?, confidence_threshold = ?, camera_id = ?, resolution = ?
        WHERE id = 1
    ''', (safety_mode, alert_delay, confidence_threshold, camera_id, resolution))
    conn.commit()
    conn.close()

def get_recent_events(limit=50):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_setting(key, value):
    valid_keys = ['safety_mode', 'alert_delay', 'confidence_threshold', 'camera_id', 'resolution', 'model_name']
    if key not in valid_keys:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE settings
        SET {key} = ?
        WHERE id = 1
    ''', (value,))
    conn.commit()
    conn.close()

# Initializing on import for convenience
init_db()
