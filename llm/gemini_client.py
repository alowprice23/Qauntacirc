import os
import logging
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from .client import LLMClient, QuantumState, StandardChatResponse

logger = logging.getLogger(__name__)

class GeminiClient(LLMClient):
    """
    LLMClient implementation for Google's Gemini models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-pro",
        **kwargs: Any,
    ):
        super().__init__(api_key=api_key or os.environ.get("GOOGLE_API_KEY"), model=model, **kwargs)
        if self.api_key is None:
            raise ValueError("Google API key is required.")
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

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
        """
        Generate a chat response from a list of messages.
        This requires managing conversation history.
        """
        chat_session = self.client.start_chat(history=self._format_history(messages[:-1]))

        def api_call() -> StandardChatResponse:
            last_message = messages[-1]["content"]
            response = chat_session.send_message(last_message, **kwargs)

            # Gemini does not provide token usage details in the response object.
            # We need to calculate it manually.
            prompt_tokens = self.client.count_tokens(contents=[m["content"] for m in messages]).total_tokens
            completion_tokens = self.client.count_tokens(contents=[response.text]).total_tokens

            self._track_cost(prompt_tokens, completion_tokens)

            # Transform the response to the standardized format
            return {
                "id": f"gemini-{response.candidates[0].index}",  # Gemini doesn't provide a unique ID
                "model": self.model,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response.text,
                        },
                        "finish_reason": response.candidates[0].finish_reason.name,
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }

        return self._handle_request(api_call)


    def embed(
        self,
        texts: List[str],
        quantum_context: Optional[QuantumState] = None,
        embedding_model: str = "models/embedding-001",
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts."""

        def api_call():
            result = genai.embed_content(
                model=embedding_model,
                content=texts,
                task_type="retrieval_document",
                **kwargs
            )
            # Cost for embeddings needs to be tracked here
            # For now, we will just log it.
            logger.info(f"Gemini embedding generated for {len(texts)} documents.")
            return result['embedding']

        return self._handle_request(api_call)

    def _format_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Formats message history for the Gemini API."""
        history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})
        return history

    def _track_cost(self, prompt_tokens: int, completion_tokens: int) -> None:
        """
        Tracks cost based on token count, as per Gemini Pro pricing.
        """
        # Pricing for Gemini Pro as of early 2024: $0.125 / 1M characters for input, $0.375 / 1M characters for output
        # We will use token-based pricing for consistency.
        # $0.125/1M tokens for prompt, $0.375/1M tokens for completion
        prompt_cost = (prompt_tokens / 1_000_000) * 0.125
        completion_cost = (completion_tokens / 1_000_000) * 0.375

        total_cost = prompt_cost + completion_cost
        super()._track_cost(total_cost)
