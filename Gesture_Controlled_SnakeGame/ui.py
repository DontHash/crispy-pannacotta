# ui.py
# Updated HomeScreen.draw to display the processed (mirrored & cropped) preview used by MediaPipe
# and to draw a bounding box around the detected hand when available (classifier.last_bbox).
# Also draws small landmark dots if available.

import pygame
import cv2
import numpy as np
import time
from gesture.gesture_model import GestureClassifier

class HomeScreen:
    def __init__(self, screen, cam_index=0, show_camera_preview=True):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.SysFont("arial", 36)
        self.small = pygame.font.SysFont("arial", 20)
        self.show_camera_preview = show_camera_preview
        # Use DirectShow on Windows where available for more reliable capture
        try:
            self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap.release()
                self.cap = cv2.VideoCapture(cam_index)
        except Exception:
            self.cap = cv2.VideoCapture(cam_index)
        # classifier instance for preview/ready checks (target_size must match for consistent preview)
        self.classifier = GestureClassifier(verbose=False, target_size=320)
        self.ready = False
        self._last_ready_check_time = 0.0
        self.ready_check_interval = 0.12  # seconds between quick checks

        self._last_gesture = None
        self._last_conf = 0.0

    def close(self):
        if self.cap:
            self.cap.release()
        if self.classifier:
            try:
                self.classifier.close()
            except Exception:
                pass

    def draw(self, last_gesture=None, confidence=0.0):
        """
        Draw the Home screen. Uses classifier.last_frame_processed (mirrored & cropped)
        as the preview image so the bbox coordinates align with the preview.
        """
        # Update quick readiness periodically
        if time.time() - self._last_ready_check_time > self.ready_check_interval:
            self.update_ready_status()
            self._last_ready_check_time = time.time()

        self.screen.fill((10,10,10))
        title = self.font.render("Gesture Snake", True, (200,250,200))
        subtitle = self.small.render("Use hand gestures to control the snake. 'Pinch' to START.", True, (200,200,200))
        instr = self.small.render("Show gesture and wait until 'Gesture Ready' shows YES, then press SPACE to start.", True, (200,200,200))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 80))
        self.screen.blit(subtitle, (self.width//2 - subtitle.get_width()//2, 140))
        self.screen.blit(instr, (self.width//2 - instr.get_width()//2, 180))

        # ready indicator
        ready_text = "YES" if self.ready else "NO"
        ready_color = (80, 220, 120) if self.ready else (220, 80, 80)
        ready_surf = self.small.render(f"Gesture Ready: {ready_text}", True, ready_color)
        self.screen.blit(ready_surf, (40, self.height - 40))

        # camera preview area (use classifier.last_frame_processed if available)
        preview_img = None
        if self.classifier and self.classifier.last_frame_processed is not None:
            preview_img = self.classifier.last_frame_processed
        elif self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Mirror so preview matches processed frame (but note processed frame is cropped/resized)
                frame = cv2.flip(frame, 1)
                # center-crop and resize to classifier target size for visual consistency
                h, w = frame.shape[:2]
                side = min(h, w)
                sx = (w - side) // 2
                sy = (h - side) // 2
                square = frame[sy:sy+side, sx:sx+side]
                preview_img = cv2.resize(square, (self.classifier.target_size, self.classifier.target_size), interpolation=cv2.INTER_AREA)

        if preview_img is not None and self.show_camera_preview:
            # Convert BGR -> RGB for pygame
            preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(preview_rgb.swapaxes(0,1))
            # Draw preview at top-right
            padding = 20
            preview_w = 200
            # maintain aspect ratio (it's square)
            preview_h = preview_w
            preview_surf = pygame.transform.smoothscale(surf, (preview_w, preview_h))
            px = self.width - preview_w - padding
            py = 20
            self.screen.blit(preview_surf, (px, py))

            # Draw bbox around detected hand if available (classifier.last_bbox is relative to processed frame)
            if self.classifier.last_bbox:
                bx, by, bw, bh = self.classifier.last_bbox
                # scale bbox from processed size -> preview size
                scale_x = preview_w / float(self.classifier.target_size)
                scale_y = preview_h / float(self.classifier.target_size)
                rx = int(px + bx * scale_x)
                ry = int(py + by * scale_y)
                rw = int(bw * scale_x)
                rh = int(bh * scale_y)
                # draw rectangle outline
                pygame.draw.rect(self.screen, (255, 200, 50), pygame.Rect(rx, ry, rw, rh), width=2)

            # Optionally draw small landmark dots
            if self.classifier.last_landmarks:
                for (lx, ly, lz) in self.classifier.last_landmarks:
                    sx = int(px + lx * preview_w)
                    sy = int(py + ly * preview_h)
                    pygame.draw.circle(self.screen, (120, 200, 255), (sx, sy), 3)

        # show last gesture & confidence
        gesture_text = f"Last gesture: {self._last_gesture} ({self._last_conf:.2f})" if self._last_gesture else "Last gesture: -"
        gsurf = self.small.render(gesture_text, True, (220,220,180))
        self.screen.blit(gsurf, (40, self.height - 70))

    def sample_gesture(self):
        """
        Read one frame and return predicted label + confidence.
        Ensures the classifier receives mirrored frames (predict flips internally).
        """
        if not (self.cap and self.cap.isOpened()):
            return None, 0.0
        ret, frame = self.cap.read()
        if not ret:
            return None, 0.0
        try:
            action, conf = self.classifier.predict(frame)
            # store last seen for UI
            self._last_gesture = action
            self._last_conf = conf
            return action, conf
        except Exception:
            return None, 0.0

    def update_ready_status(self, movement_conf_min=0.25):
        """
        Non-blocking quick check: sample one frame and update self.ready.
        """
        action, conf = self.sample_gesture()
        if action in ("UP","DOWN","LEFT","RIGHT") and conf >= movement_conf_min:
            self.ready = True
        else:
            self.ready = False
        return self.ready

    def check_gesture_ready(self, timeout=4.0, sample_interval=0.12, required_ratio=0.5, movement_conf_min=0.25):
        """
        Blocking readiness check. Samples frames for up to `timeout` seconds.
        """
        if not (self.cap and self.cap.isOpened()):
            return False

        end_time = time.time() + timeout
        total = 0
        good = 0
        while time.time() < end_time:
            action, conf = self.sample_gesture()
            total += 1
            if action in ("UP","DOWN","LEFT","RIGHT") and conf >= movement_conf_min:
                good += 1
            time.sleep(sample_interval)

        ratio = (good / total) if total > 0 else 0.0
        self.ready = ratio >= required_ratio
        return self.ready