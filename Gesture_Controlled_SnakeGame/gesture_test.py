"""Gesture test window: live camera + hand skeleton + raw/filtered direction.

Lets you check hand sign detection and tune the direction threshold before
playing. Uses the exact same GestureClassifier + DirectionFilter as the game.

Keys:
  [  ]  decrease/increase direction threshold
  r     reset the direction filter
  d     toggle filter (compare raw vs filtered)
  q/ESC quit
"""

import sys
import time

import cv2
import mediapipe as mp
import numpy as np

from gesture.direction_filter import DirectionFilter
from gesture.gesture_model import GestureClassifier, direction_vector

DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")
SCALE = 2  # 320x320 processed frame -> 640x640 display
PANEL_H = 190


def main():
    cam_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("[Error] Could not open webcam.")
        sys.exit(1)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

    clf = GestureClassifier(target_size=320)
    filt = DirectionFilter()
    mp_hands = mp.solutions.hands
    connections = mp_hands.HAND_CONNECTIONS

    bypass_filter = False
    fps = 0.0
    last = time.perf_counter()
    key = None

    while key not in (ord("q"), 27):
        ret, frame = cap.read()
        if not ret:
            continue

        action, conf = clf.predict(frame)
        vec = clf.last_vector
        raw_action = action if action in DIRECTIONS or action == "START" else None

        if vec is not None and raw_action in DIRECTIONS:
            filtered = filt.update(*vec)
        else:
            filtered = None
        if bypass_filter:
            shown = raw_action
        else:
            shown = filtered if filtered is not None else (filt.current if raw_action in DIRECTIONS else None)

        img = clf.last_frame_processed
        if img is None:
            continue
        disp = cv2.resize(img, (img.shape[1] * SCALE, img.shape[0] * SCALE), interpolation=cv2.INTER_NEAREST)

        if clf.last_landmarks:
            pts = [(int(x * disp.shape[1]), int(y * disp.shape[0])) for x, y, _ in clf.last_landmarks]
            for a, b in connections:
                cv2.line(disp, pts[a], pts[b], (90, 200, 255), 1)
            for p in pts:
                cv2.circle(disp, p, 2, (255, 255, 255), -1)
        if clf.last_bbox:
            bx, by, bw, bh = clf.last_bbox
            cv2.rectangle(disp, (bx * SCALE, by * SCALE),
                          ((bx + bw) * SCALE, (by + bh) * SCALE), (255, 200, 50), 2)

        if vec is not None:
            w = disp.shape[1] // 2
            h = disp.shape[0] // 2
            vx = int(vec[0] * 60)
            vy = int(vec[1] * 60)
            cv2.arrowedLine(disp, (w, h), (w + vx, h + vy), (80, 255, 120), 3, tipLength=0.35)

        big_arrow = {"UP": "▲", "DOWN": "▼", "LEFT": "◀", "RIGHT": "▶", "START": "✊"}.get(shown, "")
        cv2.putText(disp, big_arrow, (disp.shape[1] - 90, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, (80, 255, 120) if shown else (80, 80, 80), 4)

        now = time.perf_counter()
        fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, now - last))
        last = now

        panel = np.zeros((PANEL_H, disp.shape[1], 3), dtype=np.uint8)
        lines = [
            f"RAW    : {str(raw_action):6s} conf={conf:.2f}",
            f"VECTOR : ndx={vec[0]:+.2f} ndy={vec[1]:+.2f} mag={((vec[0]**2 + vec[1]**2) ** 0.5):.2f}" if vec else "VECTOR : none",
            f"FILTER : {str(shown):6s} current={filt.current} flip_lock={'ARMED' if filt._flip_start else 'off'}",
            f"THRESH : {filt.threshold:.2f}  mag_ema={filt.mag:.2f}  bypass={'ON' if bypass_filter else 'off'}",
            f"FPS    : {fps:.0f}   keys: [ ] threshold, r reset, d bypass, q quit",
        ]
        for i, line in enumerate(lines):
            cv2.putText(panel, line, (12, 26 + i * 34),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (220, 220, 220), 2)

        cv2.imshow("Gesture Test", np.vstack([disp, panel]))
        key = cv2.waitKey(1) & 0xFF
        if key == ord("]"):
            filt.threshold = min(0.6, filt.threshold + 0.02)
        elif key == ord("["):
            filt.threshold = max(0.05, filt.threshold - 0.02)
        elif key == ord("r"):
            filt.reset()
        elif key == ord("d"):
            bypass_filter = not bypass_filter

    cap.release()
    clf.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
