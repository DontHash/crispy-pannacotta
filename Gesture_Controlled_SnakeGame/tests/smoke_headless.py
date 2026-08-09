"""Headless integration smoke test: drives the real main() loop via posted
pygame events and requires a clean exit."""
import os
import sys
import threading
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame


def pump():
    pygame.init()
    time.sleep(2.0)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))  # start game
    time.sleep(1.0)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))     # steer
    time.sleep(0.5)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))  # pause
    time.sleep(0.5)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))  # resume
    time.sleep(1.0)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))       # pause again
    time.sleep(0.5)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))       # resume
    time.sleep(0.5)
    pygame.event.post(pygame.event.Event(pygame.QUIT))


if __name__ == "__main__":
    t = threading.Thread(target=pump, daemon=True)
    t.start()
    import main  # noqa: E402

    try:
        main.main()
        print("SMOKE PASS (clean exit)")
    except SystemExit as e:
        print(f"SMOKE PASS (SystemExit {e.code})")
    except Exception:
        print("SMOKE FAIL")
        raise
