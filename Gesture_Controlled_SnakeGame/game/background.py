# game/background.py
# Draws background grid and subtle gradient for the game area.

import pygame

class Background:
    def __init__(self, surface, grid_size=20, color1=(30,30,30), color2=(20,20,20)):
        self.surface = surface
        self.grid_size = grid_size
        self.color1 = color1
        self.color2 = color2

    def draw(self):
        w, h = self.surface.get_size()
        # simple two-tone checkerboard
        cols = w // self.grid_size + 1
        rows = h // self.grid_size + 1
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c * self.grid_size, r * self.grid_size, self.grid_size, self.grid_size)
                if (r + c) % 2 == 0:
                    pygame.draw.rect(self.surface, self.color1, rect)
                else:
                    pygame.draw.rect(self.surface, self.color2, rect)
        # optional subtle center highlight
        overlay = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        pygame.draw.circle(overlay, (255,255,255,10), (w//2, h//2), min(w,h)//2)
        self.surface.blit(overlay, (0,0))