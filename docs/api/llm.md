---
generation_method: "This document is intended to be auto-generated from the Python docstrings in the `/llm` directory using a tool like `mkdocstrings`. The content below is a manually-created placeholder."
---

# API Reference: `llm`

This document provides a reference for the LLM (Large Language Model) integration clients. The `llm` module provides a unified interface for interacting with various third-party LLM providers.

## `BaseLLMClient`

**`llm.client.BaseLLMClient`**

An abstract base class that defines the common interface for all LLM clients.

### Abstract Methods

#### `get_completion(prompt: str, temperature: float = 0.7) -> str`

Requests a completion from the LLM based on the given prompt.

- **Parameters**:
    - `prompt` (`str`): The input prompt to send to the model.
    - `temperature` (`float`): The sampling temperature to use.
- **Returns**:
    - `str`: The model's response text.

#### `get_embedding(text: str) -> list[float]`

Generates a vector embedding for the given text.

- **Parameters**:
    - `text` (`str`): The text to embed.
- **Returns**:
    - `list[float]`: The embedding vector.

---

## Example Client: `OpenAIClient`

**`llm.openai_client.OpenAIClient`**

A client for interacting with the OpenAI API (e.g., GPT-4).

### Configuration

The `OpenAIClient` is initialized with an API key and a model name.

- **`api_key`**: Your OpenAI API key. Can also be set via the `OPENAI_API_KEY` environment variable.
- **`model`**: The name of the model to use, e.g., `"gpt-4-turbo"`.

### Usage

```python
from llm.openai_client import OpenAIClient

client = OpenAIClient(model="gpt-4-turbo")
prompt = "Explain the significance of the Banach fixed-point theorem in 50 words."
response = client.get_completion(prompt)
print(response)
```

This client handles the details of making HTTP requests to the OpenAI API, including authentication, rate limiting (`llm/rate_limiter.py`), and error handling.
