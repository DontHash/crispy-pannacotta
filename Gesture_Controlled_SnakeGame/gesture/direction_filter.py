# gesture/direction_filter.py
# Low-latency direction filter: emits on the first strong detection (no
# confirmation cycle), uses a magnitude EMA as a deadzone against noise,
# and a flip-lock that only delays exact reversals (~90ms) to stop jitter.
# Perpendicular turns are always accepted immediately.

import math
import time

OPPOSITES = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


class DirectionFilter:
    def __init__(self, alpha=0.4, threshold=0.18, flip_lock_ms=90):
        self.alpha = alpha
        self.threshold = threshold
        self.flip_lock_ms = flip_lock_ms
        self.mag = 0.0
        self.current = None
        self._flip_start = None

    def reset(self):
        self.mag = 0.0
        self.current = None
        self._flip_start = None

    @staticmethod
    def _classify(ndx, ndy):
        if abs(ndx) >= abs(ndy):
            if ndx > 0.0:
                return "RIGHT"
            if ndx < 0.0:
                return "LEFT"
        else:
            if ndy < 0.0:
                return "UP"
            if ndy > 0.0:
                return "DOWN"
        return None

    def update(self, ndx, ndy, t_ms=None):
        """Feed a normalized direction vector; returns a direction on change or None."""
        if t_ms is None:
            t_ms = int(time.monotonic() * 1000)

        mag = math.hypot(ndx, ndy)
        self.mag = self.alpha * mag + (1.0 - self.alpha) * self.mag
        if self.mag < self.threshold:
            return None

        action = self._classify(ndx, ndy)
        if action is None:
            return None

        if self.current == action:
            self._flip_start = None
            return action

        if action == OPPOSITES.get(self.current):
            if self._flip_start is None:
                self._flip_start = t_ms
                return None
            if t_ms - self._flip_start < self.flip_lock_ms:
                return None

        self.current = action
        self._flip_start = None
        return action
