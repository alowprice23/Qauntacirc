from .decomposer import CommandDecomposer
from .dependency_analyzer import DependencyAnalyzer
from .execution_planner import ExecutionPlanner
from .context_manager import ContextManager, SessionContext
from .command_history import CommandHistory
from .auto_completion import AutoCompletion
from typing import Dict, Any

class NLProcessor:
    """
    Handles complex, multi-step software engineering commands.
    This class orchestrates the decomposition, dependency analysis,
    and execution planning, and provides auto-completion.
    """

    def __init__(self):
        self.decomposer = CommandDecomposer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.planner = ExecutionPlanner()
        self.context_manager = ContextManager()
        # The processor now owns the command history and auto-completion engine
        self.command_history = CommandHistory()
        self.auto_completer = AutoCompletion(self.command_history)

    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Processes a complex command and stores the result in history.
        """
        # 1. Decompose
        decomposition = self.decomposer.decompose(command)
        atomic_ops = decomposition.get("atomic_operations", [])

        if not atomic_ops:
            return {"error": "Could not understand the command."}

        # 2. Analyze Dependencies
        dependency_analysis = self.dependency_analyzer.analyze_dependencies(atomic_ops)
        dependency_graph = dependency_analysis.get("dependency_graph", {})

        # 3. Create Plan
        plan_result = self.planner.create_plan(dependency_graph)

        if "error" in plan_result:
            return plan_result

        # 4. Update Context
        updated_context = self.context_manager.update_context(
            command=command,
            decomposition=decomposition,
            dependency_graph=dependency_analysis,
            plan=plan_result
        )

        # 5. Compile and store the final result
        last_entry = updated_context.history[-1]
        final_result = {
            "command": command, # Make sure the original command is in the result
            "decomposed_operations": last_entry.get("decomposed_operations"),
            "dependency_graph": last_entry.get("dependency_graph"),
            "optimal_execution_plan": last_entry.get("optimal_execution_plan"),
            "updated_context": {
                "session_energy": updated_context.energy,
                "history_count": len(updated_context.history)
            },
            "mathematical_complexity": last_entry.get("mathematical_complexity"),
            "energy_impact_prediction": last_entry.get("predicted_energy_impact")
        }

        # Add the detailed result to our long-term command history
        self.command_history.add_entry(final_result)

        return final_result

    def get_completion_suggestions(self, partial_input: str) -> Dict[str, Any]:
        """
        Provides intelligent auto-completion for a partial command.
        """
        return self.auto_completer.get_suggestions(partial_input)
