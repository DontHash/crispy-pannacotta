import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import unittest

from controller.input_controller import InputController


class TestInputController(unittest.TestCase):
    def test_initial_direction(self):
        c = InputController(initial="RIGHT")
        self.assertEqual(c.update(), "RIGHT")
        self.assertEqual(c.get_vector(), (1, 0))

    def test_submit_applies_direction(self):
        c = InputController(initial="RIGHT")
        c.submit("UP")
        self.assertEqual(c.update(), "UP")

    def test_immediate_reverse_blocked(self):
        c = InputController(initial="RIGHT")
        c.submit("LEFT")
        self.assertEqual(c.update(), "RIGHT")

    def test_queue_allows_turn_after_moving(self):
        c = InputController(initial="RIGHT")
        c.submit("UP")
        self.assertEqual(c.update(), "UP")
        c.submit("LEFT")
        self.assertEqual(c.update(), "LEFT")

    def test_set_force_blocks_reverse(self):
        c = InputController(initial="RIGHT")
        c.set_force("LEFT")
        self.assertEqual(c.get_vector(), (1, 0))

    def test_set_force_allows_valid(self):
        c = InputController(initial="RIGHT")
        c.set_force("DOWN")
        self.assertEqual(c.get_vector(), (0, 1))

    def test_invalid_direction_ignored(self):
        c = InputController(initial="RIGHT")
        c.submit("BANANA")
        self.assertEqual(c.update(), "RIGHT")

    def test_duplicate_queued_directions_deduped(self):
        c = InputController(initial="RIGHT")
        c.submit("UP")
        c.submit("UP")
        c.submit("LEFT")
        c.submit("DOWN")
        self.assertEqual(c.update(), "UP")
        self.assertEqual(c.update(), "LEFT")
        self.assertEqual(c.update(), "DOWN")


    def test_submit_priority_flushes_stale_queue(self):
        c = InputController(initial="RIGHT")
        c.submit("UP")
        c.submit("LEFT")
        c.submit_priority("DOWN")
        self.assertEqual(c.update(), "DOWN")
        self.assertEqual(c.update(), "DOWN")

    def test_submit_priority_validates_direction(self):
        c = InputController(initial="RIGHT")
        c.submit_priority("BANANA")
        self.assertEqual(c.update(), "RIGHT")


if __name__ == "__main__":
    unittest.main()
