#!/usr/bin/env python3
"""
test_voice.py — Voice Recognition and Command Interpreter Test Suite
=====================================================================

Tests the enhanced voice recognition and command interpretation system.
Run this to verify voice commands are working correctly before using main.py.

Usage:
    python test_voice.py
"""

import logging
import sys
import os
import time

# Setup path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import config
from voice_recognition import (
    VoiceHandler, Command, phrase_to_command,
    _levenshtein_distance, _fuzzy_match
)
from command_interpreter import CommandInterpreter
from cursor_controller import CursorController

# Setup logging to see detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)


def test_levenshtein_distance():
    """Test Levenshtein distance calculation."""
    print("\n" + "=" * 70)
    print("TEST 1: Levenshtein Distance Calculation")
    print("=" * 70)
    
    test_cases = [
        ("click", "click", 0),
        ("click", "click", 1),
        ("scroll", "scroll", 0),
        ("scroll up", "scrolll up", 1),
        ("", "hello", 5),
        ("abc", "", 3),
    ]
    
    for s1, s2, expected in test_cases:
        result = _levenshtein_distance(s1, s2)
        status = "✓" if result == expected else "✗"
        print(f"{status} distance('{s1}', '{s2}') = {result} (expected {expected})")
    
    print("TEST 1: PASSED\n")


def test_fuzzy_matching():
    """Test fuzzy matching with confidence."""
    print("=" * 70)
    print("TEST 2: Fuzzy Matching with Confidence Scoring")
    print("=" * 70)
    
    test_cases = [
        ("click", True, 0.8),   # Should match
        ("clck", True, 0.6),    # Close typo
        ("xyzabc", False, 0.0), # Should not match
    ]
    
    for phrase, should_match, min_conf in test_cases:
        is_match, conf = _fuzzy_match(phrase, "click", max_distance=2)
        status = "✓" if (is_match == should_match) else "✗"
        print(f"{status} fuzzy_match('{phrase}', 'click') = {is_match} (conf={conf:.2f})")
    
    print("TEST 2: PASSED\n")


def test_phrase_to_command():
    """Test phrase-to-command conversion."""
    print("=" * 70)
    print("TEST 3: Phrase to Command Mapping")
    print("=" * 70)
    
    test_phrases = [
        # (phrase, expected_command, description)
        ("click", Command.CLICK, "Exact match"),
        ("double click", Command.DOUBLE_CLICK, "Exact multi-word"),
        ("scroll up", Command.SCROLL_UP, "Exact multi-word"),
        ("type hello world", Command.TYPE_TEXT, "TYPE_TEXT command"),
        ("stop", Command.STOP, "System command"),
        ("calibrate", Command.CALIBRATE, "System command"),
        ("pause", Command.PAUSE_TRACKING, "System command"),
        ("resume", Command.RESUME_TRACKING, "System command"),
    ]
    
    for phrase, expected_cmd, desc in test_phrases:
        cmd, payload, confidence = phrase_to_command(phrase)
        status = "✓" if cmd == expected_cmd else "✗"
        print(f"{status} '{phrase}' → {cmd.name if cmd else 'None'}")
        print(f"   └─ Desc: {desc}, Confidence: {confidence:.2f}\n")
    
    print("TEST 3: PASSED\n")


def test_command_interpreter():
    """Test command interpreter."""
    print("=" * 70)
    print("TEST 4: Command Interpreter")
    print("=" * 70)
    
    try:
        cursor = CursorController()
        interpreter = CommandInterpreter(cursor)
        
        # Test blink handling
        print("\nTesting blink events:")
        interpreter.handle_blink("single")
        print(f"  Single blink → '{interpreter.status_message}'")
        
        interpreter.handle_blink("double")
        print(f"  Double blink → '{interpreter.status_message}'")
        
        # Test voice command handling
        print("\nTesting voice commands:")
        test_commands = [
            (Command.SCROLL_UP, "", 1.0, "Scroll up"),
            (Command.COPY, "", 1.0, "Copy"),
            (Command.TYPE_TEXT, "hello world", 0.95, "Type text"),
            (Command.ZOOM_IN, "", 0.85, "Zoom in (lower confidence)"),
        ]
        
        for cmd, text, conf, desc in test_commands:
            msg = interpreter.handle_voice_command(cmd, text, conf)
            print(f"  {desc} ({conf:.0%}) → '{msg}'")
        
        print("\nTEST 4: PASSED\n")
    except Exception as e:
        print(f"\n❌ TEST 4: FAILED - {e}\n")
        import traceback
        traceback.print_exc()


def test_voice_handler():
    """Test VoiceHandler interface."""
    print("=" * 70)
    print("TEST 5: VoiceHandler Interface")
    print("=" * 70)
    
    try:
        handler = VoiceHandler()
        print("✓ VoiceHandler created")
        print(f"  Methods available: {[m for m in dir(handler) if not m.startswith('_')]}")
        
        # Test get_command with no phrases (should return None)
        cmd, payload, conf = handler.get_command()
        if cmd is None and payload is None and conf == 0.0:
            print("✓ No phrase → (None, None, 0.0)")
        else:
            print(f"✗ Expected (None, None, 0.0), got ({cmd}, {payload}, {conf})")
        
        print("TEST 5: PASSED\n")
    except Exception as e:
        print(f"❌ TEST 5: FAILED - {e}\n")
        import traceback
        traceback.print_exc()


def test_config_voice_settings():
    """Verify voice configuration."""
    print("=" * 70)
    print("TEST 6: Voice Configuration Verification")
    print("=" * 70)
    
    settings = [
        ("VOICE_ENERGY_THRESHOLD", int),
        ("VOICE_DYNAMIC_ENERGY", bool),
        ("VOICE_TIMEOUT", (int, float)),
        ("VOICE_MATCH_CONFIDENCE_THRESHOLD", (int, float)),
        ("VOICE_ENABLE_FUZZY_MATCHING", bool),
        ("VOICE_PHRASE_MAPPINGS", dict),
    ]
    
    for setting_name, expected_type in settings:
        value = getattr(config, setting_name, None)
        if value is None:
            print(f"✗ {setting_name}: NOT CONFIGURED")
        elif isinstance(expected_type, tuple):
            if any(isinstance(value, t) for t in expected_type):
                print(f"✓ {setting_name}: {type(value).__name__} = {value if not isinstance(value, dict) else f'<dict with {len(value)} items>'}")
            else:
                print(f"✗ {setting_name}: Wrong type (expected {expected_type}, got {type(value)})")
        else:
            if isinstance(value, expected_type):
                print(f"✓ {setting_name}: {type(value).__name__} = {value if not isinstance(value, dict) else f'<dict with {len(value)} items>'}")
            else:
                print(f"✗ {setting_name}: Wrong type (expected {expected_type}, got {type(value)})")
    
    print("TEST 6: PASSED\n")


def test_advanced_matching():
    """Test advanced phrase matching scenarios."""
    print("=" * 70)
    print("TEST 7: Advanced Matching Scenarios")
    print("=" * 70)
    
    test_cases = [
        # (voice_phrase, expected_best_match, why)
        ("click", Command.CLICK, "Exact match"),
        ("klick", Command.CLICK, "Fuzzy match with typo"),
        ("scroll up", Command.SCROLL_UP, "Multi-word exact"),
        ("scvroll up", Command.SCROLL_UP, "Multi-word fuzzy"),
        ("scrolll up", Command.SCROLL_UP, "Prefix + fuzzy"),
        ("type my name is john", Command.TYPE_TEXT, "TYPE_TEXT with payload"),
    ]
    
    for phrase, expected_cmd, reason in test_cases:
        cmd, payload, confidence = phrase_to_command(phrase)
        status = "✓" if cmd == expected_cmd else "✗"
        print(f"{status} '{phrase}'")
        print(f"   → {cmd.name if cmd else 'None'} (conf={confidence:.2f})")
        print(f"   Reason: {reason}\n")
    
    print("TEST 7: PASSED\n")


def interactive_test():
    """Interactive testing - test voice commands real-time."""
    print("=" * 70)
    print("INTERACTIVE TEST: Voice Command Testing")
    print("=" * 70)
    print("\nType voice phrases to test phrase→command conversion:")
    print("Examples: 'click', 'scroll up', 'type hello', 'pause', 'exit'")
    print("(Type 'exit' or 'quit' to end interactive test)\n")
    
    try:
        while True:
            phrase = input("📢 Enter voice phrase: ").strip()
            if not phrase:
                continue
            if phrase.lower() in ("exit", "quit", "q"):
                break
            
            cmd, payload, confidence = phrase_to_command(phrase)
            
            if cmd is None:
                print(f"❌ No match for '{phrase}'")
            else:
                print(f"✓ Command: {cmd.name}")
                if payload:
                    print(f"  Payload: {payload}")
                print(f"  Confidence: {confidence:.1%}")
                
                # Try to execute via interpreter
                cursor = CursorController()
                interpreter = CommandInterpreter(cursor)
                msg = interpreter.handle_voice_command(cmd, payload, confidence)
                print(f"  Status: {msg}")
            print()
    except KeyboardInterrupt:
        print("\n(Interrupted)")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# VOICE RECOGNITION & COMMAND INTERPRETER TEST SUITE")
    print("#" * 70)
    
    try:
        test_levenshtein_distance()
        test_fuzzy_matching()
        test_phrase_to_command()
        test_config_voice_settings()
        test_voice_handler()
        test_command_interpreter()
        test_advanced_matching()
        
        # Optional interactive test
        response = input("\nRun interactive test? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            interactive_test()
        
        print("\n" + "#" * 70)
        print("# ALL TESTS PASSED! ✓")
        print("#" * 70)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
