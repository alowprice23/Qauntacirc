import pytest
from unittest.mock import MagicMock, patch
from core.irrefutability_engine import IrrefutabilityEngine
from core.types import BuildArtifacts, PredicateResult, SystemVerification, VerificationResult
import os

@pytest.fixture
def engine():
    """Fixture for a clean IrrefutabilityEngine instance."""
    return IrrefutabilityEngine()

def test_irrefutability_engine_instantiation(engine):
    """Tests that the IrrefutabilityEngine can be instantiated."""
    assert engine is not None
    assert engine.axioms is not None
    assert engine.decidable_predicates is not None
    assert engine.proof_checkers is not None

def test_verify_acceptance_irrefutability_all_predicates_pass(engine):
    """
    Tests verify_acceptance_irrefutability when all predicates pass.
    """
    artifacts = BuildArtifacts(files=[])

    # Mock all predicates to return a successful result
    for predicate_name in engine.decidable_predicates:
        engine.decidable_predicates[predicate_name] = MagicMock(
            return_value=PredicateResult(
                predicate=predicate_name,
                value=True,
                witness="mock witness",
                checker_used="mock_checker",
                replayable=True,
                hash="mock_hash"
            )
        )

    # Case 1: Correct decision (True == True)
    result_true = engine.verify_acceptance_irrefutability(
        build_artifacts=artifacts,
        acceptance_decision=True
    )
    assert result_true.decision_irrefutable is True
    assert result_true.logical_conjunction is True

def test_compile_artifacts_success(engine, tmpdir):
    """Tests the compilation simulation with a valid file."""
    p = tmpdir.join("valid.py")
    p.write("def hello():\n    print('hello')")
    result = engine._compile_artifacts([str(p)])
    assert result['success'] is True

def test_compile_artifacts_file_not_found(engine):
    """Tests the compilation simulation with a missing file."""
    result = engine._compile_artifacts(["non_existent_file.py"])
    assert result['success'] is False
    assert "File not found" in result['error_log']

def test_compile_artifacts_syntax_error(engine, tmpdir):
    """Tests the compilation simulation with a syntax error."""
    p = tmpdir.join("invalid.py")
    p.write("def hello()")
    result = engine._compile_artifacts([str(p)])
    assert result['success'] is False
    assert "Syntax error" in result['error_log']

def test_run_static_analysis_success(engine, tmpdir):
    """Tests the static analysis simulation with a clean file."""
    p = tmpdir.join("clean.py")
    p.write("def hello():\n    print('hello')")
    result = engine._run_static_analysis([str(p)])
    assert len(result['issues']) == 0

def test_run_static_analysis_with_todo(engine, tmpdir):
    """Tests the static analysis simulation with a TODO comment."""
    p = tmpdir.join("todo.py")
    p.write("# TODO: fix this")
    result = engine._run_static_analysis([str(p)])
    assert len(result['issues']) == 1
    assert result['issues'][0]['description'] == 'Found TODO comment.'

def test_run_static_analysis_long_function(engine, tmpdir):
    """Tests the static analysis simulation with a long function."""
    p = tmpdir.join("long.py")
    long_function = "def long_func():\n" + "\n".join(["    pass" for _ in range(51)])
    p.write(long_function)
    result = engine._run_static_analysis([str(p)])
    assert len(result['issues']) == 1
    assert "is too long" in result['issues'][0]['description']

def test_run_static_analysis_high_complexity(engine, tmpdir):
    """Tests the static analysis simulation with a high complexity function."""
    p = tmpdir.join("complex.py")
    complex_function = """
def complex_func(a, b, c, d, e, f, g, h, i, j, k):
    if a > b and b > c and c > d and d > e and e > f and f > g and g > h and h > i and i > j and j > k:
        return 1
    elif a < b < c < d < e < f < g < h < i < j < k:
        return 2
    else:
        return 3
"""
    p.write(complex_function)
    result = engine._run_static_analysis([str(p)])
    assert len(result['issues']) == 1
    assert "has a high cyclomatic complexity" in result['issues'][0]['description']

def test_risk_bound_predicate_success(engine):
    """Tests the risk bound predicate when the risk is within budget."""
    artifacts = BuildArtifacts(
        metadata={
            'test_results': {'total_tests': 1000, 'total_failures': 1},
            'risk_budget': {'empirical_budget': 1e-3}
        }
    )
    result = engine._risk_bound_predicate(artifacts)
    assert result.value is True

def test_risk_bound_predicate_failure(engine):
    """Tests the risk bound predicate when the risk exceeds the budget."""
    artifacts = BuildArtifacts(
        metadata={
            'test_results': {'total_tests': 100, 'total_failures': 30},
            'risk_budget': {'empirical_budget': 1e-6}
        }
    )
    result = engine._risk_bound_predicate(artifacts)
    assert result.value is False

def test_prove_irrefutability_theorem(engine):
    """Tests that the irrefutability theorem can be generated."""
    theorem = engine.prove_irrefutability_theorem()
    assert theorem is not None
    assert theorem.certainty_level == "MATHEMATICAL"
    assert len(theorem.proof_steps) == 5

def test_generate_final_irrefutability_certificate(engine):
    """Tests the generation of the final irrefutability certificate."""
    system_verification = SystemVerification(
        energy_proofs="mock",
        convergence_proofs="mock",
        functor_proofs="mock",
        agent_validations="mock",
        risk_calculations="mock",
        closure_proofs="mock",
        statistical_tests="mock",
        integration_results="mock"
    )
    certificate = engine.generate_final_irrefutability_certificate(system_verification)
    assert certificate is not None
    assert certificate.irrefutability_score == 1.0
    assert certificate.mathematical_certainty_level == "IRREFUTABLE"

def test_generate_final_irrefutability_certificate_weighting(engine):
    """Tests the weighting logic in the final certificate generation."""
    system_verification = SystemVerification()

    with patch.object(engine, '_analyze_mathematical_certainty', return_value={
        'formal_proof_coverage': 0.8,
        'statistical_bound_quality': 0.7,
        'empirical_test_strength': 0.6,
        'logical_foundation_soundness': 0.5,
        'closure_complete': True,
    }):
        certificate = engine.generate_final_irrefutability_certificate(system_verification)

    expected_score = (0.4 * 0.8) + (0.3 * 0.7) + (0.2 * 0.6) + (0.1 * 0.5)
    assert abs(certificate.irrefutability_score - expected_score) < 1e-9
    assert certificate.mathematical_certainty_level == "STATISTICALLY_SOUND"

def test_verify_mathematical_certainty(engine):
    """Tests the verification of mathematical certainty for a list of claims."""
    claims = [
        "Energy function is non-negative",
        "Basin capture probability ≥ 0.9",
        "This is a new claim"
    ]

    with patch.object(engine, '_execute_mathematical_verification', return_value={'proven': True, 'witness': 'w', 'checker_output': 'o'}), \
         patch.object(engine, '_execute_statistical_verification', return_value={'significant': True, 'test_statistic': 's', 'confidence_interval': (0.1, 0.9), 'data_hash': 'h'}):

        result = engine.verify_mathematical_certainty(claims)

    assert result.mathematical_certainty_count == 1
    assert result.statistical_certainty_count == 1
    assert result.unverified_count == 1
