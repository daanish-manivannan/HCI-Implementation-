import config


def _remap(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Linearly remap *value* from [in_min..in_max] → [out_min..out_max], clamped."""
    if in_max == in_min:
        return (out_min + out_max) / 2.0
    t = (value - in_min) / (in_max - in_min)
    t = max(0.0, min(1.0, t))          # clamp to [0, 1]
    return out_min + t * (out_max - out_min)


class GazeTracker:
    """
    Gaze-to-screen coordinate converter based on iris landmarks.

    Instead of a raw 1:1 mapping, the iris position is remapped from the
    "comfortable movement window" defined by HEAD_RANGE_MIN/MAX in config.py
    to the full screen extent.  This means small, natural head movements
    are enough to reach any screen edge.

    Tune HEAD_RANGE_MIN_X / HEAD_RANGE_MAX_X (and Y equivalents) in
    config.py to adjust sensitivity:
        • Smaller range  →  more sensitive  (less head movement required)
        • Larger range   →  less sensitive  (more head movement required)
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.is_calibrated = False

    def get_screen_coords(self, landmarks, iw: int, ih: int):
        if landmarks is None:
            return self.screen_w // 2, self.screen_h // 2

        try:
            left_iris  = landmarks[config.LEFT_IRIS_CENTER]
            right_iris = landmarks[config.RIGHT_IRIS_CENTER]

            # Average of both iris centres (normalised 0–1 in webcam frame)
            raw_x = (left_iris.x + right_iris.x) / 2.0
            raw_y = (left_iris.y + right_iris.y) / 2.0

            # Remap comfortable head-pose range → full screen
            screen_x = _remap(
                raw_x,
                config.HEAD_RANGE_MIN_X, config.HEAD_RANGE_MAX_X,
                0.0, float(self.screen_w - 1),
            )
            screen_y = _remap(
                raw_y,
                config.HEAD_RANGE_MIN_Y, config.HEAD_RANGE_MAX_Y,
                0.0, float(self.screen_h - 1),
            )

            self.is_calibrated = True
            return int(screen_x), int(screen_y)
        except Exception:
            return self.screen_w // 2, self.screen_h // 2
