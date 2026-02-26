from ultralytics import YOLO
import logging
import torch
import numpy as np

logger = logging.getLogger(__name__)

class Detector:
    def __init__(self, model_path="yolov8n.pt", device="cpu", conf=0.4):
        self.device = device
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            self.device = "cpu"
            
        self.model = YOLO(model_path)
        self.conf = conf
        logger.info(f"Loaded model {model_path} on {self.device}")

    def track(self, frame, tracker_type="bytetrack"):
        # track method handles detection + tracking natively
        results = self.model.track(
            source=frame,
            device=self.device,
            conf=self.conf,
            persist=True,
            tracker=f"{tracker_type}.yaml",
            verbose=False
        )
        return results[0]

    def get_tracks(self, result):
        """Extract tracks into [[x1, y1, x2, y2, id, conf, cls]] format"""
        tracks = []
        if result.boxes is not None and result.boxes.id is not None:
            # result.boxes.data is [N, 6] or [N, 7] with IDs
            # Standard format: [x1, y1, x2, y2, id, conf, cls]
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                track_id = int(box.id[0].item())
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                tracks.append([x1, y1, x2, y2, track_id, conf, cls])
        return tracks
