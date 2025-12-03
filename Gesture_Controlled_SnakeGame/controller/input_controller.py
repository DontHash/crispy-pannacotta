# controller/input_controller.py
# Maps gesture labels & keyboard inputs to movement directions, enforces no-immediate-reverse rule.

from collections import deque

# Directions as vectors (x, y)
DIR_VECTORS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

OPPOSITES = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

class InputController:
    def __init__(self, initial="RIGHT"):
        self.current = initial  # 'UP','DOWN','LEFT','RIGHT'
        self._pending = deque(maxlen=3)  # small queue for smoothing rapid inputs

    def submit(self, direction):
        """Submit a desired direction (string). It will be queued and applied when valid."""
        if direction not in DIR_VECTORS:
            return
        # Avoid duplicates in queue
        if len(self._pending) == 0 or self._pending[-1] != direction:
            self._pending.append(direction)

    def update(self):
        """Try to apply next pending direction; return currently active direction."""
        if self._pending:
            cand = self._pending.popleft()
            # disallow immediate reverse
            if OPPOSITES[cand] != self.current:
                self.current = cand
        return self.current

    def set_force(self, direction):
        """Force set direction (used by keyboard); bypasses queue but still blocks reverse."""
        if direction in DIR_VECTORS and OPPOSITES[direction] != self.current:
            self.current = direction

    def get_vector(self):
        return DIR_VECTORS[self.current]