import os
import math
from typing import Tuple, Optional, List

import cv2
import numpy as np
import mediapipe as mp

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("ABSL_CPP_MIN_LOG_LEVEL", "2")

_DIRECTION_THRESHOLD = 0.18
_PINCH_THRESHOLD = 0.08
_MAX_HANDS = 1

WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_MCP = 9


def _dist(ax, ay, bx, by) -> float:
    return math.hypot(ax - bx, ay - by)


def direction_vector(landmarks: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
    """Normalized wrist->index-tip vector, scaled by hand size. None if malformed."""
    if landmarks is None or len(landmarks) < 21:
        return None
    wrist = landmarks[WRIST]
    index_tip = landmarks[INDEX_TIP]
    middle_mcp = landmarks[MIDDLE_MCP]
    dx = index_tip[0] - wrist[0]
    dy = index_tip[1] - wrist[1]
    scale = max(1e-4, _dist(wrist[0], wrist[1], middle_mcp[0], middle_mcp[1]))
    return (dx / scale, dy / scale)


def classify_landmarks(
    landmarks: List[Tuple[float, float]],
    handedness_score: float = 0.6,
) -> Tuple[Optional[str], float]:
    """Classify gesture from 21 normalized (x, y) landmarks.

    Returns (action, confidence): 'UP'|'DOWN'|'LEFT'|'RIGHT'|'START' or None.
    Pure function; no MediaPipe dependency.
    """
    if landmarks is None or len(landmarks) < 21:
        return None, 0.0

    wrist = landmarks[WRIST]
    thumb_tip = landmarks[THUMB_TIP]
    index_tip = landmarks[INDEX_TIP]

    pinch_dist = _dist(thumb_tip[0], thumb_tip[1], index_tip[0], index_tip[1])
    if pinch_dist < _PINCH_THRESHOLD:
        conf = min(0.99, 0.55 + (0.45 * handedness_score))
        return "START", conf

    vec = direction_vector(landmarks)
    if vec is None:
        return None, 0.0
    ndx, ndy = vec

    action = None
    base_conf = max(0.15, handedness_score * 0.9)

    if abs(ndx) >= abs(ndy):
        if ndx > _DIRECTION_THRESHOLD:
            action = "RIGHT"
        elif ndx < -_DIRECTION_THRESHOLD:
            action = "LEFT"
    else:
        if ndy < -_DIRECTION_THRESHOLD:
            action = "UP"
        elif ndy > _DIRECTION_THRESHOLD:
            action = "DOWN"

    if action:
        strength = min(1.0, max(abs(ndx), abs(ndy)))
        conf = float(min(1.0, base_conf * 0.6 + 0.4 * strength))
        return action, conf

    return None, 0.0


class GestureClassifier:
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        verbose: bool = False,
        target_size: int = 256,
    ):
        self.verbose = verbose
        self.target_size = target_size
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=_MAX_HANDS,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.last_landmarks: Optional[List[Tuple[float, float, float]]] = None
        self.last_bbox: Optional[Tuple[int, int, int, int]] = None
        self.last_frame_processed: Optional[np.ndarray] = None
        self.last_vector: Optional[Tuple[float, float]] = None

        if self.verbose:
            print("[GestureClassifier] MediaPipe Hands initialized (mirroring enabled)")

    def _center_crop_square(self, frame: np.ndarray, target_size: Optional[int] = None) -> np.ndarray:
        h, w = frame.shape[:2]
        if h != w:
            side = min(h, w)
            start_x = (w - side) // 2
            start_y = (h - side) // 2
            frame = frame[start_y:start_y + side, start_x:start_x + side]
        if target_size and (frame.shape[0] != target_size or frame.shape[1] != target_size):
            frame = cv2.resize(frame, (target_size, target_size), interpolation=cv2.INTER_AREA)
        return frame

    def predict(self, frame: np.ndarray) -> Tuple[Optional[str], float]:
        self.last_landmarks = None
        self.last_bbox = None
        self.last_frame_processed = None
        self.last_vector = None

        if frame is None:
            return None, 0.0

        frame_sq = self._center_crop_square(cv2.flip(frame, 1), target_size=self.target_size)
        self.last_frame_processed = frame_sq

        results = self.hands.process(cv2.cvtColor(frame_sq, cv2.COLOR_BGR2RGB))

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return None, 0.0

        hand = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0].classification[0]
        score = float(getattr(handedness, "score", 0.6))

        lms = [(lm.x, lm.y) for lm in hand.landmark]
        self.last_landmarks = [(lm.x, lm.y, lm.z) for lm in hand.landmark]

        xs = [lm.x for lm in hand.landmark]
        ys = [lm.y for lm in hand.landmark]
        min_x, min_y = min(xs), min(ys)
        max_x, max_y = max(xs), max(ys)
        pad_x = (max_x - min_x) * 0.1
        pad_y = (max_y - min_y) * 0.1
        img_h, img_w = frame_sq.shape[:2]
        self.last_bbox = (
            int(max(0.0, min_x - pad_x) * img_w),
            int(max(0.0, min_y - pad_y) * img_h),
            max(2, int(min(1.0, max_x + pad_x) - max(0.0, min_x - pad_x)) * img_w),
            max(2, int(min(1.0, max_y + pad_y) - max(0.0, min_y - pad_y)) * img_h),
        )

        self.last_vector = direction_vector(lms)
        return classify_landmarks(lms, handedness_score=score)

    def close(self):
        try:
            self.hands.close()
        except Exception:
            pass
