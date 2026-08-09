# game/snake.py
# Classic grid snake with smooth interpolated rendering.
# Movement is grid-cell based (exact collisions); rendering is continuous.

import numpy as np
import pygame


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


class Snake:
    def __init__(self, grid_cols=40, grid_rows=30, cell=20, start_length=3, speed=8):
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.cell = cell
        self.speed = speed  # cells per second
        self.max_steps_per_frame = 4

        cx, cy = grid_cols // 2, grid_rows // 2
        self.cells = [(cx - i, cy) for i in range(start_length)]
        self._prev_cells = self.cells[:]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self._grow_pending = 0
        self._acc = 0.0
        self.alive = True
        self._visited = [self.cells[0]]

        self._glow = None

    @property
    def head_cell(self):
        return self.cells[0]

    @property
    def progress(self):
        """0..1 interpolation progress toward the current cell (for smooth rendering)."""
        return min(1.0, self._acc * self.speed)

    def set_direction(self, dvec):
        if (dvec[0], dvec[1]) != (-self.direction[0], -self.direction[1]):
            self.next_direction = dvec

    def grow(self, cells):
        self._grow_pending += cells

    def eats(self, food_cell):
        return self.cells[0] == food_cell

    def on_cell(self, cell):
        return cell in self.cells

    def _step(self):
        self.direction = self.next_direction
        hx, hy = self.cells[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]

        if nx < 0 or nx >= self.grid_cols or ny < 0 or ny >= self.grid_rows:
            self.alive = False
            return

        head = (nx, ny)
        body = self.cells if self._grow_pending > 0 else self.cells[:-1]
        if head in body:
            self.alive = False
            return

        self.cells.insert(0, head)
        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self.cells.pop()

    def update(self, dt=1.0):
        if not self.alive:
            return
        interval = 1.0 / self.speed
        self._acc += dt
        steps = 0
        self._visited = [self.cells[0]]
        while self._acc >= interval and steps < self.max_steps_per_frame:
            self._prev_cells = self.cells[:]
            self._acc -= interval
            self._step()
            if not self.alive:
                break
            self._visited.append(self.cells[0])
            steps += 1

    @property
    def visited(self):
        """Grid cells the head occupied during the most recent update."""
        return self._visited

    def _cell_pixel(self, cell):
        return (cell[0] * self.cell + self.cell / 2.0, cell[1] * self.cell + self.cell / 2.0)

    def render_points(self, progress=1.0):
        """Pixel-space points along the snake path, spaced one cell apart."""
        head = _lerp(self._cell_pixel(self._prev_cells[0]),
                     self._cell_pixel(self.cells[0]), progress)
        path = [head] + [self._cell_pixel(c) for c in self.cells[1:]]
        if len(path) < 2:
            return path

        out = [path[0]]
        acc = 0.0
        target = float(self.cell)
        i = 1
        while i < len(path) and len(out) < len(self.cells):
            p_prev, p = path[i - 1], path[i]
            seg = ((p[0] - p_prev[0]) ** 2 + (p[1] - p_prev[1]) ** 2) ** 0.5
            while seg > 0 and acc + seg >= target:
                r = (target - acc) / seg
                out.append((p_prev[0] + (p[0] - p_prev[0]) * r,
                            p_prev[1] + (p[1] - p_prev[1]) * r))
                target += self.cell
            acc += seg
            i += 1
        while len(out) < len(self.cells):
            out.append(out[-1])
        return out

    def head_pixel(self, progress=1.0):
        return _lerp(self._cell_pixel(self._prev_cells[0]),
                     self._cell_pixel(self.cells[0]), progress)

    def _glow_sprite(self, radius):
        if self._glow is None:
            size = radius * 2
            yy, xx = np.mgrid[0:size, 0:size]
            dist = np.sqrt((xx - radius + 0.5) ** 2 + (yy - radius + 0.5) ** 2)
            alpha = np.clip((1.0 - dist / radius) * 70, 0, 70).astype(np.uint8)
            glow = np.zeros((size, size, 4), dtype=np.uint8)
            glow[..., 0] = 60
            glow[..., 1] = 190
            glow[..., 2] = 90
            glow[..., 3] = alpha
            surf = pygame.image.frombuffer(glow, (size, size), "RGBA")
            try:
                surf = surf.convert_alpha()
            except pygame.error:
                pass
            self._glow = surf
        return self._glow

    def draw(self, surface, progress=1.0):
        if len(self.cells) < 1:
            return
        radius = int(self.cell * 0.42)
        glow = self._glow_sprite(radius * 3)
        gw2, gh2 = glow.get_width() // 2, glow.get_height() // 2

        pts = self.render_points(progress)
        for x, y in pts[1:]:
            surface.blit(glow, (x - gw2, y - gh2))
            pygame.draw.circle(surface, (60, 190, 90), (int(x), int(y)), radius)

        hx, hy = self.head_pixel(progress)
        hx, hy = int(hx), int(hy)
        surface.blit(glow, (hx - gw2, hy - gh2))
        pygame.draw.circle(surface, (110, 230, 120), (hx, hy), radius + 3)

        dx, dy = self.direction
        if dx == 0 and dy == 0:
            dx = 1
        perp = (-dy, dx)
        eye_r = max(2, radius // 2)
        for side in (-1, 1):
            ex = hx + perp[0] * side * radius * 0.55 + dx * radius * 0.35
            ey = hy + perp[1] * side * radius * 0.55 + dy * radius * 0.35
            pygame.draw.circle(surface, (255, 255, 255), (int(ex), int(ey)), eye_r)
            px = ex + dx * eye_r * 0.5
            py = ey + dy * eye_r * 0.5
            pygame.draw.circle(surface, (20, 40, 25), (int(px), int(py)), max(1, eye_r - 1))
