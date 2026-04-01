#!/usr/bin/env python3
"""
LLM INTEGRATION QUICK START GUIDE
═══════════════════════════════════════════════════════════════════════════════

PROJECT: HCI (Hands-Free Human-Computer Interaction) System
STATUS: ✓ LLM FULLY INTEGRATED & TESTED
MODEL: llama3:8b (8B parameters, 4.7 GB)

═══════════════════════════════════════════════════════════════════════════════
QUICK START
═══════════════════════════════════════════════════════════════════════════════

1. VERIFY OLLAMA IS RUNNING
   ────────────────────────
   Open a new terminal and run:
      ollama serve
   
   You should see:
      Listening on 127.0.0.1:11434

2. START THE HCI SYSTEM
   ─────────────────────
   In your project directory:
      python main.py
   
   The system will initialize:
      ✓ Webcam and face detection
      ✓ Voice recognition
      ✓ LLM (llama3:8b)
      ✓ Gaze and blink tracking


═══════════════════════════════════════════════════════════════════════════════
WHAT'S NEW - LLM FEATURES
═══════════════════════════════════════════════════════════════════════════════

✓ Model Detection
  - Automatically detects available Ollama models
  - Prefers llama3:8b (highest quality)
  - Falls back to llama3.2:3b or qwen2.5-coder:7b if needed

✓ Voice Command Enhancement
  - LLM understands natural voice input
  - Maps "i want to press the left button" → "left click"
  - Handles varied phrasing and intent

✓ Intelligent Interpretation
  - LLM provides semantic understanding of commands
  - Better handles ambiguous or poorly recognized speech
  - Works alongside fuzzy matching for robustness

✓ Graceful Degradation
  - If Ollama unavailable, system continues without LLM
  - Falls back to local matching algorithms
  - No performance impact when LLM disabled


═══════════════════════════════════════════════════════════════════════════════
CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

Location: config.py

Key Settings:
   LLM_ENABLED = True                    # Enable/disable LLM features
   LLM_OLLAMA_HOST = "localhost"         # Ollama server address
   LLM_OLLAMA_PORT = 11434               # Ollama server port
   LLM_TIMEOUT = 30.0                    # Request timeout (seconds)
   LLM_MODEL = None                      # Auto-detect (or set specific model)
   LLM_ENHANCE_VOICE_COMMANDS = True     # Enable voice enhancement

Model Preference Order (auto-selected):
   1. llama3:8b           (8B params) - BEST QUALITY ⭐
   2. llama3.2:3b         (3B params) - Lightweight
   3. qwen2.5-coder:7b    (7B params) - Code-focused


═══════════════════════════════════════════════════════════════════════════════
TESTING
═══════════════════════════════════════════════════════════════════════════════

Test LLM Integration:
   python test_llm.py
   
   Tests:
   ✓ Ollama connectivity
   ✓ Model detection
   ✓ Inference (2+2=?)
   ✓ Voice command enhancement

Verify Full Integration:
   python verify_integration.py
   
   Tests:
   ✓ All module imports
   ✓ LLM initialization
   ✓ CommandInterpreter with LLM


═══════════════════════════════════════════════════════════════════════════════
AVAILABLE MODELS
═══════════════════════════════════════════════════════════════════════════════

Currently Installed:
   ✓ llama3:8b           → 4.7 GB (Primary, 8B params)
   ✓ llama3.2:3b         → 2.0 GB (Lightweight, 3B params)
   ✓ qwen2.5-coder:7b    → 4.7 GB (Code-focused, 7B params)

Check Available Models:
   ollama list

Pull Additional Models:
   ollama pull llama3.1:8b    # Alternative 8B llama
   ollama pull mistral:7b     # Mistral (fast, ~4.1 GB)
   ollama pull neural-chat    # Optimized for chat


═══════════════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Issue: "Ollama not running"
Solution:
   1. Ensure Ollama is installed (https://ollama.ai)
   2. Open terminal and run: ollama serve
   3. Keep terminal open while running HCI system

Issue: Model not found
Solution:
   1. Check: ollama list (see installed models)
   2. Pull model: ollama pull llama3:8b
   3. Wait for download to complete (~5-10 minutes)

Issue: LLM very slow or timing out
Solution:
   1. Increase timeout in config.py: LLM_TIMEOUT = 60.0
   2. Use smaller model: llama3.2:3b
   3. Check system resources (RAM, CPU)

Issue: "ModuleNotFoundError: llm_handler"
Solution:
   1. Ensure you're in the project directory
   2. Check: python -c "import sys; print(sys.path)"
   3. Project root should be in Python path


═══════════════════════════════════════════════════════════════════════════════
PERFORMANCE NOTES
═══════════════════════════════════════════════════════════════════════════════

First Inference: May take 5-10 seconds (model loading)
Subsequent Inferences: ~1-3 seconds (llama3:8b on moderate hardware)

To Improve Performance:
   1. Use GPU if available
      ollama serve --gpu all    # Use all GPU memory
   
   2. Reduce model size
      Switch to llama3.2:3b (~0.5-1 sec per inference)
   
   3. Increase system RAM
      llama3:8b needs ~10-12 GB total system RAM
   
   4. Close other applications


═══════════════════════════════════════════════════════════════════════════════
API ENDPOINTS (For Custom Integration)
═══════════════════════════════════════════════════════════════════════════════

Ollama API: http://localhost:11434

Generate Endpoint:
   POST /api/generate
   {
     "model": "llama3:8b",
     "prompt": "What is 2+2?",
     "stream": false
   }

List Models Endpoint:
   GET /api/tags

Example (Python):
   from llm_handler import initialize_llm, is_llm_available, get_llm
   
   llm = initialize_llm()
   if is_llm_available():
      success, response = llm.generate("Hello!")
      print(response)


═══════════════════════════════════════════════════════════════════════════════
FILES CREATED/MODIFIED
═══════════════════════════════════════════════════════════════════════════════

New Files:
   ✓ llm_handler.py              - LLM abstraction layer
   ✓ test_llm.py                 - LLM functionality tests
   ✓ verify_integration.py        - Integration verification

Modified Files:
   ✓ main.py                      - Added LLM initialization
   ✓ config.py                    - Added LLM configuration options
   ✓ command_interpreter.py       - Added LLM support parameter

═══════════════════════════════════════════════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

1. Start Ollama:           ollama serve
2. Run main system:        python main.py
3. Calibrate (press C)
4. Speak commands naturally
5. Watch console for [LLM] messages showing enhancements

Enjoy your AI-enhanced hands-free system! 🚀
"""

if __name__ == "__main__":
    print(__doc__)
