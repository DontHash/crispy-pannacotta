# game/audio.py
# Synthesized sound effects (no external assets). Safe on machines without audio.

import numpy as np
import pygame


class SoundFX:
    def __init__(self):
        self.enabled = False
        self.eat_sound = None
        self.game_over_sound = None
        try:
            pygame.mixer.init()
            self.eat_sound = self._tone(880, 0.08, volume=0.35, wave="square")
            self.game_over_sound = self._tone(220, 0.6, volume=0.5, wave="sine", descend=True)
            self.enabled = True
        except Exception:
            self.enabled = False

    def _tone(self, freq, duration, volume=0.5, wave="sine", descend=False, sample_rate=22050):
        n = int(sample_rate * duration)
        t = np.linspace(0.0, duration, n, endpoint=False)
        f = freq * np.linspace(1.0, 0.5, n) if descend else np.full(n, freq)
        phase = 2.0 * np.pi * f * t
        s = np.sign(np.sin(phase)) if wave == "square" else np.sin(phase)
        envelope = np.linspace(1.0, 0.05, n)
        data = (s * envelope * volume * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(data)
        sound.set_volume(volume)
        return sound

    def play_eat(self):
        if self.enabled and self.eat_sound:
            self.eat_sound.play()

    def play_game_over(self):
        if self.enabled and self.game_over_sound:
            self.game_over_sound.play()
