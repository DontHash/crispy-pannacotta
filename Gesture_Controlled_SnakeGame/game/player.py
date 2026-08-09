# game/player.py
# Player class: tracks score, start time and elapsed time.
# HighScore: tiny JSON-backed persistence for the best score.

import json
import os
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


class HighScore:
    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            with open(self.path, "r") as f:
                return max(0, int(json.load(f)))
        except (OSError, ValueError, TypeError):
            return 0

    def submit(self, score):
        """Record score; returns True if it is a new best."""
        if score <= self.load():
            return False
        try:
            with open(self.path, "w") as f:
                json.dump(score, f)
        except OSError:
            return False
        return True


def default_highscore_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "highscore.json")
