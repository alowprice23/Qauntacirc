"""
This module provides tools for composing proofs from different verification systems
and for validating their certificates.
"""
from typing import List, Dict, Any, Literal
import tempfile
import os
import z3
from core.constraint_solver import ConstraintSolver
from proofs.coq import verify_coq_script

class ProofCertificate:
    """
    Represents a proof certificate from a verification system.
    """
    def __init__(self,
                 theorem: str,
                 status: Literal["Proved", "Disproved", "Unknown"],
                 evidence: Dict[str, Any],
                 validator: Literal["Z3", "Coq"],
                 dependencies: List[str] = None):
        self.theorem = theorem
        self.status = status
        self.evidence = evidence
        self.validator = validator
        self.dependencies = dependencies or []

    def __repr__(self):
        return f"ProofCertificate(theorem='{self.theorem}', status='{self.status}', validator='{self.validator}')"

def validate_certificate(certificate: ProofCertificate) -> bool:
    """
    Validates a proof certificate using the appropriate validator.
    """
    if certificate.validator == "Z3":
        solver = ConstraintSolver()
        constraints = certificate.evidence.get("constraints", [])
        variables = certificate.evidence.get("variables", {})
        return solver.solve(constraints, variables)
    elif certificate.validator == "Coq":
        script = certificate.evidence.get("script", "")
        if not script:
            return False
        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(script)
            script_path = f.name
        try:
            verified, _ = verify_coq_script(script_path)
            return verified
        finally:
            # The .vo and .glob files are removed by verify_coq_script,
            # but the .v file needs to be removed here.
            if os.path.exists(script_path):
                os.remove(script_path)
    return False

def compose_proofs(certificates: List[ProofCertificate]) -> List[ProofCertificate]:
    """
    Composes multiple proof certificates, respecting dependencies.

    This is a simplified topological sort. A more robust implementation
    would handle cycles.
    """
    sorted_certs = []
    certs_by_theorem = {c.theorem: c for c in certificates}

    visited = set()

    def visit(cert):
        if cert.theorem in visited:
            return
        for dep_theorem in cert.dependencies:
            if dep_theorem in certs_by_theorem:
                visit(certs_by_theorem[dep_theorem])
        sorted_certs.append(cert)
        visited.add(cert.theorem)

    for cert in certificates:
        visit(cert)

    return sorted_certs
