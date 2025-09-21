import pytest
from coq_interface import CoqKernelChecker

class MockProofTerm:
    def __init__(self, script, name="test_theorem"):
        self.proof_script = script
        self.theorem_name = name

def test_coq_kernel_checker_success():
    """
    Tests that the CoqKernelChecker returns success for a valid proof script.
    """
    checker = CoqKernelChecker()
    proof_term = MockProofTerm("Theorem test: forall n: nat, n = n. Proof. reflexivity. Qed.")
    result = checker.verify(proof_term)
    assert result.success is True
    assert result.error_log is None

def test_coq_kernel_checker_no_theorem():
    """
    Tests that the CoqKernelChecker returns failure for a script without a 'Theorem' keyword.
    """
    checker = CoqKernelChecker()
    proof_term = MockProofTerm("This is not a valid proof script.")
    result = checker.verify(proof_term)
    assert result.success is False
    assert "does not contain a 'Theorem' keyword" in result.error_log

def test_coq_kernel_checker_no_proof():
    """
    Tests that the CoqKernelChecker returns failure for a script without a 'Proof.' keyword.
    """
    checker = CoqKernelChecker()
    proof_term = MockProofTerm("Theorem test: forall n: nat, n = n.")
    result = checker.verify(proof_term)
    assert result.success is False
    assert "does not contain a 'Proof.' keyword" in result.error_log

def test_coq_kernel_checker_unbalanced_parens_open():
    """
    Tests that the CoqKernelChecker returns failure for a script with unclosed parentheses.
    """
    checker = CoqKernelChecker()
    proof_term = MockProofTerm("Theorem test: (forall n: nat, n = n. Proof. reflexivity. Qed.")
    result = checker.verify(proof_term)
    assert result.success is False
    assert "Mismatched parentheses: unclosed '('" in result.error_log

def test_coq_kernel_checker_unbalanced_parens_close():
    """
    Tests that the CoqKernelChecker returns failure for a script with unexpected closing parentheses.
    """
    checker = CoqKernelChecker()
    proof_term = MockProofTerm("Theorem test: forall n: nat, n = n). Proof. reflexivity. Qed.")
    result = checker.verify(proof_term)
    assert result.success is False
    assert "Mismatched parentheses: unexpected ')'" in result.error_log

def test_coq_kernel_checker_no_qed():
    """
    Tests that the CoqKernelChecker returns failure for a script without a 'Qed.' keyword.
    """
    checker = CoqKernelChecker()
    proof_term = MockProofTerm("Theorem test: forall n: nat, n = n. Proof. reflexivity.")
    result = checker.verify(proof_term)
    assert result.success is False
    assert "does not contain a 'Qed.' keyword" in result.error_log
