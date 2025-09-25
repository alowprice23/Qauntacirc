import asyncio
import logging
from typing import List, Dict, Any, Tuple

from agents.base.agent import QuantumAgent
from core.config_loader import load_config
from core.types import QuantaCircConfig, AgentTask, AgentResult, Status

log = logging.getLogger(__name__)

class PlanckForgeAgent(QuantumAgent):
    """
    An agent specializing in quantizing high-level requirements into discrete,
    verifiable tasks.
    """
    def __init__(self, config: QuantaCircConfig):
        super().__init__(name="PlanckForge", config=config)

    @property
    def capabilities(self) -> List[str]:
        return ["requirements_quantization", "task_decomposition"]

    def can_handle(self, task: AgentTask) -> Tuple[bool, str]:
        """Decline tasks that don't have a text payload."""
        if isinstance(task.payload, dict) and task.payload.get("text"):
            return True, ""
        return False, "Task payload must be a dict with a non-empty 'text' field."

    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Processes a high-level requirement and breaks it down into quanta.
        """
        log.info(f"PlanckForge received task: {task.payload.get('text')}")

        # Simulate the work of quantization
        await asyncio.sleep(2)  # Simulate I/O or CPU-bound work

        quantized_tasks = [
            {"id": "task-001", "description": "Define API endpoints for JWT"},
            {"id": "task-002", "description": "Create user schema with password hash"},
            {"id": "task-003", "description": "Implement token generation logic"},
        ]

        result_payload = {
            "message": "Requirement quantized successfully.",
            "quantized_tasks": quantized_tasks,
            "energy_impact": {"static": -50.0, "dynamic": -20.0}
        }

        return AgentResult(
            task_id=task.id,
            agent_name=self.name,
            action_taken=True,
            result=result_payload,
            status=Status.SUCCESS,
        )

async def main():
    """Main entry point to run the agent as a standalone service."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    config = load_config()
    agent = PlanckForgeAgent(config)

    try:
        await agent.start()
        log.info("PlanckForge Agent is running. Press Ctrl+C to stop.")
        # Keep the agent running indefinitely
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("PlanckForge Agent is shutting down.")
    finally:
        await agent.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass