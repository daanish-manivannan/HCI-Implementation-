"""
llm_agent.py
────────────
Natural Language parser using a local Ollama model.
Translates conversational user instructions into strict system Enums & payloads.
"""

import json
import logging
import requests
from voice_recognition import Command

logger = logging.getLogger(__name__)

# Configurable options
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"  # Change to your locally pulled model (e.g. 'mistral', 'llama3')

PROMPT_TEMPLATE = """You are the Natural Language engine for a Hands-Free computer control system.
The user will speak a phrase. Your job is to classify this phrase into ONE of the system's strict Command enums.
If the command requires specific target information (like the name of an app to open, or code to generate), provide it in the payload.

Available Commands:
- CLICK, DOUBLE_CLICK, RIGHT_CLICK
- SCROLL_UP, SCROLL_DOWN
- GO_BACK, GO_FORWARD
- COPY, PASTE, UNDO, REDO, SELECT_ALL
- ZOOM_IN, ZOOM_OUT, ZOOM_RESET
- OPEN_BROWSER, NEW_TAB, CLOSE_TAB, SWITCH_TAB, CLOSE_WINDOW
- TAKE_SCREENSHOT
- PAUSE_TRACKING, RESUME_TRACKING, CALIBRATE, STOP
- OPEN_APP (Payload: name of app, e.g. 'calculator', 'chrome')
- OPEN_WEBSITE (Payload: domain name, e.g. 'github.com')
- TOGGLE_DARK_MODE, MINIMIZE_ALL, LOCK_SCREEN
- GENERATE_CODE (Payload: what code they want to generate, e.g. 'python hello world')
- EXECUTE_CODE (Payload: what code they want to execute)
- TYPE_TEXT (Payload: the exact text to type like a keyboard)

Respond STRICTLY in valid JSON format with no markdown, no backticks, and no extra text.
Format:
{
  "command": "COMMAND_NAME",
  "payload": "optional payload text or null string"
}

User phrase: "%s"
"""

def parse_natural_language(phrase: str) -> tuple[Command, str]:
    """
    Passes the spoken phrase to Ollama and returns the mapped Command and payload.
    Returns (None, "") if parsing fails.
    """
    if not phrase or len(phrase.strip()) < 2:
        return None, ""

    prompt = PROMPT_TEMPLATE % phrase

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"    # Forces Ollama to output valid JSON
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=5.0)
        response.raise_for_status()
        
        data = response.json()
        result_text = data.get("response", "").strip()
        
        parsed = json.loads(result_text)
        cmd_str = parsed.get("command", "")
        payload_str = parsed.get("payload", "")

        # Handle nulls
        if payload_str is None:
            payload_str = ""

        # Map string to Enum
        try:
            cmd_enum = Command[cmd_str]
            logger.info(f"[LLM] Successfully mapped '{phrase}' to {cmd_enum.name} (Payload: '{payload_str}')")
            return cmd_enum, str(payload_str)
        except KeyError:
            logger.warning(f"[LLM] Invalid command returned by model: '{cmd_str}'")
            return None, ""

    except requests.exceptions.ConnectionError:
        logger.error(f"[LLM] Failed to connect to Ollama at {OLLAMA_URL}. Is it running?")
    except requests.exceptions.Timeout:
        logger.error("[LLM] Ollama response timed out.")
    except json.JSONDecodeError as e:
        logger.error(f"[LLM] Failed to parse JSON from model: {e}")
    except Exception as e:
        logger.error(f"[LLM] Unexpected error: {e}")

    return None, ""
