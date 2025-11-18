import os
import logging
from typing import Any, Dict, List, Optional

import anthropic

from .client import LLMClient, QuantumState, StandardChatResponse

logger = logging.getLogger(__name__)

class AnthropicClient(LLMClient):
    """
    LLMClient implementation for Anthropic's Claude models using the Messages API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        **kwargs: Any,
    ):
        super().__init__(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"), model=model, **kwargs)
        if self.api_key is None:
            raise ValueError("Anthropic API key is required.")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a text completion from a prompt."""
        messages = [{"role": "user", "content": prompt}]
        chat_completion = self.chat(messages, quantum_context, **kwargs)
        return chat_completion["choices"][0]["message"]["content"]

    def chat(
        self,
        messages: List[Dict[str, str]],
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> StandardChatResponse:
        """Generate a chat response from a list of messages."""

        # The Messages API requires a 'max_tokens' parameter.
        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = 1024

        def api_call() -> StandardChatResponse:
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )
            self._track_cost_from_usage(response.usage)

            # Transform the response to the standardized format
            return {
                "id": response.id,
                "model": response.model,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.content[0].text,
                        },
                        "finish_reason": response.stop_reason,
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            }

        return self._handle_request(api_call)

    def embed(
        self,
        texts: List[str],
        quantum_context: Optional[QuantumState] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Embedding is not a standard feature of the public Anthropic API."""
        logger.warning("Anthropic API does not support embeddings.")
        raise NotImplementedError("Anthropic API does not support embeddings.")

    def _track_cost_from_usage(self, usage: anthropic.types.Usage) -> None:
        """Calculate and track cost based on token usage from the Messages API."""
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        cost = self._calculate_cost(input_tokens, output_tokens)
        if cost is not None:
            self._track_cost(cost)

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Optional[float]:
        """
        Calculates the cost of a request based on the model and token counts.
        Prices as of early 2024 for Claude 3.
        """
        pricing = {
            "claude-3-opus-20240229": {"input": 15.00 / 1_000_000, "output": 75.00 / 1_000_000},
            "claude-3-sonnet-20240229": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
            "claude-3-haiku-20240307": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
        }

        model_pricing = pricing.get(self.model)
        if not model_pricing:
            logger.warning(f"Cost tracking not available for model: {self.model}")
            return None

        cost = (input_tokens * model_pricing["input"]) + (output_tokens * model_pricing["output"])
        return cost
