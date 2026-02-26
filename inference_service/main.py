import cv2
import time
import logging
import numpy as np
from config.config import config
from inference_service.pipeline.capture import VideoCapture
from inference_service.pipeline.detector import Detector
from inference_service.pipeline.tracker import Tracker
from inference_service.events.engine import EventEngine
from inference_service.metrics.writer import DataWriter

# Configure Logging
logging.basicConfig(level=config.logging.get("level", "INFO"))
logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self):
        self.conf = config.inference
        self.writer = DataWriter(
            redis_url=config.storage.get("redis_url"),
            sqlite_path=config.storage.get("sqlite_path")
        )
        
        self.capture = VideoCapture(
            source=self.conf.get("input_source"),
            width=self.conf.get("resize_width"),
            fps_throttle=self.conf.get("fps_throttle")
        )
        
        self.detector = Detector(
            model_path=self.conf.get("model_path"),
            device=self.conf.get("device"),
            conf=self.conf.get("confidence_threshold")
        )
        
        self.tracker = Tracker(tracker_type=config.tracking.get("tracker_type"))
        self.event_engine = EventEngine(config.events)
        
        self.running = False
        self.state = "STOPPED"

    def run(self):
        logger.info("Starting Inference Engine...")
        self.capture.start()
        self.running = True
        self.state = "RUNNING"
        self.writer.set_status(self.state)

        frame_count = 0
        start_time = time.time()

        try:
            while self.running:
                loop_start = time.time()
                
                ret, frame = self.capture.read()
                if not ret:
                    time.sleep(0.01)
                    continue

                # 1. Capture -> Stage Timer
                t1 = time.time()
                
                # 2. Track (using native model.track)
                result = self.detector.track(frame, tracker_type=config.tracking.get("tracker_type", "bytetrack"))
                tracks = self.detector.get_tracks(result)
                t2 = time.time()
                t3 = time.time() # Track stage combined with detect now

                # 4. Events
                events = self.event_engine.process(tracks)
                for event in events:
                    event["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self.writer.push_event(event)
                t4 = time.time()

                # 5. Overlay (Optional for streaming, but we'll do it for MJPEG simplicity)
                annotated_frame = self._draw_annotations(frame, tracks, events)
                
                # 6. Push to Redis (MJPEG)
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                self.writer.set_frame(buffer.tobytes())

                # Metrics Calculation
                frame_count += 1
                if frame_count % 30 == 0:
                    fps = 30 / (time.time() - start_time)
                    start_time = time.time()
                    
                    metrics = {
                        "fps": round(fps, 2),
                        "latency_detect": round((t2 - t1) * 1000, 2),
                        "latency_track": round((t3 - t2) * 1000, 2),
                        "latency_event": round((t4 - t3) * 1000, 2),
                        "total_latency": round((time.time() - loop_start) * 1000, 2),
                        "state": self.state
                    }
                    self.writer.push_metrics(metrics)

        except Exception as e:
            logger.exception("Inference Loop Error")
            self.state = "ERROR"
            self.writer.set_status(self.state)
        finally:
            self.stop()

    def _draw_annotations(self, frame, tracks, events):
        # Draw bounding boxes and track IDs
        for track in tracks:
            x1, y1, x2, y2, track_id, conf, cls = track
            color = (0, 255, 0) # Green for active tracks
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame, f"ID: {int(track_id)}", (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw ROI zones
        if config.events.get("roi_intrusion", {}).get("enabled"):
            for zone in config.events.get("roi_intrusion", {}).get("zones", []):
                pts = np.array(zone["coords"], np.int32)
                cv2.polylines(frame, [pts], True, (0, 0, 255), 2)
                
        # Draw Crossing Lines
        if config.events.get("line_crossing", {}).get("enabled"):
            for line in config.events.get("line_crossing", {}).get("lines", []):
                pts = np.array(line["coords"], np.int32)
                cv2.line(frame, tuple(pts[0]), tuple(pts[1]), (255, 0, 0), 2)
                
        return frame

    def stop(self):
        self.running = False
        self.state = "STOPPED"
        self.capture.stop()
        self.writer.set_status(self.state)

if __name__ == "__main__":
    engine = InferenceEngine()
    engine.run()
