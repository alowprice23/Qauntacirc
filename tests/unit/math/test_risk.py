import unittest
import z3
import numpy as np
from proofs.composition import ProofCertificate
from math_utils.risk import compute_risk_bound, validate_risk_bound_mc

def dummy_system_model(failure_prob: float):
    """A dummy system model with a known probability of failure."""
    def model():
        return np.random.rand() > failure_prob
    return model

class TestRiskComputation(unittest.TestCase):

    def test_compute_risk_bound_z3(self):
        evidence = {"constraints": ["x > 5", "y < 10"], "variables": {"x": z3.IntSort(), "y": z3.IntSort()}}
        cert = ProofCertificate("thm1", "Proved", evidence, "Z3")
        risk = compute_risk_bound([cert])
        self.assertAlmostEqual(risk, 0.0004)

    def test_compute_risk_bound_coq(self):
        script = "Require Import Lia. Definition f(x:Z):Z := x+1. Theorem t: forall x, f x = x+1. Proof. intros. unfold f. lia. Qed."
        evidence = {"script": script}
        cert = ProofCertificate("thm2", "Proved", evidence, "Coq")
        risk = compute_risk_bound([cert])
        self.assertAlmostEqual(risk, 0.00114)

    def test_compute_risk_bound_disproved(self):
        cert = ProofCertificate("thm3", "Disproved", {}, "Z3")
        risk = compute_risk_bound([cert])
        self.assertAlmostEqual(risk, 100.0 / 1000)

    def test_compute_risk_bound_unknown(self):
        cert = ProofCertificate("thm4", "Unknown", {}, "Coq")
        risk = compute_risk_bound([cert])
        self.assertAlmostEqual(risk, 50.0 / 1000)

    def test_validate_risk_bound_mc_success(self):
        risk_bound = 0.2
        failure_prob = 0.1
        model = dummy_system_model(failure_prob)
        self.assertTrue(validate_risk_bound_mc(risk_bound, model, num_samples=10000))

    def test_validate_risk_bound_mc_failure(self):
        risk_bound = 0.1
        failure_prob = 0.2
        model = dummy_system_model(failure_prob)
        self.assertFalse(validate_risk_bound_mc(risk_bound, model, num_samples=10000))

if __name__ == '__main__':
    unittest.main()
