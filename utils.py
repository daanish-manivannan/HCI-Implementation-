import numpy as np
from scipy.spatial.distance import euclidean


def eye_aspect_ratio(landmarks, indices, iw: int, ih: int) -> float:
    pts = []
    for idx in indices:
        lm = landmarks[idx]
        pts.append((lm.x * iw, lm.y * ih))
    if len(pts) < 6:
        return 0.0
    A = euclidean(pts[1], pts[5])
    B = euclidean(pts[2], pts[4])
    C = euclidean(pts[0], pts[3])
    return (A + B) / (2.0 * C) if C > 0 else 0.0
