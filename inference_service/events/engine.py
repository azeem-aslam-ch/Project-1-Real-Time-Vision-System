import numpy as np
import logging
import time
from shapely.geometry import Point, Polygon, LineString

logger = logging.getLogger(__name__)
class EventEngine:
    def __init__(self, config):
        self.config = config
        self.line_crossing_conf = config.get("line_crossing", {})
        self.roi_intrusion_conf = config.get("roi_intrusion", {})
        self.cooldown = config.get("cooldown_seconds", 5)
        
        # Track history for line crossing: {id: [last_centroid, current_centroid]}
        self.track_history = {}
        self.last_triggered = {} # {(track_id, event_type): timestamp}

    def process(self, tracks):
        """
        tracks: list of [x1, y1, x2, y2, id, conf, cls]
        """
        current_events = []
        
        for track in tracks:
            x1, y1, x2, y2, track_id, conf, cls = track
            centroid = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            # 1. ROI Intrusion
            if self.roi_intrusion_conf.get("enabled"):
                for zone in self.roi_intrusion_conf.get("zones", []):
                    if self._is_point_in_poly(centroid, zone["coords"]):
                        last_t = self.last_triggered.get((track_id, f"roi_{zone['id']}"), 0)
                        if time.time() - last_t > self.cooldown:
                            event = {
                                "type": "roi_intrusion",
                                "zone_id": zone["id"],
                                "track_id": track_id,
                                "class_id": cls
                            }
                            current_events.append(event)
                            self.last_triggered[(track_id, f"roi_{zone['id']}")] = time.time()

            # 2. Line Crossing
            if self.line_crossing_conf.get("enabled"):
                if track_id in self.track_history:
                    last_centroid = self.track_history[track_id]
                    for line in self.line_crossing_conf.get("lines", []):
                        if self._is_line_crossed(last_centroid, centroid, line["coords"]):
                            last_t = self.last_triggered.get((track_id, f"line_{line['id']}"), 0)
                            if time.time() - last_t > self.cooldown:
                                event = {
                                    "type": "line_crossing",
                                    "line_id": line["id"],
                                    "track_id": track_id,
                                    "class_id": cls
                                }
                                current_events.append(event)
                                self.last_triggered[(track_id, f"line_{line['id']}")] = time.time()
                
                self.track_history[track_id] = centroid

        # Cleanup track history (simple version: keep only current ids)
        current_ids = {t[4] for t in tracks}
        self.track_history = {k: v for k, v in self.track_history.items() if k in current_ids}
        
        return current_events

    def _is_point_in_poly(self, point, poly_coords):
        poly = Polygon(poly_coords)
        return poly.contains(Point(point))

    def _is_line_crossed(self, p1, p2, line_coords):
        movement_line = LineString([p1, p2])
        boundary_line = LineString(line_coords)
        return movement_line.intersects(boundary_line)
