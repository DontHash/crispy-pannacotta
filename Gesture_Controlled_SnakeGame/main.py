import argparse
import os
import sys

import pygame

from game.audio import SoundFX
from game.background import Background, PROJECT_ROOT
from game.game import Game, GameState
from gesture.gesture_service import GestureService
from ui import HomeScreen

WIDTH, HEIGHT = 800, 600
FPS = 60

KEY_DIRECTIONS = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
}


def main():
    parser = argparse.ArgumentParser(description="Gesture Controlled Snake Game")
    parser.add_argument("--no-camera", action="store_true", help="run without webcam (keyboard only)")
    parser.add_argument("--cam-index", type=int, default=0, help="webcam index")
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gesture Snake")
    clock = pygame.time.Clock()

    sfx = SoundFX()
    try:
        pygame.mixer.music.load(os.path.join(PROJECT_ROOT, "Assets", "BG_Music1.mp3"))
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except Exception:
        print("[Warning] Could not load background music.")

    game = Game(width=WIDTH, height=HEIGHT, sfx=sfx)
    bg = Background()
    home = HomeScreen(screen)
    svc = GestureService(cam_index=args.cam_index if not args.no_camera else None)
    if args.no_camera:
        home.ready = True
    svc.start()

    running = True
    last_frame_id = -1
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state in (GameState.PLAYING, GameState.PAUSED):
                        game.toggle_pause()
                    elif game.state == GameState.GAME_OVER:
                        running = False
                elif event.key == pygame.K_p and game.state in (GameState.PLAYING, GameState.PAUSED):
                    game.toggle_pause()
                elif event.key == pygame.K_SPACE and game.state == GameState.HOME and home.ready:
                    game.start_playing()
                elif event.key == pygame.K_r and game.state == GameState.GAME_OVER:
                    game.start_playing()
                elif event.key in KEY_DIRECTIONS:
                    game.set_forced_direction(KEY_DIRECTIONS[event.key])

        result = svc.latest()
        if result is not None and result.frame_id != last_frame_id:
            last_frame_id = result.frame_id
            if result.action is not None and result.confidence >= 0.25:
                game.submit_gesture(result.action, result.confidence)

        game.update(dt)

        if game.state == GameState.HOME:
            home.draw(result)
        else:
            game.draw(screen, bg, result)
        pygame.display.flip()

    svc.stop()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
