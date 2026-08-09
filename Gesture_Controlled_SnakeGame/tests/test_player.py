import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import json
import tempfile
import time
import unittest

from game.player import Player, HighScore


class TestPlayer(unittest.TestCase):
    def test_add_score(self):
        p = Player()
        p.start()
        p.add_score(3)
        self.assertEqual(p.score, 3)

    def test_start_resets_score(self):
        p = Player()
        p.start()
        p.add_score(5)
        p.start()
        self.assertEqual(p.score, 0)

    def test_elapsed_before_start_zero(self):
        self.assertEqual(Player().elapsed(), 0.0)

    def test_elapsed_increases(self):
        p = Player()
        p.start()
        time.sleep(0.05)
        self.assertGreaterEqual(p.elapsed(), 0.04)

    def test_pause_freezes_elapsed(self):
        p = Player()
        p.start()
        time.sleep(0.05)
        p.pause()
        t1 = p.elapsed()
        time.sleep(0.05)
        t2 = p.elapsed()
        p.resume()
        time.sleep(0.05)
        t3 = p.elapsed()
        self.assertAlmostEqual(t1, t2, places=2)
        self.assertGreater(t3, t2)


class TestHighScore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_default_zero(self):
        self.assertEqual(HighScore(self.path).load(), 0)

    def test_submit_saves_new_best(self):
        hs = HighScore(self.path)
        self.assertTrue(hs.submit(10))
        self.assertEqual(hs.load(), 10)
        self.assertFalse(hs.submit(8))
        self.assertEqual(hs.load(), 10)

    def test_persists_across_instances(self):
        hs = HighScore(self.path)
        hs.submit(42)
        self.assertEqual(HighScore(self.path).load(), 42)

    def test_corrupt_file_returns_zero(self):
        with open(self.path, "w") as f:
            f.write("not json")
        self.assertEqual(HighScore(self.path).load(), 0)


if __name__ == "__main__":
    unittest.main()
