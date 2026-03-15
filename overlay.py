"""
overlay.py — Real-Time HUD Overlay Renderer
============================================
Draws all visual debug / status information onto the OpenCV frame:
  - Facial landmarks (eye mesh + iris rings)
  - Gaze vector arrow
  - EAR bars (left / right)
  - Status panel  (mode, last action, FPS, calibration progress)
  - Scroll zone indicators
  - Blink event flash
"""

import time
import numpy as np
import cv2

from eye_tracker import (
    GazeResult,
    LEFT_EYE_OUTLINE,
    RIGHT_EYE_OUTLINE,
)
import config

C_GREEN  = (0,   220,  80)
C_RED    = (0,    60, 220)
C_YELLOW = (0,   200, 200)
C_WHITE  = (240, 240, 240)
C_CYAN   = (240, 200, 0)
C_ORANGE = (0,   140, 255)
C_PURPLE = (180,  60, 180)
C_GRAY   = (100, 100, 100)
C_DARK   = (30,   30,  30)

FONT = cv2.FONT_HERSHEY_SIMPLEX


class HUDOverlay:

    def __init__(self):
        self._fps_history = []
        self._last_frame_time = time.monotonic()
        self._blink_flash_until = 0.0

    def draw(self, frame, gaze, left_ear, right_ear, mode_name,
             last_action, recent_actions, voice_phrase,
             calibrated, calib_pct, listening=False) -> np.ndarray:
        out = frame.copy()
        now = time.monotonic()
        fps = self._update_fps(now)

        if gaze is not None:
            lm = gaze.landmarks_px
            if config.SHOW_LANDMARKS:
                self._draw_eye_mesh(out, lm)
                self._draw_iris(out, gaze)
            if config.SHOW_GAZE_VECTOR:
                self._draw_gaze_arrow(out, frame.shape, gaze)

        if config.SHOW_EAR_VALUES:
            self._draw_ear_bars(out, left_ear, right_ear)

        if config.SHOW_STATUS_OVERLAY:
            self._draw_status_panel(out, mode_name, last_action,
                                    recent_actions, voice_phrase,
                                    fps, calibrated, calib_pct, listening)

        self._draw_scroll_zones(out, frame.shape)

        # Draw listening indicator if active
        if listening and getattr(config, 'VOICE_SHOW_LISTENING_STATUS', True):
            self._draw_listening_indicator(out)

        if now < self._blink_flash_until:
            cv2.rectangle(out, (0, 0),
                          (out.shape[1], out.shape[0]), C_CYAN, 5)
        return out

    def trigger_blink_flash(self):
        self._blink_flash_until = time.monotonic() + 0.15

    def _update_fps(self, now):
        dt = now - self._last_frame_time
        self._last_frame_time = now
        fps = 1.0 / max(dt, 1e-6)
        self._fps_history.append(fps)
        if len(self._fps_history) > 30:
            self._fps_history.pop(0)
        return float(np.mean(self._fps_history))

    def _draw_eye_mesh(self, frame, landmarks):
        for indices in (LEFT_EYE_OUTLINE, RIGHT_EYE_OUTLINE):
            pts = np.array([landmarks[i].astype(int) for i in indices],
                           dtype=np.int32)
            cv2.polylines(frame, [pts], isClosed=True,
                          color=C_GREEN, thickness=1, lineType=cv2.LINE_AA)

    def _draw_iris(self, frame, gaze):
        for centre in (gaze.left_iris_px, gaze.right_iris_px):
            cv2.circle(frame, centre, 3, C_CYAN,  -1, cv2.LINE_AA)
            cv2.circle(frame, centre, 7, C_YELLOW, 1, cv2.LINE_AA)

    def _draw_gaze_arrow(self, frame, shape, gaze):
        h, w = shape[:2]
        cx, cy = w // 2, h // 2
        dx, dy = gaze.gaze_offset
        end_x = int(cx + dx * w * 2.0)
        end_y = int(cy + dy * h * 2.0)
        cv2.arrowedLine(frame, (cx, cy), (end_x, end_y),
                        C_ORANGE, 2, tipLength=0.3,
                        line_type=cv2.LINE_AA)

    def _draw_ear_bars(self, frame, left_ear, right_ear):
        h, w = frame.shape[:2]
        bar_max_h, bar_w, margin = 80, 20, 10
        for i, (ear, label) in enumerate(
                [(left_ear, "L"), (right_ear, "R")]):
            x = w - margin - (2 - i) * (bar_w + 8)
            cv2.rectangle(frame,
                          (x, h - margin - bar_max_h),
                          (x + bar_w, h - margin), C_DARK, -1)
            fill_h = min(int(ear * bar_max_h / 0.45), bar_max_h)
            colour = C_GREEN if ear > config.EAR_OPEN_THRESHOLD else C_RED
            cv2.rectangle(frame,
                          (x, h - margin - fill_h),
                          (x + bar_w, h - margin), colour, -1)
            cv2.rectangle(frame,
                          (x, h - margin - bar_max_h),
                          (x + bar_w, h - margin), C_WHITE, 1)
            cv2.putText(frame, label,
                        (x + 4, h - margin - bar_max_h - 5),
                        FONT, 0.5, C_WHITE, 1, cv2.LINE_AA)
            cv2.putText(frame, f"{ear:.2f}",
                        (x - 5, h - margin + 15),
                        FONT, 0.35, C_WHITE, 1, cv2.LINE_AA)

    def _draw_status_panel(self, frame, mode, last_action, recent,
                           voice, fps, calibrated, calib_pct, listening=False):
        h, w = frame.shape[:2]
        panel_w, panel_h = 280, 230
        panel = np.zeros((panel_h, panel_w, 3), dtype=np.uint8)
        panel[:] = C_DARK

        # Listening status (top of panel)
        if listening:
            listening_color = C_CYAN
            listening_text = "[MIC] LISTENING..."
        else:
            listening_color = C_GRAY
            listening_text = "[MIC] Ready"
        
        cv2.putText(panel, listening_text,
                    (8, 20), FONT, 0.6, listening_color, 2, cv2.LINE_AA)

        cv2.putText(panel, f"FPS: {fps:.1f}",
                    (8, 45), FONT, 0.5, C_GREEN, 1, cv2.LINE_AA)
        mode_col = {"NORMAL": C_GREEN, "SCROLL": C_YELLOW,
                    "DRAG": C_ORANGE,  "PAUSED": C_RED}.get(mode, C_WHITE)
        cv2.putText(panel, f"Mode: {mode}",
                    (8, 65), FONT, 0.5, mode_col, 1, cv2.LINE_AA)
        if not calibrated:
            pct = int(calib_pct * 100)
            cv2.putText(panel, f"Calibrating... {pct}%",
                        (8, 85), FONT, 0.45, C_YELLOW, 1, cv2.LINE_AA)
            cv2.rectangle(panel, (8, 91),
                          (8 + int(calib_pct * 264), 101), C_YELLOW, -1)
        else:
            cv2.putText(panel, "Calibrated OK",
                        (8, 85), FONT, 0.45, C_GREEN, 1, cv2.LINE_AA)
        cv2.putText(panel, f"Action: {last_action[:24]}",
                    (8, 120), FONT, 0.45, C_CYAN, 1, cv2.LINE_AA)
        if voice:
            cv2.putText(panel, f"Voice: {voice[:26]}",
                        (8, 140), FONT, 0.4, C_PURPLE, 1, cv2.LINE_AA)
        cv2.putText(panel, "Recent:", (8, 165),
                    FONT, 0.4, C_GRAY, 1, cv2.LINE_AA)
        for j, act in enumerate(recent[-3:]):
            cv2.putText(panel, f"  {act[:30]}",
                        (8, 181 + j * 14), FONT, 0.35,
                        C_GRAY, 1, cv2.LINE_AA)

        overlay_region = frame[10:10 + panel_h, 10:10 + panel_w]
        cv2.addWeighted(panel, config.OVERLAY_ALPHA,
                        overlay_region, 1 - config.OVERLAY_ALPHA,
                        0, overlay_region)
        cv2.rectangle(frame, (10, 10),
                      (10 + panel_w, 10 + panel_h), C_GRAY, 1)

    def _draw_scroll_zones(self, frame, shape):
        h, w = shape[:2]
        zone = int(h * getattr(config, 'SCROLL_ZONE_FRACTION', 0.08))
        cv2.rectangle(frame, (0, 0), (w, zone), (40, 40, 0), -1)
        cv2.putText(frame, "^ SCROLL UP",
                    (w // 2 - 50, zone - 5),
                    FONT, 0.4, C_YELLOW, 1, cv2.LINE_AA)
        cv2.rectangle(frame, (0, h - zone), (w, h), (40, 40, 0), -1)
        cv2.putText(frame, "v SCROLL DOWN",
                    (w // 2 - 55, h - 5),
                    FONT, 0.4, C_YELLOW, 1, cv2.LINE_AA)

    def _draw_listening_indicator(self, frame):
        """Draw animated listening indicator at the bottom center of the frame."""
        h, w = frame.shape[:2]
        
        # Pulsing circle indicator
        time_val = time.monotonic()
        pulse = int(5 + 5 * np.sin(time_val * 4))  # Pulse animation
        
        center_x = w // 2
        center_y = h - 40
        
        # Draw pulsing circles
        cv2.circle(frame, (center_x, center_y), pulse + 15, (0, 150, 200), 1)
        cv2.circle(frame, (center_x, center_y), pulse + 10, (0, 180, 240), 1)
        cv2.circle(frame, (center_x, center_y), 8, C_CYAN, -1)
        
        cv2.putText(frame, "LISTENING",
                    (center_x - 50, center_y + 25),
                    FONT, 0.6, C_CYAN, 2, cv2.LINE_AA)


_hud = HUDOverlay()


def draw_overlay(frame, **kwargs):
    # Map main.py overlay inputs to HUDOverlay.draw interface.
    return _hud.draw(
        frame,
        gaze=None,
        left_ear=kwargs.get('ear', 0.0),
        right_ear=kwargs.get('ear', 0.0),
        mode_name=kwargs.get('mode_text', ''),
        last_action=kwargs.get('voice_text', '') or kwargs.get('blink_type', ''),
        recent_actions=[],
        voice_phrase=kwargs.get('voice_text', ''),
        calibrated=True,  # uncalibrated state shown via mode_text
        calib_pct=0.0,
        listening=kwargs.get('listening', False),
    )


def draw_calibration_target(frame, x, y, remaining_ms):
    color = (0, 220, 255)
    radius = max(5, int(15 * (remaining_ms / 0.5)))
    cv2.circle(frame, (x, y), radius, color, 2, cv2.LINE_AA)
    cv2.circle(frame, (x, y), 3, color, -1, cv2.LINE_AA)
    return frame
