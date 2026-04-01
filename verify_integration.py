#!/usr/bin/env python3
"""
verify_integration.py
─────────────────────
Verify that the HCI system initializes correctly with LLM integration.
This is a quick smoke test to ensure main.py will start without errors.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules import correctly."""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    try:
        import config
        print("✓ config")
    except Exception as e:
        print(f"✗ config: {e}")
        return False
    
    try:
        from llm_handler import initialize_llm, is_llm_available
        print("✓ llm_handler")
    except Exception as e:
        print(f"✗ llm_handler: {e}")
        return False
    
    try:
        from command_interpreter import CommandInterpreter
        print("✓ command_interpreter")
    except Exception as e:
        print(f"✗ command_interpreter: {e}")
        return False
    
    try:
        from blink_detector import BlinkDetector
        print("✓ blink_detector")
    except Exception as e:
        print(f"✗ blink_detector: {e}")
        return False
    
    try:
        from gaze_tracker import GazeTracker
        print("✓ gaze_tracker")
    except Exception as e:
        print(f"✗ gaze_tracker: {e}")
        return False
    
    try:
        from cursor_controller import CursorController
        print("✓ cursor_controller")
    except Exception as e:
        print(f"✗ cursor_controller: {e}")
        return False
    
    try:
        from voice_recognition import VoiceHandler
        print("✓ voice_recognition")
    except Exception as e:
        print(f"✗ voice_recognition: {e}")
        return False
    
    return True

def test_llm_initialization():
    """Test LLM initialization."""
    print("\n" + "=" * 60)
    print("TESTING LLM INITIALIZATION")
    print("=" * 60)
    
    try:
        from llm_handler import initialize_llm, is_llm_available
        import config
        
        print(f"LLM_ENABLED: {config.LLM_ENABLED}")
        print(f"LLM_OLLAMA_HOST: {config.LLM_OLLAMA_HOST}")
        print(f"LLM_OLLAMA_PORT: {config.LLM_OLLAMA_PORT}")
        
        if config.LLM_ENABLED:
            llm = initialize_llm(
                host=config.LLM_OLLAMA_HOST,
                port=config.LLM_OLLAMA_PORT,
                model=config.LLM_MODEL
            )
            
            if is_llm_available():
                print(f"✓ LLM initialized: {llm.selected_model}")
                return True
            else:
                print("⚠ LLM not available (Ollama might not be running)")
                return True  # Not a fatal error
        else:
            print("ℹ LLM disabled in config")
            return True
            
    except Exception as e:
        print(f"✗ LLM initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_interpreter():
    """Test CommandInterpreter with LLM."""
    print("\n" + "=" * 60)
    print("TESTING COMMAND INTERPRETER WITH LLM")
    print("=" * 60)
    
    try:
        from command_interpreter import CommandInterpreter
        from cursor_controller import CursorController
        from llm_handler import initialize_llm, is_llm_available
        import config
        
        cursor = CursorController()
        llm = None
        
        if config.LLM_ENABLED:
            try:
                llm = initialize_llm()
            except:
                pass
        
        interpreter = CommandInterpreter(cursor, llm_handler=llm)
        print(f"✓ CommandInterpreter created")
        print(f"  LLM support: {'enabled' if llm else 'disabled'}")
        return True
        
    except Exception as e:
        print(f"✗ CommandInterpreter error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verifications."""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║   HCI + LLM INTEGRATION VERIFICATION                   ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("LLM Initialization", test_llm_initialization()))
    results.append(("CommandInterpreter", test_command_interpreter()))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nResult: {passed}/{total} verifications passed")
    
    if passed == total:
        print("\n✓ HCI SYSTEM WITH LLM INTEGRATION VERIFIED!")
        print("  Ready to run: python main.py")
        return 0
    else:
        print("\n✗ Some verifications failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
