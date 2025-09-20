import pytest
from unittest.mock import patch
from agents.uncertain_ai.agent import UncertainAIAgent
from core.types import (
    SystemState, Module, EnergyBreakdown, LyapunovMetrics, SoftwareState,
    UncertaintyAnalysis
)
from datetime import datetime

@pytest.fixture
def uncertain_agent():
    """Fixture for an UncertainAIAgent instance."""
    return UncertainAIAgent()

@pytest.fixture
def system_state_with_uncertainty():
    """Fixture for a SystemState with data for uncertainty analysis."""
    modules = [
        Module(name="a.py", normalized_ast=b"...", semantic_tokens=["a", "b", "c"], cyclomatic_complexity=5, duplication_factor=0.1, coverage_deficit=0.2, last_refactor=datetime.now()),
        Module(name="b.py", normalized_ast=b"...", semantic_tokens=["d", "e", "f", "g"], cyclomatic_complexity=10, duplication_factor=0.0, coverage_deficit=0.1, last_refactor=datetime.now())
    ]
    requirements = [
        "The system must be secure.",
        "The system must be fast and responsive."
    ]
    state = SystemState(
        software_state=SoftwareState(),
        modules=modules,
        requirements=requirements,
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
    )
    return state

def test_apply_physics_principle_calculates_uncertainty(uncertain_agent, system_state_with_uncertainty):
    """
    Tests that apply_physics_principle correctly calculates uncertainty metrics.
    """
    # Mock the test generator and risk quantifier to return predictable results
    with patch.object(uncertain_agent.test_generator, 'generate_tests', return_value=["new_test_1"]) as mock_gen, \
         patch.object(uncertain_agent.risk_quantifier, 'compute_chernoff_bounds') as mock_risk:

        mock_risk.return_value = {"lower_bound": 0.0, "upper_bound": 0.1, "confidence": 0.95}

        # Act
        result = uncertain_agent.apply_physics_principle(system_state_with_uncertainty)

        # Assert
        assert isinstance(result, UncertaintyAnalysis)
        assert result.success is True
        assert result.agent_name == "uncertain_ai"
        assert result.physics_principle == "Uncertainty Principle"

        # Check that uncertainty was calculated
        assert result.spec_uncertainty > 0
        assert result.impl_uncertainty > 0
        assert result.uncertainty_product > 0

        # Check if the principle was satisfied or not, and if tests were generated
        if result.satisfies_principle:
            mock_gen.assert_not_called()
            assert len(result.additional_tests) == 0
        else:
            mock_gen.assert_called_once()
            assert len(result.additional_tests) > 0

        # Check that risk was quantified
        mock_risk.assert_called_once()
        assert result.risk_bounds is not None

def test_apply_physics_principle_no_requirements_or_modules(uncertain_agent):
    """
    Tests that the agent handles a state with no requirements or modules.
    """
    state = SystemState(
        software_state=SoftwareState(),
        modules=[],
        requirements=[],
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
    )

    # Act
    result = uncertain_agent.apply_physics_principle(state)

    # Assert
    assert isinstance(result, UncertaintyAnalysis)
    assert result.success is True
    assert result.spec_uncertainty == 0
    assert result.impl_uncertainty == 0
    assert result.uncertainty_product == 0
    # With zero uncertainty, the principle is satisfied
    assert result.satisfies_principle is True
    assert len(result.additional_tests) == 0
