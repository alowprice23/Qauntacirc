from typing import List, Dict, Any
import json

from core.types import QCState as State, AgentTask as Proposal, AgentResult as Action
from memory.constellation import ConstellationMemory
from memory.query import QueryBuilder

class AgentMemory:
    """
    Manages an agent's memory, including long-term storage and retrieval
    of decision-making patterns using the Constellation memory system.
    """
    def __init__(self, constellation_client: ConstellationMemory, agent_id: str):
        """
        Initializes the AgentMemory.

        Args:
            constellation_client: The client for the Constellation memory system.
            agent_id: The ID of the agent this memory belongs to.
        """
        self.constellation = constellation_client
        self.agent_id = agent_id

    def _create_state_summary(self, state: "State") -> str:
        """
        Converts a state object into a descriptive string for semantic search.
        """
        # This can be made more sophisticated, perhaps by summarizing the most
        # important components of the state.
        return f"Agent '{self.agent_id}' observed a state with energy {state.energy:.2f} in the '{state.optimization_phase}' phase."

    def record_decision(self, state: "State", proposal: "Proposal", action: "Action", outcome: str):
        """
        Records a decision-making event in the Constellation memory.

        Args:
            state: The state in which the decision was made.
            proposal: The proposal being considered.
            action: The action that was taken.
            outcome: The outcome of the action (e.g., 'success', 'failure').
        """
        decision_details = {
            "state_summary": self._create_state_summary(state),
            "proposal": proposal.to_dict() if hasattr(proposal, 'to_dict') else str(proposal),
            "action": action.to_dict() if hasattr(action, 'to_dict') else str(action),
            "outcome": outcome,
        }

        content = json.dumps(decision_details, indent=2)
        fact_type = f"decision_{outcome.lower()}"

        self.constellation.add_fact(
            content=content,
            fact_type=fact_type,
            owner=self.agent_id
        )

    def find_similar_decisions(self, current_state: "State", top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves past decisions made in similar states using semantic search.
        """
        query_text = self._create_state_summary(current_state)

        query = (
            QueryBuilder()
            .search(query_text)
            .mode("semantic")
            .with_types(["decision_success", "decision_failure"])
            .owned_by(self.agent_id)
            .limit(top_k)
            .build()
        )

        results = self.constellation.query(query)
        # Results are tuples of (node_id, data), we just return the data
        return [data for _, data in results]

    def learn_from_outcomes(self, successful_actions: List["Action"], failed_actions: List["Action"]):
        """
        Learns from successful and failed actions by adding them to the memory
        as artifacts to be processed by the NLP pipeline.
        """
        for action in successful_actions:
            content = f"Successful action taken: {action}"
            self.constellation.learn_from_artifact(
                artifact_type="successful_action",
                content=content,
                owner=self.agent_id
            )

        for action in failed_actions:
            content = f"Failed action attempt: {action}"
            self.constellation.learn_from_artifact(
                artifact_type="failed_action",
                content=content,
                owner=self.agent_id
            )