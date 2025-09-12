from datetime import datetime
from typing import List, Dict, Any

from agents.base.agent import PhysicsBasedAgent
from core.types import SystemState, PhysicsResult, Observable, AgentAction
from memory.constellation import ConstellationMemory
from memory.contracts import MemoryGuidance, MemoryUpdate, ActionResult
from memory.types import ConstellationQuery, Intent, Plan, ExecutionResult
from common.verification import AgentCertificate

class MemoryInterface:
    """A simple interface to the constellation memory."""
    def __init__(self, constellation: ConstellationMemory):
        self.constellation = constellation

class MemoryAwareAgent(PhysicsBasedAgent):
    """
    An agent that consults with the constellation memory before and after actions.
    """
    def __init__(self, agent_type: str, constellation: ConstellationMemory):
        super().__init__(physics_principle=agent_type, mathematical_formula="N/A")
        self.constellation = constellation
        self.memory_interface = MemoryInterface(constellation)

    # --- Memory-related methods ---
    def consult_memory_before_action(self, current_state: SystemState) -> MemoryGuidance:
        """Consults constellation memory for relevant patterns and constraints."""
        query_text = f"Similar to current system state with energy {current_state.energy_breakdown.total}"

        similar_situations = self.constellation.query_facts(ConstellationQuery(
            text=query_text,
            filters={"state_type": "SystemState"},
            mathematical_filters={}
        ))

        relevant_patterns = [fact.fact.content for fact in similar_situations.facts]
        recommendations = [f"Found {len(relevant_patterns)} similar patterns."]

        guidance = MemoryGuidance(
            patterns=relevant_patterns,
            recommendations=recommendations,
            mathematical_justification="dummy_justification_from_consultation",
            confidence=0.9,
            risk_assessment={"level": "low", "details": "placeholder"}
        )
        return guidance

    def update_memory_after_action(self, action: AgentAction, result: ActionResult) -> MemoryUpdate:
        """Updates constellation memory with action outcomes and learned patterns."""
        dummy_intent = Intent(description=action.action_type)
        dummy_plan = Plan(steps=[str(action.params)])

        # Convert ActionResult to ExecutionResult
        exec_result = ExecutionResult(**result.model_dump())

        learning_result = self.constellation.learn_pattern(
            intent=dummy_intent,
            plan=dummy_plan,
            result=exec_result
        )

        if learning_result and learning_result.pattern_node:
            update = MemoryUpdate(
                pattern_node=learning_result.pattern_node,
                memory_delta=0.1, # placeholder value
                learning_certificate=learning_result.mathematical_certificate or "N/A"
            )
            return update
        return None

    # --- Abstract method implementations ---
    def apply_physics_principle(self, system_state: SystemState) -> PhysicsResult:
        """A demonstration of the agent's workflow including memory consultation."""
        print(f"\n--- MemoryAwareAgent ({self.physics_principle}) applying principle ---")

        # 1. Consult memory before acting
        print("1. Consulting memory...")
        guidance = self.consult_memory_before_action(system_state)
        print(f"   - Guidance received: {guidance.recommendations}")

        # 2. Perform a dummy action
        print("2. Performing action...")
        action = AgentAction(agent_id=self.physics_principle, action_type="dummy_action", params={"guidance_used": True})
        result = ActionResult(
            success=True,
            confidence=0.95,
            success_metrics={"dummy_metric": 1.0},
            energy_delta=-0.05,
            convergence_metrics={"dummy_conv": 0.01}
        )
        print("   - Action complete.")

        # 3. Update memory with the outcome
        print("3. Updating memory with outcome...")
        update = self.update_memory_after_action(action, result)
        if update:
            print(f"   - Memory update successful. Certificate: {update.learning_certificate}")
        else:
            print("   - Memory update failed or was not applicable.")

        print("--- Agent finished ---")
        return PhysicsResult()

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measures a dummy observable."""
        return Observable(name="awareness_level", value=1.0, unit="units")

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: PhysicsResult) -> AgentCertificate:
        """Generates a dummy certificate for the operation."""
        return AgentCertificate(
            agent_name=self.physics_principle,
            timestamp=datetime.now(),
            data_hash="dummy_hash_value",
            signature="dummy_signature_value"
        )
