from core.types import CompletenessProof

class MockAgentCommunicationProtocol:
    async def send_message(self, agent_id: str, message: dict):
        pass

class MockClosureRuleEngine:
    class MockCompletenessProof(CompletenessProof):
        def __init__(self):
            super().__init__(
                obligation_count=0,
                proof_steps=[],
                verification_method="mock",
                confidence=1.0,
            )

    class MockClosureResult:
        def __init__(self):
            self.is_closed = True
            self.is_minimal = True
            self.completeness_proof = MockClosureRuleEngine.MockCompletenessProof()

    def verify_closure(self, requirements, obligations):
        return self.MockClosureResult()

class MockEnergyCalculator:
    class MockEnergyBreakdown:
        def __init__(self):
            self.total = 100.0

    def compute_total_energy(self, state):
        return self.MockEnergyBreakdown()

class MockLyapunovMonitor:
    class MockLyapunovMetrics:
        def __init__(self):
            self.phi = 0.5

    def compute(self, state):
        return self.MockLyapunovMetrics()

class MockClosureValidator:
    def validate(self, state):
        return {"is_valid": True}
