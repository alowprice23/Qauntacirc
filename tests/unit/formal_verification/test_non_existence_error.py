import pytest
import asyncio
from formal_verification.non_existence_error import (
    NonExistenceErrorFramework,
    SystemOutput,
    DetectedError,
    ErrorFreeVerificationResult,
    ErrorPreventionResult,
    SelfHealingResult,
)
from core.data_models import (
    SystemState,
    QuantumState,
    SoftwareState,
    EnergyBreakdown,
    LyapunovMetrics,
)

@pytest.fixture
def framework():
    """Provides an instance of the NonExistenceErrorFramework."""
    return NonExistenceErrorFramework()

@pytest.fixture
def sample_system_output():
    """Provides a sample SystemOutput object."""
    return SystemOutput(content="Sample system output data.")

@pytest.fixture
def sample_system_state():
    """Provides a sample SystemState object."""
    return SystemState(
        software_state=SoftwareState(),
        quantum_state=QuantumState(),
        energy_breakdown=EnergyBreakdown(total=0.0, complexity=0.0, coupling=0.0, constraint=0.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=0.0, energy=0.0, test_penalty=0.0, obligation_penalty=0.0)
    )

@pytest.fixture
def sample_detected_error():
    """Provides a sample DetectedError object."""
    return DetectedError(predicate_name="factual_accuracy_error", details={"info": "some details"})


@pytest.mark.asyncio
async def test_instantiation(framework):
    """Tests that the framework can be instantiated."""
    assert framework is not None
    assert len(framework.error_predicates) == 12

@pytest.mark.asyncio
async def test_verify_error_free_operation_mathematically_success(framework, sample_system_output):
    """Tests the verification method in a success scenario (no errors)."""
    result = await framework.verify_error_free_operation_mathematically(sample_system_output)
    assert isinstance(result, ErrorFreeVerificationResult)
    assert result.error_free is True
    assert result.non_existence_formula_satisfied is True
    assert result.violated_predicate is None
    assert "PROOF: All predicates are false." in result.mathematical_error_free_proof

@pytest.mark.asyncio
async def test_predictive_error_prevention_with_mathematical_bounds(framework, sample_system_state):
    """Tests the predictive prevention method."""
    result = await framework.predictive_error_prevention_with_mathematical_bounds(sample_system_state)
    assert isinstance(result, ErrorPreventionResult)
    assert result.predictive_error_prevention_successful is True
    assert len(result.error_probability_analysis) == 12

@pytest.mark.asyncio
async def test_execute_autonomous_self_healing(framework, sample_detected_error, sample_system_state):
    """Tests the autonomous self-healing method."""
    result = await framework.execute_autonomous_self_healing(sample_detected_error, sample_system_state)
    assert isinstance(result, SelfHealingResult)
    assert result.healing_successful is True
    assert result.healing_strategy.strategy_name == "Optimal"
