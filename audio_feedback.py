"""
audio_feedback.py
─────────────────
Provides a non-blocking Text-to-Speech (TTS) manager using pyttsx3.
Runs the TTS engine in a background thread to prevent GUI/camera stuttering.
"""

import threading
import queue
import pyttsx3
import logging

logger = logging.getLogger(__name__)

class TTSManager:
    def __init__(self):
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        logger.info("TTSManager background thread started.")

    def _worker(self):
        # Initialize pyttsx3 inside the thread to avoid COM/threading issues
        try:
            self.engine = pyttsx3.init()
            # Optional: configure voice properties
            self.engine.setProperty('rate', 170)  # Speed of speech
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            return

        while not self._stop_event.is_set():
            try:
                # Wait for text to speak
                text = self._queue.get(timeout=0.1)
                if text is None:  # Shutdown signal
                    break
                
                logger.debug(f"[TTS] Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTS Engine error: {e}")

    def speak(self, text: str):
        """Queue text to be spoken asynchronously."""
        if text:
            self._queue.put(text)

    def stop(self):
        """Signal the thread to shut down nicely."""
        self._stop_event.set()
        # Wake up the queue if waiting
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass

# Global Singleton access
_instance = TTSManager()

def speak(text: str):
    """Utility to queue text globally."""
    _instance.speak(text)

def stop():
    """Utility to clean up TTS thread."""
    _instance.stop()
