#!/usr/bin/env python3
"""
test_all_commands.py
────────────────────
Comprehensive test suite for all voice commands.
Tests every command to verify functionality and show output.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from voice_recognition import phrase_to_command, Command, VoiceRecognizer
from command_interpreter import CommandInterpreter
from cursor_controller import CursorController
from windows_commands import WindowsCommandHandler
from code_generator import CodeGenerator

def print_header(title):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_test(test_num, description):
    """Print test label."""
    print(f"\n[TEST {test_num}] {description}")
    print("-" * 70)

def print_result(status, message):
    """Print result with status."""
    symbol = "[OK]" if status else "[FAIL]"
    print(f"{symbol} {message}")

# ============================================================
# TEST SUITE
# ============================================================

def test_voice_commands():
    """Test voice command recognition."""
    print_header("TEST VOICE COMMAND RECOGNITION")
    
    test_cases = [
        # Navigation commands
        ("scroll up", Command.SCROLL_UP, ""),
        ("scroll down", Command.SCROLL_DOWN, ""),
        ("go back", Command.GO_BACK, ""),
        ("go forward", Command.GO_FORWARD, ""),
        
        # Click commands
        ("click", Command.CLICK, ""),
        ("right click", Command.RIGHT_CLICK, ""),
        ("double click", Command.DOUBLE_CLICK, ""),
        
        # Text commands
        ("copy", Command.COPY, ""),
        ("paste", Command.PASTE, ""),
        ("select all", Command.SELECT_ALL, ""),
        ("undo", Command.UNDO, ""),
        ("redo", Command.REDO, ""),
        
        # Zoom commands
        ("zoom in", Command.ZOOM_IN, ""),
        ("zoom out", Command.ZOOM_OUT, ""),
        ("zoom reset", Command.ZOOM_RESET, ""),
        
        # Browser commands
        ("open browser", Command.OPEN_BROWSER, ""),
        ("new tab", Command.NEW_TAB, ""),
        ("close tab", Command.CLOSE_TAB, ""),
        ("switch tab", Command.SWITCH_TAB, ""),
        ("close window", Command.CLOSE_WINDOW, ""),
        ("take screenshot", Command.TAKE_SCREENSHOT, ""),
        
        # Windows system commands
        ("open chrome", Command.OPEN_APP, "chrome"),
        ("open firefox", Command.OPEN_APP, "firefox"),
        ("open notepad", Command.OPEN_APP, "notepad"),
        ("minimize all", Command.MINIMIZE_ALL, ""),
        ("minimize windows", Command.MINIMIZE_ALL, ""),
        ("show desktop", Command.MINIMIZE_ALL, ""),
        ("toggle dark mode", Command.TOGGLE_DARK_MODE, ""),
        ("lock screen", Command.LOCK_SCREEN, ""),
        ("lock", Command.LOCK_SCREEN, ""),
        ("open settings", Command.OPEN_SETTINGS, ""),
        ("settings", Command.OPEN_SETTINGS, ""),
        ("calculator", Command.OPEN_CALCULATOR, ""),
        ("open calculator", Command.OPEN_CALCULATOR, ""),
        ("refresh", Command.REFRESH_SCREEN, ""),
        ("refresh screen", Command.REFRESH_SCREEN, ""),
        
        # Code commands
        ("generate code", Command.GENERATE_CODE, ""),
        ("execute code", Command.EXECUTE_CODE, ""),
        ("open code in editor", Command.OPEN_CODE_IN_EDITOR, ""),
        
        # Complex phrases
        ("select the text open chrome", Command.OPEN_APP, "chrome"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (phrase, expected_cmd, expected_payload) in enumerate(test_cases, 1):
        cmd, payload, confidence = phrase_to_command(phrase)
        
        if cmd == expected_cmd:
            passed += 1
            print_result(True, f"'{phrase}' → {cmd.name} (confidence: {confidence:.2f})")
        else:
            failed += 1
            print_result(False, f"'{phrase}' → Expected {expected_cmd.name}, Got {cmd.name if cmd else 'NONE'}")
    
    print(f"\n[SUMMARY] Passed: {passed}/{len(test_cases)}")
    if failed > 0:
        print(f"[WARNING] Failed: {failed} tests")
    
    return failed == 0

def test_windows_commands():
    """Test Windows command handlers."""
    print_header("TEST WINDOWS COMMAND HANDLERS")
    
    test_cases = [
        ("chrome", "Chrome Browser"),
        ("notepad", "Notepad"),
        ("firefox", "Firefox"),
        ("calc", "Calculator"),
        ("vscode", "Visual Studio Code"),
    ]
    
    passed = 0
    failed = 0
    
    print("\n[NOTE] These will attempt to launch actual applications!")
    print("[INFO] Close apps to avoid clutter. Testing command-only (not actually launching).\n")
    
    for i, (app_name, description) in enumerate(test_cases, 1):
        print_test(i, f"Windows Command: Launch {description}")
        
        # Test the handler recognizes the app
        if app_name.lower() in WindowsCommandHandler.BUILTIN_APPS:
            passed += 1
            cmd = WindowsCommandHandler.BUILTIN_APPS[app_name.lower()]
            print_result(True, f"'{app_name}' found in BUILTIN_APPS → '{cmd}'")
        else:
            failed += 1
            print_result(False, f"'{app_name}' NOT in BUILTIN_APPS")
    
    print(f"\n[SUMMARY] Passed: {passed}/{len(test_cases)}")
    return failed == 0

def test_code_generation():
    """Test code generation."""
    print_header("TEST CODE GENERATION")
    
    test_cases = [
        ("hello world", "python", "Simple output"),
        ("palindrome", "python", "Algorithm"),
        ("fibonacci", "python", "Algorithm"),
        ("factorial", "python", "Algorithm"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (code_request, language, description) in enumerate(test_cases, 1):
        print_test(i, f"Generate Code: {description} ({code_request} in {language})")
        
        try:
            code, msg = CodeGenerator.generate_code(code_request, language)
            if code:
                passed += 1
                lines = code.count('\n')
                print_result(True, f"Generated {lines} lines of code")
                print(f"[PREVIEW]\n{code[:100]}...")
            else:
                failed += 1
                print_result(False, f"No code generated: {msg}")
        except Exception as e:
            failed += 1
            print_result(False, f"Exception: {e}")
    
    print(f"\n[SUMMARY] Passed: {passed}/{len(test_cases)}")
    return failed == 0

def test_interpreter_commands():
    """Test CommandInterpreter routing."""
    print_header("TEST COMMAND INTERPRETER ROUTING")
    
    cursor = CursorController()
    interpreter = CommandInterpreter(cursor)
    
    test_cases = [
        (Command.COPY, "", "Copy command"),
        (Command.PASTE, "", "Paste command"),
        (Command.SCROLL_UP, "", "Scroll up"),
        (Command.CLICK, "", "Click"),
        (Command.TYPE_TEXT, "Hello World", "Type text"),
        (Command.OPEN_APP, "chrome", "Open app"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (cmd, text, description) in enumerate(test_cases, 1):
        print_test(i, f"Interpreter: {description}")
        
        try:
            msg = interpreter.handle_voice_command(cmd, text, confidence=0.9)
            if msg:
                passed += 1
                print_result(True, f"Result: {msg}")
            else:
                failed += 1
                print_result(False, "No result returned")
        except Exception as e:
            failed += 1
            print_result(False, f"Exception: {e}")
    
    print(f"\n[SUMMARY] Passed: {passed}/{len(test_cases)}")
    return failed == 0

def test_microphone_detection():
    """Test microphone detection."""
    print_header("TEST MICROPHONE DETECTION")
    
    print("\n[TEST] Checking microphone availability...")
    
    try:
        from voice_recognition import _diagnose_microphone
        result = _diagnose_microphone()
        
        if result:
            print_result(True, "Microphone is available and functional")
        else:
            print_result(False, "Microphone detection failed")
            print("[INFO] Check:")
            print("  1. Is microphone connected?")
            print("  2. Is microphone enabled in Windows Settings?")
            print("  3. Is another app using the microphone?")
        
        return result
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False

def show_quick_reference():
    """Show quick reference of all commands."""
    print_header("QUICK REFERENCE - ALL VOICE COMMANDS")
    
    commands = {
        "Navigation": [
            "scroll up / scroll down",
            "go back / go forward",
        ],
        "Click & Select": [
            "click / right click / double click",
            "copy / paste / select all",
            "undo / redo",
        ],
        "Zoom & View": [
            "zoom in / zoom out / zoom reset",
            "open browser / new tab / close tab / switch tab",
        ],
        "Windows Control": [
            "open [app] - e.g., 'open chrome', 'open notepad'",
            "minimize all / show desktop",
            "toggle dark mode",
            "lock screen / lock",
            "open settings / settings",
            "calculator / open calculator",
            "refresh / refresh screen",
        ],
        "Code Generation": [
            "generate code [language] - e.g., 'generate hello world in python'",
            "execute code [language] - generates and runs",
            "open code in editor [language] - generates and saves to Desktop",
        ],
        "Text Input": [
            "type [text] - e.g., 'type Hello World'",
        ],
    }
    
    for category, cmds in commands.items():
        print(f"\n{category}:")
        for cmd in cmds:
            print(f"  • {cmd}")

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE VOICE COMMAND TEST SUITE")
    print("=" * 70)
    
    results = {}
    
    try:
        results["Voice Commands"] = test_voice_commands()
    except Exception as e:
        print(f"\n[ERROR] Voice command test failed: {e}")
        results["Voice Commands"] = False
    
    try:
        results["Windows Commands"] = test_windows_commands()
    except Exception as e:
        print(f"\n[ERROR] Windows command test failed: {e}")
        results["Windows Commands"] = False
    
    try:
        results["Code Generation"] = test_code_generation()
    except Exception as e:
        print(f"\n[ERROR] Code generation test failed: {e}")
        results["Code Generation"] = False
    
    try:
        results["Command Interpreter"] = test_interpreter_commands()
    except Exception as e:
        print(f"\n[ERROR] Interpreter test failed: {e}")
        results["Command Interpreter"] = False
    
    try:
        results["Microphone"] = test_microphone_detection()
    except Exception as e:
        print(f"\n[ERROR] Microphone test failed: {e}")
        results["Microphone"] = False
    
    # Final summary
    print_header("FINAL TEST SUMMARY")
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("[SUCCESS] All tests passed! System is ready to use.")
    else:
        print("[WARNING] Some tests failed. See details above.")
    print("=" * 70)
    
    # Show quick reference
    show_quick_reference()
    
    print("\n[NEXT STEPS]")
    print("  1. Run: python main.py")
    print("  2. Wait for 'VOICE RECOGNITION STATUS' message")
    print("  3. Speak a command (e.g., 'open chrome', 'copy', 'click')")
    print("  4. Watch console for [Voice] INPUT DETECTED and results")
    print("\n")

if __name__ == "__main__":
    main()
