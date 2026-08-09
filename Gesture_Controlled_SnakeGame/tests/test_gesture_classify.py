import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import unittest

from gesture.gesture_model import classify_landmarks


def _landmarks_for(wrist, thumb_tip, index_tip, middle_mcp):
    """Build a 21-landmark list; only indices 0, 4, 8, 9 are meaningful."""
    lms = [(0.5, 0.5)] * 21
    lms[0] = wrist
    lms[4] = thumb_tip
    lms[8] = index_tip
    lms[9] = middle_mcp
    return lms


class TestClassifyLandmarks(unittest.TestCase):
    def test_hand_pointing_right(self):
        lms = _landmarks_for(wrist=(0.4, 0.5), thumb_tip=(0.45, 0.5),
                             index_tip=(0.7, 0.5), middle_mcp=(0.48, 0.5))
        action, conf = classify_landmarks(lms)
        self.assertEqual(action, "RIGHT")
        self.assertGreater(conf, 0.0)

    def test_hand_pointing_left(self):
        lms = _landmarks_for(wrist=(0.6, 0.5), thumb_tip=(0.55, 0.5),
                             index_tip=(0.3, 0.5), middle_mcp=(0.52, 0.5))
        action, _ = classify_landmarks(lms)
        self.assertEqual(action, "LEFT")

    def test_hand_pointing_up(self):
        lms = _landmarks_for(wrist=(0.5, 0.6), thumb_tip=(0.5, 0.55),
                             index_tip=(0.5, 0.3), middle_mcp=(0.5, 0.52))
        action, _ = classify_landmarks(lms)
        self.assertEqual(action, "UP")

    def test_hand_pointing_down(self):
        lms = _landmarks_for(wrist=(0.5, 0.4), thumb_tip=(0.5, 0.45),
                             index_tip=(0.5, 0.7), middle_mcp=(0.5, 0.48))
        action, _ = classify_landmarks(lms)
        self.assertEqual(action, "DOWN")

    def test_pinch_returns_start(self):
        lms = _landmarks_for(wrist=(0.5, 0.5), thumb_tip=(0.52, 0.5),
                             index_tip=(0.53, 0.5), middle_mcp=(0.55, 0.5))
        action, conf = classify_landmarks(lms)
        self.assertEqual(action, "START")
        self.assertGreater(conf, 0.5)

    def test_ambiguous_returns_none(self):
        lms = _landmarks_for(wrist=(0.5, 0.5), thumb_tip=(0.44, 0.44),
                             index_tip=(0.51, 0.51), middle_mcp=(0.6, 0.6))
        action, conf = classify_landmarks(lms)
        self.assertIsNone(action)
        self.assertEqual(conf, 0.0)

    def test_weak_direction_returns_none(self):
        lms = _landmarks_for(wrist=(0.5, 0.5), thumb_tip=(0.4, 0.4),
                             index_tip=(0.52, 0.5), middle_mcp=(0.65, 0.5))
        action, _ = classify_landmarks(lms)
        self.assertIsNone(action)


if __name__ == "__main__":
    unittest.main()
