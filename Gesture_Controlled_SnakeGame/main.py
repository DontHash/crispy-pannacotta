import pygame
import sys
import cv2
import random
import time

from gesture.gesture_model import GestureClassifier
from controller.input_controller import InputController
from game.snake import Snake
from game.background import Background
from game.player import Player
from ui import HomeScreen

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 30

def spawn_food(margin=40):
    x = random.randint(margin, WIDTH - margin)
    y = random.randint(margin, HEIGHT - margin)
    return (x, y)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gesture Snake")
    clock = pygame.time.Clock()

    # Initialize modules
    bg = Background(screen, grid_size=24)
    player = Player()
    snake = Snake(start_pos=(WIDTH//2, HEIGHT//2))
    controller = InputController(initial="RIGHT")

    # Gesture classifier and webcam
    cap = cv2.VideoCapture(0)
    classifier = GestureClassifier(verbose=False)
    last_gesture = None
    last_conf = 0.0
    # throttle gesture inference (don't run every frame)
    gesture_interval = 0.18  # seconds
    last_gesture_time = 0.0

    # Home screen
    home = HomeScreen(screen, cam_index=0, show_camera_preview=True)
    in_home = True

    food = spawn_food()
    food_radius = 8

    player.start()
    running = True
    game_over = False

    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds per frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if in_home:
                    if event.key == pygame.K_SPACE:
                        # If quick ready indicates gestures captured, start immediately.
                        if home.ready:
                            in_home = False
                            player.start()
                            snake = Snake(start_pos=(WIDTH//2, HEIGHT//2))
                            controller = InputController(initial="RIGHT")
                            food = spawn_food()
                            game_over = False
                        else:
                            # Otherwise run a short blocking check to confirm camera can see gestures
                            # This will sample for up to 4 seconds and set home.ready accordingly.
                            print("[main] Camera not ready. Performing quick check for gestures...")
                            ok = home.check_gesture_ready(timeout=4.0, sample_interval=0.12, required_ratio=0.5, movement_conf_min=0.25)
                            if ok:
                                print("[main] Gesture camera ready. Starting game.")
                                in_home = False
                                player.start()
                                snake = Snake(start_pos=(WIDTH//2, HEIGHT//2))
                                controller = InputController(initial="RIGHT")
                                food = spawn_food()
                                game_over = False
                            else:
                                print("[main] Could not detect gestures reliably. Please adjust camera/lighting and try again.")
                else:
                    # gameplay keys (unchanged)
                    if event.key == pygame.K_UP:
                        controller.set_force("UP")
                    elif event.key == pygame.K_DOWN:
                        controller.set_force("DOWN")
                    elif event.key == pygame.K_LEFT:
                        controller.set_force("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        controller.set_force("RIGHT")
                    elif event.key == pygame.K_r and game_over:
                        # restart
                        player.start()
                        snake = Snake(start_pos=(WIDTH//2, HEIGHT//2))
                        controller = InputController(initial="RIGHT")
                        food = spawn_food()
                        game_over = False

# Also, in the home-screen loop (when in_home), ensure the UI keeps updating:
        if in_home:
            home.draw()  # this will internally call update_ready_status periodically
            pygame.display.flip()
            continue
            if time.time() - last_gesture_time > gesture_interval:
                ret, frame = cap.read()
                if ret:
                    try:
                        action, conf = classifier.predict(frame)
                        last_gesture = action
                        last_conf = conf
                        last_gesture_time = time.time()
                        # start if Confirm detected with decent confidence
                        if action == "START" and conf > 0.55:
                            in_home = False
                            player.start()
                            snake = Snake(start_pos=(WIDTH//2, HEIGHT//2))
                            controller = InputController(initial="RIGHT")
                            food = spawn_food()
                            game_over = False
                    except Exception:
                        # model inference may error — keep home running
                        pass
            home.draw(last_gesture, last_conf)
            pygame.display.flip()
            continue

        # In-game: sample gesture periodically to control snake
        if time.time() - last_gesture_time > gesture_interval:
            ret, frame = cap.read()
            if ret:
                try:
                    action, conf = classifier.predict(frame)
                    last_gesture = action
                    last_conf = conf
                    last_gesture_time = time.time()
                    # only submit movement gestures
                    if action in ("UP", "DOWN", "LEFT", "RIGHT") and conf > 0.25:
                        controller.submit(action)
                except Exception:
                    pass

        # update direction from controller
        dir_string = controller.update()
        snake.set_direction({
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0),
        }[dir_string])

        # update snake physics
        snake.update(dt=1.0)

        # check boundary collision
        hx, hy = snake.body_points[0]
        if hx < 0 or hy < 0 or hx > WIDTH or hy > HEIGHT:
            game_over = True
            snake.alive = False

        # check self collision
        if snake.collides_self():
            game_over = True
            snake.alive = False

        # check food collision
        if snake.collides_with_point(food, radius=14):
            player.add_score(1)
            snake.grow(50)  # grow by some pixels
            food = spawn_food()

        # draw
        bg.draw()
        # food
        pygame.draw.circle(screen, (255, 50, 50), (int(food[0]), int(food[1])), food_radius)
        snake.draw(screen)

        # HUD
        font = pygame.font.SysFont("Arial", 20)
        score_surf = font.render(f"Score: {player.score}", True, (240,240,240))
        time_surf = font.render(f"Time: {int(player.elapsed())}s", True, (240,240,240))
        gesture_surf = font.render(f"Gesture: {last_gesture} {last_conf:.2f}", True, (200,200,120))
        screen.blit(score_surf, (10, 10))
        screen.blit(time_surf, (10, 30))
        screen.blit(gesture_surf, (10, 50))

        if game_over:
            go_font = pygame.font.SysFont("Arial", 48)
            text = go_font.render("GAME OVER", True, (255, 50, 50))
            sub = font.render("Press R to restart or ESC to quit", True, (255,255,255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 16))

        pygame.display.flip()

        if not running:
            break

    # cleanup
    home.close()
    cap.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()