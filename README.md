# Hands-Free Human Computer Interaction System

> Control your computer with your eyes and voice — no mouse, no keyboard required.

Built with Python, MediaPipe, OpenCV, SpeechRecognition, and PyAutoGUI.

---

## Quick Start

### Prerequisites

- **Python 3.10+** (tested on 3.13)
- **Webcam** (any USB or built-in camera)
- **Microphone** (for voice commands)
- **Windows 10/11** (primary target; Linux/macOS partial support)
- **Internet connection** (for Google Speech Recognition; offline via PocketSphinx)

### 1. Clone & Setup

```bash
git clone <repo-url>
cd HCI-Implementation-

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate          # Windows (cmd)
venv\Scripts\Activate.ps1      # Windows (PowerShell)
source venv/bin/activate       # Linux / macOS
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Windows extras** (if PyAudio fails):
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux extras**:
```bash
sudo apt-get install -y python3-dev portaudio19-dev python3-tk
```

### 3. Run

```bash
python main.py                 # Full system (eye + voice)
python main.py --no-gaze       # Voice-only (no camera)
python main.py --no-voice      # Eye-only (no microphone)
python main.py --debug         # With debug logging
```

### 4. Calibrate

1. Look directly at the **centre of your screen**
2. Hold still while the **yellow bar** fills (~2 seconds)
3. Once **"Calibrated OK"** appears, you're ready

Re-calibrate anytime: press **C** or say **"calibrate"**.

---

## System Architecture

```
  Webcam ──▶ EyeTracker (MediaPipe) ──▶ GazeResult ──┐
                                                       ▼
  Microphone ──▶ VoiceRecognizer ──▶ CommandInterpreter ──▶ CursorController
                                            │                  (PyAutoGUI)
                                    BlinkDetector ─────────┘
```

| File | Purpose |
|------|---------|
| `main.py` | Entry point, webcam loop, keyboard shortcuts |
| `config.py` | All thresholds, sensitivities, feature flags |
| `eye_tracker.py` | MediaPipe Face Mesh → iris tracking → gaze offset |
| `blink_detector.py` | EAR-based blink classification (single/double/hold/wink) |
| `cursor_controller.py` | Gaze → cursor movement via PyAutoGUI |
| `voice_recognition.py` | Background speech recognition + phrase→command parsing |
| `command_interpreter.py` | Maps voice/blink events → OS actions |
| `code_generator.py` | Voice-driven code snippet generation |
| `windows_commands.py` | Windows-specific app launch, settings, volume, etc. |
| `overlay.py` | HUD renderer (eye mesh, EAR bars, status panel) |

---

## Voice Commands

> Full reference: [`VOICE_CHEAT_SHEET.md`](VOICE_CHEAT_SHEET.md)

### Mouse & Navigation
| Command | Action |
|---------|--------|
| `click` / `right click` / `double click` | Mouse buttons |
| `scroll up` / `scroll down` | Scroll (3 lines) |
| `scroll 3 pages down` | Scroll with amount |
| `page up` / `page down` | Scroll one page |
| `go back` / `go forward` | Browser navigation |

### Editing
| Command | Action |
|---------|--------|
| `copy` / `paste` / `cut` | Clipboard |
| `undo` / `redo` | History |
| `select all` / `select` | Selection |
| `type hello world` | Type text |
| `zoom in` / `zoom out` / `zoom reset` | Zoom |

### Apps & Websites
| Command | Action |
|---------|--------|
| `open chrome` / `open vs code` / `open notepad` | Launch apps |
| `open youtube` / `open google` | Open websites |
| `open youtube.com` | Any URL with a dot |
| `browse youtube.com` | Explicit browse |
| `search how to code python` | Google search |
| `close browser` / `close this window` | Close (Alt+F4) |
| `new tab` / `close tab` / `switch tab` | Tab control |

### Code Generation
| Command | Action |
|---------|--------|
| `generate hello world` | Generate & open in Notepad |
| `generate fibonacci in vscode` | Generate & open in VS Code |
| `generate palindrome in notepad` | Explicit Notepad |
| `execute hello world` | Generate, run & show output |

### System Control
| Command | Action |
|---------|--------|
| `volume up` / `volume down` / `mute` | Volume |
| `increase brightness` / `decrease brightness` | Brightness |
| `toggle bluetooth` | Bluetooth settings |
| `minimize all` / `maximize all` | Window management |
| `toggle dark mode` / `change theme` | Theme switch |
| `lock screen` | Lock PC |
| `open settings sound` | Settings category |
| `take screenshot` | Screenshot |

---

## Blink Gestures

| Gesture | How | Action |
|---------|-----|--------|
| Single blink | Normal blink (both eyes) | Left click |
| Double blink | Two quick blinks | Double click |
| Hold blink | Eyes closed ~1 second | Right click |
| Left wink | Left eye only | Drag toggle |
| Right wink | Right eye only | Scroll mode |

---

## Configuration

Edit `config.py` to customise:

```python
# Cursor
GAZE_SENSITIVITY_X  = 8.0      # Cursor speed (higher = faster)
SMOOTHING_FACTOR    = 0.25     # 0.1 = smooth, 0.5 = responsive

# Blink detection
EAR_CLOSE_THRESHOLD = 0.20     # Lower = more sensitive

# Voice
VOICE_LANGUAGE      = "en-US"  # Try "en-IN" for Indian English

# Code generation
PREFERRED_EDITOR    = "notepad" # "notepad" | "vscode" | "auto"

# Camera
CAMERA_INDEX        = 0        # Try 1 if wrong camera selected
CAMERA_FPS          = 30       # Lower = less CPU usage
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Cursor drifts | Press `C` to re-calibrate; improve lighting |
| False blink clicks | Raise `EAR_CLOSE_THRESHOLD` to `0.22` |
| Voice not recognised | Check internet connection |
| PyAudio install fails | `pip install pipwin && pipwin install pyaudio` |
| "Cannot open camera" | Set `CAMERA_INDEX = 1` in config.py |
| High CPU usage | Set `CAMERA_FPS = 15` in config.py |
| Code generates but editor empty | Check `PREFERRED_EDITOR` in config.py |
| "App not found" for VS Code | Ensure `code` is on your system PATH |

---

## License

MIT — free for personal and commercial use.
