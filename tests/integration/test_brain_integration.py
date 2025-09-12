import pytest
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from pydantic import BaseModel

# --- Imports from the application ---
from agent.brain import QuantumAgentBrain, QuantumAgent, CapabilityManager
from llm.client import LLMClient
from core.types import Intent, Plan, QCState, CapabilityToken, Permission

# --- Mock Clients for Integration Testing ---

class MockOpenAIClient(LLMClient):
    """A mock client that identifies itself as OpenAI."""
    async def _do_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        return {"id": "openai-response", "model": "mock-openai", "choices": [{"message": {"role": "assistant", "content": "{}"}}], "usage": {}}

class MockAnthropicClient(LLMClient):
    """A mock client that identifies itself as Anthropic."""
    async def _do_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        return {"id": "anthropic-response", "model": "mock-anthropic", "choices": [{"message": {"role": "assistant", "content": "{}"}}], "usage": {}}


# --- Integration Tests ---

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for our test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

def test_llm_provider_switching(event_loop):
    """
    Tests that the QuantumAgentBrain can be initialized with different LLM clients
    and that the client is correctly assigned.
    """
    capability_manager = CapabilityManager()
    agents = {"default": QuantumAgent("default")}

    # Initialize with MockOpenAIClient
    brain_openai = QuantumAgentBrain(
        llm_client=MockOpenAIClient(api_key="mock", model="mock-openai"),
        agents=agents,
        capability_manager=capability_manager
    )
    # A simple check to ensure it's alive and the correct client is used
    assert brain_openai.llm_client.model == "mock-openai"


    # Initialize with MockAnthropicClient
    brain_anthropic = QuantumAgentBrain(
        llm_client=MockAnthropicClient(api_key="mock", model="mock-anthropic"),
        agents=agents,
        capability_manager=capability_manager
    )
    assert brain_anthropic.llm_client.model == "mock-anthropic"

def test_capability_token_enforcement():
    """
    Tests the capability token verification logic in the LLMClient base class.
    This logic is critical for the system's security.
    """
    # Use any concrete client to test the base class method, as it's shared.
    client = MockOpenAIClient(api_key="mock", model="mock-model")

    # 1. Test with a valid token and correct permissions
    valid_token = CapabilityToken(
        agent_id="test_agent",
        allowed_tools=["file_reader", "code_writer"],
        permissions={Permission.READ_FILES, Permission.WRITE_FILES},
        expires_at=datetime.utcnow() + timedelta(hours=1),
        energy_budget=100.0,
        signature="valid"
    )
    assert client.verify_capability(valid_token, "file_reader", Permission.READ_FILES) == True
    assert client.verify_capability(valid_token, "code_writer", Permission.WRITE_FILES) == True

    # 2. Test with a disallowed tool
    assert client.verify_capability(valid_token, "shell_executor", Permission.EXECUTE_TOOLS) == False

    # 3. Test with a tool that the agent has, but a permission it lacks
    assert client.verify_capability(valid_token, "file_reader", Permission.EXECUTE_TOOLS) == False

    # 4. Test with an expired token
    # We use .construct() to create an instance of the model without running validation,
    # which is necessary here because our validator would normally prevent creating an expired token.
    expired_token = CapabilityToken.construct(
        agent_id="test_agent",
        allowed_tools=["file_reader"],
        permissions={Permission.READ_FILES},
        expires_at=datetime.utcnow() - timedelta(seconds=1), # Expired
        energy_budget=100.0,
        signature="expired"
    )
    assert client.verify_capability(expired_token, "file_reader", Permission.READ_FILES) == False
