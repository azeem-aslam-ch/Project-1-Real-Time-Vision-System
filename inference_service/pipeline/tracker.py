from ultralytics.trackers import BOTSORT, BYTETracker
from pathlib import Path
import yaml
import numpy as np

class Tracker:
    def __init__(self, tracker_type="bytetrack"):
        self.tracker_type = tracker_type
        # Load default tracker config from ultralytics if needed
        # Or define a simple dict
        self.config = {
            "tracker_type": tracker_type,
            "track_high_thresh": 0.5,
            "track_low_thresh": 0.1,
            "new_track_thresh": 0.6,
            "track_buffer": 30,
            "match_thresh": 0.8,
            "gating_low": 2.55,
            "gating_high": 14.3,
            "proximity_thresh": 0.5,
            "appearance_thresh": 0.25,
            "with_reid": False
        }
        
        if tracker_type == "bytetrack":
            self.tracker = BYTETracker(args=self.as_namespace(self.config), frame_rate=30)
        else:
            self.tracker = BOTSORT(args=self.as_namespace(self.config), frame_rate=30)

    def as_namespace(self, d):
        from types import SimpleNamespace
        return SimpleNamespace(**d)

    def update(self, detections, frame):
        """
        detections: numpy array of [x1, y1, x2, y2, conf, cls]
        returns: tracked_objects [[x1, y1, x2, y2, id, conf, cls]]
        """
        if len(detections) == 0:
            return []
            
        tracks = self.tracker.update(detections, frame)
        return tracks
