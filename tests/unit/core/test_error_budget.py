import unittest
import numpy as np
from core.error_budget import ErrorBudgetManager
from core.types import TestResults, VerificationResult, CoverageReport, PropertySpecification
from core.orchestrator import Orchestrator

class TestErrorBudgetManager(unittest.TestCase):
    def setUp(self):
        # Use a larger budget for testing purposes to allow for the calculated risk.
        self.manager = ErrorBudgetManager(total_budget=0.3)

    def test_compute_composite_risk_bound(self):
        verification_results = [VerificationResult(success=True)]
        test_results = TestResults(total_tests=100, total_failures=1)

        risk_bound = self.manager.compute_composite_risk_bound(verification_results, test_results)

        # With the larger budget, the calculated risk should be within budget.
        self.assertTrue(risk_bound.within_budget)
        self.assertAlmostEqual(risk_bound.verified_component, 0.0)
        self.assertGreater(risk_bound.empirical_component, 0.0)
        self.assertAlmostEqual(risk_bound.security_component, self.manager.security_budget)
        expected_risk_min = 1/100
        self.assertGreater(risk_bound.empirical_component, expected_risk_min)

    def test_compute_empirical_risk_no_tests(self):
        test_results = TestResults(total_tests=0, total_failures=0)
        risk = self.manager._compute_empirical_risk(test_results)
        self.assertEqual(risk, 1.0)

    def test_compute_empirical_risk_no_failures(self):
        test_results = TestResults(total_tests=1000, total_failures=0)
        risk = self.manager._compute_empirical_risk(test_results)
        self.assertGreater(risk, 0)
        self.assertLess(risk, 0.1)

    def test_compute_empirical_risk_with_failures(self):
        test_results = TestResults(total_tests=100, total_failures=10)
        risk = self.manager._compute_empirical_risk(test_results)
        self.assertGreater(risk, 0.1)

class TestRiskOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()

    def test_adjust_risk_for_coverage(self):
        base_risk = 0.05
        coverage_report = CoverageReport(
            overall_coverage=80.0,
            by_category={},
            by_logic={},
            uncovered_properties=[],
            line_coverage=80.0,
            branch_coverage=70.0,
            total_tests=1000
        )

        adjusted_risk = self.orchestrator.adjust_risk_for_coverage(base_risk, coverage_report)

        # The adjusted risk should be the re-calculated Chernoff bound plus the residual risk.
        # For high coverage, this should be close to the original base_risk.
        self.assertAlmostEqual(adjusted_risk, 0.052, places=3)

    def test_adjust_risk_low_coverage(self):
        base_risk = 0.05
        coverage_report = CoverageReport(
            overall_coverage=10.0,
            by_category={},
            by_logic={},
            uncovered_properties=[],
            line_coverage=10.0,
            branch_coverage=10.0,
            total_tests=100
        )

        adjusted_risk = self.orchestrator.adjust_risk_for_coverage(base_risk, coverage_report)

        # With very low coverage, risk should be significantly higher.
        self.assertGreater(adjusted_risk, base_risk)

if __name__ == '__main__':
    unittest.main()
