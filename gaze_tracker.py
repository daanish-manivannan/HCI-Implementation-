import config


class GazeTracker:
    """Simple gaze-to-screen coordinate converter based on iris landmarks."""

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.is_calibrated = False

    def get_screen_coords(self, landmarks, iw: int, ih: int):
        if landmarks is None:
            return self.screen_w // 2, self.screen_h // 2

        try:
            left_iris = landmarks[config.LEFT_IRIS_CENTER]
            right_iris = landmarks[config.RIGHT_IRIS_CENTER]

            x = (left_iris.x + right_iris.x) / 2.0
            y = (left_iris.y + right_iris.y) / 2.0

            screen_x = int(min(max(0, x * self.screen_w), self.screen_w - 1))
            screen_y = int(min(max(0, y * self.screen_h), self.screen_h - 1))

            self.is_calibrated = True
            return screen_x, screen_y
        except Exception:
            return self.screen_w // 2, self.screen_h // 2
