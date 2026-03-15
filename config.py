"""
config.py — Central configuration for Hands-Free HCI System
"""

# ─── Screen & Camera ────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1920   # updated at runtime via pyautogui.size()
SCREEN_HEIGHT = 1080
WEBCAM_INDEX  = 0      # 0 = default webcam
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480

# ─── Gaze / Cursor ──────────────────────────────────────────────────────────
# How aggressively iris offset is amplified into cursor displacement
GAZE_SENSITIVITY_X = 8.0
GAZE_SENSITIVITY_Y = 10.0

# Exponential smoothing (0=frozen, 1=raw).  0.12 feels natural.
CURSOR_SMOOTHING = 0.12

# Normalised iris offset smaller than this is ignored (dead-zone)
GAZE_DEADZONE = 0.015

# ─── Blink Detection ────────────────────────────────────────────────────────
# Eye Aspect Ratio below this threshold → eye considered CLOSED
EAR_THRESHOLD = 0.21

# Consecutive frames EAR must stay below threshold to register a blink
EAR_CONSEC_FRAMES = 3

# Seconds between blink events (debounce)
BLINK_DEBOUNCE_SEC = 0.4

# If a second blink begins within this window after the first → double-click
DOUBLE_BLINK_WINDOW_SEC = 0.45

# EAR must stay below threshold for >= this many frames → LONG blink (right-click)
LONG_BLINK_FRAMES = 18   # ≈ 0.6 s at 30 fps

# ─── Voice Recognition ──────────────────────────────────────────────────────
# OPTIMIZED for continuous, system-wide listening (NO WAKE MECHANISM)
VOICE_ENERGY_THRESHOLD        = 150  # Lower = more sensitive (was 200, increased sensitivity)
VOICE_DYNAMIC_ENERGY          = False  # Disabled for consistency
VOICE_PAUSE_THRESHOLD         = 0.6  # Pause threshold (increased for longer listening)
VOICE_TIMEOUT                 = 30.0  # Max wait between words (EXTENDED from 15.0 to 30.0)
VOICE_PHRASE_TIME_LIMIT       = 60.0  # Allow long phrases (EXTENDED from 30.0 to 60.0)
VOICE_LANGUAGE                = "en-US"
VOICE_NON_SPEAKING_DURATION   = 0.4  # Shorter gap (was 0.3)
VOICE_LISTENING_TIMEOUT       = 120.0  # Auto-reset after 2 minutes (NEW)
VOICE_SHOW_LISTENING_STATUS   = True  # Display listening indicator in overlay (NEW)

# ─── Voice Command Recognition (Advanced) ──────────────────────────────────
# Confidence threshold for fuzzy matching (0.0-1.0, higher = stricter)
VOICE_MATCH_CONFIDENCE_THRESHOLD = 0.65

# Use Levenshtein distance for fuzzy matching (advanced matching)
VOICE_ENABLE_FUZZY_MATCHING = True

# Maximum characters to teleport phrase before giving up
VOICE_MAX_PHRASE_LENGTH = 100

# Enable voice feedback/confirmation (TTS optional, text for now)
VOICE_ENABLE_FEEDBACK = True

# Logging level: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
VOICE_LOG_LEVEL = "INFO"

# Voice command feedback
VOICE_COMMAND_FEEDBACK_DURATION = 2.0  # Show voice command status for N seconds
VOICE_ERROR_FEEDBACK_DURATION   = 3.0  # Show errors for longer

# List of voice phrases to recognize (customize here for better accuracy)
VOICE_PHRASE_MAPPINGS = {
    # Navigation
    "click": "CLICK",
    "double click": "DOUBLE_CLICK",
    "right click": "RIGHT_CLICK",
    "scroll up": "SCROLL_UP",
    "scroll down": "SCROLL_DOWN",
    "go back": "GO_BACK",
    "go forward": "GO_FORWARD",
    "back": "GO_BACK",
    "forward": "GO_FORWARD",
    
    # Editing
    "copy": "COPY",
    "paste": "PASTE",
    "undo": "UNDO",
    "redo": "REDO",
    "select all": "SELECT_ALL",
    "select": "SELECT_ALL",
    
    # Zoom
    "zoom in": "ZOOM_IN",
    "zoom out": "ZOOM_OUT",
    "zoom reset": "ZOOM_RESET",
    "reset zoom": "ZOOM_RESET",
    
    # Browser/Window
    "open browser": "OPEN_BROWSER",
    "browser": "OPEN_BROWSER",
    "new tab": "NEW_TAB",
    "close tab": "CLOSE_TAB",
    "switch tab": "SWITCH_TAB",
    "close window": "CLOSE_WINDOW",
    "take screenshot": "TAKE_SCREENSHOT",
    "screenshot": "TAKE_SCREENSHOT",
    
    # System
    "calibrate": "CALIBRATE",
    "calibration": "CALIBRATE",
    "pause": "PAUSE_TRACKING",
    "resume": "RESUME_TRACKING",
    "stop": "STOP",
    "quit": "STOP",
    "exit": "STOP",
}

# ─── MediaPipe FaceMesh ─────────────────────────────────────────────────────
MAX_NUM_FACES            = 1
REFINE_LANDMARKS         = True   # enables iris landmarks 468-477
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE  = 0.7
MEDIAPIPE_FACE_LANDMARK_MODEL_PATH = None  # Required for MediaPipe Tasks API (new MP version with mp.tasks)

# ─── MediaPipe landmark indices ─────────────────────────────────────────────
# Right eye (camera-left = user's right)
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
# Left eye
LEFT_EYE_INDICES  = [362, 385, 387, 263, 373, 380]

# Ear landmark groups (blink detector expects these names)
LEFT_EYE_EAR = LEFT_EYE_INDICES
RIGHT_EYE_EAR = RIGHT_EYE_INDICES

# Blink threshold aliases (legacy names)
EAR_BLINK_THRESHOLD = EAR_THRESHOLD
EAR_CONSEC_FRAMES = EAR_CONSEC_FRAMES
LONG_BLINK_FRAMES = LONG_BLINK_FRAMES

# Iris centres (refined landmarks)
LEFT_IRIS_CENTER  = 468
RIGHT_IRIS_CENTER = 473

# Blink timing alias
DOUBLE_BLINK_INTERVAL = DOUBLE_BLINK_WINDOW_SEC

# Eye corners for horizontal normalisation
RIGHT_EYE_LEFT_CORNER  = 133
RIGHT_EYE_RIGHT_CORNER = 33
LEFT_EYE_LEFT_CORNER   = 362
LEFT_EYE_RIGHT_CORNER  = 263

# ─── Scroll ─────────────────────────────────────────────────────────────────
SCROLL_AMOUNT = 3
SCROLL_LINES = 3
SCROLL_ZONE_FRACTION = 0.08
# ─── Cursor & Click behavior ───────────────────────────────────────
PYAUTOGUI_FAILSAFE = True
PYAUTOGUI_PAUSE = 0.0
CLICK_COOLDOWN_SEC = 0.2
# ─── Debug / UI ─────────────────────────────────────────────────────────────
SHOW_LANDMARKS   = True
SHOW_EAR_VALUE   = True
SHOW_EAR_VALUES  = SHOW_EAR_VALUE
SHOW_GAZE_ARROW  = True
SHOW_GAZE_VECTOR = SHOW_GAZE_ARROW   # alias used by overlay.py
SHOW_STATUS_OVERLAY = True
OVERLAY_FONT_SCALE = 0.55
OVERLAY_ALPHA      = 0.7
OVERLAY_SCALE      = 1.0
EAR_OPEN_THRESHOLD = EAR_THRESHOLD


