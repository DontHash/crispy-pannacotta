import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tempfile
import unittest

from game.game import Game, GameState, spawn_food
from game.player import HighScore


def make_game(**kw):
    kw.setdefault("width", 200)
    kw.setdefault("height", 200)
    kw.setdefault("cell", 20)
    kw.setdefault("start_speed", 8)
    kw.setdefault("highscore", HighScore(tempfile.mktemp(suffix=".json")))
    kw.setdefault("seed", 42)
    return Game(**kw)


STEP = 1 / 8  # one step at start_speed=8


class TestSpawnFood(unittest.TestCase):
    def test_food_on_empty_grid_cell(self):
        g = make_game()
        g.start_playing()
        for _ in range(30):
            fx, fy = g.food
            self.assertGreaterEqual(fx, 0)
            self.assertLess(fx, g.grid_cols)
            self.assertGreaterEqual(fy, 0)
            self.assertLess(fy, g.grid_rows)
            self.assertNotIn(g.food, g.snake.cells)
            g.food = spawn_food(g.snake, g.grid_cols, g.grid_rows, g.rng)

    def test_food_never_on_snake(self):
        g = make_game()
        g.start_playing()
        g.snake.grow(100)
        for _ in range(60):
            g.update(dt=STEP)
        for _ in range(30):
            fx, fy = spawn_food(g.snake, g.grid_cols, g.grid_rows, g.rng)
            self.assertNotIn((fx, fy), g.snake.cells)


class TestGame(unittest.TestCase):
    def test_initial_state_home(self):
        g = make_game()
        self.assertEqual(g.state, GameState.HOME)
        self.assertEqual(g.snake.cells[0], (5, 5))

    def test_start_playing_transitions_and_resets(self):
        g = make_game()
        g.start_playing()
        self.assertEqual(g.state, GameState.PLAYING)
        self.assertEqual(g.player.score, 0)
        self.assertEqual(g.snake.cells[0], (5, 5))

    def test_gesture_start_from_home(self):
        g = make_game()
        g.submit_gesture("START", 0.9)
        self.assertEqual(g.state, GameState.PLAYING)

    def test_direction_applied_on_first_detection(self):
        g = make_game()
        g.start_playing()
        g.submit_gesture("UP", 0.9)
        g.update(dt=STEP)
        self.assertEqual(g.snake.cells[0], (5, 4))

    def test_latest_gesture_wins_over_stale_queue(self):
        g = make_game()
        g.start_playing()
        g.submit_gesture("LEFT", 0.9)
        g.submit_gesture("UP", 0.9)
        g.update(dt=STEP)
        self.assertEqual(g.snake.cells[0], (5, 4))

    def test_none_gesture_is_noop(self):
        g = make_game()
        g.start_playing()
        g.submit_gesture(None, 0.0)
        g.update(dt=STEP)
        self.assertEqual(g.snake.cells[0], (6, 5))

    def test_eating_increments_score_and_speed(self):
        g = make_game()
        g.start_playing()
        g.food = (6, 5)
        g.update(dt=STEP)
        self.assertEqual(g.player.score, 1)
        self.assertGreater(g.snake.speed, g.start_speed)
        self.assertNotEqual(g.food, (6, 5))

    def test_eating_spawns_particles(self):
        g = make_game()
        g.start_playing()
        g.food = (6, 5)
        g.update(dt=STEP)
        self.assertGreater(len(g.particles), 0)

    def test_speed_ramp_capped(self):
        g = make_game(width=600, height=300, start_speed=8, speed_increment=1, max_speed=12)
        g.start_playing()
        for i in range(8):
            g.food = (g.snake.cells[0][0] + 1, g.snake.cells[0][1])
            g.update(dt=STEP)
        self.assertEqual(g.player.score, 8)
        self.assertEqual(g.snake.speed, 12)

    def test_wall_collision_game_over(self):
        g = make_game()
        g.start_playing()
        g.snake.cells = [(9, 5), (8, 5), (7, 5)]
        g.snake._prev_cells = g.snake.cells[:]
        g.snake.direction = (1, 0)
        g.snake.next_direction = (1, 0)
        g.update(dt=STEP)
        self.assertEqual(g.state, GameState.GAME_OVER)
        self.assertFalse(g.snake.alive)

    def test_self_collision_game_over(self):
        g = make_game()
        g.start_playing()
        g.snake.cells = [(5, 5), (4, 5), (4, 4), (5, 4), (5, 3)]
        g.snake._prev_cells = g.snake.cells[:]
        g.controller.set_force("UP")
        g.update(dt=STEP)
        self.assertEqual(g.state, GameState.GAME_OVER)

    def test_game_over_saves_highscore(self):
        g = make_game()
        g.start_playing()
        g.player.add_score(7)
        g.snake.cells = [(9, 5), (8, 5), (7, 5)]
        g.snake._prev_cells = g.snake.cells[:]
        g.snake.direction = (1, 0)
        g.snake.next_direction = (1, 0)
        g.update(dt=STEP)
        self.assertEqual(g.state, GameState.GAME_OVER)
        self.assertEqual(g.highscore.load(), 7)

    def test_restart_from_game_over(self):
        g = make_game()
        g.start_playing()
        g.snake.cells = [(9, 5), (8, 5), (7, 5)]
        g.snake._prev_cells = g.snake.cells[:]
        g.snake.direction = (1, 0)
        g.snake.next_direction = (1, 0)
        g.update(dt=STEP)
        self.assertEqual(g.state, GameState.GAME_OVER)
        g.start_playing()
        self.assertEqual(g.state, GameState.PLAYING)
        self.assertEqual(g.player.score, 0)
        self.assertEqual(g.snake.cells[0], (5, 5))

    def test_pause_freezes_snake(self):
        g = make_game()
        g.start_playing()
        g.toggle_pause()
        self.assertEqual(g.state, GameState.PAUSED)
        before = g.snake.cells[:]
        g.update(dt=1.0)
        self.assertEqual(g.snake.cells, before)
        g.toggle_pause()
        g.update(dt=STEP)
        self.assertNotEqual(g.snake.cells[0], before[0])

    def test_game_over_ignores_updates(self):
        g = make_game()
        g.start_playing()
        g.snake.cells = [(9, 5), (8, 5), (7, 5)]
        g.snake._prev_cells = g.snake.cells[:]
        g.snake.direction = (1, 0)
        g.snake.next_direction = (1, 0)
        g.update(dt=STEP)
        self.assertEqual(g.state, GameState.GAME_OVER)
        before = g.snake.cells[:]
        g.update(dt=1.0)
        self.assertEqual(g.snake.cells, before)


if __name__ == "__main__":
    unittest.main()
