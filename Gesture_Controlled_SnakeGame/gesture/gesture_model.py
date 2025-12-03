import os
import math
from typing import Tuple, Optional, List

import cv2
import numpy as np
import mediapipe as mp

# Reduce TF / absl verbosity (set before MediaPipe init)
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("ABSL_CPP_MIN_LOG_LEVEL", "2")

# Tunable thresholds
_DIRECTION_THRESHOLD = 0.18
_PINCH_THRESHOLD = 0.08
_MAX_HANDS = 1

class GestureClassifier:
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        verbose: bool = False,
        target_size: int = 320,
    ):
        self.verbose = verbose
        self.target_size = target_size  # square size used for processing
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=_MAX_HANDS,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # last detection artifacts for UI/debug
        self.last_landmarks: Optional[List[Tuple[float, float, float]]] = None
        self.last_bbox: Optional[Tuple[int, int, int, int]] = None  # x,y,w,h in pixels relative to processed frame
        self.last_frame_processed: Optional[np.ndarray] = None  # BGR image that was passed to MediaPipe

        if self.verbose:
            print("[GestureClassifier] MediaPipe Hands initialized (mirroring enabled)")

    def _norm_dist(self, a, b) -> float:
        return math.hypot(a.x - b.x, a.y - b.y)

    def _center_crop_square(self, frame: np.ndarray, target_size: Optional[int] = None) -> np.ndarray:
        h, w = frame.shape[:2]
        if h == w and target_size is None:
            out = frame
        else:
            side = min(h, w)
            start_x = (w - side) // 2
            start_y = (h - side) // 2
            out = frame[start_y:start_y + side, start_x:start_x + side]
        if target_size:
            out = cv2.resize(out, (target_size, target_size), interpolation=cv2.INTER_AREA)
        return out

    def predict(self, frame: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Predict action from a BGR cv2 frame (numpy array).
        Returns (action, confidence) where action is one of 'UP','DOWN','LEFT','RIGHT','START' or None.
        Side-effects:
          - self.last_frame_processed: the square BGR image used for detection (mirrored)
          - self.last_landmarks: list of normalized (x,y,z) for each landmark in processed image coords
          - self.last_bbox: (x, y, w, h) bbox in pixels relative to last_frame_processed, or None
        """
        self.last_landmarks = None
        self.last_bbox = None
        self.last_frame_processed = None

        if frame is None:
            return None, 0.0

        # Mirror horizontally so preview and gestures are intuitive (left/right match user view).
        frame_flipped = cv2.flip(frame, 1)

        # Crop to square and resize to target_size for MediaPipe
        frame_sq = self._center_crop_square(frame_flipped, target_size=self.target_size)
        self.last_frame_processed = frame_sq.copy()

        # Convert BGR -> RGB for MediaPipe
        img_rgb = cv2.cvtColor(frame_sq, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return None, 0.0

        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0].classification[0]
        score = float(getattr(handedness, "score", 0.6))

        # save normalized landmarks
        self.last_landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

        # Compute bbox in processed image pixel coordinates from landmarks
        xs = [lm.x for lm in hand_landmarks.landmark]
        ys = [lm.y for lm in hand_landmarks.landmark]
        min_x = max(0.0, min(xs))
        min_y = max(0.0, min(ys))
        max_x = min(1.0, max(xs))
        max_y = min(1.0, max(ys))

        img_h, img_w = frame_sq.shape[:2]
        # add small padding (10% of hand box)
        pad_x = (max_x - min_x) * 0.1
        pad_y = (max_y - min_y) * 0.1
        min_x_p = max(0.0, min_x - pad_x)
        min_y_p = max(0.0, min_y - pad_y)
        max_x_p = min(1.0, max_x + pad_x)
        max_y_p = min(1.0, max_y + pad_y)

        x_px = int(min_x_p * img_w)
        y_px = int(min_y_p * img_h)
        w_px = max(2, int((max_x_p - min_x_p) * img_w))
        h_px = max(2, int((max_y_p - min_y_p) * img_h))
        self.last_bbox = (x_px, y_px, w_px, h_px)

        # Key landmarks for gesture heuristics
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

        # Pinch detection -> START
        pinch_dist = self._norm_dist(thumb_tip, index_tip)
        if pinch_dist < _PINCH_THRESHOLD:
            conf = min(0.99, 0.55 + (0.45 * score))
            return "START", conf

        # Direction: wrist -> index tip (note: image coords y down)
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y

        # Normalize by wrist->middle_mcp as hand scale
        ref_pt = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        scale = max(1e-4, self._norm_dist(wrist, ref_pt))
        ndx = dx / scale
        ndy = dy / scale

        action = None
        base_conf = max(0.15, score * 0.9)

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

    def close(self):
        try:
            self.hands.close()
        except Exception:
            pass