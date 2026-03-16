"""
blink_detector.py
Detection of single, double, and long blinks via Eye Aspect Ratio (EAR).

EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
"""

import time
import numpy as np
from scipy.spatial.distance import euclidean
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import (
    LEFT_EYE_EAR, RIGHT_EYE_EAR,
    EAR_CONSEC_FRAMES,
    DOUBLE_BLINK_INTERVAL, LONG_BLINK_FRAMES,
)
import config


def _ear(landmarks, indices, iw: int, ih: int) -> float:
    pts = []
    for idx in indices:
        lm = landmarks[idx]
        pts.append((lm.x * iw, lm.y * ih))
    A = euclidean(pts[1], pts[5])
    B = euclidean(pts[2], pts[4])
    C = euclidean(pts[0], pts[3])
    return (A + B) / (2.0 * C) if C > 0 else 0.0


class BlinkDetector:
    def __init__(self):
        self._closed_frames = 0
        self._blink_times = []
        self._long_blink_active = False
        self.single_blink = False
        self.double_blink = False
        self.long_blink = False
        self.ear = 0.0

    def update(self, landmarks, iw: int, ih: int) -> None:
        self.single_blink = False
        self.double_blink = False
        self.long_blink = False
        left_ear  = _ear(landmarks, LEFT_EYE_EAR,  iw, ih)
        right_ear = _ear(landmarks, RIGHT_EYE_EAR, iw, ih)
        self.ear = (left_ear + right_ear) / 2.0
        if self.ear < config.EAR_BLINK_THRESHOLD:
            self._closed_frames += 1
            if self._closed_frames >= LONG_BLINK_FRAMES:
                self.long_blink = True
                self._long_blink_active = True
        else:
            if self._closed_frames >= EAR_CONSEC_FRAMES and not self._long_blink_active:
                self._register_blink()
            self._closed_frames = 0
            self._long_blink_active = False

    def _register_blink(self) -> None:
        now = time.time()
        self._blink_times = [t for t in self._blink_times if now - t <= DOUBLE_BLINK_INTERVAL]
        self._blink_times.append(now)
        if len(self._blink_times) >= 2:
            self.double_blink = True
            self._blink_times.clear()
        else:
            self.single_blink = True
