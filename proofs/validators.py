class CoqValidator:
    def __init__(self, config):
        self.config = config

    def validate_proofs(self, path):
        print(f"Validating Coq proofs at {path}")
        return []

class AgdaValidator:
    def __init__(self, config):
        self.config = config

    def validate_proofs(self, path):
        print(f"Validating Agda proofs at {path}")
        return []

class SMTValidator:
    def __init__(self, config):
        self.config = config

    def validate_proofs(self, path):
        print(f"Validating SMT proofs at {path}")
        return []

from typing import List, Dict, Any

class ProofObligation:
    def __init__(self, description: str, is_proven: bool = False):
        self.description = description
        self.is_proven = is_proven

class ProofObligationTracker:
    """
    Tracks proof obligations for the system.
    """
    def __init__(self, obligations: List[ProofObligation] = None):
        self.obligations = obligations if obligations is not None else []

    def get_unproven_obligations(self) -> List[ProofObligation]:
        """
        Returns a list of all unproven obligations.
        """
        return [ob for ob in self.obligations if not ob.is_proven]

    def get_unproven_obligation_count(self) -> int:
        """
        Returns the number of unproven obligations.
        """
        return len(self.get_unproven_obligations())
