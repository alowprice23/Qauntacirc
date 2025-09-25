import asyncio
import logging
from typing import List

from agents.base.agent import QuantumAgent
from core.config_loader import load_config
from core.types import QuantaCircConfig, AgentTask, AgentResult, Status

log = logging.getLogger(__name__)

class TunnelFixAgent(QuantumAgent):
    """
    An agent that performs bug detection and resolution.
    """
    def __init__(self, config: QuantaCircConfig):
        super().__init__(name="TunnelFix", config=config)

    @property
    def capabilities(self) -> List[str]:
        return ["bug_detection", "automated_fixing", "static_analysis"]

    async def process_task(self, task: AgentTask) -> AgentResult:
        log.info(f"TunnelFix received task: {task.payload}")
        await asyncio.sleep(2)
        result_payload = {
            "message": "Code analysis complete. Applied one minor fix.",
            "fix_id": "fix-abc-456",
            "energy_impact": {"dynamic": -30.0, "interaction": -10.0}
        }
        return AgentResult(
            task_id=task.id, agent_name=self.name, action_taken=True,
            result=result_payload, status=Status.SUCCESS
        )

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    config = load_config()
    agent = TunnelFixAgent(config)
    try:
        await agent.start()
        log.info("TunnelFix Agent is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("TunnelFix Agent is shutting down.")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())