"""
llm_handler.py
──────────────
LLM integration using Ollama for enhanced command interpretation 
and AI-powered voice command enhancement.

Supports:
  - Automatic model detection
  - Ollama API communication
  - Command enhancement with LLM reasoning
  - Fallback to local processing when LLM unavailable
"""

import json
import logging
import urllib.request
import urllib.error
import time
from typing import Optional, Dict, Tuple
from enum import Enum

# Setup logging
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


class LLMModel(Enum):
    """Available LLM models for HCI tasks"""
    LLAMA3_8B = "llama3:8b"              # Preferred: Better quality (8B params, ~4.7 GB)
    LLAMA32_3B = "llama3.2:3b"           # Lightweight fallback (3B params, ~2.0 GB)
    QWEN25_CODER_7B = "qwen2.5-coder:7b" # Alternative: code/technical tasks (7B params, ~4.7 GB)


class OllamaLLMHandler:
    """
    Interface to Ollama LLM service for enhanced HCI capabilities.
    
    Features:
    ─────────
    - Auto-detect available models
    - Generate command suggestions from voice input
    - Enhance command matching with semantic understanding
    - Graceful degradation when Ollama unavailable
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 11434,
                 timeout: float = 30.0,
                 model: Optional[str] = None):
        """
        Initialize Ollama LLM handler.
        
        Args:
            host: Ollama server host (default: localhost)
            port: Ollama server port (default: 11434, standard Ollama port)
            timeout: Request timeout in seconds
            model: Specific model to use (auto-detects if None)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self._available_models: Optional[list] = None
        self._selected_model: Optional[str] = None
        self._is_available = False
        
        logger.info(f"[LLM] Ollama handler initialized (server: {self.base_url})")
        
        # Auto-detect available models and set default
        if model:
            self._selected_model = model
            logger.info(f"[LLM] Using specified model: {model}")
        else:
            self._detect_and_set_model()
    
    def health_check(self) -> Tuple[bool, str]:
        """
        Check if Ollama service is running and accessible.
        
        Returns:
            Tuple of (is_available, status_message)
        """
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET"
            )
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                self._available_models = [m.get('name') for m in data.get('models', [])]
                self._is_available = True
                
                status = f"✓ Ollama is running ({len(self._available_models)} models available)"
                logger.info(f"[LLM] {status}")
                logger.info(f"[LLM] Available models: {', '.join(self._available_models)}")
                
                return True, status
                
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            self._is_available = False
            status = f"✗ Ollama not running: {type(e).__name__}"
            logger.warning(f"[LLM] {status}")
            return False, status
        except Exception as e:
            self._is_available = False
            status = f"✗ LLM error: {str(e)}"
            logger.error(f"[LLM] {status}")
            return False, status
    
    def _detect_and_set_model(self) -> None:
        """Auto-detect and set the best available model."""
        is_available, status = self.health_check()
        
        if not is_available or not self._available_models:
            logger.warning("[LLM] No models available - will run in degraded mode")
            return
        
        # Prefer larger models for better quality: llama3:8b > qwen > llama3.2:3b
        preferred_order = [
            LLMModel.LLAMA3_8B.value,           # Best quality (8B)
            LLMModel.QWEN25_CODER_7B.value,     # Good for technical
            LLMModel.LLAMA32_3B.value,          # Lightweight fallback
        ]
        
        for preferred_model in preferred_order:
            if preferred_model in self._available_models:
                self._selected_model = preferred_model
                logger.info(f"[LLM] Selected model: {preferred_model}")
                return
        
        # Fallback to first available model
        if self._available_models:
            self._selected_model = self._available_models[0]
            logger.info(f"[LLM] No preferred model found, using: {self._selected_model}")
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available and functional."""
        return self._is_available and self._selected_model is not None
    
    @property
    def selected_model(self) -> Optional[str]:
        """Get the currently selected model name."""
        return self._selected_model
    
    @property
    def available_models(self) -> list:
        """Get list of available models."""
        return self._available_models or []
    
    def generate(self, prompt: str, stream: bool = False) -> Tuple[bool, str]:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt/query
            stream: Whether to stream response (not used in simple implementation)
        
        Returns:
            Tuple of (success, response_text)
        """
        if not self.is_available:
            return False, "[LLM unavailable - using local processing]"
        
        try:
            payload = {
                "model": self._selected_model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5  # Lower temperature for consistency
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                result = data.get('response', '')
                logger.debug(f"[LLM] Generated response ({len(result)} chars)")
                return True, result.strip()
                
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            logger.warning(f"[LLM] Request failed: {type(e).__name__}")
            return False, f"[LLM request failed: {type(e).__name__}]"
        except Exception as e:
            logger.error(f"[LLM] Generation error: {str(e)}")
            return False, f"[LLM error: {str(e)}]"
    
    def enhance_command(self, voice_input: str) -> Tuple[bool, str]:
        """
        Use LLM to understand and enhance voice input interpretation.
        
        Args:
            voice_input: Raw voice recognition output
        
        Returns:
            Tuple of (success, enhanced_command_or_interpretation)
        """
        if not self.is_available:
            return False, voice_input
        
        prompt = f"""You are an intelligent command interpreter for a hands-free computer interaction system.
A user said: "{voice_input}"

Interpret what action they likely want. Be concise and direct.
Return ONLY the interpreted command or action (e.g., 'left click', 'scroll down', 'open browser')."""
        
        return self.generate(prompt)
    
    def summarize_text(self, text: str, max_length: int = 100) -> Tuple[bool, str]:
        """
        Summarize text with LLM.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
        
        Returns:
            Tuple of (success, summary)
        """
        if not self.is_available:
            return False, text[:max_length]
        
        prompt = f"""Summarize the following text in {max_length} characters or less:
{text}"""
        
        return self.generate(prompt)
    
    def answer_question(self, question: str) -> Tuple[bool, str]:
        """
        Answer a question with LLM.
        
        Args:
            question: Question to answer
        
        Returns:
            Tuple of (success, answer)
        """
        if not self.is_available:
            return False, "LLM unavailable"
        
        return self.generate(question)


# Global LLM handler instance
_llm_handler: Optional[OllamaLLMHandler] = None


def initialize_llm(host: str = "localhost", 
                   port: int = 11434,
                   model: Optional[str] = None) -> OllamaLLMHandler:
    """
    Initialize the global LLM handler instance.
    
    Args:
        host: Ollama server host
        port: Ollama server port
        model: Specific model to use
    
    Returns:
        Initialized LLM handler
    """
    global _llm_handler
    _llm_handler = OllamaLLMHandler(host=host, port=port, model=model)
    return _llm_handler


def get_llm() -> Optional[OllamaLLMHandler]:
    """Get the global LLM handler instance."""
    return _llm_handler


def is_llm_available() -> bool:
    """Check if LLM is available."""
    return _llm_handler is not None and _llm_handler.is_available
