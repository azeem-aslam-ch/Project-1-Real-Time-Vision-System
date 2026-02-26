import cv2
import time
import logging
from threading import Thread, Lock

logger = logging.getLogger(__name__)

class VideoCapture:
    def __init__(self, source, width=640, fps_throttle=None):
        self.source = source
        self.width = width
        self.fps_throttle = fps_throttle
        self.cap = cv2.VideoCapture(source)
        self.frame = None
        self.running = False
        self.lock = Lock()
        self.last_capture_time = 0
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open source: {source}")
            
    def start(self):
        self.running = True
        self.thread = Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def _update(self):
        while self.running:
            if self.fps_throttle:
                time_elapsed = time.time() - self.last_capture_time
                if time_elapsed < 1.0 / self.fps_throttle:
                    time.sleep(0.001)
                    continue

            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Grab failed, attempting reconnect...")
                self.cap.release()
                time.sleep(2)
                self.cap = cv2.VideoCapture(self.source)
                continue

            # Resize for performance
            if self.width:
                h, w = frame.shape[:2]
                aspect = w / h
                new_h = int(self.width / aspect)
                frame = cv2.resize(frame, (self.width, new_h))

            with self.lock:
                self.frame = frame
                self.last_capture_time = time.time()

    def read(self):
        with self.lock:
            return self.frame is not None, self.frame

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.cap.release()

    def get_fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)
