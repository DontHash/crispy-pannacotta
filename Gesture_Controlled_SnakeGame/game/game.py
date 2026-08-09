# game/game.py
# Game state machine: owns player, snake, food, controller, scoring and rules.
# Pure logic (no pygame rendering) so it is fully unit-testable.

import math
import random
from enum import Enum

import pygame

from controller.input_controller import InputController
from game.player import Player, HighScore, default_highscore_path
from game.snake import Snake

DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")


class GameState(Enum):
    HOME = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3


def spawn_food(snake, grid_cols, grid_rows, rng):
    """Pick a random empty grid cell for the food (never on the snake)."""
    occupied = set(snake.cells)
    free = [(c, r) for r in range(grid_rows) for c in range(grid_cols)
            if (c, r) not in occupied]
    if free:
        return rng.choice(free)
    return (grid_cols // 2, grid_rows // 2)


class Game:
    def __init__(self, width=800, height=600, sfx=None, highscore=None,
                 cell=20, start_speed=8, speed_increment=0.35, max_speed=16, seed=None):
        self.width = width
        self.height = height
        self.cell = cell
        self.grid_cols = width // cell
        self.grid_rows = height // cell
        self.start_speed = start_speed
        self.speed_increment = speed_increment
        self.max_speed = max_speed
        self.rng = random.Random(seed)
        self.sfx = sfx
        self.highscore = highscore or HighScore(default_highscore_path())

        self.state = GameState.HOME
        self.player = Player()
        self.snake = Snake(self.grid_cols, self.grid_rows, cell=cell, speed=start_speed)
        self.food = spawn_food(self.snake, self.grid_cols, self.grid_rows, self.rng)
        self.controller = InputController(initial="RIGHT")
        self.particles = []

    def start_playing(self):
        if self.state in (GameState.HOME, GameState.GAME_OVER):
            self.snake = Snake(self.grid_cols, self.grid_rows, cell=self.cell, speed=self.start_speed)
            self.controller = InputController(initial="RIGHT")
            self.player.start()
            self.food = spawn_food(self.snake, self.grid_cols, self.grid_rows, self.rng)
            self.particles = []
            self.state = GameState.PLAYING

    def toggle_pause(self):
        if self.state == GameState.PLAYING:
            self.player.pause()
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.player.resume()
            self.state = GameState.PLAYING

    def set_forced_direction(self, direction):
        if self.state == GameState.PLAYING:
            self.controller.set_force(direction)

    def submit_gesture(self, action, conf=0.0):
        """Feed a filtered gesture detection (already debounced by DirectionFilter)."""
        if action is None:
            return
        if self.state == GameState.HOME and action == "START":
            self.start_playing()
        elif self.state == GameState.PLAYING and action in DIRECTIONS:
            self.controller.submit_priority(action)

    def _game_over(self):
        self.snake.alive = False
        self.state = GameState.GAME_OVER
        if self.highscore:
            self.highscore.submit(self.player.score)
        if self.sfx:
            self.sfx.play_game_over()

    def _spawn_particles(self):
        fx = self.food[0] * self.cell + self.cell / 2
        fy = self.food[1] * self.cell + self.cell / 2
        for _ in range(14):
            ang = self.rng.uniform(0.0, 6.2832)
            spd = self.rng.uniform(40.0, 140.0)
            self.particles.append({
                "x": fx, "y": fy,
                "vx": spd * math.cos(ang),
                "vy": spd * math.sin(ang),
                "life": self.rng.uniform(0.25, 0.55),
            })

    def _update_particles(self, dt):
        keep = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] > 0:
                keep.append(p)
        self.particles = keep

    def _eat(self):
        self.player.add_score(1)
        self.snake.grow(1)
        self.snake.speed = min(self.max_speed, self.start_speed + self.player.score * self.speed_increment)
        self.food = spawn_food(self.snake, self.grid_cols, self.grid_rows, self.rng)
        self._spawn_particles()
        if self.sfx:
            self.sfx.play_eat()

    def update(self, dt=1.0):
        if self.state != GameState.PLAYING:
            return
        self.controller.update()
        self.snake.set_direction(self.controller.get_vector())
        self.snake.update(dt)
        if not self.snake.alive:
            self._game_over()
            return
        if self.food in self.snake.visited:
            self._eat()
        self._update_particles(dt)

    def _ensure_fonts(self):
        if getattr(self, "_font", None) is None:
            self._font = pygame.font.SysFont("Arial", 20)
            self._big = pygame.font.SysFont("Arial", 48)
            self._mid = pygame.font.SysFont("Arial", 30)

    def _grid_surface(self):
        if getattr(self, "_grid_surf", None) is None:
            surf = pygame.Surface((self.width, self.height))
            surf.fill((24, 28, 25))
            c = self.cell
            for r in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if (r + col) % 2 == 0:
                        surf.fill((29, 34, 30), (col * c, r * c, c, c))
            self._grid_surf = surf
        return self._grid_surf

    def _hud_surface(self, gesture_label):
        key = (self.player.score, int(self.player.elapsed()), round(self.snake.speed, 1), gesture_label)
        if getattr(self, "_hud", None) and self._hud[0] == key:
            return self._hud[1]
        score = self._font.render(f"Score: {self.player.score}", True, (240, 240, 240))
        time = self._font.render(f"Time: {key[1]}s", True, (240, 240, 240))
        speed = self._font.render(f"Speed: {self.snake.speed:.1f}", True, (180, 220, 180))
        gesture = self._font.render(f"Gesture: {gesture_label}", True, (200, 200, 120))
        high = self._font.render(f"Best: {self.highscore.load()}", True, (255, 220, 120))
        hud = (score, time, speed, gesture, high)
        self._hud = (key, hud)
        return hud

    def draw(self, surface, bg=None, gesture_result=None):
        self._ensure_fonts()
        if bg is not None:
            bg.draw(surface)
        else:
            surface.fill((10, 10, 10))
        surface.blit(self._grid_surface(), (0, 0))

        gesture_label = "-"
        if gesture_result is not None and gesture_result.action:
            gesture_label = f"{gesture_result.action} {gesture_result.confidence:.2f}"

        if self.state == GameState.HOME:
            self._draw_home(surface)
            return

        self._draw_food(surface)
        self._draw_particles(surface)
        self.snake.draw(surface, progress=self.snake.progress)

        hud = self._hud_surface(gesture_label)
        for i, surf in enumerate(hud):
            surface.blit(surf, (10, 10 + i * 22))

        if self.state == GameState.PAUSED:
            self._center_text(surface, self._mid, "PAUSED - P/ESC to resume", (220, 220, 220), 140)
        elif self.state == GameState.GAME_OVER:
            self._center_text(surface, self._big, "GAME OVER", (255, 60, 60), 150)
            score = self._mid.render(f"Score: {self.player.score}   Best: {self.highscore.load()}",
                                     True, (255, 255, 255))
            sub = self._font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
            surface.blit(score, (self.width // 2 - score.get_width() // 2, 210))
            surface.blit(sub, (self.width // 2 - sub.get_width() // 2, 260))

    def _draw_food(self, surface):
        fx = self.food[0] * self.cell + self.cell / 2
        fy = self.food[1] * self.cell + self.cell / 2
        t = pygame.time.get_ticks() / 1000.0
        radius = int(self.cell * 0.4 + 2.0 * math.sin(t * 6.0))
        pygame.draw.circle(surface, (255, 60, 50), (int(fx), int(fy)), radius + 4)
        pygame.draw.circle(surface, (255, 90, 80), (int(fx), int(fy)), radius)
        pygame.draw.circle(surface, (255, 220, 200), (int(fx) - radius // 3, int(fy) - radius // 3), max(2, radius // 3))

    def _draw_particles(self, surface):
        for p in self.particles:
            a = int(200 * max(0.0, min(1.0, p["life"] / 0.3)))
            color = (255, int(180 * a / 255) + 75, 60)
            pygame.draw.circle(surface, color, (int(p["x"]), int(p["y"])), 3)

    def _draw_home(self, surface):
        title = self._big.render("Gesture Snake", True, (200, 250, 200))
        instr1 = self._font.render("Use hand gestures to control the snake. Pinch to START.", True, (200, 200, 200))
        instr2 = self._font.render("Show a movement gesture until READY = YES, then press SPACE.", True, (200, 200, 200))
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 60))
        surface.blit(instr1, (self.width // 2 - instr1.get_width() // 2, 130))
        surface.blit(instr2, (self.width // 2 - instr2.get_width() // 2, 160))

    def _center_text(self, surface, font, text, color, y):
        surf = font.render(text, True, color)
        surface.blit(surf, (self.width // 2 - surf.get_width() // 2, y))
