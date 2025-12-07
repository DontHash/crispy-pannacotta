# game/snake.py
# Smooth slender glowing snake (constant width, grows only in length).

import pygame
import math

def catmull_rom_chain(points, count=12):
    if len(points) < 2:
        return points[:]
    pts = []
    ext = [points[0]] + points + [points[-1]]
    for i in range(len(ext)-3):
        p0, p1, p2, p3 = ext[i], ext[i+1], ext[i+2], ext[i+3]
        for t_step in range(count):
            t = t_step / float(count)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2*p1[0]) +
                       (-p0[0] + p2[0]) * t +
                       (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
            y = 0.5 * ((2*p1[1]) +
                       (-p0[1] + p2[1]) * t +
                       (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
            pts.append((x, y))
    pts.append(points[-1])
    return pts


class Snake:
    def __init__(self, start_pos, color=(200, 200, 255), speed=4, segment_length=18):
        self.color = color
        self.speed = speed
        self.segment_length = segment_length

        self.body_points = [start_pos]
        # total length in pixels the snake should occupy
        self.target_length = segment_length * 5
        self.head_pos = list(start_pos)
        self.direction = (1, 0)
        self.alive = True

        self.radius = 3   # constant thickness → slender snake

    def set_direction(self, dvec):
        self.direction = dvec

    def grow(self, pixels):
        # ONLY increases length — not width
        self.target_length += pixels

    def update(self, dt=1.0):
        if not self.alive:
            return

        dx = self.direction[0] * self.speed * dt
        dy = self.direction[1] * self.speed * dt
        self.head_pos[0] += dx
        self.head_pos[1] += dy

        # insert new head point
        self.body_points.insert(0, (self.head_pos[0], self.head_pos[1]))

        # Rebuild the body_points so that the total path length equals target_length.
        # If the current path is shorter than target_length we keep the entire path (i.e. snake grows).
        new_points = [self.body_points[0]]
        accumulated = 0.0

        for i in range(len(self.body_points) - 1):
            x1, y1 = self.body_points[i]
            x2, y2 = self.body_points[i + 1]
            seg = math.hypot(x2 - x1, y2 - y1)

            # if adding whole segment doesn't exceed target, keep p2
            if accumulated + seg <= self.target_length:
                new_points.append((x2, y2))
                accumulated += seg
            else:
                # need partial segment to exactly reach target_length
                remain = self.target_length - accumulated
                if seg > 0 and remain > 0:
                    ratio = remain / seg
                    nx = x1 + (x2 - x1) * ratio
                    ny = y1 + (y2 - y1) * ratio
                    new_points.append((nx, ny))
                # reached target length — stop adding further tail points
                break

        # If accumulated < target_length and we've appended all original points,
        # that's fine: snake is still "growing" until it reaches target_length.
        self.body_points = new_points

    def draw(self, surface):
        if len(self.body_points) < 2:
            return

        smooth = catmull_rom_chain(self.body_points, count=10)

        # --- CONSTANT WIDTH SNAKE (slender) ---
        radius = self.radius
        glow_radius = int(radius * 2.3)

        for i, (x, y) in enumerate(smooth):
            # glowing outer layer
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (200, 200, 255, 45), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (x - glow_radius, y - glow_radius))

            
            body_color = (230, 230, 255)
            pygame.draw.circle(surface, body_color, (int(x), int(y)), radius)

    def head_rect(self, size=12):
        x, y = self.body_points[0]
        return pygame.Rect(int(x - size/2), int(y - size/2), size, size)

    def collides_with_point(self, point, radius=10):
        px, py = point
        hx, hy = self.body_points[0]
        return (hx - px)**2 + (hy - py)**2 <= radius*radius

    def collides_self(self):
        # require a minimum number of points before self-collision checking
        if len(self.body_points) < 8:
            return False

        hx, hy = self.body_points[0]
        # start checking a bit into the body to avoid immediate neighbor collisions (false positives)
        # use a distance threshold based on radius (a little buffer)
        thresh = (self.radius * 1.8) ** 2
        for p in self.body_points[8:]:
            if (hx - p[0])**2 + (hy - p[1])**2 < thresh:
                return True
        return False