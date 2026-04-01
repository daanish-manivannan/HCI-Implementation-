"""
code_generator.py
─────────────────
Voice-driven code generation and execution.

Supports:
  - Simple code snippets (hello world, etc.)
  - Algorithm implementations (palindrome, fibonacci, etc.)
  - Error fixing and auto-execution
  - Language auto-detection
  - Multi-language support: Python, Java, C++, JavaScript, etc.
"""

import logging
import subprocess
import tempfile
import os
import sys
from typing import Dict, Tuple, Optional
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


class CodeGenerator:
    """
    Generates and executes code snippets based on voice instructions.
    """

    # Common code snippets for various languages and patterns
    SNIPPETS = {
        # Hello World variations
        ("hello world", "python"): '''print("Hello, World!")''',
        ("hello world", "java"): '''public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}''',
        ("hello world", "java_simple"): '''System.out.println("Hello, World!");''',
        ("hello world", "cpp"): '''#include <iostream>
using namespace std;
int main() {
    cout << "Hello, World!" << endl;
    return 0;
}''',
        ("hello world", "javascript"): '''console.log("Hello, World!");''',
        ("hello world", "csharp"): '''using System;
class Program {
    static void Main() {
        Console.WriteLine("Hello, World!");
    }
}''',
        
        # Palindrome
        ("palindrome", "python"): '''def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

test = "racecar"
print(f"{test} is palindrome: {is_palindrome(test)}")
print(f"civic is palindrome: {is_palindrome('civic')}")''',

        ("palindrome", "java"): '''public class Palindrome {
    public static boolean isPalindrome(String s) {
        s = s.toLowerCase().replaceAll("\\\\s", "");
        return s.equals(new StringBuilder(s).reverse().toString());
    }
    
    public static void main(String[] args) {
        System.out.println("racecar: " + isPalindrome("racecar"));
        System.out.println("civic: " + isPalindrome("civic"));
    }
}''',

        ("palindrome", "javascript"): '''function isPalindrome(s) {
    s = s.toLowerCase().replace(/\\s/g, "");
    return s === s.split("").reverse().join("");
}

console.log("racecar: " + isPalindrome("racecar"));
console.log("civic: " + isPalindrome("civic"));''',
        
        # Factorial
        ("factorial", "python"): '''def factorial(n):
    if n < 0:
        return "Invalid input"
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

print(f"5! = {factorial(5)}")
print(f"10! = {factorial(10)}")''',

        ("factorial", "javascript"): '''function factorial(n) {
    if (n < 0) return "Invalid input";
    if (n === 0 || n === 1) return 1;
    return n * factorial(n - 1);
}

console.log("5! = " + factorial(5));
console.log("10! = " + factorial(10));''',

        # Fibonacci
        ("fibonacci", "python"): '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("Fibonacci sequence (first 10):")
for i in range(10):
    print(fibonacci(i), end=" ")''',

        ("fibonacci", "javascript"): '''function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

console.log("Fibonacci sequence (first 10):");
for (let i = 0; i < 10; i++) {
    process.stdout.write(fibonacci(i) + " ");
}''',

        # Prime number checker
        ("prime number", "python"): '''def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

print("Prime numbers up to 20:")
for i in range(20):
    if is_prime(i):
        print(i, end=" ")''',

        # Reverse string
        ("reverse string", "python"): '''text = "Hello World"
reversed_text = text[::-1]
print(f"Original: {text}")
print(f"Reversed: {reversed_text}")''',

        ("reverse string", "javascript"): '''let text = "Hello World";
let reversed = text.split("").reverse().join("");
console.log("Original: " + text);
console.log("Reversed: " + reversed);''',

        # Sum of numbers
        ("sum numbers", "python"): '''numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = sum(numbers)
print(f"Numbers: {numbers}")
print(f"Sum: {total}")''',
    }

    LANGUAGE_EXTENSIONS = {
        "python": ".py",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c",
        "javascript": ".js",
        "csharp": ".cs",
    }

    LANGUAGE_EXECUTORS = {
        "python": "python",
        "javascript": "node",
        "java": "java",
        "cpp": "a.exe",  # After compilation
        "c": "a.exe",
    }

    def __init__(self):
        logger.info("CodeGenerator initialized")

    @staticmethod
    def detect_language(request: str) -> str:
        """
        Detect programming language from request.
        
        Returns: "python", "java", "javascript", "cpp", "csharp", etc.
        """
        request_lower = request.lower()
        
        languages = {
            "python": ["python", "py"],
            "java": ["java"],
            "javascript": ["javascript", "js", "node"],
            "cpp": ["cpp", "c++", "cplus"],
            "c": ["c ", "c language"],
            "csharp": ["csharp", "c#"],
        }
        
        for lang, keywords in languages.items():
            for keyword in keywords:
                if keyword in request_lower:
                    logger.info("[CodeGen] Detected language: %s", lang)
                    return lang
        
        # Default to Python
        logger.info("[CodeGen] No language specified, defaulting to Python")
        return "python"

    @staticmethod
    def generate_code(request: str, language: str = None) -> Tuple[str, str]:
        """
        Generate code snippet based on request.
        
        Args:
            request: What code to generate (e.g., "hello world", "palindrome")
            language: Optional language (auto-detected if not specified)
        
        Returns:
            (code, message)
        """
        try:
            if language is None:
                language = CodeGenerator.detect_language(request)
            
            request_lower = request.lower()
            
            # Try to find matching snippet
            for (pattern, lang), code in CodeGenerator.SNIPPETS.items():
                if pattern in request_lower and lang == language:
                    logger.info("[CodeGen] Found matching snippet: %s (%s)", pattern, lang)
                    return code, f"✓ Generated {pattern} in {language}"
            
            # Fallback: create a basic hello world if nothing matches
            logger.warning("[CodeGen] No matching snippet found for: %s", request)
            default_code = CodeGenerator.SNIPPETS.get(
                ("hello world", language),
                'print("Generated code snippet")'
            )
            return default_code, f"Generated basic code in {language}"
        
        except Exception as e:
            logger.error("[CodeGen] Error generating code: %s", e)
            return "", f"❌ Error: {str(e)}"

    @staticmethod
    def execute_code(code: str, language: str = "python") -> Tuple[bool, str]:
        """
        Execute code snippet and return results.
        
        Args:
            code: Code to execute
            language: Programming language
        
        Returns:
            (success, output)
        """
        temp_file = None
        try:
            language_lower = language.lower()
            ext = CodeGenerator.LANGUAGE_EXTENSIONS.get(language_lower, ".py")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            logger.info("[CodeGen] Created temp file: %s", temp_file)
            
            # Execute based on language
            if language_lower == "python":
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif language_lower == "javascript":
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif language_lower == "java":
                # Compile first
                class_name = Path(temp_file).stem
                compile_result = subprocess.run(
                    ["javac", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if compile_result.returncode != 0:
                    return False, f"Compilation error:\n{compile_result.stderr}"
                
                # Run
                result = subprocess.run(
                    ["java", "-cp", os.path.dirname(temp_file), class_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                return False, f"❌ Language '{language}' execution not supported yet"
            
            if result.returncode != 0:
                logger.error("[CodeGen] Execution error: %s", result.stderr)
                return False, f"Execution error:\n{result.stderr}"
            
            output = result.stdout.strip()
            logger.info("[CodeGen] Execution successful: %s", output[:100])
            return True, output
        
        except subprocess.TimeoutExpired:
            logger.error("[CodeGen] Code execution timeout")
            return False, "❌ Execution timeout (exceeded 30 seconds)"
        except Exception as e:
            logger.error("[CodeGen] Error executing code: %s", e)
            return False, f"❌ Error: {str(e)}"
        finally:
            # Cleanup
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.debug("[CodeGen] Cleaned up temp file: %s", temp_file)
                except:
                    pass

    # Ordered list of editors to try in "auto" mode.
    # Each entry: (display_name, [command, ...])
    # The file path is appended as the last argument.
    EDITOR_CHAINS = [
        ("VS Code",        ["code"]),
        ("Notepad++",      ["notepad++", "notepad++.exe"]),
        ("Sublime Text",   ["subl", "sublime_text"]),
        ("Atom",           ["atom"]),
        ("Notepad",        ["notepad"]),  # Always available on Windows — last resort
    ]

    # Map config.PREFERRED_EDITOR string → command list (exact/forced pick)
    EDITOR_COMMANDS = {
        "vscode":          ["code"],
        "notepadplusplus": ["notepad++", "notepad++.exe"],
        "sublime":         ["subl", "sublime_text"],
        "atom":            ["atom"],
        "notepad":         ["notepad"],
    }

    # Known Windows installation paths to probe when the command is not on PATH.
    # Each value is a list of glob-friendly partial paths under common roots.
    _WIN_EDITOR_PATHS = {
        "code": [
            r"Microsoft VS Code\bin\code.cmd",
            r"Microsoft VS Code\Code.exe",
        ],
        "notepad++": [
            r"Notepad++\notepad++.exe",
        ],
        "subl": [
            r"Sublime Text\subl.exe",
            r"Sublime Text 3\subl.exe",
            r"Sublime Text 4\subl.exe",
        ],
        "atom": [
            r"atom\atom.exe",
        ],
    }

    @classmethod
    def _resolve_editor_exe(cls, cmd: str) -> str:
        """
        Return the best executable path for *cmd*.
        1. If *cmd* is already on PATH, return it as-is.
        2. Otherwise probe known Windows install locations.
        Falls back to returning *cmd* unchanged so the caller can still try.
        """
        import shutil, os
        if shutil.which(cmd):
            return cmd
        # Probe common install roots
        roots = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            os.path.expandvars(r"%PROGRAMFILES%"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%"),
        ]
        for suffix_list in (cls._WIN_EDITOR_PATHS.get(cmd) or []):
            for root in roots:
                candidate = os.path.join(root, suffix_list)
                if os.path.isfile(candidate):
                    logger.debug("[CodeGen] Resolved '%s' -> %s", cmd, candidate)
                    return candidate
        return cmd  # give up — let the caller try anyway

    @staticmethod
    def _try_launch_editor(commands: list, filepath: str) -> bool:
        """Try each executable in *commands* until one succeeds. Returns True on success."""
        import sys, shutil
        for cmd in commands:
            resolved = CodeGenerator._resolve_editor_exe(cmd)
            # Verify the editor actually exists before trying to launch
            if not shutil.which(resolved) and not os.path.isfile(resolved):
                logger.debug("[CodeGen] Editor not found: %s", resolved)
                continue
            try:
                if sys.platform == "win32":
                    import subprocess as _sp
                    _sp.Popen(
                        f'cmd /c "{resolved}" "{filepath}"',
                        shell=False,
                        stdout=_sp.DEVNULL,
                        stderr=_sp.DEVNULL,
                    )
                else:
                    subprocess.Popen([resolved, filepath])
                logger.info("[CodeGen] Launched '%s' with file: %s", resolved, filepath)
                return True
            except (FileNotFoundError, OSError) as exc:
                logger.debug("[CodeGen] Editor '%s' failed: %s", resolved, exc)
        return False

    @staticmethod
    def open_in_editor(code: str, language: str = "python",
                       editor: str = None) -> str:
        """
        Open an editor and paste the generated code into it (hands-free).

        Workflow:
        1. Save code to a Desktop file as backup.
        2. Launch the preferred editor (with file OR empty).
        3. Wait for the editor to appear.
        4. Copy code to clipboard and Ctrl+V paste into the window.
        """
        import time, shutil

        try:
            import config as _cfg
            preferred = (editor or getattr(_cfg, "PREFERRED_EDITOR", "auto")).lower().strip()
        except Exception:
            preferred = editor.lower().strip() if editor else "auto"

        try:
            # ── 1. Save code to Desktop as backup ──
            ext = CodeGenerator.LANGUAGE_EXTENSIONS.get(language.lower(), ".py")
            desktop = os.path.expanduser("~/Desktop")
            filename = f"code_snippet_{int(time.time())}{ext}"
            filepath = os.path.join(desktop, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            logger.info("[CodeGen] Saved code to: %s", filepath)

            # ── 2. Copy code to clipboard ──
            def _copy_to_clipboard(text):
                try:
                    import pyperclip
                    pyperclip.copy(text)
                    return
                except Exception:
                    pass
                try:
                    import tkinter as tk
                    r = tk.Tk(); r.withdraw()
                    r.clipboard_clear(); r.clipboard_append(text)
                    r.update(); r.destroy()
                except Exception:
                    pass

            _copy_to_clipboard(code)

            # ── 3. Determine which editor to launch ──
            _DISPLAY_NAMES = {
                "vscode": "VS Code", "notepadplusplus": "Notepad++",
                "sublime": "Sublime Text", "atom": "Atom", "notepad": "Notepad",
            }
            _LAUNCH_CMDS = {
                "vscode": "code", "notepadplusplus": "notepad++",
                "sublime": "subl", "atom": "atom", "notepad": "notepad",
            }

            if preferred in _LAUNCH_CMDS:
                chain = [(preferred, _LAUNCH_CMDS[preferred])]
                # Always add notepad as fallback if not already the preference
                if preferred != "notepad":
                    chain.append(("notepad", "notepad"))
            else:
                chain = [
                    ("vscode", "code"), ("notepadplusplus", "notepad++"),
                    ("sublime", "subl"), ("atom", "atom"), ("notepad", "notepad"),
                ]

            launched_as = None
            use_paste = False  # whether we need to paste after opening

            for key, exe in chain:
                resolved = CodeGenerator._resolve_editor_exe(exe)
                if not (shutil.which(resolved) or os.path.isfile(resolved)):
                    logger.debug("[CodeGen] Editor not found: %s", resolved)
                    continue
                try:
                    import subprocess as _sp
                    if key == "notepad":
                        # Open Notepad empty — we'll paste into it
                        _sp.Popen("notepad", stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
                        use_paste = True
                    else:
                        # Open editor with file path
                        _sp.Popen(
                            f'cmd /c "{resolved}" "{filepath}"',
                            shell=False,
                            stdout=_sp.DEVNULL, stderr=_sp.DEVNULL,
                        )
                    launched_as = _DISPLAY_NAMES.get(key, key.title())
                    logger.info("[CodeGen] Launched %s (%s)", launched_as, resolved)
                    break
                except Exception as exc:
                    logger.debug("[CodeGen] %s failed: %s", exe, exc)

            if not launched_as:
                # Absolute last resort
                os.startfile(filepath)
                return f"[OK] Code saved & opened: {filename}"

            # ── 4. Wait then paste for Notepad (needs empty window + paste) ──
            if use_paste:
                time.sleep(1.5)
                try:
                    import pyautogui
                    pyautogui.hotkey("ctrl", "v")
                    logger.info("[CodeGen] Pasted %d chars into %s", len(code), launched_as)
                except Exception as exc:
                    logger.warning("[CodeGen] Paste failed: %s", exc)

            return f"[OK] Opened in {launched_as}: {filename}"

        except Exception as e:
            logger.error("[CodeGen] Error in open_in_editor: %s", e)
            return f"[ERROR] {str(e)}"

    @staticmethod
    def open_in_notepad(code: str, language: str = "python") -> str:
        """Open code directly in Windows Notepad."""
        return CodeGenerator.open_in_editor(code, language, editor="notepad")

