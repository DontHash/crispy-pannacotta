
import pygame
import os

class Background:
    def __init__(self, surface, image_path="Gesture_Controlled_SnakeGame/Assets/Disco_background1.jpg"):
        self.surface = surface
        
        # Load and scale background image
        if not os.path.exists(image_path):
            print(f"[Warning] Background image not found: {image_path}")
            self.bg = None
        else:
            img = pygame.image.load(image_path).convert()
            w, h = surface.get_size()
            self.bg = pygame.transform.scale(img, (w, h))

    def draw(self):
        if self.bg:
            self.surface.blit(self.bg, (0, 0))
        else:
            # fallback: plain dark background
            self.surface.fill((20, 20, 20))
