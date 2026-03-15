# Voice-Controlled System Commands & Code Generation Guide

## Overview

The enhanced voice recognition system now supports:
- **Windows System Commands**: App launching, navigation, system control
- **Code Generation**: Voice-driven code snippet generation and execution
- **All Existing Features**: Fully preserved (navigation, clicking, scrolling, etc.)

---

## Windows System Commands

### App Launching

**Pattern**: `open [app name]`

**Examples**:
- "open chrome" → Launches Chrome
- "open word" → Opens Microsoft Word
- "open vscode" → Opens Visual Studio Code
- "open notepad" → Opens Notepad
- "open firefox" → Launches Firefox
- "open discord" → Opens Discord

**Supported Apps** (20+ built-in apps):
- **Browsers**: chrome, edge, firefox, internet explorer
- **Office**: word, excel, powerpoint, outlook, onenote
- **Development**: vscode, python, visual studio
- **Communication**: teams, discord, telegram, zoom
- **System**: cmd, powershell, terminal

**Returns**: Status message like "✓ Launched Chrome"

---

### System Navigation & Control

| Command | Effect | Status |
|---------|--------|--------|
| `minimize all` | Minimize all windows | 📉 All windows minimized |
| `minimize windows` | Same as above | 📉 All windows minimized |
| `show desktop` | Same as above | 📉 All windows minimized |
| `toggle dark mode` | Switch dark/light mode | 🌙 Dark Mode or ☀️ Light Mode |
| `dark mode` | Enable dark mode | 🌙 Dark Mode |
| `light mode` | Enable light mode | ☀️ Light Mode |
| `lock screen` | Lock Windows | 🔒 Screen locked |
| `lock` | Alias for lock screen | 🔒 Screen locked |
| `lock desktop` | Lock desktop | 🔒 Screen locked |
| `open settings` | Open Windows Settings | ⚙️ Settings opened |
| `settings` | Alias for settings | ⚙️ Settings opened |
| `open settings [category]` | Open specific settings | ⚙️ Settings opened (category) |
| `open calculator` | Open Calculator app | 🧮 Calculator opened |
| `calculator` | Alias for calculator | 🧮 Calculator opened |
| `refresh` | Refresh screen | 🔄 Screen refreshed |
| `refresh screen` | Refresh desktop | 🔄 Screen refreshed |

**Settings Categories**:
- `sound` → Sound settings
- `display` → Display settings
- `keyboard` → Keyboard settings
- `mouse` → Mouse settings
- `wifi` → WiFi settings
- `bluetooth` → Bluetooth settings
- `battery` → Battery saver
- `apps` → Apps & features

---

### Website Opening

**Pattern**: `open website [URL]` or `browse [URL]`

**Examples**:
- "open website google.com" → Opens Google
- "browse youtube.com" → Opens YouTube
- "open website amazon.com" → Opens Amazon
- "browse stackoverflow.com" → Opens StackOverflow

**Note**: Automatically adds `https://` if not provided

**Returns**: Status like "🌐 Opened: https://google.com"

---

### Folder Navigation

**Pattern**: `open folder [path]`

**Examples**:
- "open folder desktop" → Opens Desktop folder
- "open folder documents" → Opens Documents
- "open folder c:\\users\\username\\downloads" → Opens specific folder

**Returns**: Status like "📁 Opened: C:/Users/Username/Desktop"

---

## Code Generation Commands

### Basic Code Snippet Generation

**Pattern**: `generate [snippet name] in [language]` or `generate [snippet name]`

**Supported Languages**: Python, Java, JavaScript, C++, C#

**Supported Snippets**:
1. **hello world** - Classic hello world program
2. **palindrome** - Palindrome checker with examples
3. **factorial** - Factorial calculator
4. **fibonacci** - Fibonacci sequence generator
5. **prime number** - Prime number checker
6. **reverse string** - String reversal
7. **sum numbers** - Sum of numbers

**Examples**:

```
Generate with language specified:
- "generate hello world in python"
- "generate palindrome in java"
- "generate fibonacci in javascript"

Generate in default language (Python):
- "generate hello world"
- "generate factorial"
- "generate prime number"
```

**Output**: 
- Status: "✓ Generated palindrome in python"
- Code is generated but not opened

---

### Code Execution

**Pattern**: `execute [snippet name]` or `execute [snippet name] in [language]`

**Examples**:
- "execute hello world" → Generate & run hello world (Python)
- "execute palindrome in python" → Run palindrome checker
- "execute fibonacci in javascript" → Run Fibonacci sequence
- "execute factorial" → Run factorial in Python

**Process**:
1. Generates code based on request
2. Detects language from request (default: Python)
3. Creates temporary file
4. Compiles (if needed, e.g., Java)
5. Executes the code
6. Returns output in overlay

**Returns**: 
- On success: Output snippet like "✓ Code executed successfully: [output]"
- On error: Error message with details

**Supported Execution**:
- Python: Directly executed
- JavaScript: Requires Node.js
- Java: Compiled then executed
- (C++/C require manual compilation)

---

### Advanced: Generate and Open in VS Code

**Pattern**: `open [snippet] in editor`

**Examples**:
- "generate palindrome in python" → Creates file on Desktop
- File opens in VS Code for editing

**Returns**: Status like "📝 Opened in VS Code: code_snippet_1234567890.py"

---

## Full Command Reference

### Existing Commands (Still Supported)

**Navigation & Clicking**:
- Scroll up / Scroll down
- Go back / Go forward
- Click / Right-click / Double-click

**Editing**:
- Copy / Paste / Undo / Redo
- Select all
- Type [text]

**Browser**:
- New tab / Close tab / Switch tab
- Open browser
- Close window

**Utilities**:
- Zoom in / Zoom out / Zoom reset
- Take screenshot
- Calibrate

---

## Voice Command Matching Algorithm

Phrases are matched in priority order:

1. **TYPE_TEXT** (highest priority)
   - Pattern: "type [anything]"

2. **Parameterized Commands** (high priority)
   - Pattern: "open [app]", "generate [code]", etc.

3. **Exact Matches** (high confidence ~1.0)
   - Pattern: Exact word from command map
   - Example: "click" matches exactly

4. **Prefix Matches** (medium-high confidence)
   - Pattern: Phrase starts with command
   - Example: "minimize all windows" → "minimize all"

5. **Substring Matches** (medium confidence)
   - Pattern: Command appears anywhere in phrase
   - Example: "please maximize and minimize all" → "minimize all"

6. **Fuzzy Matches** (low-medium confidence)
   - Pattern: Similar command (Levenshtein distance ≤ 2)
   - Example: "minamize all" → "minimize all"

---

## Configuration

### Default Settings

```python
# config.py - Optional additions
VOICE_ENABLE_FUZZY_MATCHING = True        # Enable fuzzy matching
VOICE_MATCH_CONFIDENCE_THRESHOLD = 0.65   # Min. confidence for fuzzy match
```

### Language Detection for Code Generation

Auto-detects language from request:
- "python", "py" → Python
- "java" → Java
- "javascript", "js", "node" → JavaScript
- "cpp", "c++" → C++
- "csharp", "c#" → C#

Default: **Python** if no language specified

---

## Examples: Voice Interaction Flows

### Workflow 1: Launch App and Code

```
User: "Open chrome"
System: ✓ Launched Chrome

User: "Open website github.com"
System: 🌐 Opened: https://github.com

User: "Generate hello world in python"
System: ✓ Generated hello world in python

User: "Execute fibonacci"
System: ✓ Code executed successfully:
         0 1 1 2 3 5 8 13 21 34
```

### Workflow 2: Code Generation & Editing

```
User: "Generate palindrome in python"
System: ✓ Generated palindrome in python

User: "Open code in editor"
System: 📝 Opened in VS Code: code_snippet_1234567890.py

[VS Code opens with generated code ready to edit]
```

### Workflow 3: System Control

```
User: "Minimize all"
System: 📉 All windows minimized

User: "Toggle dark mode"
System: Switched to 🌙 Dark Mode

User: "Lock screen"
System: 🔒 Screen locked
```

---

## Error Handling

All commands include error handling:

- **App Not Found**: "❌ Failed to launch [app]"
- **Invalid Folder**: "❌ Folder not found: [path]"
- **Code Generation Failed**: "❌ Failed to generate code"
- **Execution Error**: "❌ Execution failed: [error details]"
- **Timeout**: "❌ Execution timeout (exceeded 30 seconds)"

---

## Performance Notes

- **App Launch**: < 2 seconds typically
- **Code Generation**: < 500ms
- **Code Execution**: 
  - Python: 1-3 seconds
  - JavaScript: 1-3 seconds
  - Java: 3-5 seconds (includes compilation)
- **Max Execution Time**: 30 seconds (configurable)

---

## Troubleshooting

### "No match for phrase"
- Microphone may have heard something unclear
- Try speaking more clearly
- Repeat the phrase

### Code execution fails
- Ensure required runtime is installed:
  - Python 3.x for Python code
  - Node.js for JavaScript
  - Java JDK for Java code
- Check for syntax errors if custom code

### App won't launch
- App may not be installed
- Try opening it manually or use full app path
- Check app name spelling

### Dark mode toggle doesn't work
- May require administrative privileges
- Try toggling manually in Settings
- Some systems may have this restricted

---

## Integration with Existing Features

**All existing features remain fully functional**:
- Blink detection (single/double/long)
- Eye gaze tracking
- Cursor control
- Voice commands (all original ones)
- Calibration system
- Overlay display

**New features are added without interference** - they coexist seamlessly with existing functionality.

---

## Architecture

### New Modules
- **windows_commands.py**: Windows system operations
- **code_generator.py**: Code generation and execution

### Updated Modules
- **voice_recognition.py**: Added new Command types and phrase_to_command logic
- **command_interpreter.py**: New command handlers

### Unchanged Modules
- All other modules (blink_detector.py, gaze_tracker.py, etc.) remain unchanged

---

## Voice Command Examples

**Quick Reference**:

```
App Launching:
  "open chrome" | "open word" | "open vscode"

System Control:
  "minimize all" | "toggle dark mode" | "lock screen"

Settings:
  "open settings" | "open settings sound"

Code Generation:
  "generate hello world"
  "generate palindrome in python"
  "generate fibonacci in javascript"

Code Execution:
  "execute hello world"
  "execute palindrome in java"
  "execute factorial"

Navigation:
  "open website google.com"
  "open folder desktop"
```

---

## Support

For issues or feature requests related to Windows commands or code generation:
1. Check the error message in the system overlay
2. Check logs in console output
3. Verify command syntax matches examples
4. Ensure all dependencies are installed

