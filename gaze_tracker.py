import config
import numpy as np
import cv2


class KalmanFilter2D:
    def __init__(self):
        # 4 state variables: x, y, dx, dy
        self.state = np.zeros(4, dtype=np.float32)
        # State transition matrix (assuming constant velocity, dt=1)
        self.F = np.array([[1, 0, 1, 0],
                           [0, 1, 0, 1],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]], dtype=np.float32)
        # Measurement matrix (we only measure x and y)
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]], dtype=np.float32)
        # Covariance matrix
        self.P = np.eye(4, dtype=np.float32) * 1000
        
        # INCREASE R for more smoothing (trust measurement less)
        # DECREASE Q for more smoothing (trust prediction more)
        smoothing = getattr(config, 'CURSOR_SMOOTHING', 0.12)
        measurement_noise = max(0.01, 1.0 - smoothing) * 10.0
        
        self.R = np.array([[measurement_noise, 0],
                           [0, measurement_noise]], dtype=np.float32)
        self.Q = np.eye(4, dtype=np.float32) * (smoothing * 0.1)
        
        self.is_initialized = False

    def update(self, z):
        z = np.array(z, dtype=np.float32)
        
        smoothing = getattr(config, 'CURSOR_SMOOTHING', 0.12)
        measurement_noise = max(0.01, 1.0 - smoothing) * 10.0
        self.R[0,0] = measurement_noise
        self.R[1,1] = measurement_noise
        np.fill_diagonal(self.Q, smoothing * 0.1)
        
        if not self.is_initialized:
            self.state[0] = z[0]
            self.state[1] = z[1]
            self.is_initialized = True
            return self.state[0], self.state[1]

        # Predict
        self.state = np.dot(self.F, self.state)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

        # Update
        y = z - np.dot(self.H, self.state)
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        self.state = self.state + np.dot(K, y)
        self.P = self.P - np.dot(np.dot(K, self.H), self.P)

        return self.state[0], self.state[1]


class GazeTracker:
    """Hybrid Head-Pose + Gaze tracker with Kalman Smoothing."""

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.is_calibrated = False
        self.kalman = KalmanFilter2D()
        
        # Standard 3D face model points
        # Nose, Chin, R-Eye-R-Corner, L-Eye-L-Corner, R-Mouth, L-Mouth
        self.face3Dmodel = np.array([
            [0.0, 0.0, 0.0],             # Nose tip
            [0.0, -330.0, -65.0],        # Chin
            [-225.0, 170.0, -135.0],     # Right eye right corner (user's right)
            [225.0, 170.0, -135.0],      # Left eye left corner (user's left)
            [-150.0, -150.0, -125.0],    # Right Mouth corner
            [150.0, -150.0, -125.0]      # Left Mouth corner
        ], dtype=np.float64)
        
        # Tuning parameters for head mapping
        self.yaw_amplification = 1.8
        self.pitch_amplification = 2.0

    def get_screen_coords(self, landmarks, iw: int, ih: int):
        if landmarks is None:
            return self.screen_w // 2, self.screen_h // 2

        try:
            # 1. ── Extract 2D image points for head pose estimation ──
            # MediaPipe indices: Nose=1, Chin=152, R-Eye-R=33, L-Eye-L=263, R-Mouth=61, L-Mouth=291
            image_points = np.array([
                [landmarks[1].x * iw, landmarks[1].y * ih],
                [landmarks[152].x * iw, landmarks[152].y * ih],
                [landmarks[33].x * iw, landmarks[33].y * ih],
                [landmarks[263].x * iw, landmarks[263].y * ih],
                [landmarks[61].x * iw, landmarks[61].y * ih],
                [landmarks[291].x * iw, landmarks[291].y * ih]
            ], dtype=np.float64)

            # Camera internals (assume standard focal length)
            focal_length = iw
            center = (iw / 2, ih / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]], dtype=np.float64)
            dist_coeffs = np.zeros((4, 1)) # Assume no lens distortion
            
            # Solve PnP
            success, rvec, tvec = cv2.solvePnP(self.face3Dmodel, image_points, camera_matrix, dist_coeffs)
            
            # Convert rotation vector to euler angles
            rmat, _ = cv2.Rodrigues(rvec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            
            # Angles in degrees
            pitch = angles[0]   # Up/Down
            yaw = angles[1]     # Left/Right
            # roll = angles[2]

            # 2. ── Map Head Pose to Screen Coordinates (Macro Movement) ──
            # Center of the screen is [yaw=0, pitch=0]
            # Normalize yaw and pitch assuming roughly ±20 degrees is the edge of the screen
            yaw_normalized = (yaw * self.yaw_amplification) / 20.0
            pitch_normalized = (pitch * self.pitch_amplification) / 15.0
            
            # Note: yaw directions might be inverted depending on mirroring
            macro_x = ((yaw_normalized + 1.0) / 2.0) * self.screen_w
            macro_y = ((pitch_normalized + 1.0) / 2.0) * self.screen_h

            # 3. ── Extract Iris Offset for Micro-Movement ──
            left_iris = landmarks[config.LEFT_IRIS_CENTER]
            left_eye_l = landmarks[config.LEFT_EYE_LEFT_CORNER]
            left_eye_r = landmarks[config.LEFT_EYE_RIGHT_CORNER]
            
            # Horizontal relative position of iris within the eye socket (0.0 to 1.0)
            eye_width = abs(left_eye_r.x - left_eye_l.x)
            if eye_width > 0:
                iris_offset_ratio = (left_iris.x - left_eye_l.x) / eye_width - 0.5
            else:
                iris_offset_ratio = 0.0

            # Map iris offset to pixels (e.g. max ±200 pixels)
            micro_x = iris_offset_ratio * getattr(config, 'GAZE_SENSITIVITY_X', 8.0) * 100
            
            # 4. ── Combine Macro and Micro ──
            raw_screen_x = macro_x + micro_x
            raw_screen_y = macro_y # Pitch handles Y mostly
            
            # Apply Kalman Filter to smooth the result
            filtered_x, filtered_y = self.kalman.update([raw_screen_x, raw_screen_y])

            # Bound strictly to the monitor boundaries
            screen_x = int(np.clip(filtered_x, 0, self.screen_w - 1))
            screen_y = int(np.clip(filtered_y, 0, self.screen_h - 1))

            self.is_calibrated = True
            return screen_x, screen_y
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self.screen_w // 2, self.screen_h // 2
