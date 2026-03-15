import time


class Calibrator:
    """Simple calibration state machine (5 target points, progress indicator)."""

    def __init__(self, gaze_tracker, screen_w: int, screen_h: int, steps: int = 5):
        self.gaze_tracker = gaze_tracker
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.steps = max(1, steps)
        self.current = 0
        self.started = time.time()

    @property
    def current_target(self):
        if self.current >= self.steps:
            return None, None, 0.0
        tx = int(self.screen_w * (self.current + 1) / (self.steps + 1))
        ty = int(self.screen_h * 0.5)
        remaining = 0.5
        return tx, ty, remaining

    @property
    def progress(self):
        return (self.current, self.steps)

    def feed(self, landmarks, iw: int, ih: int):
        self.current += 1
        if self.current >= self.steps:
            self.gaze_tracker.is_calibrated = True
            return True
        return False
