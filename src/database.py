import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "rideshield.db"))

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
            helmet_status BOOLEAN,
            confidence REAL,
            fps REAL,
            inference_time REAL
        )
    ''')
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            confidence REAL,
            details TEXT
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT,
            description TEXT
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
            resolution TEXT DEFAULT '640x480'
        )
    ''')
    
    # Insert default settings if not exists
    cursor.execute('INSERT OR IGNORE INTO settings (id) VALUES (1)')
    
    conn.commit()
    conn.close()

def log_detection(helmet_status, confidence, fps, inference_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detections (helmet_status, confidence, fps, inference_time)
        VALUES (?, ?, ?, ?)
    ''', (helmet_status, confidence, fps, inference_time))
    conn.commit()
    conn.close()

def log_event(event_type, confidence=None, details=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (event_type, confidence, details)
        VALUES (?, ?, ?)
    ''', (event_type, confidence, details))
    conn.commit()
    conn.close()

def log_alert(alert_type, description=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (type, description)
        VALUES (?, ?)
    ''', (alert_type, description))
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
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_setting(key, value):
    valid_keys = ['safety_mode', 'alert_delay', 'confidence_threshold', 'camera_id', 'resolution']
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
