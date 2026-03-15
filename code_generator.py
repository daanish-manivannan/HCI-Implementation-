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

    @staticmethod
    def open_in_editor(code: str, language: str = "python") -> str:
        """
        Create a file and open in VS Code.
        
        Args:
            code: Code content
            language: Programming language
        
        Returns:
            Status message
        """
        try:
            ext = CodeGenerator.LANGUAGE_EXTENSIONS.get(language.lower(), ".py")
            desktop = os.path.expanduser("~/Desktop")
            
            # Create file with timestamp
            import time
            filename = f"code_snippet_{int(time.time())}{ext}"
            filepath = os.path.join(desktop, filename)
            
            with open(filepath, 'w') as f:
                f.write(code)
            
            logger.info("[CodeGen] Created file: %s", filepath)
            print(f"\n[SAVE LOCATION] Code saved to: {filepath}")
            print(f"[FILE] {filename}\n")
            
            # Open in VS Code
            try:
                subprocess.Popen(["code", filepath])
                logger.info("[CodeGen] Opened in VS Code: %s", filepath)
                return f"[OK] Code saved to Desktop: {filename}"
            except Exception as e:
                logger.warning("[CodeGen] Could not open VS Code: %s", e)
                return f"[OK] Code saved to Desktop: {filename}\n(VS Code not found, file is on Desktop)"
        except Exception as e:
            logger.error("[CodeGen] Error opening in editor: %s", e)
            return f"[ERROR] {str(e)}"
