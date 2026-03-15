#!/usr/bin/env python3
"""
fix_emoji_encoding.py
─────────────────────
Replace all emoji and Unicode characters with ASCII-safe alternatives.
This fixes Windows console encoding issues.
"""

import os
import re

# Define emoji to ASCII replacements
REPLACEMENTS = {
    # Emoji arrows and symbols
    '⬆️': '[UP]',
    '⬇️': '[DOWN]',
    '◀️': '[BACK]',
    '▶️': '[FWD]',
    '👆': '[TAP]',
    '👆👆': '[DOUBLE]',
    '🖱️': '[MOUSE]',
    '📋': '[COPY]',
    '📌': '[PIN]',
    '↶': '[UNDO]',
    '↷': '[REDO]',
    '✓': '[OK]',
    '✕': '[X]',
    '+': '[+]',
    '✓ Select all': '[OK] Select all',
    '🔍+': '[ZOOM+]',
    '🔍-': '[ZOOM-]',
    '🔍': '[ZOOM]',
    '🌐': '[WEB]',
    '🖥️': '[DESKTOP]',
    '📷': '[SCREENSHOT]',
    '⌨️': '[TYPE]',
    '🔇': '[MUTED]',
    '❌': '[ERROR]',
    '⚠️': '[WARN]',
    '💾': '[SAVE]',
    '🎤': '[MIC]',
    '⏹️': '[STOP]',
    '🎯': '[TARGET]',
    '🔴': '[RED]',
    '❌ Error': '[ERROR]',
    '❌ Blink failed': '[ERROR] Blink failed',
    
    # Check marks and symbols
    'No match': '[NO-MATCH]',
    'Untitled command': '[UNKNOWN]',
}

def fix_file(filepath):
    """Fix emoji in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace each emoji
        for emoji, ascii_val in REPLACEMENTS.items():
            if emoji in content:
                content = content.replace(emoji, ascii_val)
                print(f"  ✓ Replaced: '{emoji}' → '{ascii_val}'")
        
        # Check if any changes were made
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed: {filepath}")
            return True
        else:
            print(f"[SKIP] No emoji found: {filepath}")
            return False
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def main():
    """Fix all Python files."""
    print("=" * 70)
    print("FIXING EMOJI ENCODING IN ALL PYTHON FILES")
    print("=" * 70)
    
    files_to_fix = [
        'command_interpreter.py',
        'cursor_controller.py',
        'blink_detector.py',
        'gaze_tracker.py',
        'eye_tracker.py',
        'voice_recognition.py',
    ]
    
    fixed = 0
    skipped = 0
    
    for filename in files_to_fix:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if os.path.exists(filepath):
            print(f"\n[PROCESSING] {filename}")
            if fix_file(filepath):
                fixed += 1
            else:
                skipped += 1
        else:
            print(f"[NOT FOUND] {filename}")
    
    print("\n" + "=" * 70)
    print(f"[SUMMARY] Fixed: {fixed}, Skipped: {skipped}")
    print("=" * 70)
    
    print("\n[NEXT STEPS]")
    print("1. Run: python test_all_commands.py")
    print("2. All tests should now show ASCII output")
    print("3. Run: python main.py")
    print("4. Speak commands and see console output")
    print()

if __name__ == "__main__":
    main()
