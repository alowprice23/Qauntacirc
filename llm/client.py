import abc
import time
import logging
from typing import Any, Dict, List, Optional, TypedDict

import uuid

# Assuming a QuantumState object exists in the core module
# from core.quantum_state import QuantumState
# For now, we'll use a more detailed placeholder
class QuantumState:
    """
    A simulated representation of a quantum state for context preservation.
    In a real system, this would be a complex object with properties
    derived from a quantum computing environment.
    """
    def __init__(self, system_urgency: float = 0.5, coherence_level: float = 1.0):
        self.state_id = str(uuid.uuid4())
        self.system_urgency = system_urgency  # A value from 0.0 to 1.0
        self.coherence_level = coherence_level  # A value from 0.0 to 1.0
        self.entangled_states: Dict[str, Any] = {}

    def is_coherent(self) -> bool:
        """Determines if the quantum state is coherent enough for reliable operations."""
        return self.coherence_level > 0.75

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the quantum state to a dictionary."""
        return {
            "state_id": self.state_id,
            "system_urgency": self.system_urgency,
            "coherence_level": self.coherence_level,
            "entangled_states": list(self.entangled_states.keys()),
        }

from .rate_limiter import RateLimiter
from .validators import ResponseValidator, PromptSafetyValidator
from .capability_tokens import CapabilityToken, CapabilityTokenManager

logger = logging.getLogger(__name__)

# Standardized response format using TypedDicts for better type checking
class ChatMessage(TypedDict):
    role: str
    content: str

class ChatChoice(TypedDict):
    message: ChatMessage
    finish_reason: str

class Usage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class StandardChatResponse(TypedDict):
    id: str
    model: str
    choices: List[ChatChoice]
    usage: Usage

class LLMClient(abc.ABC):
    """Abstract base class for all LLM clients."""

    def __init__(
        self,
        api_key: str,
        model: str,
        budget_manager: Optional[Any] = None,
        rate_limiter: Optional[RateLimiter] = None,
        validator: Optional[ResponseValidator] = None,
        prompt_safety_validator: Optional[PromptSafetyValidator] = None,
        token_manager: Optional[CapabilityTokenManager] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.budget_manager = budget_manager
        self.rate_limiter = rate_limiter or RateLimiter()
        self.validator = validator or ResponseValidator()
        self.prompt_safety_validator = prompt_safety_validator or PromptSafetyValidator()
        self.token_manager = token_manager
        self.total_cost = 0.0

    @abc.abstractmethod
    def generate(
        self,
        prompt: str,
        capability_token: Optional[CapabilityToken] = None,
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a text completion from a prompt."""
        pass

    @abc.abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        capability_token: Optional[CapabilityToken] = None,
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> StandardChatResponse:
        """Generate a chat response from a list of messages."""
        pass

    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """A simplified chat method for compatibility."""
        chat_response = self.chat(messages, **kwargs)
        return {
            "response": chat_response["choices"][0]["message"]["content"],
            "usage": chat_response.get("usage"),
        }

    @abc.abstractmethod
    def embed(
        self,
        texts: List[str],
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    def _track_cost(self, cost: float):
        """Track the cost of an API call."""
        if self.budget_manager:
            self.budget_manager.track_cost(cost)
        self.total_cost += cost
        logger.info(f"Cost for this request: ${cost:.6f}. Total cost: ${self.total_cost:.6f}")

    def _apply_rate_limit(self):
        """Apply rate limiting before making an API call."""
        if self.rate_limiter:
            self.rate_limiter.wait()

    def _validate_request(self, prompt: str, capability_token: Optional[CapabilityToken], tool_name: str):
        """Performs all pre-request validation."""
        # 1. Validate token
        if self.token_manager and capability_token:
            if not self.token_manager.validate_tool_access(capability_token, tool_name):
                raise PermissionError(f"Invalid or insufficient capability token for '{tool_name}'")

        # 2. Validate input
        if self.prompt_safety_validator:
            input_validation = self.prompt_safety_validator.validate_input(prompt)
            if not input_validation.safe:
                raise ValueError(f"Input validation failed: {input_validation.reason}")

    def _validate_response(self, response: Any) -> Any:
        """Performs all post-request validation."""
        # 3. Validate output
        if self.prompt_safety_validator:
            output_content = ""
            if isinstance(response, str):
                output_content = response
            elif isinstance(response, dict) and "choices" in response:
                try:
                    output_content = response["choices"][0]["message"]["content"]
                except (KeyError, IndexError):
                    output_content = str(response)
            else:
                output_content = str(response)

            output_validation = self.prompt_safety_validator.validate_output(output_content)
            if not output_validation.safe:
                logger.error(f"Output validation failed: {output_validation.reason}")
                raise ValueError(f"Output validation failed: {output_validation.reason}")

        if not self.validator.validate(response):
            logger.warning("Response failed validation.")
            return None

        return response

    def _handle_request(self, request_func, *args, **kwargs):
        """Generic request handler with retries and rate limiting."""
        self._apply_rate_limit()
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = request_func(*args, **kwargs)
                return self._validate_response(response)
            except Exception as e:
                logger.error(f"API call failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def get_total_cost(self) -> float:
        """Get the total cost accumulated by this client."""
        return self.total_cost

    def _preserve_quantum_context(self, quantum_context: Optional[QuantumState]) -> Dict[str, Any]:
        """
        Serializes or prepares quantum context to be sent with the LLM request.
        This is a placeholder for actual quantum context integration.
        """
        if quantum_context:
            # In a real implementation, this would involve complex serialization
            # of the quantum state to be passed to a quantum-aware LLM.
            logger.info("Preserving quantum context for LLM interaction.")
            return quantum_context.to_dict()
        return {}
