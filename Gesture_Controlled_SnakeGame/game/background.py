import os

import pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Background:
    def __init__(self, image_path=None):
        self.image_path = image_path or os.path.join(PROJECT_ROOT, "Assets", "Disco_background1.jpg")
        self.bg = None
        self._size = None

    def draw(self, surface):
        size = surface.get_size()
        if self.bg is None or self._size != size:
            self._size = size
            self.bg = None
            if os.path.exists(self.image_path):
                try:
                    img = pygame.image.load(self.image_path).convert()
                    self.bg = pygame.transform.smoothscale(img, size)
                except Exception:
                    self.bg = None
        if self.bg is not None:
            surface.blit(self.bg, (0, 0))
        else:
            surface.fill((20, 20, 20))
