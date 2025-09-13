import os
import logging
from typing import Any, Dict, List, Optional

import openai

from .client import LLMClient, StandardChatResponse
from core.data_models import QCState as QuantumState

logger = logging.getLogger(__name__)

class OpenAIClient(LLMClient):
    """
    LLMClient implementation for OpenAI models (GPT-4, GPT-3.5).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        **kwargs: Any,
    ):
        super().__init__(api_key=api_key or os.environ.get("OPENAI_API_KEY"), model=model, **kwargs)
        if self.api_key is None:
            raise ValueError("OpenAI API key is required.")
        self.client = openai.OpenAI(api_key=self.api_key)

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
            quantum_params = self._preserve_quantum_context(quantum_context)
            # In a real scenario, quantum_params would be merged into the request
            # For now, it's a placeholder.

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )
            self._track_cost_from_usage(response.usage)
            return response.to_dict()

        return self._handle_request(api_call)

    def embed(
        self,
        texts: List[str],
        quantum_context: Optional[QuantumState] = None,
        embedding_model: str = "text-embedding-ada-002",
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts."""

        def api_call():
            response = self.client.embeddings.create(
                input=texts,
                model=embedding_model,
                **kwargs,
            )
            self._track_cost_from_usage(response.usage, model=embedding_model)
            return [item.embedding for item in response.data]

        return self._handle_request(api_call)

    def _track_cost_from_usage(self, usage: Any, model: Optional[str] = None) -> None:
        """Calculate and track cost based on token usage."""
        model_name = model or self.model
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens

        cost = self._calculate_cost(prompt_tokens, completion_tokens, model_name)
        if cost is not None:
            self._track_cost(cost)

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model_name: str) -> Optional[float]:
        """
        Calculates the cost of a request based on the model and token counts.
        Prices as of late 2023.
        """
        pricing = {
            "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
            "gpt-4-32k": {"prompt": 0.06 / 1000, "completion": 0.12 / 1000},
            "gpt-3.5-turbo": {"prompt": 0.0015 / 1000, "completion": 0.002 / 1000},
            "text-embedding-ada-002": {"prompt": 0.0001 / 1000, "completion": 0},
        }

        model_pricing = pricing.get(model_name)
        if not model_pricing:
            logger.warning(f"Cost tracking not available for model: {model_name}")
            return None

        cost = (prompt_tokens * model_pricing["prompt"]) + (completion_tokens * model_pricing.get("completion", 0))
        return cost
