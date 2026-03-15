# Voice Commands - Quick Reference Card

## NEW Windows System Commands

### App Launcher
```
open [app]           "open chrome", "open word", "open vscode"
                     "open notepad", "open discord", "open firefox"
```

### System Control
```
minimize all         Show desktop / minimize all windows
toggle dark mode     Switch between dark and light theme
lock screen          Lock Windows
open settings        Open Windows Settings
open settings [cat]  "open settings sound", "open settings display"
open calculator      Open Calculator
refresh screen       Refresh desktop
```

### Web Navigation
```
open website [url]   "open website google.com"
browse [url]         "browse youtube.com"
open folder [path]   "open folder desktop"
```

## NEW Code Generation Commands

### Generate Code
```
generate [snippet]           "generate hello world"
generate [snippet] in [lang] "generate palindrome in python"
                            "generate fibonacci in javascript"
```

### Execute Code
```
execute [snippet]           "execute hello world"
execute [snippet] in [lang] "execute factorial in python"
                           "execute prime number in javascript"
```

### Supported Code Snippets
- `hello world` - Classic hello world
- `palindrome` - Palindrome checker
- `factorial` - Factorial calculator
- `fibonacci` - Fibonacci sequence
- `prime number` - Prime number checker
- `reverse string` - String reversal
- `sum numbers` - Sum calculation

### Supported Languages
- `python` (default) - Python 3.x
- `java` - Java with compilation
- `javascript` - Node.js required
- `cpp` / `c++` - C++
- `csharp` / `c#` - C#

## Supported Built-in Apps

| Category | Apps |
|----------|------|
| **Browsers** | chrome, firefox, edge, internet explorer |
| **Office** | word, excel, powerpoint, outlook, onenote |
| **Dev** | vscode, python, visual studio |
| **Communication** | teams, discord, telegram, zoom |
| **System** | cmd, powershell, terminal, notepad |
| **Media** | vlc, spotify, windows media player |

## EXISTING Commands (Still Work!)

### Navigation
```
scroll up / scroll down    "scroll up", "scroll down"
go back / go forward       "go back", "go forward"
```

### Clicking
```
click                      "click"
right click                "right click"
double click               "double click"
```

### Editing
```
copy / paste               "copy", "paste"
undo / redo                "undo", "redo"
select all                 "select all"
type [text]                "type hello world"
```

### Browser
```
new tab / close tab        "new tab", "close tab"
switch tab                 "switch tab"
open browser               "open browser"
close window               "close window"
```

### Utilities
```
zoom in / zoom out         "zoom in", "zoom out"
zoom reset                 "zoom reset"
take screenshot            "take screenshot"
calibrate                  "calibrate"
```

## Usage Examples

### Scenario 1: Launch App & Work
```
"open chrome"              → Chrome opens
"open website github.com"  → GitHub opens in browser
```

### Scenario 2: Generate & Run Code
```
"generate hello world"     → Code generated
"execute hello world"      → Code runs, output shown
```

### Scenario 3: System Management
```
"minimize all"             → All windows hidden
"toggle dark mode"         → Theme switched
"lock screen"              → Screen locked
```

### Scenario 4: Code Generation in Specific Language
```
"generate palindrome in python"           → Python code
"execute fibonacci in javascript"         → JavaScript runs
"generate factorial in java"              → Java code compiled & run
```

## Command Matching Priority

If you say something unclear, voice system tries to match in this order:

1. **Exact match** - "click" exactly matches "click" ✓
2. **Prefix** - "click now" starts with "click" ✓
3. **Substring** - "just click here" contains "click" ✓
4. **Fuzzy** - "clck" is similar to "click" ✓

## Status Messages

| Status | Meaning |
|--------|---------|
| ✓ Launched chrome | App started successfully |
| 🌐 Opened: google.com | Website opened |
| ✓ Generated hello world in python | Code generated |
| ✓ Code executed successfully: [output] | Code ran successfully |
| ❌ Failed to launch chrome | App not found or error |
| ❌ Execution failed | Code had error or timed out |

## Tips & Tricks

### App Launching
- Say app name clearly: "chrome" not "browser"
- Use exact app name if it doesn't work first time
- Add custom apps to BUILTIN_APPS in windows_commands.py

### Code Generation
- Default language is Python (specify language to change)
- Snippets are templates - great for learning
- Generated code opens on Desktop if needed

### System Control
- "minimize all" hides all windows (works like Win+D)
- "toggle dark mode" switches theme instantly
- "lock screen" requires confirmation on some systems

### Combo Commands
```
"open chrome"               + "open website youtube.com"
"generate fibonacci"        + "execute fibonacci"
"minimize all"             + "lock screen"
```

## Keyboard Shortcuts (In Webcam Window)

| Key | Action |
|-----|--------|
| Q or ESC | Quit |
| C | Calibrate |
| P | Pause/Resume |
| R | Reset calibration |
| D | Debug overlay |
| S | Screenshot |

## Error Handling

If something doesn't work:

1. **Unclear recognition?** → Speak more clearly
2. **App won't launch?** → Check app name spelling
3. **Code won't execute?** → Verify code syntax
4. **Settings won't toggle?** → May need admin rights

## Next Steps

1. Try: "open notepad"
2. Try: "generate hello world"
3. Try: "execute hello world"
4. Try: "minimize all"
5. Try: "open settings sound"

---

**All existing features remain fully functional!** 🎉

Voice control is now supercharged with system integration and code generation! 🚀

