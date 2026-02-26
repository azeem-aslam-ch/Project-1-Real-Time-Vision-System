import redis
import sqlite3
import json
import time
import logging

logger = logging.getLogger(__name__)

class DataWriter:
    def __init__(self, redis_url="redis://localhost:6379/0", sqlite_path="data/events.db"):
        self.redis = redis.from_url(redis_url)
        self.sqlite_path = sqlite_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                target_id TEXT,
                track_id INTEGER,
                class_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def push_metrics(self, metrics):
        """Push real-time metrics to Redis"""
        self.redis.set("vision:metrics", json.dumps(metrics))

    def push_event(self, event):
        """Log event to Redis (latest) and SQLite (history)"""
        # Redis latest events (keep last 10)
        self.redis.lpush("vision:events", json.dumps(event))
        self.redis.ltrim("vision:events", 0, 9)
        
        # SQLite history
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_history (event_type, target_id, track_id, class_id)
            VALUES (?, ?, ?, ?)
        ''', (event["type"], event.get("zone_id") or event.get("line_id"), event["track_id"], event["class_id"]))
        conn.commit()
        conn.close()

    def set_frame(self, frame_bytes):
        """Store latest MJPEG frame in Redis"""
        self.redis.set("vision:latest_frame", frame_bytes)

    def set_status(self, status):
        """Set inference engine status (RUNNING, STOPPED, ERROR)"""
        self.redis.set("vision:status", status)
