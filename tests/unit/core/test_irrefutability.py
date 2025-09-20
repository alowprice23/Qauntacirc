import pytest
from core.irrefutability_engine import IrrefutabilityEngine
from core.types import BuildArtifacts

def test_irrefutability_engine_instantiation():
    """
    Tests that the IrrefutabilityEngine can be instantiated.
    """
    try:
        engine = IrrefutabilityEngine()
        assert engine is not None
    except Exception as e:
        pytest.fail(f"Failed to instantiate IrrefutabilityEngine: {e}")

def test_verify_acceptance_irrefutability_runs():
    """
    A simple smoke test to ensure verify_acceptance_irrefutability runs without errors.
    """
    engine = IrrefutabilityEngine()
    artifacts = BuildArtifacts(files=["test.py"])

    # Since there are no predicates initialized, the logical conjunction will be True.
    # We test both a correct and incorrect acceptance decision.

    # Case 1: Correct decision (True == True)
    result_true = engine.verify_acceptance_irrefutability(
        build_artifacts=artifacts,
        acceptance_decision=True
    )
    assert result_true is not None
    assert result_true.decision_irrefutable is True

    # Case 2: Incorrect decision (False != True)
    result_false = engine.verify_acceptance_irrefutability(
        build_artifacts=artifacts,
        acceptance_decision=False
    )
    assert result_false is not None
    assert result_false.decision_irrefutable is False
