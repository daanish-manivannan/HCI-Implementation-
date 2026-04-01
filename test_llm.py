#!/usr/bin/env python3
"""
test_llm.py
───────────
Test LLM integration with Ollama.

Tests:
  1. Ollama service availability
  2. Model detection
  3. Model inference
  4. Voice command enhancement
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_handler import initialize_llm, get_llm, is_llm_available

def test_ollama_connectivity():
    """Test 1: Check if Ollama is running."""
    print("\n" + "="*60)
    print("TEST 1: OLLAMA CONNECTIVITY")
    print("="*60)
    
    llm = initialize_llm()
    is_available, status = llm.health_check()
    print(f"Status: {status}")
    
    if is_available:
        print(f"✓ Ollama is accessible")
        print(f"✓ Models available: {', '.join(llm.available_models)}")
        return True
    else:
        print(f"✗ Ollama is not accessible at {llm.base_url}")
        print(f"\nTo start Ollama, run: ollama serve")
        return False

def test_model_detection():
    """Test 2: Verify model selection."""
    print("\n" + "="*60)
    print("TEST 2: MODEL DETECTION")
    print("="*60)
    
    llm = get_llm()
    if not llm:
        print("✗ LLM not initialized")
        return False
    
    print(f"✓ Selected model: {llm.selected_model}")
    print(f"  Is available: {llm.is_available}")
    
    if llm.is_available:
        print(f"✓ Model is ready for inference")
        return True
    else:
        print(f"✗ Model not available for inference")
        return False

def test_simple_inference():
    """Test 3: Run a simple inference."""
    print("\n" + "="*60)
    print("TEST 3: SIMPLE INFERENCE")
    print("="*60)
    
    llm = get_llm()
    if not llm or not llm.is_available:
        print("✗ LLM not available for inference")
        return False
    
    print(f"Sending request to {llm.selected_model}...")
    print("(This may take a moment for first load...)\n")
    
    success, response = llm.generate("What is 2+2?")
    
    if success:
        print(f"✓ Model responded:")
        print(f"  Response: {response[:100]}..." if len(response) > 100 else f"  Response: {response}")
        return True
    else:
        print(f"✗ Model failed: {response}")
        return False

def test_command_enhancement():
    """Test 4: Voice command enhancement."""
    print("\n" + "="*60)
    print("TEST 4: VOICE COMMAND ENHANCEMENT")
    print("="*60)
    
    llm = get_llm()
    if not llm or not llm.is_available:
        print("✗ LLM not available for enhancement")
        return False
    
    test_inputs = [
        "i want to press the left button",
        "scroll down on this page",
        "go to the address bar"
    ]
    
    print("Testing voice command interpretation:\n")
    
    for voice_input in test_inputs:
        print(f"Voice input: '{voice_input}'")
        success, interpretation = llm.enhance_command(voice_input)
        
        if success:
            print(f"  Interpretation: {interpretation[:80]}...")
        else:
            print(f"  Error: {interpretation}")
        print()
    
    return True

def test_ollama_status():
    """Test 5: Show Ollama service status."""
    print("\n" + "="*60)
    print("TEST 5: OLLAMA STATUS")
    print("="*60)
    
    llm = get_llm()
    print(f"Ollama Server: {llm.base_url}")
    print(f"Selected Model: {llm.selected_model}")
    print(f"Available Models: {len(llm.available_models) if llm._available_models else 'Unknown'}")
    
    if llm._available_models:
        for model in llm._available_models:
            marker = "→" if model == llm.selected_model else " "
            print(f"  {marker} {model}")
    
    print(f"LLM Ready: {'✓' if llm.is_available else '✗'}")
    
    return True

def main():
    """Run all tests."""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║         HCI PROJECT - LLM INTEGRATION TEST SUITE          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Test 1: Connectivity
    if test_ollama_connectivity():
        results.append(("Ollama Connectivity", True))
        
        # Only run other tests if Ollama is available
        results.append(("Model Detection", test_model_detection()))
        results.append(("Simple Inference", test_simple_inference()))
        results.append(("Command Enhancement", test_command_enhancement()))
    else:
        results.append(("Ollama Connectivity", False))
        print("\n⚠ Skipping other tests - Ollama is not running.")
        print("\nTo start Ollama:")
        print("  1. Open a new terminal")
        print("  2. Run: ollama serve")
        print("  3. Wait for startup message")
        print("  4. Re-run this test")
    
    test_ollama_status()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ LLM INTEGRATION SUCCESSFUL!")
        print("The HCI project is ready to use LLM features.")
        return 0
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
