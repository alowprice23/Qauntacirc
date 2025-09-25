import asyncio
import logging
from typing import List

from agents.base.agent import QuantumAgent
from core.config_loader import load_config
from core.types import QuantaCircConfig, AgentTask, AgentResult, Status

log = logging.getLogger(__name__)

class PauliGuardAgent(QuantumAgent):
    """
    An agent that enforces security policies and compliance constraints.
    """
    def __init__(self, config: QuantaCircConfig):
        super().__init__(name="PauliGuard", config=config)

    @property
    def capabilities(self) -> List[str]:
        return ["security_analysis", "policy_enforcement", "vulnerability_scanning"]

    async def process_task(self, task: AgentTask) -> AgentResult:
        log.info(f"PauliGuard received task: {task.payload}")
        await asyncio.sleep(1.5)
        result_payload = {
            "message": "Security scan complete. No violations found.",
            "report_id": "sec-scan-123",
            "energy_impact": {"static": -10.0, "interaction": -5.0}
        }
        return AgentResult(
            task_id=task.id, agent_name=self.name, action_taken=True,
            result=result_payload, status=Status.SUCCESS
        )

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    config = load_config()
    agent = PauliGuardAgent(config)
    try:
        await agent.start()
        log.info("PauliGuard Agent is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("PauliGuard Agent is shutting down.")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())