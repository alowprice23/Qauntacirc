import pytest
import logging
from unittest.mock import patch, MagicMock

from llm.anthropic_client import AnthropicClient

def test_anthropic_client_initialization_with_api_key():
    """Test that the AnthropicClient initializes correctly with a provided API key."""
    with patch('llm.anthropic_client.anthropic.Anthropic') as mock_anthropic_class:
        client = AnthropicClient(api_key="test_api_key")
        assert client.api_key == "test_api_key"
        assert client.model == "claude-3-opus-20240229"
        # Verify that the underlying client was instantiated
        mock_anthropic_class.assert_called_once_with(api_key="test_api_key")

def test_anthropic_client_initialization_with_env_variable(monkeypatch):
    """Test that the AnthropicClient initializes correctly with an API key from env."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_api_key_from_env")
    with patch('llm.anthropic_client.anthropic.Anthropic') as mock_anthropic_class:
        client = AnthropicClient()
        assert client.api_key == "test_api_key_from_env"
        mock_anthropic_class.assert_called_once_with(api_key="test_api_key_from_env")

def test_anthropic_client_initialization_missing_api_key(monkeypatch):
    """Test that a ValueError is raised if the API key is missing."""
    # Ensure the environment variable is not set
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Anthropic API key is required."):
        AnthropicClient(api_key=None)

def test_anthropic_client_model_override():
    """Test that the model can be overridden during initialization."""
    with patch('llm.anthropic_client.anthropic.Anthropic'):
        client = AnthropicClient(api_key="test_api_key", model="claude-3-sonnet-20240229")
        assert client.model == "claude-3-sonnet-20240229"

def test_generate_calls_chat_and_returns_content():
    """Test that generate calls chat and returns the correct content."""
    with patch('llm.anthropic_client.anthropic.Anthropic'):
        client = AnthropicClient(api_key="test_api_key")

    # This is a mock of the StandardChatResponse dictionary
    mock_chat_response = {
        "id": "chatcmpl-123",
        "model": client.model,
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }

    # Patch the 'chat' method on the instance
    with patch.object(AnthropicClient, 'chat', return_value=mock_chat_response) as mock_chat:
        prompt = "Hello, world!"
        # We need to instantiate the client within the context of the patch
        # or patch the instance itself. Let's patch the class.
        client_instance = AnthropicClient(api_key="test_api_key")
        response = client_instance.generate(prompt, quantum_context=None)

        # Verify that chat was called correctly
        expected_messages = [{"role": "user", "content": prompt}]
        mock_chat.assert_called_once_with(
            expected_messages,
            None
        )

        # Verify that the response is the content of the first choice's message
        assert response == "This is a test response."

def test_chat_method_transforms_response_correctly():
    """Test that the chat method calls the API and transforms the response."""
    with patch('llm.anthropic_client.anthropic.Anthropic') as mock_anthropic_class:
        # Configure the mock response from the anthropic library
        mock_api_response = MagicMock()
        mock_api_response.id = "msg_0123"
        mock_api_response.model = "claude-3-opus-20240229"
        mock_api_response.content = [MagicMock(text="Hello from Claude")]
        mock_api_response.stop_reason = "end_turn"
        mock_api_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        # Set the mock response on the client instance
        mock_anthropic_instance = mock_anthropic_class.return_value
        mock_anthropic_instance.messages.create.return_value = mock_api_response

        client = AnthropicClient(api_key="test_api_key")

        # Mock the _handle_request to bypass rate limiting and retries for this unit test
        with patch.object(client, '_handle_request', side_effect=lambda func: func()) as mock_handler:
            messages = [{"role": "user", "content": "Hello"}]
            response = client.chat(messages)

            # Verify the API call
            mock_anthropic_instance.messages.create.assert_called_once_with(
                model=client.model,
                messages=messages,
                max_tokens=1024  # Default value
            )

    # Verify the transformed response
    expected_response = {
        "id": "msg_0123",
        "model": "claude-3-opus-20240229",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello from Claude",
                },
                "finish_reason": "end_turn",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }
    assert response == expected_response

def test_chat_method_with_custom_max_tokens():
    """Test that max_tokens can be overridden in the chat method."""
    with patch('llm.anthropic_client.anthropic.Anthropic') as mock_anthropic_class:
        mock_anthropic_instance = mock_anthropic_class.return_value

        # Create a more specific mock for the response to avoid TypeErrors
        mock_api_response = MagicMock()
        mock_api_response.usage = MagicMock(input_tokens=10, output_tokens=20)
        # Add other necessary attributes to satisfy the transformation logic
        mock_api_response.id = "msg_custom_tokens"
        mock_api_response.model = "claude-3-opus-20240229"
        mock_api_response.content = [MagicMock(text="Custom token response")]
        mock_api_response.stop_reason = "stop"
        mock_anthropic_instance.messages.create.return_value = mock_api_response

        client = AnthropicClient(api_key="test_api_key")
        with patch.object(client, '_handle_request', side_effect=lambda func: func()):
            messages = [{"role": "user", "content": "Hello"}]
            client.chat(messages, max_tokens=500)

            # Verify the API call used the custom max_tokens
            mock_anthropic_instance.messages.create.assert_called_once_with(
                model=client.model,
                messages=messages,
                max_tokens=500
            )

def test_chat_method_tracks_cost():
    """Test that the chat method correctly tracks the cost of the API call."""
    with patch('llm.anthropic_client.anthropic.Anthropic') as mock_anthropic_class:
        # Configure the mock response with usage data
        mock_api_response = MagicMock()
        mock_api_response.id = "msg_cost"
        mock_api_response.model = "claude-3-opus-20240229"
        mock_api_response.content = [MagicMock(text="cost test")]
        mock_api_response.stop_reason = "stop"
        mock_api_response.usage = MagicMock(input_tokens=100, output_tokens=200)

        mock_anthropic_instance = mock_anthropic_class.return_value
        mock_anthropic_instance.messages.create.return_value = mock_api_response

        client = AnthropicClient(api_key="test_api_key", model="claude-3-opus-20240229")

        # We patch _track_cost on the base class or the instance
        with patch.object(client, '_track_cost') as mock_track_cost, \
             patch.object(client, '_handle_request', side_effect=lambda func: func()):

            client.chat([{"role": "user", "content": "Tell me a story"}])

            # Calculate expected cost for the specific model
            # opus: 15.00 input, 75.00 output per million tokens
            expected_cost = (100 * (15.00 / 1_000_000)) + (200 * (75.00 / 1_000_000))
            mock_track_cost.assert_called_once()
            # Use pytest.approx for floating point comparison
            assert mock_track_cost.call_args[0][0] == pytest.approx(expected_cost)

def test_embed_method_raises_not_implemented_error():
    """Test that the embed method raises NotImplementedError."""
    with patch('llm.anthropic_client.anthropic.Anthropic'):
        client = AnthropicClient(api_key="test_api_key")
        with pytest.raises(NotImplementedError, match="Anthropic API does not support embeddings."):
            client.embed(["some text"])

@pytest.mark.parametrize(
    "model, input_tokens, output_tokens, expected_cost",
    [
        ("claude-3-opus-20240229", 1000, 2000, (1000 * 15.00 / 1_000_000) + (2000 * 75.00 / 1_000_000)),
        ("claude-3-sonnet-20240229", 1000, 2000, (1000 * 3.00 / 1_000_000) + (2000 * 15.00 / 1_000_000)),
        ("claude-3-haiku-20240307", 1000, 2000, (1000 * 0.25 / 1_000_000) + (2000 * 1.25 / 1_000_000)),
    ]
)
def test_calculate_cost_for_supported_models(model, input_tokens, output_tokens, expected_cost):
    """Test cost calculation for various supported models."""
    with patch('llm.anthropic_client.anthropic.Anthropic'):
        client = AnthropicClient(api_key="test_api_key", model=model)
        cost = client._calculate_cost(input_tokens, output_tokens)
        assert cost == pytest.approx(expected_cost)

def test_calculate_cost_for_unsupported_model(caplog):
    """Test that cost calculation returns None for an unsupported model."""
    # We need to set the logger level to capture WARNING messages
    caplog.set_level(logging.WARNING)

    with patch('llm.anthropic_client.anthropic.Anthropic'):
        client = AnthropicClient(api_key="test_api_key", model="unsupported-model")
        cost = client._calculate_cost(100, 200)

    assert cost is None
    # Check that the warning was logged
    assert "Cost tracking not available for model: unsupported-model" in caplog.text
