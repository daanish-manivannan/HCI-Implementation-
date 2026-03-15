
import logging
import queue
import threading
import time
from enum import Enum, auto
from typing import Optional, Tuple

import speech_recognition as sr

import config

# Setup logging for voice recognition
logger = logging.getLogger(__name__)
_voice_handler = logging.StreamHandler()
_voice_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
))
logger.addHandler(_voice_handler)
logger.setLevel(logging.DEBUG)  # Always DEBUG to see voice input
logger.info("Voice recognition logger initialized (UTF-8 mode)")


def _diagnose_microphone():
    """Diagnose microphone availability and PyAudio setup."""
    try:
        import pyaudio
        logger.info("[OK] PyAudio is installed and importable")
    except ImportError:
        logger.warning("✗ PyAudio not installed - install with: pip install pyaudio")
        return False
    
    try:
        # Try to access PyAudio directly to check available devices
        import pyaudio
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        
        if device_count == 0:
            logger.warning("✗ No audio devices found")
            pa.terminate()
            return False
        
        logger.info("[OK] Found %d audio device(s):", device_count)
        input_device_found = False
        for i in range(device_count):
            try:
                info = pa.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    input_device_found = True
                    logger.info("  Device %d (INPUT): %s", i, info['name'])
            except:
                pass
        
        pa.terminate()
        
        if not input_device_found:
            logger.warning("✗ No input devices (microphones) found")
            return False
    except Exception as e:
        logger.warning("✗ Cannot access PyAudio devices: %s", str(e))
        return False
    
    try:
        # Try to create a microphone object
        mic = sr.Microphone()
        logger.info("[OK] Default microphone object created successfully")
        return True
    except Exception as e:
        logger.error("✗ Cannot create microphone object: %s", str(e))
        return False


class VoiceRecognizer:
    """Background continuous speech recogniser."""

    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold         = config.VOICE_ENERGY_THRESHOLD
        self._recognizer.dynamic_energy_threshold = config.VOICE_DYNAMIC_ENERGY
        self._recognizer.pause_threshold          = config.VOICE_PAUSE_THRESHOLD
        
        # CRITICAL FIX: pause_threshold must be >= non_speaking_duration
        # Set non_speaking_duration to be slightly less than pause_threshold
        self._recognizer.non_speaking_duration = config.VOICE_PAUSE_THRESHOLD * 0.8

        self._microphone: Optional[sr.Microphone] = None
        self._command_queue = queue.Queue(maxsize=32)
        self._stop_event  = threading.Event()
        self._thread: Optional[threading.Thread]  = None
        self.enabled = True
        self._microphone_test_passed = False
        self._is_listening = False  # Track if actively listening (NEW)
        self._last_listen_time = time.time()  # Track listening activity (NEW)
        
        # Run diagnostic check
        logger.info("[AUDIO] Running microphone diagnostic...")
        if _diagnose_microphone():
            self._microphone_test_passed = True
            logger.info("[OK] Microphone diagnostic passed")
        else:
            logger.warning("⚠ Microphone diagnostic failed - voice may not work")
        
        logger.info("VoiceRecognizer initialized for SYSTEM-WIDE CONTINUOUS listening (no wake word)")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        # Always-active listening (no pause mechanism)
        self._thread = threading.Thread(
            target=self._listen_loop,
            name="VoiceListenerThread", daemon=True
        )
        self._thread.start()
        logger.info("VoiceRecognizer thread started.")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3.0)
        logger.info("VoiceRecognizer stopped.")

    def _init_microphone(self) -> bool:
        """Try multiple strategies to initialize microphone."""
        # Strategy 1: Default microphone
        try:
            logger.debug("Strategy 1: Trying default microphone...")
            mic = sr.Microphone()
            with mic as source:
                logger.debug("Adjusting for ambient noise (strategy 1)...")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self._microphone = mic
            logger.info("[OK] Strategy 1 successful: Default microphone initialized")
            return True
        except Exception as e:
            logger.debug("Strategy 1 failed: %s", str(e))
        
        # Strategy 2: Try different device indices
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            device_count = pa.get_device_count()
            logger.debug("Strategy 2: Found %d audio devices, trying each...", device_count)
            
            for device_index in range(device_count):
                try:
                    info = pa.get_device_info_by_index(device_index)
                    if info['maxInputChannels'] > 0:
                        logger.debug("  Device %d: %s", device_index, info['name'])
                        mic = sr.Microphone(device_index=device_index)
                        with mic as source:
                            logger.debug("  Adjusting noise for device %d...", device_index)
                            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        self._microphone = mic
                        logger.info("[OK] Strategy 2 successful: Microphone initialized with device %d: %s", device_index, info['name'])
                        return True
                except Exception as inner_e:
                    logger.debug("  Device %d failed: %s", device_index, str(inner_e))
                    continue
            pa.terminate()
        except Exception as e:
            logger.debug("Strategy 2 failed: %s", str(e))
        
        logger.error("✗ All microphone initialization strategies failed")
        return False

    def pause(self):
        """Note: System-wide listening always active. This method is deprecated but kept for compatibility."""
        logger.debug("Voice.pause() called - voice continues listening (always active system-wide)")

    def resume(self):
        """Note: System-wide listening always active. This method is deprecated but kept for compatibility."""
        logger.debug("Voice.resume() called - voice was never paused")

    def get_phrase(self) -> Optional[str]:
        """Non-blocking: return next recognised phrase or None."""
        try:
            phrase = self._command_queue.get_nowait()
            logger.info("[QUEUE] PHRASE FROM QUEUE: '%s'", phrase[:100])
            return phrase
        except queue.Empty:
            return None

    @property
    def is_listening(self) -> bool:
        """Return True if actively listening for voice."""
        return self._is_listening
    
    def _update_listening_state(self):
        """Update listening state based on timeout."""
        now = time.time()
        listening_timeout = getattr(config, 'VOICE_LISTENING_TIMEOUT', 120.0)
        if now - self._last_listen_time > listening_timeout:
            self._is_listening = False

    def _listen_loop(self):
        """
        Continuous listening loop for system-wide voice interaction.
        NO WAKE WORD mechanism - always listening and responding.
        Auto-recovery from microphone errors.
        """
        mic_init_attempts = 0
        max_init_attempts = 3
        
        while not self._stop_event.is_set():
            # Initialize/reinitialize microphone with retries
            if self._microphone is None:
                if mic_init_attempts >= max_init_attempts:
                    logger.error("Failed to initialize microphone after %d attempts.", max_init_attempts)
                    logger.error("[MIC] TROUBLESHOOTING:")
                    logger.error("  1. Check if PyAudio is installed: pip install pyaudio")
                    logger.error("  2. Check if headset/microphone is connected and enabled")
                    logger.error("  3. Check Windows Settings > Privacy > Microphone (enable microphone access)")
                    logger.error("  4. Check if another app is using the microphone")
                    logger.error("  Retrying in 10 seconds...")
                    self.enabled = False
                    time.sleep(10.0)
                    mic_init_attempts = 0
                    continue
                    
                logger.info("[AUDIO] Microphone init attempt %d/%d...", mic_init_attempts + 1, max_init_attempts)
                if self._init_microphone():
                    mic_init_attempts = 0  # Reset counter on success
                else:
                    mic_init_attempts += 1
                    time.sleep(2.0)
                    continue
            
            # Skip if not enabled (but auto-recover)
            if not self.enabled:
                logger.debug("Voice waiting to recover... (will retry in 1s)")
                time.sleep(1.0)
                self.enabled = True  # Auto-enable for recovery
                continue
            
            # Continuous listening loop (system-wide, always active)
            try:
                # Mark as listening
                self._is_listening = True
                self._last_listen_time = time.time()
                
                with self._microphone as source:
                    try:
                        # Listen continuously - no minimum silence requirement
                        logger.debug("[MIC] Listening for voice commands (system-wide)...")
                        audio = self._recognizer.listen(
                            source,
                            timeout=config.VOICE_TIMEOUT,  # Max wait between words
                            phrase_time_limit=config.VOICE_PHRASE_TIME_LIMIT,  # Max phrase length
                        )
                        # Successfully captured audio
                        mic_init_attempts = 0
                        self._is_listening = True
                        self._last_listen_time = time.time()
                    except sr.WaitTimeoutError:
                        # Normal: waiting for speech to start
                        logger.debug("[MIC] Listening... (no speech yet)")
                        self._is_listening = True
                        self._last_listen_time = time.time()
                        continue
                    except sr.RequestError as exc:
                        logger.warning("[MIC] Microphone request error: %s. Will retry...", exc)
                        self._is_listening = False
                        time.sleep(1.0)
                        continue
                
                # Process recognized phrase
                phrase = self._recognise(audio)
                if phrase:
                    logger.info("[AUDIO] VOICE HEARD: '%s'", phrase[:100])
                    self._is_listening = True
                    self._last_listen_time = time.time()
                    try:
                        self._command_queue.put_nowait(phrase)
                    except queue.Full:
                        # Queue is full - drop oldest command to make room
                        logger.warning("[MIC] Voice queue full - removing oldest command")
                        try:
                            self._command_queue.get_nowait()  # Drop oldest
                            self._command_queue.put_nowait(phrase)  # Add new
                            logger.info("[AUDIO] Queue recovered, new command queued")
                        except:
                            pass
                else:
                    logger.debug("[MIC] Speech detected but not recognized")
                    self._is_listening = True
                    self._last_listen_time = time.time()
                    
            except OSError as exc:
                logger.warning("[MIC] Microphone error: %s. Recovering...", exc)
                self._microphone = None  # Force reinitialization
                self._is_listening = False
                time.sleep(1.0)
            except Exception as exc:
                logger.exception("[MIC] Unexpected error: %s", exc)
                self._is_listening = False
                time.sleep(1.0)

    def _recognise(self, audio: sr.AudioData) -> Optional[str]:
        try:
            return self._recognizer.recognize_google(
                audio, language=config.VOICE_LANGUAGE
            ).lower().strip()
        except sr.UnknownValueError:
            pass  # Speech detected but not understood — normal
        except sr.RequestError as exc:
            logger.warning("Google SR unavailable (no internet?): %s", exc)

        # Sphinx offline fallback — only if installed
        try:
            return self._recognizer.recognize_sphinx(audio).lower().strip()
        except sr.UnknownValueError:
            pass
        except ImportError:
            pass  # pocketsphinx not installed — skip silently
        except Exception as exc:
            logger.debug("Sphinx fallback error: %s", exc)

        return None


class Command(Enum):
    # Existing commands
    STOP = auto()
    CALIBRATE = auto()
    PAUSE_TRACKING = auto()
    RESUME_TRACKING = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()
    GO_BACK = auto()
    GO_FORWARD = auto()
    CLICK = auto()
    RIGHT_CLICK = auto()
    DOUBLE_CLICK = auto()
    COPY = auto()
    PASTE = auto()
    UNDO = auto()
    REDO = auto()
    SELECT_ALL = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    ZOOM_RESET = auto()
    OPEN_BROWSER = auto()
    CLOSE_WINDOW = auto()
    NEW_TAB = auto()
    CLOSE_TAB = auto()
    SWITCH_TAB = auto()
    TAKE_SCREENSHOT = auto()
    TYPE_TEXT = auto()
    
    # Windows system commands
    OPEN_APP = auto()
    OPEN_FOLDER = auto()
    OPEN_WEBSITE = auto()
    MINIMIZE_ALL = auto()
    TOGGLE_DARK_MODE = auto()
    LOCK_SCREEN = auto()
    OPEN_SETTINGS = auto()
    OPEN_CALCULATOR = auto()
    REFRESH_SCREEN = auto()
    
    # Code generation commands
    GENERATE_CODE = auto()
    EXECUTE_CODE = auto()
    OPEN_CODE_IN_EDITOR = auto()


VOICE_COMMAND_MAP = {
    # System control
    "stop": Command.STOP,
    "quit": Command.STOP,
    "exit": Command.STOP,
    "calibrate": Command.CALIBRATE,
    "calibration": Command.CALIBRATE,
    "pause": Command.PAUSE_TRACKING,
    "pause tracking": Command.PAUSE_TRACKING,
    "resume": Command.RESUME_TRACKING,
    "resume tracking": Command.RESUME_TRACKING,

    # Mouse / click
    "click": Command.CLICK,
    "right click": Command.RIGHT_CLICK,
    "double click": Command.DOUBLE_CLICK,

    # Navigation
    "scroll up": Command.SCROLL_UP,
    "scroll down": Command.SCROLL_DOWN,
    "go back": Command.GO_BACK,
    "go forward": Command.GO_FORWARD,
    "back": Command.GO_BACK,         # shorthand alias
    "forward": Command.GO_FORWARD,   # shorthand alias

    # Editing
    "copy": Command.COPY,
    "paste": Command.PASTE,
    "undo": Command.UNDO,
    "redo": Command.REDO,
    "select all": Command.SELECT_ALL,
    "select": Command.SELECT_ALL,    # shorthand alias

    # Zoom
    "zoom in": Command.ZOOM_IN,
    "zoom out": Command.ZOOM_OUT,
    "zoom reset": Command.ZOOM_RESET,
    "reset zoom": Command.ZOOM_RESET,

    # Browser / tabs
    "open browser": Command.OPEN_BROWSER,
    "browser": Command.OPEN_BROWSER,        # shorthand alias
    "new tab": Command.NEW_TAB,
    "close tab": Command.CLOSE_TAB,
    "switch tab": Command.SWITCH_TAB,
    "close window": Command.CLOSE_WINDOW,

    # Screenshot
    "take screenshot": Command.TAKE_SCREENSHOT,
    "screenshot": Command.TAKE_SCREENSHOT,   # shorthand alias

    # Windows system
    "minimize all": Command.MINIMIZE_ALL,
    "minimize windows": Command.MINIMIZE_ALL,
    "show desktop": Command.MINIMIZE_ALL,
    "toggle dark mode": Command.TOGGLE_DARK_MODE,
    "dark mode": Command.TOGGLE_DARK_MODE,
    "light mode": Command.TOGGLE_DARK_MODE,
    "lock screen": Command.LOCK_SCREEN,
    "lock": Command.LOCK_SCREEN,
    "open settings": Command.OPEN_SETTINGS,
    "settings": Command.OPEN_SETTINGS,
    "open calculator": Command.OPEN_CALCULATOR,
    "calculator": Command.OPEN_CALCULATOR,
    "refresh": Command.REFRESH_SCREEN,
    "refresh screen": Command.REFRESH_SCREEN,

    # Code generation
    "generate code": Command.GENERATE_CODE,
    "execute code": Command.EXECUTE_CODE,
    "open code in editor": Command.OPEN_CODE_IN_EDITOR,
}


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def _fuzzy_match(phrase: str, reference: str, max_distance: int = 2) -> Tuple[bool, float]:
    """
    Fuzzy match phrase against reference.
    Returns (is_match, confidence) where confidence is 0.0-1.0
    """
    distance = _levenshtein_distance(phrase, reference)
    if distance <= max_distance:
        confidence = 1.0 - (distance / max(len(phrase), len(reference), 1))
        return True, confidence
    return False, 0.0


def phrase_to_command(phrase: str) -> Tuple[Optional[Command], str, float]:
    """
    Convert voice phrase to Command enum and payload.
    Returns (Command, payload_text, confidence_score)
    
    Supports parameterized commands:
      - "open [app]" -> OPEN_APP with app name as payload
      - "generate [code] in [language]" -> GENERATE_CODE with code description
      - "open [website]" -> OPEN_WEBSITE with URL as payload
      - "open folder [path]" -> OPEN_FOLDER with path as payload
    """
    if not phrase:
        return None, "", 0.0
    
    logger.info("[PHRASE_TO_COMMAND] INPUT: '%s'", phrase)
    
    phrase = phrase.strip().lower()
    
    # Check for TYPE_TEXT command (highest priority)
    if phrase.startswith("type "):
        text = phrase[5:].strip()
        logger.info("Voice: TYPE_TEXT with payload='%s'", text[:50])
        return Command.TYPE_TEXT, text, 1.0
    
    # Check for "select [something]" - handle as SELECT or SELECT_ALL
    if phrase.startswith("select "):
        remaining = phrase[7:].strip()
        if remaining in ["all", "everything", "text"]:
            logger.info("Voice: SELECT_ALL detected from phrase '%s'", phrase)
            return Command.SELECT_ALL, "", 0.90
        elif "open" in remaining or any(app in remaining for app in ["chrome", "firefox", "edge", "notepad", "calculator", "settings"]):
            # Phrase like "select the text open chrome" - extract the "open" part
            open_idx = remaining.find("open")
            if open_idx != -1:
                app_name = remaining[open_idx+5:].strip()
                if app_name:
                    logger.info("Voice: Extracted OPEN_APP from compound phrase, app='%s'", app_name)
                    return Command.OPEN_APP, app_name, 0.85
    
    # Check for OPEN_APP command: "open [app]"
    if phrase.startswith("open ") and not any(x in phrase for x in ["folder", "settings", "calculator", "browser", "website"]):
        app_name = phrase[5:].strip()
        if app_name:
            logger.info("Voice: OPEN_APP with payload='%s'", app_name)
            return Command.OPEN_APP, app_name, 0.95
    
    # Check for OPEN_WEBSITE command: "open [website]"
    if phrase.startswith("open website ") or phrase.startswith("browse "):
        if phrase.startswith("open website "):
            url = phrase[13:].strip()
        else:
            url = phrase[7:].strip()
        if url:
            logger.info("Voice: OPEN_WEBSITE with payload='%s'", url)
            return Command.OPEN_WEBSITE, url, 0.95
    
    # Check for OPEN_FOLDER command: "open folder [path]"
    if phrase.startswith("open folder "):
        folder_path = phrase[12:].strip()
        if folder_path:
            logger.info("Voice: OPEN_FOLDER with payload='%s'", folder_path)
            return Command.OPEN_FOLDER, folder_path, 0.95
    
    # Check for GENERATE_CODE command: "generate [code] in [language]" or "generate [code]"
    if phrase.startswith("generate "):
        code_request = phrase[9:].strip()
        if code_request:
            logger.info("Voice: GENERATE_CODE with payload='%s'", code_request)
            return Command.GENERATE_CODE, code_request, 0.95
    
    # Check for EXECUTE_CODE command: "execute [code description]"
    if phrase.startswith("execute "):
        code_desc = phrase[8:].strip()
        if code_desc:
            logger.info("Voice: EXECUTE_CODE with payload='%s'", code_desc)
            return Command.EXECUTE_CODE, code_desc, 0.95
    
    # Exact match (highest confidence)
    if phrase in VOICE_COMMAND_MAP:
        cmd = VOICE_COMMAND_MAP[phrase]
        logger.info("Voice: Exact match for '%s' -> %s", phrase, cmd.name)
        return cmd, phrase, 1.0
    
    # Prefix matching (medium-high confidence)
    for key in sorted(VOICE_COMMAND_MAP.keys(), key=len, reverse=True):
        if phrase.startswith(key):
            cmd = VOICE_COMMAND_MAP[key]
            confidence = min(1.0, len(key) / len(phrase))
            logger.info("Voice: Prefix match '%s' in '%s' -> %s (conf=%.2f)", 
                       key, phrase, cmd.name, confidence)
            return cmd, phrase, confidence
    
    # Substring matching (medium confidence)
    matches = []
    for key, cmd in VOICE_COMMAND_MAP.items():
        if key in phrase:
            confidence = len(key) / len(phrase)
            matches.append((confidence, key, cmd))
    
    if matches:
        matches.sort(reverse=True)
        confidence, key, cmd = matches[0]
        logger.info("Voice: Substring match '%s' in '%s' -> %s (conf=%.2f)", 
                   key, phrase, cmd.name, confidence)
        return cmd, phrase, confidence
    
    # Fuzzy matching (if enabled in config)
    if getattr(config, 'VOICE_ENABLE_FUZZY_MATCHING', True):
        best_match = None
        best_confidence = 0.0
        
        for key, cmd in VOICE_COMMAND_MAP.items():
            is_match, confidence = _fuzzy_match(phrase, key)
            if is_match and confidence > best_confidence:
                best_match = (cmd, key)
                best_confidence = confidence
        
        min_confidence = getattr(config, 'VOICE_MATCH_CONFIDENCE_THRESHOLD', 0.65)
        if best_match and best_confidence >= min_confidence:
            cmd, matched_key = best_match
            logger.info("Voice: Fuzzy match '%s' -> '%s' -> %s (conf=%.2f)", 
                       phrase, matched_key, cmd.name, best_confidence)
            return cmd, phrase, best_confidence
    
    # Keyword-based fallback matching (look for single keyword in phrase)
    words = phrase.split()
    for word in words:
        if word in VOICE_COMMAND_MAP:
            cmd = VOICE_COMMAND_MAP[word]
            confidence = 0.70
            logger.info("Voice: Keyword match '%s' found in phrase '%s' -> %s (conf=%.2f)", 
                       word, phrase, cmd.name, confidence)
            return cmd, phrase, confidence
    
    logger.warning("Voice: [NO-MATCH] for phrase '%s'", phrase[:50])
    return None, phrase, 0.0


class VoiceHandler:
    def __init__(self):
        self._recognizer = VoiceRecognizer()
        self.last_command = None
        self.last_confidence = 0.0

    def start(self):
        logger.info("VoiceHandler: Starting voice recognition")
        self._recognizer.start()

    def stop(self):
        logger.info("VoiceHandler: Stopping voice recognition")
        self._recognizer.stop()

    def get_command(self) -> Tuple[Optional[Command], str, float]:
        """
        Get next voice command.
        Returns (Command, payload_text, confidence_score)
        Confidence ranges from 0.0 (no match) to 1.0 (exact match)
        """
        phrase = self._recognizer.get_phrase()
        if not phrase:
            return None, None, 0.0

        cmd, payload, confidence = phrase_to_command(phrase)
        self.last_command = cmd
        self.last_confidence = confidence
        return cmd, payload, confidence

    @property
    def is_listening(self) -> bool:
        """Return True if currently listening for voice."""
        return self._recognizer.is_listening if hasattr(self._recognizer, 'is_listening') else False


def match_command(phrase: str, command_map: dict) -> Optional[str]:
    """Return best-matching action token for phrase, or None."""
    if not phrase:
        return None
    phrase = phrase.strip().lower()

    if phrase in command_map:
        return command_map[phrase]

    candidates = [(k, v) for k, v in command_map.items()
                  if phrase.startswith(k)]
    if candidates:
        return max(candidates, key=lambda kv: len(kv[0]))[1]

    candidates = [(k, v) for k, v in command_map.items() if k in phrase]
    if candidates:
        return max(candidates, key=lambda kv: len(kv[0]))[1]

    if phrase.startswith("type "):
        text = phrase[5:].strip()
        if text:
            return f"TYPE:{text}"

    return None
