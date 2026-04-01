# Voice Commands — Cheat Sheet

## 🖱️ Mouse & Click
```
click              │  right click        │  double click
```

## 📜 Scroll & Navigation
```
scroll up                    │  scroll down
page up                      │  page down
scroll 3 pages down          │  scroll 5 lines up
scroll down 2 pages          │  scroll up 10 lines
go back                      │  go forward
```

## ✂️ Editing
```
copy       │  paste      │  cut       │  undo       │  redo
select all │  type [text]
```

## 🔍 Zoom
```
zoom in    │  zoom out   │  zoom reset
```

## 🌐 Browser & Tabs
```
open browser                       ← Opens default browser
new tab          │  close tab      │  switch tab
close window     │  close browser  │  close this window
```

## 🚀 App Launcher
```
open [app]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
open chrome       │  open firefox     │  open edge
open notepad      │  open calculator  │  open word
open excel        │  open powerpoint  │  open outlook
open vs code      │  open vscode      │  open sublime
open notepad plus plus               │  open discord
open teams        │  open zoom        │  open whatsapp
open spotify      │  open obsidian    │  open steam
open file explorer│  open terminal    │  open paint
```

## 🌍 Websites
```
open youtube               ← Opens youtube.com
open google                ← Opens google.com
open youtube.com           ← Opens any URL with a dot
open youtube in browser    ← Explicit browser open
browse youtube.com         ← Same as above
search youtube             ← Google search for "youtube"
search how to code python  ← Google search
```

## ⚡ Code Generation
```
generate [snippet]                       ← Python (default)
generate [snippet] in [language]         ← Specific language
generate [snippet] in vscode             ← Open in VS Code
generate [snippet] in notepad++          ← Open in Notepad++
generate [snippet] in sublime            ← Open in Sublime Text
execute [snippet]                        ← Run code and show output
```
**Snippets**: hello world, palindrome, factorial, fibonacci, prime number, reverse string, sum numbers
**Languages**: python, java, javascript, cpp, csharp
**Editors**: vscode, notepad++, sublime, atom, notepad

> Set `PREFERRED_EDITOR` in `config.py` (`"auto"`, `"vscode"`, etc.)

## 🖥️ System Control
```
minimize all       │  maximize all      │  show desktop
toggle dark mode   │  change theme      │  switch theme
lock screen        │  open settings     │  refresh screen
take screenshot
```

## 🔊 Volume & Brightness
```
volume up    │  increase volume  │  louder
volume down  │  decrease volume  │  quieter
mute         │  unmute

brightness up   │  increase brightness  │  brighter
brightness down │  decrease brightness  │  dimmer
```

## 📶 Connectivity
```
bluetooth              ← Opens Bluetooth settings
turn on bluetooth      │  turn off bluetooth
```

## ⚙️ Settings
```
open settings                  ← Main settings
open settings sound            ← Sound settings
open settings display          ← Display settings
open settings bluetooth        ← Bluetooth settings
open settings personalization  ← Theme/wallpaper
open settings windows update   ← Windows Update
```
**Categories**: sound, display, keyboard, mouse, wifi, bluetooth, battery, apps, personalization, accounts, updates, privacy, network

---

## 🎯 Quick Test Sequence

1. `"open chrome"` → Chrome opens ✓
2. `"open youtube"` → YouTube opens in browser ✓
3. `"scroll 3 pages down"` → Scrolls 3 pages ✓
4. `"generate hello world"` → Code opens in editor ✓
5. `"volume up"` → Volume increases ✓
6. `"close window"` → Window closes ✓

---

## 💡 Tips

- Speak naturally — pause briefly between words
- `"open [app]"` tries built-in apps first, then PATH, then shell
- Websites, URLs (with dots), and well-known sites auto-detected
- `"close [anything]"` sends Alt+F4 to the foreground window
- `"search [query]"` does a Google search
- Scroll amounts: **lines** (3 per unit) or **pages** (15 per unit)
