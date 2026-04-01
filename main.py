#!/usr/bin/env python3
"""
main.py — Hands-Free Human-Computer Interaction System
═══════════════════════════════════════════════════════
Entry point.  Orchestrates:
    1. Webcam capture (OpenCV)
    2. Face / iris landmark detection (MediaPipe Face Mesh)
    3. Gaze tracking  → cursor movement
    4. Blink detection → click / drag actions
    5. Voice recognition → commands + text input
    6. Optional 5-point calibration routine

Keyboard shortcuts (when webcam window is focused)
───────────────────────────────────────────────────
    Q / ESC     – quit
    C           – run calibration
    P           – pause / resume gaze tracking
    R           – reset calibration
    D           – toggle debug overlay
    S           – take screenshot (saves to desktop)
"""

import sys
import os
import time
import traceback
import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Optional imports for MediaPipe Tasks API (newer versions >=0.10.30)
try:
    from mediapipe.tasks.python.vision.core import image as mp_image
    from mediapipe.tasks.python.vision.core import vision_task_running_mode as mp_running_mode
    from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions
    from mediapipe.tasks.python.core.base_options import BaseOptions as _BaseOptions
    _HAS_TASKS_API = True
except Exception:
    mp_image = None
    mp_running_mode = None
    FaceLandmarker = None
    FaceLandmarkerOptions = None
    _BaseOptions = None
    _HAS_TASKS_API = False

# ── Project root on path ─────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from blink_detector import BlinkDetector
from gaze_tracker import GazeTracker
from cursor_controller import CursorController
from voice_recognition import VoiceHandler, Command
from command_interpreter import CommandInterpreter
from calibration import Calibrator
from overlay import draw_overlay, draw_calibration_target
from llm_handler import initialize_llm, is_llm_available

# ── Screen dimensions ────────────────────────
SCREEN_W, SCREEN_H = pyautogui.size()


def build_face_mesh():
    """Initialize face mesh detector based on MediaPipe API availability."""
    if hasattr(mp, "solutions") and getattr(mp.solutions, "face_mesh", None):
        return mp.solutions.face_mesh.FaceMesh(
            max_num_faces            = config.MAX_NUM_FACES,
            refine_landmarks        = config.REFINE_LANDMARKS,
            min_detection_confidence= config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence = config.MIN_TRACKING_CONFIDENCE,
        )

    # New MediaPipe Tasks API path
    if FaceLandmarker and FaceLandmarkerOptions and mp_image and mp_running_mode and _BaseOptions:
        model_path = getattr(config, "MEDIAPIPE_FACE_LANDMARK_MODEL_PATH", None)
        if not model_path:
            raise RuntimeError(
                "No MediaPipe face landmarker model path configured. "
                "Set config.MEDIAPIPE_FACE_LANDMARK_MODEL_PATH to a .task model file."
            )
        # Resolve relative paths based on the script's directory
        if not os.path.isabs(model_path):
            model_path = os.path.join(ROOT, model_path)
        if not os.path.exists(model_path):
            raise RuntimeError(
                f"MediaPipe model file not found: {model_path}\n"
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            )

        base_options = _BaseOptions(model_asset_path=model_path)
        options = FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_running_mode.VisionTaskRunningMode.IMAGE,
            num_faces=config.MAX_NUM_FACES,
            min_face_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        return FaceLandmarker.create_from_options(options)

    raise RuntimeError("MediaPipe face mesh API not available. Please install mediapipe <=0.10.5.")


def open_camera():
    # On Windows, CAP_DSHOW (DirectShow) is required for reliable frame capture.
    # Try it first, then fall back to the default backend.
    backends = []
    if sys.platform == "win32":
        backends.append(cv2.CAP_DSHOW)
    backends.append(0)  # 0 = default backend

    cap = None
    for backend in backends:
        if backend == 0:
            cap = cv2.VideoCapture(config.WEBCAM_INDEX)
        else:
            cap = cv2.VideoCapture(config.WEBCAM_INDEX, backend)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS,          30)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"[Camera] Opened with backend {'DirectShow' if backend == cv2.CAP_DSHOW else 'default'}")
                return cap
            cap.release()

    raise RuntimeError(
        f"Cannot open camera index {config.WEBCAM_INDEX}. "
        "Check that a webcam is connected and not in use."
    )


def main():
    print("=" * 60)
    print("  Hands-Free HCI System")
    print("=" * 60)
    print(f"  Screen: {SCREEN_W} x {SCREEN_H}")
    print(f"  Camera: index {config.WEBCAM_INDEX}")
    print(f"  Voice:  {getattr(config, 'VOICE_RECOGNITION_ENGINE', 'speech-recognition')}")
    print("-" * 60)
    print("  Controls (webcam window must be focused):")
    print("    Q / ESC  Quit")
    print("    C        Calibrate")
    print("    P        Pause / Resume tracking")
    print("    R        Reset calibration")
    print("    D        Toggle debug overlay")
    print("=" * 60)

    cap          = open_camera()
    print('[System] Camera opened')
    face_mesh    = build_face_mesh()
    print('[System] Face mesh initialized')
    blink_det    = BlinkDetector()
    gaze_tracker = GazeTracker(SCREEN_W, SCREEN_H)
    cursor       = CursorController()
    voice        = VoiceHandler()
    print('[System] Voice handler created')
    
    # ── Initialize LLM ──────────────────────────
    llm = None
    if config.LLM_ENABLED:
        try:
            llm = initialize_llm(
                host=config.LLM_OLLAMA_HOST,
                port=config.LLM_OLLAMA_PORT,
                model=config.LLM_MODEL
            )
            if is_llm_available():
                print(f'[LLM] ✓ LLM initialized: {llm.selected_model}')
            else:
                print('[LLM] ⚠ LLM unavailable - will use local processing')
        except Exception as e:
            print(f'[LLM] Error initializing LLM: {e}')
            print('[LLM] Continuing without LLM support...')
    
    interpreter  = CommandInterpreter(cursor, llm_handler=llm)
    calibrator   = None

    voice.start()
    print('[System] Voice thread started')
    print('=' * 60)
    print('[VOICE RECOGNITION STATUS]')
    print('  * Waiting for voice input...')
    print('  * Speak a command when ready')
    print('  * Check console for [Voice] messages')
    if is_llm_available():
        print('[LLM] * LLM-powered command enhancement enabled')
    print('=' * 60)

    tracking_active = True
    show_overlay    = getattr(config, 'SHOW_OVERLAY', True)
    calibrating     = False
    last_voice_text = ""
    blink_flash_str = ""
    blink_flash_end = 0.0
    action_status   = ""
    action_end      = 0.0
    gaze_x          = SCREEN_W  / 2
    gaze_y          = SCREEN_H  / 2
    
    # Listening status tracking (NEW)
    previous_listening_state = None
    listening_change_logged = False

    headless = os.environ.get('HEADLESS', '0').lower() in ('1', 'true', 'yes')
    if headless:
        print("[System] Running in headless mode (no cv2.imshow).")
    else:
        print("[System] Ready. Press 'C' in the webcam window to calibrate first.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[Camera] Frame capture failed. Exiting.")
                break

            frame = cv2.flip(frame, 1)
            ih, iw = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            if hasattr(face_mesh, "process"):
                results = face_mesh.process(rgb)
                face_landmarks_list = getattr(results, "multi_face_landmarks", None)
                using_legacy_api = True
            else:
                # MediaPipe Tasks API
                mp_image_obj = mp_image.Image(image_format=mp_image.ImageFormat.SRGB, data=rgb)
                detection = face_mesh.detect(mp_image_obj)
                face_landmarks_list = getattr(detection, "face_landmarks", None)
                using_legacy_api = False

            rgb.flags.writeable = True
            face_detected = bool(face_landmarks_list)

            now = time.time()
            blink_flash_str = blink_flash_str if now < blink_flash_end else ""
            action_status   = action_status   if now < action_end      else ""

            if face_detected:
                if using_legacy_api and face_landmarks_list:
                    landmarks = face_landmarks_list[0].landmark
                    draw_face_landmarks = face_landmarks_list[0]
                elif face_landmarks_list:
                    landmarks = face_landmarks_list[0] if isinstance(face_landmarks_list[0], list) else face_landmarks_list[0]
                    draw_face_landmarks = face_landmarks_list[0]
                else:
                    landmarks = []
                    draw_face_landmarks = None

                if calibrating and calibrator is not None:
                    tx, ty, remaining_ms = calibrator.current_target
                    if tx is not None:
                        done = calibrator.feed(landmarks, iw, ih)
                        if show_overlay:
                            fx = int(tx / SCREEN_W * iw)
                            fy = int(ty / SCREEN_H * ih)
                            draw_calibration_target(frame, fx, fy, remaining_ms)
                        if done:
                            calibrating = False
                            calibrator  = None
                            print("[System] Calibration complete.")
                    continue

                if tracking_active:
                    gaze_x, gaze_y = gaze_tracker.get_screen_coords(landmarks, iw, ih)
                    cursor.move(gaze_x, gaze_y)

                    blink_det.update(landmarks, iw, ih)
                    if blink_det.double_blink:
                        interpreter.handle_blink("double")
                        blink_flash_str = "double"
                        blink_flash_end = now + 0.3
                    elif blink_det.single_blink:
                        interpreter.handle_blink("single")
                        blink_flash_str = "single"
                        blink_flash_end = now + 0.2
                    elif blink_det.long_blink:
                        interpreter.handle_blink("long")
                        blink_flash_str = "long"
                        blink_flash_end = now + 0.4

            # Check listening status and print status messages ONLY on state change (NEW)
            current_listening = voice.is_listening if hasattr(voice, 'is_listening') else False
            if current_listening != previous_listening_state:
                status_text = "LISTENING" if current_listening else "READY"
                print(f"[Status] {status_text}")
                previous_listening_state = current_listening
            
            cmd, text, confidence = voice.get_command()
            if cmd is not None:
                last_voice_text = text or ""
                confidence_indicator = "*" * int(confidence * 5)  # Visual indicator (stars instead of emojis)
                print()
                print("="*60)
                print(f"[Voice] *** INPUT DETECTED ***")
                print(f"[Voice] Recognized Phrase: {last_voice_text!r}")
                print(f"[Voice] Detected Command: {cmd.name}")
                print(f"[Voice] Confidence: {confidence:.2f} {confidence_indicator}")
                print(f"[Voice] Payload Text: {text!r}")
                print("="*60)
                print()
                
                if cmd == Command.STOP:
                    print("[Voice] [STOP] Stop command received. Exiting.")
                    break
                elif cmd == Command.CALIBRATE:
                    calibrating = True
                    calibrator  = Calibrator(gaze_tracker, SCREEN_W, SCREEN_H)
                    print("[Voice] [CALIBRATE] Calibration triggered by voice command.")
                elif cmd == Command.PAUSE_TRACKING:
                    tracking_active = False
                    print("[Voice] [PAUSE] Tracking PAUSED by voice command.")
                elif cmd == Command.RESUME_TRACKING:
                    tracking_active = True
                    print("[Voice] [RESUME] Tracking RESUMED by voice command.")
                else:
                    msg = interpreter.handle_voice_command(cmd, text or "", confidence)
                    print(f"[Voice] [ACTION] {msg}")
                    action_status = msg
                    action_end    = now + 1.5

            if show_overlay:
                mode_str = "TRACKING" if tracking_active else "PAUSED"
                if calibrating:
                    step, total = calibrator.progress if calibrator else (0, 5)
                    mode_str = f"CALIBRATING ({step+1}/{total})"
                if not gaze_tracker.is_calibrated:
                    mode_str += " (uncalibrated)"

                ear_val = blink_det.ear if face_detected else 0.0
                status_line = action_status or interpreter.status_message
                listening_status = voice.is_listening if hasattr(voice, 'is_listening') else False
                draw_overlay(
                    frame,
                    face_landmarks = draw_face_landmarks if face_detected else None,
                    ear            = ear_val,
                    gaze_x         = gaze_x,
                    gaze_y         = gaze_y,
                    mode_text      = mode_str,
                    voice_text     = last_voice_text,
                    is_dragging    = cursor.is_dragging,
                    blink_type     = blink_flash_str,
                    listening      = listening_status,  # NEW: Pass listening status
                )

                if not face_detected:
                    cv2.putText(frame, "No face detected", (iw // 2 - 90, ih // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 80, 255), 2)

            if config.OVERLAY_SCALE != 1.0:
                dw = int(iw * config.OVERLAY_SCALE)
                dh = int(ih * config.OVERLAY_SCALE)
                frame = cv2.resize(frame, (dw, dh))

            if not headless:
                try:
                    cv2.imshow("Hands-Free HCI — Press Q to quit", frame)
                    key = cv2.waitKey(1) & 0xFF
                except Exception as exc:
                    print("[System] OpenCV display failed:", exc)
                    print("[System] Falling back to headless mode; press Ctrl-C to quit.")
                    headless = True
                    key = None
                    time.sleep(0.05)
            else:
                key = None
                time.sleep(0.01)

            if key in (ord("q"), ord("Q"), 27):
                break
            elif key in (ord("c"), ord("C")):
                calibrating = True
                calibrator  = Calibrator(gaze_tracker, SCREEN_W, SCREEN_H)
                print("[System] Calibration started (5 points). Follow the targets.")
            elif key in (ord("p"), ord("P")):
                tracking_active = not tracking_active
                state = "resumed" if tracking_active else "paused"
                print(f"[System] Tracking {state}.")
            elif key in (ord("r"), ord("R")):
                gaze_tracker.is_calibrated = False
                print("[System] Calibration reset.")
            elif key in (ord("d"), ord("D")):
                show_overlay = not show_overlay
                print(f"[System] Overlay {'ON' if show_overlay else 'OFF'}.")

    except KeyboardInterrupt:
        print("\n[System] Interrupted by user.")
    except Exception as exc:
        print("[System] Unhandled exception:", exc)
        traceback.print_exc()

    finally:
        print("[System] Shutting down…")
        cursor.release_drag()
        voice.stop()
        cap.release()
        cv2.destroyAllWindows()
        if hasattr(face_mesh, "close"):
            face_mesh.close()
        print("[System] Done.")


if __name__ == "__main__":
    main()
