import uuid
from typing import List, Optional

from agents.base.agent import QuantumAgent
from core.types import SystemState, AgentTask, AgentResult, QuantizedTasks, TaskQuantum, Status
from common.utils import FrequencyAnalyzer

class NLParser:
    def parse(self, text: str) -> dict:
        return {"requirements": [text]}

class PlanckForgeAgent(QuantumAgent):
    def __init__(self, **kwargs):
        super().__init__(name="planck_forge", **kwargs)
        self.physics_principle = "Energy Quantization"
        self.mathematical_formula = "E_n = n·h·ν"
        self.h = 6.62607015e-34
        self.frequency_analyzer = FrequencyAnalyzer()
        self.nl_parser = NLParser()

    def analyze_state(self, state: SystemState) -> AgentTask:
        """
        Analyzes requirements and proposes quantized tasks based on Planck's hypothesis.
        """
        requirements_str = " ".join(state.requirements) if state.requirements else ""
        if not requirements_str and "planck_forge_input" in state.metadata:
             requirements_str = state.metadata["planck_forge_input"].get("requirements", "")

        if not requirements_str:
            return AgentTask(
                agent_name=self.name, task_type="quantization", payload={},
                status=Status.FAILED, reason="No requirements found in state."
            )

        # Core physics logic is now directly in analyze_state
        frequencies = self.frequency_analyzer.extract_frequencies(requirements_str)
        quanta = []
        for freq_data in frequencies:
            ν = freq_data.frequency
            for n in range(1, freq_data.max_harmonics + 1):
                energy_level = n * self.h * ν
                task_quantum = TaskQuantum(
                    n=n, frequency=ν, energy=energy_level,
                    description=freq_data.task_description,
                    dependencies=freq_data.dependencies
                )
                quanta.append(task_quantum)

        quantized_tasks = QuantizedTasks(quanta=quanta, total_energy=sum(q.energy for q in quanta))

        return AgentTask(
            agent_name=self.name,
            task_type="quantization",
            payload={"quantized_tasks": quantized_tasks.model_dump()},
            status=Status.SUCCESS
        )

    def validate_proposal(self, proposal: AgentTask) -> bool:
        """Validates the proposal."""
        return proposal.status == Status.SUCCESS and "quantized_tasks" in proposal.payload

    def execute(self, proposal: AgentTask) -> AgentResult:
        """Executes the proposal by returning the quantized tasks."""
        if self.validate_proposal(proposal):
            return AgentResult(
                task_id=proposal.id, agent_name=self.name, action_taken=True,
                result=proposal.payload, status=Status.SUCCESS
            )
        else:
            return AgentResult(
                task_id=proposal.id, agent_name=self.name, action_taken=False,
                error="Invalid proposal", status=Status.FAILED
            )
