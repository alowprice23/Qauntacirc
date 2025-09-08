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
