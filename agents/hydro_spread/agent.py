import asyncio
import logging
from typing import List

from agents.base.agent import QuantumAgent
from core.config_loader import load_config
from core.types import QuantaCircConfig, AgentTask, AgentResult, Status

log = logging.getLogger(__name__)

class HydroSpreadAgent(QuantumAgent):
    """
    An agent that generates documentation and spreads knowledge.
    """
    def __init__(self, config: QuantaCircConfig):
        super().__init__(name="HydroSpread", config=config)

    @property
    def capabilities(self) -> List[str]:
        return ["documentation_generation", "knowledge_propagation", "api_spec_creation"]

    async def process_task(self, task: AgentTask) -> AgentResult:
        log.info(f"HydroSpread received task: {task.payload}")
        await asyncio.sleep(1.5)
        result_payload = {
            "message": "Generated OpenAPI spec and updated README.",
            "docs_generated": ["docs/api.md", "README.md"],
            "energy_impact": {"static": -15.0}
        }
        return AgentResult(
            task_id=task.id, agent_name=self.name, action_taken=True,
            result=result_payload, status=Status.SUCCESS
        )

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    config = load_config()
    agent = HydroSpreadAgent(config)
    try:
        await agent.start()
        log.info("HydroSpread Agent is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("HydroSpread Agent is shutting down.")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())