import cv2
import threading
import time

class VideoCaptureThread:
    """
    Runs webcam capture in a dedicated background thread.
    This prevents the main loop from blocking on I/O (cap.read()),
    often resulting in a massive FPS and smoothness boost.
    """
    def __init__(self, src=0, width=640, height=480, fps=30):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {src}.")

        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()
        self.new_frame_event = threading.Event()
        
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            # If camera fails, try short sleep, but don't crash thread immediately
            if not ret:
                time.sleep(0.01)
                continue
                
            with self.lock:
                self.ret = ret
                self.frame = frame
            self.new_frame_event.set()

    def read(self):
        self.new_frame_event.wait(timeout=0.1)
        self.new_frame_event.clear()
        
        with self.lock:
            if self.frame is not None:
                return self.ret, self.frame.copy()
            return self.ret, None

    def release(self):
        self.stopped = True
        self.thread.join(timeout=1.0)
        self.cap.release()
