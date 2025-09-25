import asyncio
import logging
from typing import List

from agents.base.agent import QuantumAgent
from core.config_loader import load_config
from core.types import QuantaCircConfig, AgentTask, AgentResult, Status

log = logging.getLogger(__name__)

class UncertainAIAgent(QuantumAgent):
    """
    An agent that reasons under uncertainty and resolves ambiguities.
    """
    def __init__(self, config: QuantaCircConfig):
        super().__init__(name="UncertainAI", config=config)

    @property
    def capabilities(self) -> List[str]:
        return ["ambiguity_resolution", "bayesian_inference", "decision_making"]

    async def process_task(self, task: AgentTask) -> AgentResult:
        log.info(f"UncertainAI received task: {task.payload}")
        await asyncio.sleep(1)
        result_payload = {
            "message": "Resolved ambiguity in requirement. Selected 'OAuth 2.0' for auth.",
            "decision_confidence": 0.95,
            "energy_impact": {"static": -5.0, "interaction": 1.0}
        }
        return AgentResult(
            task_id=task.id, agent_name=self.name, action_taken=True,
            result=result_payload, status=Status.SUCCESS
        )

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    config = load_config()
    agent = UncertainAIAgent(config)
    try:
        await agent.start()
        log.info("UncertainAI Agent is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("UncertainAI Agent is shutting down.")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())