import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import time
import unittest

import numpy as np

from gesture.gesture_service import GestureService


class FakeCapture:
    def __init__(self, frames):
        self.frames = frames
        self.released = False

    def isOpened(self):
        return True

    def read(self):
        if self.frames:
            return True, self.frames.pop(0)
        return False, None

    def release(self):
        self.released = True


class FakeCaptureClosed:
    def isOpened(self):
        return False

    def read(self):
        return False, None

    def release(self):
        pass


class FakeClassifier:
    def __init__(self, action="UP", conf=0.9, preview=None):
        self.action = action
        self.conf = conf
        self.preview = preview or np.zeros((32, 32, 3), dtype=np.uint8)
        self.calls = 0
        self.last_frame_processed = self.preview
        self.last_landmarks = None
        self.last_bbox = None
        self.last_vector = (0.0, -2.0)
        self.closed = False

    def predict(self, frame):
        self.calls += 1
        self.last_frame_processed = self.preview
        return self.action, self.conf

    def close(self):
        self.closed = True


class TestGestureService(unittest.TestCase):
    def _wait_result(self, svc, timeout=3.0):
        end = time.time() + timeout
        while time.time() < end:
            r = svc.latest()
            if r is not None:
                return r
            time.sleep(0.01)
        return None

    def test_runs_and_exposes_latest_result(self):
        frames = [np.zeros((64, 64, 3), dtype=np.uint8) for _ in range(12)]
        clf = FakeClassifier()
        svc = GestureService(classifier=clf, cam_index=0,
                             capture_factory=lambda i: FakeCapture(frames[:]))
        svc.start()
        try:
            res = self._wait_result(svc)
            self.assertIsNotNone(res)
            self.assertGreater(res.frame_id, 0)
            self.assertEqual(res.action, "UP")
            self.assertEqual(res.confidence, 0.9)
            self.assertIsNotNone(res.preview)
        finally:
            svc.stop()
        self.assertFalse(svc.alive)

    def test_camera_failure_degrades_gracefully(self):
        clf = FakeClassifier()
        svc = GestureService(classifier=clf, cam_index=0,
                             capture_factory=lambda i: FakeCaptureClosed())
        svc.start()
        time.sleep(0.2)
        self.assertIsNone(svc.latest())
        svc.stop()
        self.assertFalse(svc.alive)

    def test_no_camera_mode(self):
        clf = FakeClassifier()
        svc = GestureService(classifier=clf, cam_index=None)
        svc.start()
        self.assertFalse(svc.alive)
        self.assertIsNone(svc.latest())
        svc.stop()

    def test_stop_joins_and_closes_classifier(self):
        frames = [np.zeros((64, 64, 3), dtype=np.uint8) for _ in range(3)]
        clf = FakeClassifier()
        svc = GestureService(classifier=clf, cam_index=0,
                             capture_factory=lambda i: FakeCapture(frames[:]))
        svc.start()
        svc.stop()
        self.assertTrue(clf.closed)
        self.assertFalse(svc.alive)


if __name__ == "__main__":
    unittest.main()
