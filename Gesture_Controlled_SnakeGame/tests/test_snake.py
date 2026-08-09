import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import unittest

from game.snake import Snake


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


class TestSnake(unittest.TestCase):
    def setUp(self):
        self.s = Snake(grid_cols=40, grid_rows=30, cell=20, start_length=3, speed=8)

    def test_initial_layout(self):
        self.assertEqual(self.s.cells, [(20, 15), (19, 15), (18, 15)])
        self.assertEqual(self.s.direction, (1, 0))
        self.assertTrue(self.s.alive)

    def test_update_moves_one_cell_per_interval(self):
        self.s.update(dt=1 / 8)
        self.assertEqual(self.s.cells[0], (21, 15))

    def test_update_half_interval_does_not_step(self):
        self.s.update(dt=1 / 16)
        self.assertEqual(self.s.cells[0], (20, 15))

    def test_update_accumulates_multiple_steps(self):
        self.s.update(dt=1 / 4)
        self.assertEqual(self.s.cells[0], (22, 15))

    def test_set_direction_blocks_reverse(self):
        self.s.set_direction((-1, 0))
        self.s.update(dt=1 / 8)
        self.assertEqual(self.s.cells[0], (21, 15))

    def test_set_direction_allows_turn(self):
        self.s.set_direction((0, -1))
        self.s.update(dt=1 / 8)
        self.assertEqual(self.s.cells[0], (20, 14))

    def test_wall_collision_kills(self):
        self.s.cells = [(0, 15), (1, 15), (2, 15)]
        self.s._prev_cells = self.s.cells[:]
        self.s.direction = (-1, 0)
        self.s.next_direction = (-1, 0)
        self.s.update(dt=1 / 8)
        self.assertFalse(self.s.alive)

    def test_self_collision_kills(self):
        self.s.cells = [(3, 3), (2, 3), (2, 2), (3, 2), (3, 1)]
        self.s._prev_cells = self.s.cells[:]
        self.s.direction = (0, -1)
        self.s.next_direction = (0, -1)
        self.s.update(dt=1 / 8)
        self.assertFalse(self.s.alive)

    def test_tail_cell_is_safe_when_not_growing(self):
        # tail at (2,4); moving from (2,3) down onto the tail is legal
        self.s.cells = [(2, 3), (3, 3), (3, 4), (2, 4)]
        self.s._prev_cells = self.s.cells[:]
        self.s.direction = (0, 1)
        self.s.next_direction = (0, 1)
        self.s.update(dt=1 / 8)
        self.assertTrue(self.s.alive)
        self.assertEqual(self.s.cells[0], (2, 4))

    def test_grow_adds_cells(self):
        self.s.grow(2)
        self.s.update(dt=1 / 8)
        self.assertEqual(len(self.s.cells), 4)
        self.s.update(dt=1 / 8)
        self.assertEqual(len(self.s.cells), 5)
        self.s.update(dt=1 / 8)
        self.assertEqual(len(self.s.cells), 5)

    def test_eats_detects_food_on_head(self):
        self.assertTrue(self.s.eats((20, 15)))
        self.assertFalse(self.s.eats((5, 5)))

    def test_on_cell(self):
        self.assertTrue(self.s.on_cell((19, 15)))
        self.assertFalse(self.s.on_cell((0, 0)))

    def test_render_points_spacing_and_count(self):
        self.s.update(dt=1 / 8)
        pts = self.s.render_points(progress=1.0)
        self.assertEqual(len(pts), len(self.s.cells))
        for a, b in zip(pts, pts[1:]):
            self.assertAlmostEqual(dist(a, b), self.s.cell, delta=0.6)
        self.assertAlmostEqual(pts[0][0], (21 * 20 + 10), places=3)

    def test_render_points_head_interpolates(self):
        p0 = self.s.render_points(progress=0.0)[0]
        p1 = self.s.render_points(progress=1.0)[0]
        self.assertAlmostEqual(p0[0], (20 * 20 + 10), places=3)
        self.assertAlmostEqual(p1[0], (20 * 20 + 10), places=3)
        self.s.update(dt=1 / 8)
        pm = self.s.render_points(progress=0.5)[0]
        self.assertAlmostEqual(pm[0], (20 * 20 + 10) + 10, places=3)

    def test_update_after_death_is_noop(self):
        self.s.alive = False
        before = self.s.cells[:]
        self.s.update(dt=1.0)
        self.assertEqual(self.s.cells, before)


if __name__ == "__main__":
    unittest.main()
