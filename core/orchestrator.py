import asyncio
import concurrent.futures
from typing import Dict, Any, List, Optional
from nats.aio.client import Client as NATS
from core.dependency_graph import DependencyGraph
from core.system_state import SystemState
from core.state_manager import StateManager
from core.rollback_manager import RollbackManager
from core.failure_manager import FailureManager, RecoveryStrategy
from core.resource_manager import ResourceManager
from core.metrics_manager import MetricsManager
from agents.base.agent import QuantumAgent

class Orchestrator:
    def __init__(self, config: Dict[str, Any], nats_client: NATS):
        self.config = config
        self.nats_client = nats_client
        self.dependency_graph = DependencyGraph()
        self.state_manager = StateManager(nats_client)
        self.rollback_manager = RollbackManager()
        self.failure_manager = FailureManager(self.rollback_manager)
        self.metrics_manager = MetricsManager()

        resource_limits = config.get('resource_limits', {})
        self.resource_manager = ResourceManager(
            cpu_limit=resource_limits.get('cpu'),
            memory_limit=resource_limits.get('memory')
        )

        self.agents: Dict[str, QuantumAgent] = {}
        self.agent_dependencies: Dict[str, Dict[str, List[str]]] = {}

    async def initialize(self):
        await self.state_manager.initialize()

    def register_agent(self, agent: QuantumAgent, dependencies: Dict[str, List[str]]):
        self.agents[agent.name] = agent
        self.agent_dependencies[agent.name] = dependencies
        self.dependency_graph.add_agent(
            agent.name,
            inputs=dependencies.get('inputs', []),
            outputs=dependencies.get('outputs', [])
        )
        self.metrics_manager.increment_counter("agents_registered")

    async def run(
        self,
        initial_state: SystemState,
        task: str,
        max_agents: int = 4,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.CONTINUE,
        simulate_failure: Optional[str] = None
    ) -> SystemState:
        self.metrics_manager.increment_counter("orchestration_runs_started")
        await self.state_manager.publish_state_change("orchestrator", {"status": "starting"})
        execution_plan = self.dependency_graph.resolve_dependencies()

        current_state = await self.state_manager.get_current_state(initial_state)

        with self.metrics_manager.track_execution_time("orchestration_run"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_agents) as executor:
                for agent_name in execution_plan:

                    while not self.resource_manager.is_within_limits():
                        self.metrics_manager.increment_counter("resource_throttling_events")
                        print("Resource limits exceeded. Throttling execution for 5 seconds.")
                        await asyncio.sleep(5)

                    agent = self.agents[agent_name]
                    self.rollback_manager.save_snapshot(agent_name, current_state)

                    try:
                        if agent_name == simulate_failure:
                            raise Exception(f"Simulated failure for agent {agent_name}")

                        with self.metrics_manager.track_execution_time(f"agent_{agent_name}_execution"):
                            future = executor.submit(agent.execute, current_state, task)
                            delta = future.result()

                        await self.state_manager.publish_state_change(agent_name, delta)
                        current_state = await self.state_manager.get_current_state(initial_state)
                        self.metrics_manager.increment_counter(f"agent_{agent_name}_success")

                    except Exception as e:
                        self.metrics_manager.increment_counter(f"agent_{agent_name}_failure")
                        current_state = self.failure_manager.handle_failure(
                            agent_name=agent_name,
                            exception=e,
                            recovery_strategy=recovery_strategy
                        )

        await self.state_manager.publish_state_change("orchestrator", {"status": "completed"})
        self.metrics_manager.increment_counter("orchestration_runs_completed")
        return await self.state_manager.get_current_state(initial_state)