import os
import time
import logging
from typing import Any, Dict, List, Optional

import groq

from .client import LLMClient, StandardChatResponse
from core.types import QCState as QuantumState

logger = logging.getLogger(__name__)

class GroqClient(LLMClient):
    """
    LLMClient implementation for Groq's high-speed inference.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mixtral-8x7b-32768",
        **kwargs: Any,
    ):
        super().__init__(api_key=api_key or os.environ.get("GROQ_API_KEY"), model=model, **kwargs)
        if self.api_key is None:
            raise ValueError("Groq API key is required.")
        self.client = groq.Groq(api_key=self.api_key)
        self.latencies = []

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
            start_time = time.perf_counter()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )

            end_time = time.perf_counter()
            latency = end_time - start_time
            self.latencies.append(latency)
            logger.info(f"Groq request latency: {latency:.4f}s")

            self._track_cost_from_usage(response.usage)
            return response.to_dict()

        return self._handle_request(api_call)

    def embed(
        self,
        texts: List[str],
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Embedding is not a standard feature of the Groq API."""
        logger.warning("Groq API does not support embeddings.")
        raise NotImplementedError("Groq API does not support embeddings.")

    def get_average_latency(self) -> float:
        """Returns the average latency of all requests made."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def _track_cost_from_usage(self, usage: Any) -> None:
        """Calculate and track cost based on token usage."""
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens

        cost = self._calculate_cost(prompt_tokens, completion_tokens)
        if cost is not None:
            self._track_cost(cost)

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Optional[float]:
        """
        Calculates the cost of a request based on the model and token counts.
        Pricing for Mixtral-8x7b on Groq as of early 2024.
        """
        pricing = {
            "mixtral-8x7b-32768": {"prompt": 0.27 / 1_000_000, "completion": 0.77 / 1_000_000},
            "llama2-70b-4096": {"prompt": 0.70 / 1_000_000, "completion": 0.80 / 1_000_000},
        }

        model_pricing = pricing.get(self.model)
        if not model_pricing:
            logger.warning(f"Cost tracking not available for model: {self.model}")
            return None

        cost = (prompt_tokens * model_pricing["prompt"]) + (completion_tokens * model_pricing["completion"])
        return cost
