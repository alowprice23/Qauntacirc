import os
import logging
import requests
from typing import Any, Dict, List, Optional

from .client import LLMClient, StandardChatResponse
from core.data_models import QCState as QuantumState

logger = logging.getLogger(__name__)

class OpenRouterClient(LLMClient):
    """
    LLMClient implementation for OpenRouter, which acts as a gateway to multiple models.
    """
    API_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/gpt-3.5-turbo",  # Default model
        **kwargs: Any,
    ):
        super().__init__(api_key=api_key or os.environ.get("OPENROUTER_API_KEY"), model=model, **kwargs)
        if self.api_key is None:
            raise ValueError("OpenRouter API key is required.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _do_generate(
        self,
        prompt: str,
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a text completion from a prompt."""
        messages = [{"role": "user", "content": prompt}]
        chat_completion = self._do_chat(messages, quantum_context, **kwargs)
        return chat_completion["choices"][0]["message"]["content"]

    def _do_chat(
        self,
        messages: List[Dict[str, str]],
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> StandardChatResponse:
        """Generate a chat response from a list of messages."""

        def api_call() -> StandardChatResponse:
            payload = {
                "model": self.model,
                "messages": messages,
                **kwargs,
            }
            response = requests.post(
                f"{self.API_URL}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            if "usage" in data:
                self._track_cost_from_usage(data["usage"])
            return data

        return self._handle_request(api_call)

    def embed(
        self,
        texts: List[str],
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """
        Embedding is not directly supported via a dedicated endpoint in OpenRouter's public API.
        However, some models available through OpenRouter support embeddings.
        This method would need to be implemented on a per-model basis.
        """
        logger.warning("OpenRouter does not have a dedicated embedding endpoint.")
        raise NotImplementedError("Embeddings on OpenRouter must be handled on a per-model basis.")

    def _track_cost_from_usage(self, usage: Dict[str, int]) -> None:
        """
        Tracks cost based on token usage.
        Note: OpenRouter's documentation states that for precise cost, one should query
        the generation endpoint. This is a simplified approach using the returned usage stats.
        """
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)

        logger.info(
            f"Usage for model {self.model}: "
            f"Prompt tokens: {prompt_tokens}, "
            f"Completion tokens: {completion_tokens}"
        )

        logger.warning(
            "Cost tracking for OpenRouter is not fully implemented due to dynamic pricing. "
            "This implementation only logs token usage. For accurate cost, query the "
            "generation endpoint as described in the OpenRouter documentation."
        )
        # In a real system, you'd fetch the model's price from the OpenRouter API
        # and calculate the cost.
        # e.g. cost = self.get_cost_for_model(self.model, prompt_tokens, completion_tokens)
        # self._track_cost(cost)
        pass
