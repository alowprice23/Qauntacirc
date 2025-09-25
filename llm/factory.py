import os
from typing import Optional

from .client import LLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .groq_client import GroqClient
from .gemini_client import GeminiClient
from .openrouter_client import OpenRouterClient

def get_llm_client(provider: str, api_key: Optional[str] = None, **kwargs) -> LLMClient:
    """
    Factory function to get an LLM client based on the provider.

    :param provider: The name of the LLM provider (e.g., "openai", "anthropic").
    :param api_key: The API key for the provider. If not provided, it will
                    be read from the corresponding environment variable.
    :param kwargs: Additional arguments for the client constructor.
    :return: An instance of the specified LLM client.
    """
    if provider == "openai":
        return OpenAIClient(api_key=api_key, **kwargs)
    elif provider == "anthropic":
        return AnthropicClient(api_key=api_key, **kwargs)
    elif provider == "groq":
        return GroqClient(api_key=api_key, **kwargs)
    elif provider == "gemini":
        return GeminiClient(api_key=api_key, **kwargs)
    elif provider == "openrouter":
        return OpenRouterClient(api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")