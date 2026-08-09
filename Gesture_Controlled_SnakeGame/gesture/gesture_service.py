# gesture/gesture_service.py
# Background thread owning the camera + MediaPipe classifier.
# The game loop reads the latest GestureResult without ever blocking.

import threading
from dataclasses import dataclass
from typing import Callable, Optional

import cv2
import numpy as np

from gesture.direction_filter import DirectionFilter
from gesture.gesture_model import GestureClassifier

DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")
_WARMUP_FRAMES = 5


@dataclass
class GestureResult:
    frame_id: int
    action: Optional[str]
    confidence: float
    preview: Optional[np.ndarray]
    landmarks: Optional[list]
    bbox: Optional[tuple]


class GestureService:
    def __init__(self, classifier: Optional[GestureClassifier] = None, cam_index: int = 0,
                 capture_factory: Optional[Callable[[int], object]] = None):
        self.cam_index = cam_index
        self.classifier = classifier
        self._capture_factory = capture_factory or (
            lambda idx: cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        )
        self._lock = threading.Lock()
        self._result: Optional[GestureResult] = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._filter = DirectionFilter()

    def start(self):
        if self.cam_index is None or self._thread is not None:
            return
        if self.classifier is None:
            self.classifier = GestureClassifier()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="gesture")
        self._thread.start()

    def _run(self):
        cap = None
        try:
            cap = self._capture_factory(self.cam_index)
            if cap is None or not cap.isOpened():
                return
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
            for _ in range(_WARMUP_FRAMES):
                if not cap.read()[0]:
                    break
            frame_id = 0
            while not self._stop.is_set():
                ret, frame = cap.read()
                if not ret:
                    continue
                frame_id += 1
                try:
                    action, conf = self.classifier.predict(frame)
                    if action == "START":
                        pass
                    elif action in DIRECTIONS and self.classifier.last_vector:
                        vx, vy = self.classifier.last_vector
                        action = self._filter.update(vx, vy)
                        if action is None:
                            conf = 0.0
                    else:
                        action = None
                        conf = 0.0
                    with self._lock:
                        self._result = GestureResult(
                            frame_id=frame_id,
                            action=action,
                            confidence=conf,
                            preview=self.classifier.last_frame_processed,
                            landmarks=self.classifier.last_landmarks,
                            bbox=self.classifier.last_bbox,
                        )
                except Exception:
                    continue
        finally:
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass

    def latest(self) -> Optional[GestureResult]:
        with self._lock:
            return self._result

    @property
    def alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        try:
            self.classifier.close()
        except Exception:
            pass
