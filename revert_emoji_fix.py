#!/usr/bin/env python3
"""
revert_emoji_fix.py
──────────────────
Revert the over-aggressive emoji replacement that broke code.
"""

import os

# Revert replacements - replace the bad ones
REVERSIONS = {
    '[+]': '+',  # Restore + operator
}

def fix_file(filepath):
    """Revert bad replacements in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        fixed = 0
        
        # Only revert operator-related replacements
        # Pattern: space [+] number or variable
        import re
        
        # Fix: variable [+]= value → variable += value
        content = re.sub(r'(\w+)\s*\[\+\]\s*=', r'\1 +=', content)
        if '[+] ' in content:  # After number
            content = content.replace('[+] ', '+ ')
        
        # Fix: (A [+] B) → (A + B)
        content = re.sub(r'\(\s*(\w+)\s*\[\+\]\s*(\w+)\s*\)', r'(\1 + \2)', content)
        
        # Fix: array[:30] [+] string → array[:30] + string  
        content = re.sub(r'([\]\d])\s*\[\+\]\s*\(', r'\1 + (', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Revert broken files."""
    print("Reverting over-aggressive emoji replacements...\n")
    
    files = [
        'blink_detector.py',
        'gaze_tracker.py',
        'eye_tracker.py',
        'command_interpreter.py',
        'voice_recognition.py',
    ]
    
    for filename in files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            if fix_file(filepath):
                print(f"[FIXED] {filename}")
            else:
                print(f"[SKIP] {filename}")

if __name__ == "__main__":
    main()
