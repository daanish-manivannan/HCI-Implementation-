# 🎤 Voice Commands Quick Reference

## ✅ All 34 Available Voice Commands

### 🖱️ **Mouse & Click Commands**
| Command | Action |
|---------|--------|
| `click` | Single left click |
| `double click` | Double click |
| `right click` | Right click menu |

### ⬆️ **Scroll Commands**
| Command | Action |
|---------|--------|
| `scroll up` | Scroll up 3 lines |
| `scroll down` | Scroll down 3 lines |

### 🔙 **Navigation Commands**
| Command | Action |
|---------|--------|
| `go back` / `back` | Browser back (Alt+Left) |
| `go forward` / `forward` | Browser forward (Alt+Right) |

### ✏️ **Edit Commands**
| Command | Action |
|---------|--------|
| `copy` | Copy to clipboard (Ctrl+C) |
| `paste` | Paste from clipboard (Ctrl+V) |
| `undo` | Undo last action (Ctrl+Z) |
| `redo` | Redo last action (Ctrl+Y) |
| `select all` / `select` | Select all text (Ctrl+A) |
| `type [text]` | Type custom text |

### 🔍 **Zoom Commands**
| Command | Action |
|---------|--------|
| `zoom in` | Zoom in (Ctrl++) |
| `zoom out` | Zoom out (Ctrl+-) |
| `zoom reset` | Reset zoom (Ctrl+0) |

### 🌐 **Browser Commands**
| Command | Action |
|---------|--------|
| `open browser` / `browser` | Open Google in browser |
| `new tab` | Open new tab (Ctrl+T) |
| `close tab` | Close current tab (Ctrl+W) |
| `switch tab` | Switch to next tab (Ctrl+Tab) |

### 🖥️ **Window Commands**
| Command | Action |
|---------|--------|
| `close window` | Close current window (Alt+F4) |
| `take screenshot` / `screenshot` | Screenshot (Ctrl+Shift+S) |

### ⚙️ **System Commands**
| Command | Action |
|---------|--------|
| `calibrate` / `calibration` | Start eye calibration |
| `pause` | Pause gaze tracking |
| `resume` | Resume gaze tracking |
| `stop` / `quit` / `exit` | Exit application |

---

## 🎯 Quick Start

### 1. **Start the System**
```bash
python main.py
```

### 2. **Calibrate Your Eyes** (First Time)
- Say: `calibrate`
- Follow the 5 target points on screen
- System automatically calibrates when done

### 3. **Test Basic Commands**
- Say: `click` → Executes left click at gaze position
- Say: `scroll up` → Scrolls up
- Say: `copy` → Copies selected text

### 4. **Check Confidence**
Look at terminal output:
```
[Voice] command=CLICK confidence=0.95 🎯🎯🎯🎯🎯 payload='click'
```
- 🎯🎯🎯🎯🎯 = Very high confidence
- 🎯🎯🎯 = Medium confidence
- 🎯 = Low confidence (might retry)

---

## 💡 Tips for Better Recognition

### ✅ DO:
- Speak clearly and naturally
- Use exact command names when possible
- Speak in a normal tone (not too quiet, not too loud)
- Wait for "Command executed" feedback before next command
- Keep background noise low

### ❌ DON'T:
- Mumble or slur words
- Mix in lots of filler words like "um", "like", "you know"
- Speak too softly (adjusts microphone sensitivity in config)
- Interrupt system before it processes last command
- Expect typos to always work (though they often do!)

---

## 🎤 Advanced: Voice Phrase Typo Tolerance

The system uses **Levenshtein distance matching**. These will work:

```
"click" → CLICK ✓ (exact match)
"klick" → CLICK ✓ (1 typo, 80% confidence)
"clck" → CLICK ✓ (2 typos, 80% confidence)
"foo" → ❌ (too different)

"scvroll up" → SCROLL_UP ✓ (fuzzy match)
"scrolll up" → SCROLL_UP ✓ (extra letter)
```

---

## 🔧 Configuration Tuning

**In config.py:**

### Adjust Match Strictness
```python
# Default: 0.65 (65 confidence required)
# Lower = stricter (fewer false matches)
# Higher = looser (more typos accepted)
VOICE_MATCH_CONFIDENCE_THRESHOLD = 0.65
```

### Disable/Enable Fuzzy Matching
```python
# Disable for fastest, exact-match-only behavior
VOICE_ENABLE_FUZZY_MATCHING = True
```

### Add Custom Phrases
```python
VOICE_PHRASE_MAPPINGS = {
    # Add your custom commands
    "my custom click": "CLICK",
    "activate": "RESUME_TRACKING",
}
```

### Change Logging Detail
```python
# DEBUG = very verbose (all matches logged)
# INFO = normal (commands logged)
# WARNING = errors only
VOICE_LOG_LEVEL = "INFO"
```

---

## 📊 Confidence Score Guide

| Confidence | Match Type | Example |
|-----------|-----------|---------|
| 🟢 1.00 (100%) | Exact match | "click" → CLICK |
| 🟡 0.9-1.0 | Prefix match | "scrol up" → SCROLL_UP |
| 🟡 0.7-0.9 | Substring match | "please scroll" → SCROLL_UP |
| 🟠 0.6-0.7 | Fuzzy match | "klick" → CLICK |
| 🔴 <0.6 | Rejected | Not matched |

---

## 🐛 Troubleshooting

### Problem: "No match" for valid command
**Solution:**
1. Check if command is in list above
2. Verify `VOICE_MATCH_CONFIDENCE_THRESHOLD` not too high
3. Enable `VOICE_ENABLE_FUZZY_MATCHING` for typo tolerance
4. Check microphone volume (should hear yourself in feedback)

### Problem: Wrong command detected
**Solution:**
1. Speak more clearly
2. Reduce background noise
3. Lower `VOICE_MATCH_CONFIDENCE_THRESHOLD` to increase sensitivity
4. Check console output for confidence scores

### Problem: Microphone not working
**Solution:**
```bash
# Check microphone access
python test_voice.py  # Run voice tests
```
If test fails:
1. Verify microphone is connected
2. Check Windows audio settings
3. Restart audio driver
4. Run with DEBUG logging

### Problem: System crashes on voice input
**Solution:**
1. Rare! Report to developer with error log
2. In meantime, disable voice: comment out voice startup in main.py
3. Check Python version (3.7+) and library versions

---

## 📝 Typing Commands (TYPE_TEXT)

### How to Type Custom Text
```
Say: "type hello world"
→ System types: hello world
```

### Automatic Filler Word Removal
```
Say: "type um like hello you know world"
→ System types: hello world
(um, like, you know automatically removed)
```

### Supported Filler Words Filtered:
- um, uh, er, hmm
- like, you know
- basically, literally, actually

### Special Characters
Currently no special character support. Say:
- "period" or "dot" for `.`
- "comma" for `,`
- "question mark" for `?`
- (These are future enhancements)

---

## 📈 Performance Tips

### For Faster Recognition:
1. Use exact command names (not variations)
2. Set `VOICE_ENABLE_FUZZY_MATCHING = False` if not needed
3. Keep `VOICE_MATCH_CONFIDENCE_THRESHOLD` at default 0.65

### For More Accurate Recognition:
1. Speak clearly and slowly
2. Use simple language
3. Keep background noise low
4. Position microphone close to mouth

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| [voice_recognition.py](voice_recognition.py) | Voice input & matching |
| [command_interpreter.py](command_interpreter.py) | Command execution |
| [main.py](main.py) | Main loop integration |
| [config.py](config.py) | Voice configuration |
| [test_voice.py](test_voice.py) | Test suite & debugging |

---

## 🆘 Need Help?

### 1. Check System Status
```bash
python test_voice.py
```

### 2. Enable Debug Logging
```python
# In config.py:
VOICE_LOG_LEVEL = "DEBUG"
```

### 3. Check Phrase Mapping
```bash
grep -n "VOICE_PHRASE_MAPPINGS" config.py
```

### 4. Test Individual Components
```bash
python -c "from voice_recognition import phrase_to_command; print(phrase_to_command('click'))"
```

---

## ™️ Version Info

- **Enhancement Version:** 1.0 (Advanced Level)
- **Python Version:** 3.7+
- **Dependencies:** speech-recognition, pyaudio, opencv-python, mediapipe, pyautogui
- **Date:** March 15, 2026

---

**Last Updated:** 2026-03-15  
**Status:** ✅ Production Ready
