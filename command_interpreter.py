"""
command_interpreter.py
──────────────────────
Translates blink events [+] voice Command enums into concrete
cursor / keyboard actions via CursorController.

Acts as the glue layer between perception (blink, gaze, voice)
and action (cursor, keyboard).

Supports:
  - Blink gestures (single/double/long)
  - Voice commands with state validation
  - Human-friendly status messages
  - Confidence-aware command execution
"""

import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import SCROLL_LINES
from cursor_controller import CursorController
from voice_recognition import Command

# Setup logging
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


class CommandInterpreter:
    """
    Maps high-level events to OS actions.

    Blink events
    ────────────
    single_blink  → left click
    double_blink  → double click
    long_blink    → toggle drag mode

    Voice commands
    ──────────────
    See voice_recognition.Command enum for full list.
    Includes confidence scoring support.
    """

    def __init__(self, cursor: CursorController):
        self._cursor = cursor
        self.status_message = ""          # Last action taken (for overlay display)
        self.last_command = None          # Last successfully executed command
        self.last_confidence = 0.0        # Confidence of last command match
        logger.info("CommandInterpreter initialized")

    # ── Blink actions ────────────────────────
    def handle_blink(self, blink_type: str) -> None:
        """
        Handle blink events and execute corresponding actions.
        blink_type: "single" | "double" | "long"
        """
        try:
            if blink_type == "double":
                self._cursor.double_click()
                self.status_message = "[MOUSE] Double-click"
                logger.info("[Blink] Double-click executed")
            elif blink_type == "single":
                self._cursor.left_click()
                self.status_message = "[MOUSE] Left-click"
                logger.info("[Blink] Single-click executed")
            elif blink_type == "long":
                dragging = self._cursor.toggle_drag()
                self.status_message = "[PIN] Drag START" if dragging else "[PIN] Drag END"
                logger.info("[Blink] Drag mode toggled: %s", dragging)
            else:
                logger.warning("[Blink] Unknown blink type: %s", blink_type)
        except Exception as exc:
            logger.error("[Blink] Error executing blink action: %s", exc)
            self.status_message = "[ERROR] Blink failed"

    # ── Voice actions ────────────────────────
    def handle_voice_command(self, cmd: Command, text: str, confidence: float = 1.0) -> str:
        """
        Execute voice command and return human-readable status.
        
        Args:
            cmd: Command enum value
            text: Payload text (for TYPE_TEXT commands, etc.)
            confidence: Match confidence (0.0-1.0)
        
        Returns:
            Status message for UI display
        """
        if cmd is None:
            logger.warning("[Voice] Attempted to execute None command")
            self.status_message = "[MUTED] [NO-MATCH]"
            return "No command matched"
        
        # Log command attempt with confidence
        confidence_str = "[OK]" * int(confidence * 5)  # Visual confidence indicator
        logger.info("[Voice] Executing %s (conf=%.2f) %s", cmd.name, confidence, confidence_str)
        
        try:
            c = self._cursor
            msg = ""

            if cmd == Command.SCROLL_UP:
                c.scroll(SCROLL_LINES)
                msg = "[UP] Scroll up"

            elif cmd == Command.SCROLL_DOWN:
                c.scroll(-SCROLL_LINES)
                msg = "[DOWN] Scroll down"

            elif cmd == Command.GO_BACK:
                c.hotkey("alt", "left")
                msg = "[BACK] Go back"

            elif cmd == Command.GO_FORWARD:
                c.hotkey("alt", "right")
                msg = "[FWD] Go forward"

            elif cmd == Command.CLICK:
                c.left_click()
                msg = "[TAP] Click"

            elif cmd == Command.RIGHT_CLICK:
                c.right_click()
                msg = "[MOUSE] Right-click"

            elif cmd == Command.DOUBLE_CLICK:
                c.double_click()
                msg = "[TAP][TAP] Double-click"

            elif cmd == Command.COPY:
                c.hotkey("ctrl", "c")
                msg = "[COPY] Copy"

            elif cmd == Command.PASTE:
                c.hotkey("ctrl", "v")
                msg = "[PIN] Paste"

            elif cmd == Command.UNDO:
                c.hotkey("ctrl", "z")
                msg = "[UNDO] Undo"

            elif cmd == Command.REDO:
                c.hotkey("ctrl", "y")
                msg = "[REDO] Redo"

            elif cmd == Command.SELECT_ALL:
                c.hotkey("ctrl", "a")
                msg = "[OK] Select all"

            elif cmd == Command.ZOOM_IN:
                c.hotkey("ctrl", "plus")
                msg = "[ZOOM][+] Zoom in"

            elif cmd == Command.ZOOM_OUT:
                c.hotkey("ctrl", "minus")
                msg = "[ZOOM-] Zoom out"

            elif cmd == Command.ZOOM_RESET:
                c.hotkey("ctrl", "0")
                msg = "[ZOOM] Zoom reset"

            elif cmd == Command.OPEN_BROWSER:
                import subprocess
                try:
                    if sys.platform == "win32":
                        subprocess.Popen(["start", "https://www.google.com"], shell=True)
                    else:
                        subprocess.Popen(["xdg-open", "https://www.google.com"])
                    msg = "[WEB] Browser opened"
                except Exception as e:
                    logger.error("Failed to open browser: %s", e)
                    c.hotkey("super")   # fallback: open launcher
                    msg = "[DESKTOP] Launcher opened"

            elif cmd == Command.CLOSE_WINDOW:
                c.hotkey("alt", "F4")
                msg = "[X] Close window"

            elif cmd == Command.NEW_TAB:
                c.hotkey("ctrl", "t")
                msg = "[+] New tab"

            elif cmd == Command.CLOSE_TAB:
                c.hotkey("ctrl", "w")
                msg = "[X] Close tab"

            elif cmd == Command.SWITCH_TAB:
                c.hotkey("ctrl", "tab")
                msg = "➤ Switch tab"

            elif cmd == Command.TAKE_SCREENSHOT:
                c.hotkey("ctrl", "shift", "s")
                msg = "[SCREENSHOT] Screenshot"

            elif cmd == Command.TYPE_TEXT:
                clean = _strip_fillers(text) if text else ""
                if clean:
                    c.type_text(clean)
                    display_text = clean[:30] + ("..." if len(clean) > 30 else "")
                    msg = f"[TYPE] Typed: {display_text}"
                    logger.info("[Voice] Typed text (%d chars): %s", len(clean), clean[:50])
                else:
                    msg = "[TYPE] (empty text)"
                    logger.warning("[Voice] TYPE_TEXT with empty payload")

            # ── Windows System Commands ──────────────────────
            elif cmd == Command.OPEN_APP:
                logger.info("[Voice] >>> OPEN_APP handler called with app_name='%s'", text)
                try:
                    from windows_commands import WindowsCommandHandler
                    app_name = text if text else "notepad"
                    logger.info("[Voice] >>> Calling WindowsCommandHandler.launch_app('%s')", app_name)
                    msg = WindowsCommandHandler.launch_app(app_name)
                    logger.info("[Voice] >>> App launch result: %s", msg)
                except ImportError as e:
                    msg = f"ERROR: Windows commands module not found: {e}"
                    logger.error("[Voice] >>> Import error: %s", e)
                except Exception as e:
                    msg = f"ERROR: Failed to launch app: {e}"
                    logger.error("[Voice] >>> Exception during launch: %s", e)

            elif cmd == Command.OPEN_FOLDER:
                try:
                    from windows_commands import WindowsCommandHandler
                    folder_path = text if text else os.path.expanduser("~/Desktop")
                    msg = WindowsCommandHandler.open_folder(folder_path)
                    logger.info("[Windows] Opened folder: %s", folder_path)
                except Exception as e:
                    msg = f"[ERROR] Error opening folder: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.OPEN_WEBSITE:
                try:
                    from windows_commands import WindowsCommandHandler
                    url = text if text else "google.com"
                    msg = WindowsCommandHandler.open_website(url)
                    logger.info("[Windows] Opened website: %s", url)
                except Exception as e:
                    msg = f"[ERROR] Error opening website: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.MINIMIZE_ALL:
                try:
                    from windows_commands import WindowsCommandHandler
                    msg = WindowsCommandHandler.minimize_all()
                    logger.info("[Windows] Minimized all windows")
                except Exception as e:
                    msg = f"[ERROR] Error minimizing windows: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.TOGGLE_DARK_MODE:
                try:
                    from windows_commands import WindowsCommandHandler
                    msg = WindowsCommandHandler.toggle_dark_mode()
                    logger.info("[Windows] Toggled dark mode")
                except Exception as e:
                    msg = f"[ERROR] Error toggling dark mode: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.LOCK_SCREEN:
                try:
                    from windows_commands import WindowsCommandHandler
                    msg = WindowsCommandHandler.lock_screen()
                    logger.info("[Windows] Locked screen")
                except Exception as e:
                    msg = f"[ERROR] Error locking screen: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.OPEN_SETTINGS:
                try:
                    from windows_commands import WindowsCommandHandler
                    category = text if text else None
                    msg = WindowsCommandHandler.open_settings(category)
                    logger.info("[Windows] Opened settings: %s", category or "main")
                except Exception as e:
                    msg = f"[ERROR] Error opening settings: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.OPEN_CALCULATOR:
                try:
                    from windows_commands import WindowsCommandHandler
                    msg = WindowsCommandHandler.open_calculator()
                    logger.info("[Windows] Opened calculator")
                except Exception as e:
                    msg = f"[ERROR] Error opening calculator: {e}"
                    logger.error("[Windows] Error: %s", e)

            elif cmd == Command.REFRESH_SCREEN:
                try:
                    from windows_commands import WindowsCommandHandler
                    msg = WindowsCommandHandler.refresh_screen()
                    logger.info("[Windows] Refreshed screen")
                except Exception as e:
                    msg = f"[ERROR] Error refreshing screen: {e}"
                    logger.error("[Windows] Error: %s", e)

            # ── Code Generation Commands ─────────────────────
            elif cmd == Command.GENERATE_CODE:
                try:
                    from code_generator import CodeGenerator
                    code_request = text if text else "hello world"
                    code, gen_msg = CodeGenerator.generate_code(code_request)
                    if code:
                        msg = f"[Generated Code]\n{code[:50]}...\n(Use 'open code in editor' to save it)"
                        logger.info("[CodeGen] Generated code: %s", gen_msg)
                    else:
                        msg = "[ERROR] Failed to generate code"
                        logger.error("[CodeGen] Generation failed for: %s", code_request)
                except ImportError as e:
                    msg = f"[ERROR] Code generator module not found: {e}"
                    logger.error("[CodeGen] Import error: %s", e)
                except Exception as e:
                    msg = f"[ERROR] Error generating code: {e}"
                    logger.error("[CodeGen] Error: %s", e)

            elif cmd == Command.EXECUTE_CODE:
                try:
                    from code_generator import CodeGenerator
                    code_request = text if text else "hello world"
                    
                    # Generate the code first
                    code, gen_msg = CodeGenerator.generate_code(code_request)
                    if not code:
                        msg = f"[ERROR] Could not generate code for: {code_request}"
                        logger.error("[CodeGen] Failed to generate code")
                    else:
                        # Detect language from request
                        language = CodeGenerator.detect_language(code_request)
                        
                        # Execute it
                        success, output = CodeGenerator.execute_code(code, language)
                        if success:
                            display_output = output[:100] + ("..." if len(output) > 100 else "")
                            msg = f"[EXECUTED]\n{display_output}"
                            logger.info("[CodeGen] Execution output: %s", output[:200])
                        else:
                            msg = f"[ERROR] Execution failed:\n{output}"
                            logger.error("[CodeGen] Execution error: %s", output)
                except ImportError as e:
                    msg = f"[ERROR] Code generator module not found: {e}"
                    logger.error("[CodeGen] Import error: %s", e)
                except Exception as e:
                    msg = f"[ERROR] Error executing code: {e}"
                    logger.error("[CodeGen] Error: %s", e)

            elif cmd == Command.OPEN_CODE_IN_EDITOR:
                try:
                    from code_generator import CodeGenerator
                    code_request = text if text else "hello world"
                    
                    # Generate the code
                    code, gen_msg = CodeGenerator.generate_code(code_request)
                    if code:
                        language = CodeGenerator.detect_language(code_request)
                        msg = CodeGenerator.open_in_editor(code, language)
                        logger.info("[CodeGen] Opened in editor: %s", msg)
                    else:
                        msg = f"[ERROR] Could not generate code for: {code_request}"
                        logger.error("[CodeGen] Failed to generate code")
                except ImportError as e:
                    msg = f"[ERROR] Code generator module not found: {e}"
                    logger.error("[CodeGen] Import error: %s", e)
                except Exception as e:
                    msg = f"[ERROR] Error: {e}"
                    logger.error("[CodeGen] Error: %s", e)

            else:
                logger.warning("[Voice] Unhandled command type: %s", cmd.name)
                msg = f"[WARN] {cmd.name}"

            self.last_command = cmd
            self.last_confidence = confidence
            self.status_message = msg
            logger.info("[Voice] [OK] Successfully executed: %s", msg)
            return msg

        except Exception as exc:
            logger.error("[Voice] Error executing command %s: %s", cmd.name, exc, exc_info=True)
            self.status_message = "[ERROR] Command failed"
            return f"Error: {cmd.name}"


# ── Helpers ─────────────────────────────────
_FILLERS = {
    "um", "uh", "er", "hmm", "like", "you know",
    "basically", "literally", "actually",
}

def _strip_fillers(text: str) -> str:
    words = text.lower().split()
    clean = [w for w in words if w not in _FILLERS]
    return " ".join(clean)
