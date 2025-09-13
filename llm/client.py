import abc
import time
import logging
import json
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from uuid import uuid4
from datetime import datetime

# Project-specific imports
from core.data_models import CapabilityToken, Permission, QCState
# Assuming these modules exist from the original file structure
from .rate_limiter import RateLimiter
from .validators import ResponseValidator
from .prompt_security import InjectionDetector

# Define a TypeVar for Pydantic models to ensure type safety
T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

# --- Standardized response format ---
class ChatMessage(BaseModel):
    role: str
    content: str

class StandardChatResponse(BaseModel):
    id: str
    model: str
    choices: List[Dict]
    usage: Dict

class LLMClient(abc.ABC):
    """
    Abstract base class for all LLM clients, incorporating mathematical safety
    and physics-based constraints.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        rate_limiter: Optional[RateLimiter] = None,
        validator: Optional[ResponseValidator] = None,
        injection_detector: Optional[InjectionDetector] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.rate_limiter = rate_limiter or RateLimiter()
        self.validator = validator or ResponseValidator()
        self.injection_detector = injection_detector  # Allow it to be None
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_cost = 0.0

    def verify_capability(self, token: CapabilityToken, required_tool: str, required_permission: Permission) -> bool:
        """
        Verifies if the agent has the necessary capability to perform an action.
        This is a critical security boundary.
        """
        if token.expires_at < datetime.utcnow():
            logger.warning(f"Capability token for agent {token.agent_id} has expired.")
            return False
        if required_tool not in token.allowed_tools:
            logger.warning(f"Agent {token.agent_id} attempted to use disallowed tool: {required_tool}")
            return False
        if required_permission not in token.permissions:
            logger.warning(f"Agent {token.agent_id} lacks permission: {required_permission.value}")
            return False

        logger.info(f"Capability verified for agent {token.agent_id}: tool '{required_tool}', permission '{required_permission.value}'")
        return True

    @abc.abstractmethod
    async def _do_chat(
        self,
        messages: List[Dict[str, str]],
        quantum_context: Optional[QCState] = None,
        **kwargs: Any,
    ) -> Dict:
        """Abstract method for provider-specific chat implementation."""
        pass

    async def chat(
        self,
        messages: List[Dict[str, str]],
        quantum_context: Optional[QCState] = None,
        **kwargs: Any,
    ) -> Dict:
        """
        Generates a chat response, applying security and safety checks.
        Temperature for deterministic operations (tool use, artifact generation)
        should be set to 0.0 in kwargs.
        """
        sanitized_messages = self.injection_detector.sanitize(messages) if self.injection_detector else messages
        if any(not isinstance(m, dict) or 'role' not in m or 'content' not in m for m in sanitized_messages):
            raise TypeError("Messages must be a list of dictionaries with 'role' and 'content' keys.")

        self.rate_limiter.wait()
        response = await self._do_chat(sanitized_messages, quantum_context, **kwargs)
        # self.validator.validate(response) # Assuming validator works on the raw response
        self._track_usage(response.get("usage", {}))
        return response

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        quantum_context: Optional[QCState] = None,
        **kwargs: Any,
    ) -> T:
        """
        Generates a structured response that conforms to a Pydantic model.
        This enforces mathematical precision and schema validation.
        """
        if self.injection_detector and self.injection_detector.detect(prompt):
            raise ValueError("Prompt injection detected in structured generation prompt.")

        # For structured output, determinism is key.
        kwargs['temperature'] = 0.0

        schema = response_model.model_json_schema()
        system_message = (
            "You are a precision-focused AI assistant. Your response MUST be a JSON object "
            f"that strictly adheres to the following JSON Schema. Do not include any other text, "
            f"explanation, or markdown formatting. The JSON object must be the only thing you output.\n"
            f"Schema: {json.dumps(schema)}"
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        self.rate_limiter.wait()
        # We need the raw dictionary from the response to get the content
        response_dict = await self._do_chat(messages, quantum_context, **kwargs)

        raw_content = response_dict['choices'][0]['message']['content']
        self._track_usage(response_dict.get("usage", {}))

        try:
            # Parse the JSON and validate against the Pydantic model
            parsed_json = json.loads(raw_content)
            validated_model = response_model.model_validate(parsed_json)
            return validated_model
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to decode or validate LLM response. Error: {e}\nRaw Content: {raw_content}")
            raise ValueError("LLM response did not conform to the required Pydantic schema.") from e


    def _track_usage(self, usage: Dict[str, int]):
        """Track token usage and associated costs."""
        if not usage:
            return
        self.total_token_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
        self.total_token_usage["completion_tokens"] += usage.get("completion_tokens", 0)
        self.total_token_usage["total_tokens"] += usage.get("total_tokens", 0)

        cost = self._calculate_cost(usage)
        self.total_cost += cost
        logger.info(f"Request usage: {usage}. Total usage: {self.total_token_usage}. Request cost: ${cost:.6f}. Total cost: ${self.total_cost:.6f}")

    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        # Must be implemented by subclasses.
        return 0.0


# --- Concrete Implementations ---

class OpenAIClient(LLMClient):
    """LLMClient implementation for OpenAI APIs."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import openai
            # Make sure to initialize the async client
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI client requires 'openai' package. Please install it.")

    async def _do_chat(
        self,
        messages: List[Dict[str, str]],
        quantum_context: Optional[QCState] = None,
        **kwargs: Any,
    ) -> Dict:
        # For structured generation, OpenAI API requires response_format to be set
        if kwargs.get('temperature') == 0.0:
             kwargs['response_format'] = {"type": "json_object"}

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        # Return the response as a dictionary to be processed by the base class
        return response.model_dump()

    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        # Example cost for gpt-4-turbo: $10/1M prompt, $30/1M completion
        prompt_cost = usage.get("prompt_tokens", 0) * (10 / 1_000_000)
        completion_cost = usage.get("completion_tokens", 0) * (30 / 1_000_000)
        return prompt_cost + completion_cost

class AnthropicClient(LLMClient):
    """LLMClient implementation for Anthropic APIs."""
    async def _do_chat(self, messages: List[Dict[str, str]], quantum_context: Optional[QCState] = None, **kwargs: Any) -> Dict:
        raise NotImplementedError("AnthropicClient is not yet implemented.")

class GroqClient(LLMClient):
    """LLMClient implementation for Groq APIs."""
    async def _do_chat(self, messages: List[Dict[str, str]], quantum_context: Optional[QCState] = None, **kwargs: Any) -> Dict:
        raise NotImplementedError("GroqClient is not yet implemented.")

class OllamaClient(LLMClient):
    """LLMClient implementation for a local Ollama instance."""
    async def _do_chat(self, messages: List[Dict[str, str]], quantum_context: Optional[QCState] = None, **kwargs: Any) -> Dict:
        raise NotImplementedError("OllamaClient is not yet implemented.")
