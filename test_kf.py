import numpy as np
from gaze_tracker import KalmanFilter2D
import time

kf = KalmanFilter2D()

# Test with a steady input of (960, 540)
for i in range(10):
    x, y = kf.update([960, 540])
    print(f"Update {i}: x={x:.2f}, y={y:.2f}")

# Now jump to (1200, 600)
for i in range(10):
    x, y = kf.update([1200, 600])
    print(f"Update {i+10}: x={x:.2f}, y={y:.2f}")
