# game/snake.py
# Snake model with curvy/wriggly drawing using Catmull-Rom interpolation for smooth body.
# Logical movement is continuous (pixel-based) using a velocity vector; collisions are axis-aligned rectangle tests.

import pygame
import math

def catmull_rom_chain(points, count=12):
    """
    Given list of points (x,y), return a list of interpolated points using Catmull-Rom splines.
    `count` controls subdivisions between control points.
    """
    if len(points) < 2:
        return points[:]
    # Add control points for endpoints
    pts = []
    # For endpoints, duplicate first/last
    ext = [points[0]] + points + [points[-1]]
    for i in range(len(ext)-3):
        p0, p1, p2, p3 = ext[i], ext[i+1], ext[i+2], ext[i+3]
        for t_step in range(count):
            t = t_step / float(count)
            t2 = t * t
            t3 = t2 * t
            # Catmull-Rom spline basis
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
    def __init__(self, start_pos, color=(0,255,0), speed=4, segment_length=18):
        self.color = color
        self.speed = speed  # pixels per tick
        self.segment_length = segment_length
        # body_points holds the polyline of the snake from head to tail (many points for smoothness)
        self.body_points = [start_pos]
        # target length in pixels (increases when eating)
        self.target_length = segment_length * 5  # initial length
        self.head_pos = list(start_pos)
        self.direction = (1, 0)  # unit vector direction
        self.alive = True

    def set_direction(self, dvec):
        self.direction = dvec

    def grow(self, pixels):
        self.target_length += pixels

    def update(self, dt=1.0):
        if not self.alive:
            return
        # Move head along direction
        dx = self.direction[0] * self.speed * dt
        dy = self.direction[1] * self.speed * dt
        self.head_pos[0] += dx
        self.head_pos[1] += dy
        # Insert new head at front
        self.body_points.insert(0, (self.head_pos[0], self.head_pos[1]))
        # Trim tail to maintain target_length in pixels
        cur_len = 0.0
        trimmed = []
        for i in range(len(self.body_points)-1):
            x1,y1 = self.body_points[i]
            x2,y2 = self.body_points[i+1]
            seg = math.hypot(x2-x1, y2-y1)
            cur_len += seg
            trimmed.append(self.body_points[i])
            if cur_len >= self.target_length:
                # include the final point at proportion along this segment
                over = cur_len - self.target_length
                if seg > 0:
                    ratio = (seg - over) / seg
                    nx = x1 + (x2 - x1) * ratio
                    ny = y1 + (y2 - y1) * ratio
                    trimmed.append((nx, ny))
                break
        # if trimmed shorter, keep all
        if len(trimmed) < 2:
            # not enough points yet
            trimmed = self.body_points[:]
        self.body_points = trimmed

    def draw(self, surface):
        # Smooth body points to get curvy shape
        if len(self.body_points) < 2:
            return
        smooth = catmull_rom_chain(self.body_points, count=8)
        # Draw a filled polygon for the body by drawing circles along the smooth points
        for i, (x, y) in enumerate(smooth):
            # make head slightly larger, tail smaller
            t = i / max(1, len(smooth)-1)
            radius = int(12 * (1 - (t*0.9)))  # head big, tail small
            # add wriggle: a small sine offset perpendicular to movement
            offset = 3.0 * math.sin(i * 0.4)
            pygame.draw.circle(surface, self.color, (int(x+offset), int(y)), max(2, radius))

    def head_rect(self, size=12):
        x, y = self.body_points[0]
        return pygame.Rect(int(x - size/2), int(y - size/2), size, size)

    def collides_with_point(self, point, radius=10):
        px, py = point
        # check distance to head
        hx, hy = self.body_points[0]
        return (hx - px)**2 + (hy - py)**2 <= radius*radius

    def collides_self(self):
        # simple self-collision: check head against later body segments
        if len(self.body_points) < 12:
            return False
        hx, hy = self.body_points[0]
        for p in self.body_points[12:]:
            if (hx - p[0])**2 + (hy - p[1])**2 < (12*12):
                return True
        return False