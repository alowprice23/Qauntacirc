import unittest
import z3
from proofs.composition import ProofCertificate, validate_certificate, compose_proofs
from proofs.coq import generate_coq_script

class TestComposition(unittest.TestCase):

    def test_proof_certificate(self):
        evidence = {"constraints": ["x > 5"], "variables": {"x": z3.IntSort()}}
        cert = ProofCertificate("x > 5", "Proved", evidence, "Z3")
        self.assertEqual(cert.theorem, "x > 5")
        self.assertEqual(cert.status, "Proved")
        self.assertEqual(cert.evidence, evidence)
        self.assertEqual(cert.validator, "Z3")

    def test_validate_z3_certificate_sat(self):
        evidence = {"constraints": ["x > 5"], "variables": {"x": z3.IntSort()}}
        cert = ProofCertificate("x > 5", "Proved", evidence, "Z3")
        self.assertTrue(validate_certificate(cert))

    def test_validate_z3_certificate_unsat(self):
        evidence = {"constraints": ["x > 5", "x < 5"], "variables": {"x": z3.IntSort()}}
        cert = ProofCertificate("x > 5 and x < 5", "Disproved", evidence, "Z3")
        self.assertFalse(validate_certificate(cert))

    def test_validate_coq_certificate_proved(self):
        func_name = "increment"
        func_code = "def increment(x): return x + 1"
        theorem = "increment x = x + 1"
        coq_script = generate_coq_script(func_name, func_code, theorem)
        evidence = {"script": coq_script}
        cert = ProofCertificate(theorem, "Proved", evidence, "Coq")
        self.assertTrue(validate_certificate(cert))

    def test_validate_coq_certificate_disproved(self):
        func_name = "identity"
        func_code = "def identity(x): return x"
        theorem = "identity x = x + 1" # This is false
        coq_script = generate_coq_script(func_name, func_code, theorem)
        evidence = {"script": coq_script}
        cert = ProofCertificate(theorem, "Disproved", evidence, "Coq")
        self.assertFalse(validate_certificate(cert))

    def test_compose_proofs(self):
        cert_a = ProofCertificate("A", "Proved", {}, "Z3")
        cert_b = ProofCertificate("B", "Proved", {}, "Coq")
        composed = compose_proofs([cert_a, cert_b])
        self.assertEqual(len(composed), 2)
        self.assertIn(cert_a, composed)
        self.assertIn(cert_b, composed)

    def test_compose_proofs_with_dependencies(self):
        cert_a = ProofCertificate("A", "Proved", {}, "Z3")
        cert_b = ProofCertificate("B", "Proved", {}, "Coq", dependencies=["A"])
        cert_c = ProofCertificate("C", "Proved", {}, "Z3", dependencies=["B"])

        composed = compose_proofs([cert_c, cert_b, cert_a])

        self.assertEqual(len(composed), 3)
        self.assertEqual(composed[0].theorem, "A")
        self.assertEqual(composed[1].theorem, "B")
        self.assertEqual(composed[2].theorem, "C")

if __name__ == '__main__':
    unittest.main()
