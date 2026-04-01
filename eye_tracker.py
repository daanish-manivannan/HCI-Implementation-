"""
eye_tracker.py — Webcam capture + MediaPipe face-mesh processing.

Provides a clean iterator interface over webcam frames with pre-computed
face landmarks, EAR values, and gaze ratios.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Iterator, Optional, Tuple

import cv2
import numpy as np
import mediapipe as mp

import config
from utils import eye_aspect_ratio

logger = logging.getLogger(__name__)

# MediaPipe 468+ iris and eyelid landmarks
LEFT_EYE_OUTLINE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_OUTLINE = [33, 160, 158, 133, 153, 144]


@dataclass
class GazeResult:
    landmarks_px: list
    left_iris_px: tuple
    right_iris_px: tuple
    gaze_offset: tuple


@dataclass
class FrameData:
    """All computed data for a single webcam frame."""
    frame: np.ndarray                          # BGR image (for display)
    face_detected: bool      = False
    landmarks: object        = None            # mediapipe NormalizedLandmarkList

    # EAR
    left_ear: float          = 0.0
    right_ear: float         = 0.0
    avg_ear: float           = 0.0

    # Smoothed screen gaze position
    gaze_screen: Optional[Tuple[int, int]] = None

    # Timing
    fps: float               = 0.0
    timestamp: float         = field(default_factory=time.time)


class EyeTracker:
    """
    Opens the webcam and yields :class:`FrameData` objects on each call
    to :meth:`read`.

    Usage::

        with EyeTracker() as tracker:
            for data in tracker:
                process(data)
    """

    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self._face_mesh = None
        self._mp_drawing = None
        self._mp_drawing_styles = None
        self._mp_face_mesh = None
        self._prev_time: float = time.time()
        self.frame_count: int = 0

    # ------------------------------------------------------------------ #
    # Context manager
    # ------------------------------------------------------------------ #

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, *_):
        self.release()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def open(self):
        self._open()

    def release(self):
        if self._cap and self._cap.isOpened():
            self._cap.release()
        if self._face_mesh:
            self._face_mesh.close()
        logger.info("EyeTracker released.")

    def read(self) -> Optional[FrameData]:
        """
        Capture one frame, run face-mesh inference, return FrameData.
        Returns None if capture fails.
        """
        if not self._cap or not self._cap.isOpened():
            return None

        ok, frame = self._cap.read()
        if not ok:
            logger.warning("Frame capture failed.")
            return None

        self.frame_count += 1
        frame = cv2.flip(frame, 1)   # mirror for natural interaction

        # ── FPS ─────────────────────────────────────────────────────────
        now  = time.time()
        fps  = 1.0 / max(now - self._prev_time, 1e-6)
        self._prev_time = now

        data = FrameData(frame=frame, fps=fps, timestamp=now)

        # ── MediaPipe inference ──────────────────────────────────────────
        h, w = frame.shape[:2]
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return data   # no face found

        face_lm = results.multi_face_landmarks[0]
        data.face_detected = True
        data.landmarks     = face_lm

        # ── EAR ─────────────────────────────────────────────────────────
        data.left_ear  = eye_aspect_ratio(face_lm, config.LEFT_EYE_EAR,  w, h)
        data.right_ear = eye_aspect_ratio(face_lm, config.RIGHT_EYE_EAR, w, h)
        data.avg_ear   = (data.left_ear + data.right_ear) / 2.0

        return data

    def __iter__(self) -> Iterator[FrameData]:
        """Yield FrameData objects indefinitely until capture fails."""
        while True:
            data = self.read()
            if data is None:
                break
            yield data

    # ------------------------------------------------------------------ #
    # Private
    # ------------------------------------------------------------------ #

    def _open(self):
        self._mp_face_mesh      = mp.solutions.face_mesh
        self._mp_drawing        = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles

        self._face_mesh = self._mp_face_mesh.FaceMesh(
            max_num_faces           = config.MAX_NUM_FACES,
            refine_landmarks        = config.REFINE_LANDMARKS,
            min_detection_confidence= config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence = config.MIN_TRACKING_CONFIDENCE,
        )

        self._cap = cv2.VideoCapture(config.WEBCAM_INDEX)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS, 30)

        if not self._cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera index {config.WEBCAM_INDEX}. "
                "Check the WEBCAM_INDEX setting in config.py."
            )
        logger.info("Camera %d opened (%dx%d).",
                    config.WEBCAM_INDEX, config.FRAME_WIDTH, config.FRAME_HEIGHT)

    # ─────────────────────────────────────────────────────────────────── #
    # Debug overlay helpers (called from main.py)
    # ─────────────────────────────────────────────────────────────────── #

    def draw_landmarks(self, frame: np.ndarray, landmarks):
        """Draw the full face mesh on *frame* in-place."""
        self._mp_drawing.draw_landmarks(
            image                  = frame,
            landmark_list          = landmarks,
            connections            = self._mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec  = None,
            connection_drawing_spec= self._mp_drawing_styles
                                         .get_default_face_mesh_tesselation_style(),
        )
        # Draw iris contours
        self._mp_drawing.draw_landmarks(
            image                  = frame,
            landmark_list          = landmarks,
            connections            = self._mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec  = None,
            connection_drawing_spec= self._mp_drawing_styles
                                         .get_default_face_mesh_iris_connections_style(),
        )
