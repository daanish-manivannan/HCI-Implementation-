# Hands-Free Human Computer Interaction System

> Control your computer with your eyes and voice — no mouse, no keyboard required.

Built with Python, MediaPipe, OpenCV, SpeechRecognition, and PyAutoGUI.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Descriptions](#module-descriptions)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Controls Reference](#controls-reference)
7. [Calibration Guide](#calibration-guide)
8. [Voice Commands](#voice-commands)
9. [Blink Gestures](#blink-gestures)
10. [Configuration Tuning](#configuration-tuning)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This system allows a user to interact with a computer entirely hands-free by combining:

- **Eye Tracking** — iris position via MediaPipe Face Mesh drives the cursor
- **Blink Detection** — Eye Aspect Ratio (EAR) classifies single, double, hold, and wink blinks as click/drag/scroll actions
- **Voice Commands** — continuous background speech recognition converts spoken phrases into system commands

No specialised hardware is required. A standard USB webcam and a microphone are sufficient.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Hands-Free HCI System                             │
│                                                                          │
│  ┌────────────┐   BGR frame   ┌──────────────────┐                       │
│  │   Webcam   │ ────────────▶ │   EyeTracker     │  GazeResult          │
│  │  (OpenCV)  │               │  (MediaPipe FM)  │ ─────────┐           │
│  └────────────┘               └──────────────────┘          │           │
│                                                              ▼           │
│  ┌────────────┐  AudioData    ┌──────────────────┐   ┌──────────────┐   │
│  │ Microphone │ ────────────▶ │ VoiceRecognizer  │   │    Blink     │   │
│  │ (PyAudio)  │  [thread]     │  (SpeechRecog.)  │   │  Detector   │   │
│  └────────────┘               └─────────┬────────┘   └──────┬───────┘   │
│                                         │ phrase             │ event     │
│                                         ▼                    ▼           │
│                               ┌──────────────────────────────────────┐  │
│                               │        CommandInterpreter            │  │
│                               │  • maps phrases → action tokens      │  │
│                               │  • maps blink gestures → actions     │  │
│                               │  • manages mode state machine        │  │
│                               └──────────────┬───────────────────────┘  │
│                                              │ action token              │
│                                              ▼                           │
│                               ┌──────────────────────┐                  │
│                               │   CursorController   │                  │
│                               │  (PyAutoGUI)         │                  │
│                               │  • EMA smooth move   │                  │
│                               │  • click / drag      │                  │
│                               │  • hotkeys           │                  │
│                               └──────────────────────┘                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────┐               │
│  │  HUD Overlay (OpenCV draw)                           │               │
│  │  FPS · Mode · EAR bars · Gaze arrow · Status panel  │               │
│  └──────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Module Descriptions

| File | Purpose |
|------|---------|
| `main.py` | Entry point. Opens webcam, orchestrates the main loop, handles keyboard shortcuts. |
| `config.py` | Central configuration. All thresholds, sensitivities, and feature flags live here. |
| `modules/eye_tracker.py` | Wraps MediaPipe FaceMesh. Detects 478 facial landmarks, extracts iris centres, computes normalised gaze offset, handles calibration. |
| `modules/blink_detector.py` | Computes Eye Aspect Ratio (EAR) per eye. State-machine classifies SINGLE / DOUBLE / HOLD blinks and left/right winks. |
| `modules/cursor_controller.py` | Translates gaze offsets and action tokens into OS cursor events via PyAutoGUI. Manages drag state. |
| `modules/voice_recognition.py` | Background daemon thread. Continuously listens on the microphone using SpeechRecognition (Google + Sphinx fallback). Phrase matching helper. |
| `modules/command_interpreter.py` | Maps blink events and voice phrases to action tokens. Manages NORMAL / SCROLL / DRAG / PAUSED mode state machine. |
| `modules/overlay.py` | Real-time HUD renderer. Draws eye mesh, iris rings, gaze arrow, EAR bars, and status panel onto the preview window. |

---

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate.bat       # Windows
```

### 2. Install system dependencies

**Linux (Ubuntu / Debian)**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev portaudio19-dev \
    python3-tk python3-xlib libespeak-dev
```

**macOS**
```bash
brew install portaudio
```

### 3. Install Python packages

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Full system (eye tracking + voice)
python main.py

# Voice-only (no camera required)
python main.py --no-gaze

# Eye-only (no microphone)
python main.py --no-voice

# Debug logging
python main.py --debug
```

---

## Controls Reference

| Key | Action |
|-----|--------|
| `Q` / `ESC` | Quit |
| `C` | Re-calibrate gaze |
| `P` | Pause / resume |
| `H` | Toggle HUD |
| `S` | Save screenshot |

---

## Calibration Guide

On first launch:
1. Look directly at the **centre of your screen**.
2. Hold still while the **yellow calibration bar** fills (~2 seconds).
3. Once **"Calibrated OK"** appears, cursor control is active.

Re-calibrate any time by pressing **C** or saying **"calibrate"**.

---

## Voice Commands

| Category | Phrases | Action |
|----------|---------|--------|
| Mouse | "click", "right click", "double click" | Mouse buttons |
| Mouse | "drag", "drop" | Drag and drop |
| Scroll | "scroll up/down/left/right" | Scroll |
| Navigate | "go back", "go forward", "page up/down" | Navigation |
| Edit | "copy", "paste", "cut", "undo", "redo" | Clipboard |
| Window | "close window", "minimize", "maximize" | Window management |
| Tabs | "new tab", "close tab", "next tab" | Tab control |
| Zoom | "zoom in", "zoom out", "reset zoom" | Zoom |
| Type | "type \<words\>" | Types the following text |
| Keys | "press enter/escape/tab/space" | Key presses |
| System | "pause", "resume", "calibrate" | System control |
| System | "take screenshot" | Screenshot |

---

## Blink Gestures

| Gesture | How to Perform | Action |
|---------|----------------|--------|
| Single blink | Normal blink (both eyes) | Left click |
| Double blink | Two quick blinks | Double click |
| Hold blink | Eyes closed ~1 second | Right click |
| Left wink | Left eye only | Drag toggle |
| Right wink | Right eye only | Scroll mode toggle |
| Left wink hold | Left eye closed ~1s | Zoom in |
| Right wink hold | Right eye closed ~1s | Zoom out |

---

## Configuration Tuning

Edit `config.py` to customise behaviour:

```python
GAZE_SENSITIVITY_X  = 8.0   # Cursor speed (raise for wider screens)
SMOOTHING_FACTOR    = 0.25  # 0.1 = silky smooth, 0.5 = responsive
EAR_CLOSE_THRESHOLD = 0.20  # Blink sensitivity (lower = more sensitive)
VOICE_LANGUAGE      = "en-US"  # Try "en-IN" for Indian English
CALIBRATION_FRAMES  = 60    # ~2 seconds at 30fps
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Cursor drifts | Press `C` to re-calibrate; improve lighting |
| False blink clicks | Raise `EAR_CLOSE_THRESHOLD` to `0.22` |
| Voice not recognised | Check internet; install `pocketsphinx` for offline |
| PyAudio install fails | `sudo apt-get install portaudio19-dev` |
| "Cannot open camera" | Try `CAMERA_INDEX = 1` in config.py |
| High CPU usage | Set `CAMERA_FPS = 15` in config.py |

---

## License

MIT — free for personal and commercial use.
