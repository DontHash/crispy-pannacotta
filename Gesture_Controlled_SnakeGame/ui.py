# ui.py
# HomeScreen renders the camera preview + readiness state from the shared
# GestureService results. It no longer owns a camera or classifier.

import time

import numpy as np
import pygame

DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")


class HomeScreen:
    def __init__(self, screen, ready_ttl=1.5):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.SysFont("arial", 36)
        self.small = pygame.font.SysFont("arial", 20)
        self.ready = False
        self.ready_ttl = ready_ttl
        self._last_ready_at = 0.0
        self._last_gesture = None
        self._last_conf = 0.0

        self._preview_id = None
        self._preview_surf = None
        self._last_result = None

    def update_ready(self, result):
        if result is None:
            return
        self._last_result = result
        self._last_gesture = result.action
        self._last_conf = result.confidence
        if result.action in DIRECTIONS and result.confidence >= 0.25:
            self._last_ready_at = time.time()
        self.ready = (time.time() - self._last_ready_at) < self.ready_ttl

    def _build_preview(self, result):
        if result.frame_id == self._preview_id and self._preview_surf is not None:
            return
        self._preview_id = result.frame_id
        preview = result.preview
        if preview is None:
            self._preview_surf = None
            return
        rgb = np.ascontiguousarray(preview[:, :, ::-1])
        surf = pygame.image.frombuffer(rgb, (rgb.shape[1], rgb.shape[0]), "RGB")
        self._preview_surf = pygame.transform.smoothscale(surf, (200, 200))

    def draw(self, result=None):
        if result is not None:
            self.update_ready(result)

        self.screen.fill((10, 10, 10))
        title = self.font.render("Gesture Snake", True, (200, 250, 200))
        subtitle = self.small.render("Use hand gestures to control the snake. 'Pinch' to START.", True, (200, 200, 200))
        instr = self.small.render("Show a movement gesture until READY is YES, then press SPACE.", True, (200, 200, 200))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 140))
        self.screen.blit(instr, (self.width // 2 - instr.get_width() // 2, 180))

        ready_text = "YES" if self.ready else "NO"
        ready_color = (80, 220, 120) if self.ready else (220, 80, 80)
        ready_surf = self.small.render(f"Gesture Ready: {ready_text}", True, ready_color)
        self.screen.blit(ready_surf, (40, self.height - 40))

        if result is not None:
            self._build_preview(result)

        if self._preview_surf is not None:
            px, py = self.width - 220, 20
            self.screen.blit(self._preview_surf, (px, py))
            if result is not None and result.bbox:
                bx, by, bw, bh = result.bbox
                scale_x = 200 / float(result.preview.shape[1])
                scale_y = 200 / float(result.preview.shape[0])
                rect = pygame.Rect(px + int(bx * scale_x), py + int(by * scale_y),
                                   max(2, int(bw * scale_x)), max(2, int(bh * scale_y)))
                pygame.draw.rect(self.screen, (255, 200, 50), rect, width=2)
            if result is not None and result.landmarks:
                h = result.preview.shape[0]
                for (lx, ly, _lz) in result.landmarks:
                    sx = px + int(lx * 200)
                    sy = py + int(ly * 200 / h)
                    pygame.draw.circle(self.screen, (120, 200, 255), (sx, sy), 3)

        gesture_text = f"Last gesture: {self._last_gesture} ({self._last_conf:.2f})" if self._last_gesture else "Last gesture: -"
        gsurf = self.small.render(gesture_text, True, (220, 220, 180))
        self.screen.blit(gsurf, (40, self.height - 70))
