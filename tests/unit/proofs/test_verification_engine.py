import unittest
from unittest.mock import MagicMock, patch, ANY
from proofs.validators import VerificationEngine, CompositionRules
from core.types import LogicType, PropertySpecification, VerificationResult, ComposedVerificationResult, ConsistencyCheck

class FailingVerifier:
    def verify(self, spec: str) -> dict:
        return {"success": False, "error": "Coq failed"}

class TestVerificationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = VerificationEngine()

    @patch('proofs.validators.CoqVerifier')
    @patch('proofs.validators.Z3Verifier')
    def test_verify_property_success(self, mock_z3_verifier, mock_coq_verifier):
        # Mock the verifiers to return successful results
        mock_coq_verifier.return_value.verify.return_value = {"success": True, "proves_termination": True}
        mock_z3_verifier.return_value.verify.return_value = {"success": True}

        # Mock the composition rules to return a valid consistency check
        self.engine.composition_rules.check_consistency = MagicMock(return_value=ConsistencyCheck(valid=True))

        property_spec = PropertySpecification(id="test_property", description="A test property", category="test")
        result = self.engine.verify_property(property_spec)

        self.assertTrue(result.success)
        self.assertIn(LogicType.COQ, result.logic_results)
        self.assertIn(LogicType.SMT_Z3, result.logic_results)
        self.assertTrue(result.logic_results[LogicType.COQ].success)
        self.assertTrue(result.logic_results[LogicType.SMT_Z3].success)

    def test_verify_property_failure(self):
        # Use a real object that fails instead of a mock
        self.engine.verifiers[LogicType.COQ] = FailingVerifier()

        property_spec = PropertySpecification(id="test_property", description="A test property", category="test")
        result = self.engine.verify_property(property_spec)

        self.assertFalse(result.success)
        self.assertIn("Verification failed in", result.error)

    @patch('proofs.validators.CoqVerifier')
    @patch('proofs.validators.Z3Verifier')
    def test_inconsistent_results(self, mock_z3_verifier, mock_coq_verifier):
        # Mock the verifiers to return successful results
        mock_coq_verifier.return_value.verify.return_value = {"success": True, "proves_termination": True}
        mock_z3_verifier.return_value.verify.return_value = {"success": True}

        # Mock the composition rules to return an invalid consistency check
        self.engine.composition_rules.check_consistency = MagicMock(return_value=ConsistencyCheck(valid=False, error="Inconsistent results"))

        property_spec = PropertySpecification(id="test_property", description="A test property", category="test")
        result = self.engine.verify_property(property_spec)

        self.assertFalse(result.success)
        self.assertIn("Cross-logic inconsistency", result.error)

class TestCompositionRules(unittest.TestCase):
    def setUp(self):
        self.rules = CompositionRules()

    def test_check_consistency_success(self):
        results = {
            LogicType.COQ: VerificationResult(success=True, proves_termination=True),
            LogicType.SMT_Z3: VerificationResult(success=True)
        }

        property_spec = PropertySpecification(id="test", description="test", category="test")
        check = self.rules.check_consistency(results, property_spec)
        self.assertTrue(check.valid)

    def test_check_consistency_failure(self):
        results = {
            LogicType.COQ: VerificationResult(success=True, proves_termination=True),
            LogicType.SMT_Z3: VerificationResult(success=True)
        }
        # Mocking so that Coq's assumption is not satisfied by SMT's guarantee
        self.rules._extract_guarantees = MagicMock(side_effect=[["functional_correctness", "termination"], []])
        self.rules._extract_assumptions = MagicMock(side_effect=[["arithmetic_safety"], []])

        property_spec = PropertySpecification(id="test", description="test", category="test")
        check = self.rules.check_consistency(results, property_spec)
        self.assertFalse(check.valid)
        self.assertIn("not satisfied", check.error)

if __name__ == '__main__':
    unittest.main()
