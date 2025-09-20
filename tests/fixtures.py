import pytest

@pytest.fixture
def test_system_state():
    """A pytest fixture to provide a baseline SystemState for tests."""
    pytest.skip("Fixture test_system_state is not fully implemented.")
    # In a real implementation, this would return a core.types.SystemState object
    # initialized with sensible defaults for testing.
    return {"requirements": [], "obligations": []}

@pytest.fixture
def test_llm_client():
    """A pytest fixture to provide a mock LLM client."""
    pytest.skip("Fixture test_llm_client is not fully implemented.")
    # This would return a mock of llm.client.LLMClient
    class MockLLMClient:
        def generate(self, prompt):
            return "mocked LLM response"
    return MockLLMClient()

# This is not a fixture, but a constant that can be imported by tests.
# It should be populated with all the agent classes.
ALL_AGENT_CLASSES = []
