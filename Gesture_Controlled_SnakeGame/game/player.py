# game/player.py
# Player class: tracks score, start time and elapsed time.

import time

class Player:
    def __init__(self):
        self.score = 0
        self.start_time = None
        self.paused_time = 0.0
        self._pause_start = None

    def start(self):
        self.start_time = time.time()
        self.score = 0
        self.paused_time = 0.0
        self._pause_start = None

    def add_score(self, amount=1):
        self.score += amount

    def pause(self):
        if self._pause_start is None:
            self._pause_start = time.time()

    def resume(self):
        if self._pause_start is not None:
            self.paused_time += time.time() - self._pause_start
            self._pause_start = None

    def elapsed(self):
        if self.start_time is None:
            return 0.0
        end = time.time() if self._pause_start is None else self._pause_start
        return max(0.0, end - self.start_time - self.paused_time)