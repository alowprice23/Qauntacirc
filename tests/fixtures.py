import pytest
from core.types import SystemState, SoftwareState, EnergyBreakdown, LyapunovMetrics
from agents.planck_forge.agent import PlanckForgeAgent
from agents.schrodinger_dev.agent import SchrodingerDevAgent
from agents.pauli_guard.agent import PauliGuardAgent

@pytest.fixture
def test_system_state():
    """A pytest fixture to provide a baseline SystemState for tests."""
    return SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(
            total=1000.0,
            complexity=500.0,
            coupling=300.0,
            constraint=100.0,
            debt=100.0
        ),
        lyapunov_metrics=LyapunovMetrics(
            phi=1.0,
            energy=1000.0,
            test_penalty=0.0,
            obligation_penalty=0.0
        ),
        metadata={
            'test_results': {'total_tests': 100, 'total_failures': 0},
            'risk_budget': {'empirical_budget': 1e-6},
            'policy': {'max_severity': 5},
            'proof_terms': [],
        }
    )

@pytest.fixture
def test_llm_client():
    """A pytest fixture to provide a mock LLM client."""
    class MockLLMClient:
        def generate(self, prompt):
            return "mocked LLM response"
    return MockLLMClient()

# This is not a fixture, but a constant that can be imported by tests.
# It should be populated with all the agent classes.
ALL_AGENT_CLASSES = [
    PlanckForgeAgent,
    SchrodingerDevAgent,
    PauliGuardAgent,
]
