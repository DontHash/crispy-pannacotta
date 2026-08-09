import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import unittest

from gesture.direction_filter import DirectionFilter


class TestDirectionFilter(unittest.TestCase):
    def test_strong_direction_emits_immediately(self):
        f = DirectionFilter()
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")

    def test_perpendicular_turns_are_immediate(self):
        f = DirectionFilter()
        self.assertEqual(f.update(-2.5, 0.2, t_ms=0), "LEFT")
        self.assertEqual(f.update(0.1, -2.0, t_ms=10), "UP")
        self.assertEqual(f.update(2.5, 0.2, t_ms=20), "RIGHT")
        self.assertEqual(f.update(0.1, 2.0, t_ms=30), "DOWN")

    def test_weak_input_emits_nothing(self):
        f = DirectionFilter()
        self.assertIsNone(f.update(0.1, 0.1, t_ms=0))
        self.assertIsNone(f.update(-0.05, 0.0, t_ms=10))

    def test_jitter_does_not_flip_direction(self):
        f = DirectionFilter()
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertIsNone(f.update(-0.2, 0.1, t_ms=10))
        self.assertIsNone(f.update(-0.3, 0.0, t_ms=20))

    def test_opposite_flip_requires_persistence(self):
        f = DirectionFilter(flip_lock_ms=90)
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertIsNone(f.update(-3.0, 0.0, t_ms=10))
        self.assertIsNone(f.update(-3.0, 0.0, t_ms=50))
        self.assertIsNone(f.update(-3.0, 0.0, t_ms=80))
        self.assertEqual(f.update(-3.0, 0.0, t_ms=100), "LEFT")

    def test_flip_after_persistent_opposite(self):
        f = DirectionFilter(flip_lock_ms=60)
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertIsNone(f.update(-3.0, 0.0, t_ms=30))
        self.assertIsNone(f.update(-3.0, 0.0, t_ms=60))
        self.assertEqual(f.update(-3.0, 0.0, t_ms=90), "LEFT")

    def test_turn_does_not_need_lock(self):
        f = DirectionFilter(flip_lock_ms=200)
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertEqual(f.update(0.0, 3.0, t_ms=5), "DOWN")

    def test_reset_clears_flip_lock(self):
        f = DirectionFilter(flip_lock_ms=500)
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertIsNone(f.update(-3.0, 0.0, t_ms=10))
        f.reset()
        self.assertEqual(f.update(-3.0, 0.0, t_ms=11), "LEFT")

    def test_same_direction_is_reemitted(self):
        f = DirectionFilter()
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertEqual(f.update(2.5, 0.2, t_ms=10), "RIGHT")

    def test_weak_after_strong_emits_nothing(self):
        f = DirectionFilter()
        self.assertEqual(f.update(3.0, 0.0, t_ms=0), "RIGHT")
        self.assertIsNone(f.update(0.0, 0.0, t_ms=10))


if __name__ == "__main__":
    unittest.main()
