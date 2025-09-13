from typing import List, Any, TYPE_CHECKING

from memory.types import (
    ConstellationQuery,
    Fact,
    FactNode,
    OptimizedContext,
    OptimizationProblem,
    OptimizationItem,
    TokenConstraint,
    OptimizationSolution,
    AssembledContext,
    FactType,
)
from memory.knowledge_graph import QuantumKnowledgeGraph
from memory.consistency import MathematicalConsistencyEngine

if TYPE_CHECKING:
    from memory.constellation import ConstellationMemory


class InformationOptimizer:
    """
    Solves the knapsack-like problem of selecting the most valuable facts
    for a given token budget using a greedy approach.
    """
    def solve(self, problem: OptimizationProblem) -> OptimizationSolution:
        """
        Solves the optimization problem using a greedy algorithm based on value-to-weight ratio.
        """
        items = sorted(problem.items, key=lambda x: x.value / x.weight if x.weight > 0 else float('inf'), reverse=True)

        selected_items: List[OptimizationItem] = []
        total_weight = 0
        total_value = 0

        max_weight = float('inf')
        for constraint in problem.constraints:
            if isinstance(constraint, TokenConstraint):
                max_weight = constraint.max_tokens
                break

        for item in items:
            if total_weight + item.weight <= max_weight:
                selected_items.append(item)
                total_weight += item.weight
                total_value += item.value

        return OptimizationSolution(
            selected_facts=[item.fact for item in selected_items],
            total_information=total_value,
            optimality_proof="Greedy solution (heuristic, not optimal)."
        )


class ContextAssemblyEngine:
    """
    Assembles optimal, consistent context for agents based on information-theoretic principles.
    """
    def __init__(self, constellation: 'ConstellationMemory'):
        self.constellation = constellation
        self.information_optimizer = InformationOptimizer()
        self.consistency_engine = MathematicalConsistencyEngine()

    def _compute_information_value(self, fact_node: FactNode) -> float:
        """
        Computes the information value of a fact, combining confidence and entropy.
        A high-entropy fact is less predictable and thus more informative.
        """
        # Weighting confidence and entropy. These weights can be tuned.
        confidence_weight = 0.6
        entropy_weight = 0.4

        # Entropy is in bits/byte. We can use it as a measure of information content.
        entropy = fact_node.encoding.entropy if fact_node.encoding else 0
        confidence = fact_node.fact.confidence

        return (confidence_weight * confidence) + (entropy_weight * entropy)

    def _estimate_token_cost(self, fact: Fact) -> int:
        """Estimates the token cost of a fact."""
        # A simple heuristic: number of words + number of properties.
        prop_cost = len(str(fact.mathematical_properties)) // 5 # Estimate tokens for properties
        return len(str(fact.content).split()) + prop_cost

    def _formulate_context_optimization(self, fact_nodes: List[FactNode], max_tokens: int) -> OptimizationProblem:
        """Formulates the context optimization as a knapsack problem."""
        items = []
        for fn in fact_nodes:
            items.append(OptimizationItem(
                id=fn.id,
                value=self._compute_information_value(fn),
                weight=self._estimate_token_cost(fn.fact),
                fact=fn.fact,
            ))

        return OptimizationProblem(
            objective="maximize_information",
            items=items,
            constraints=[TokenConstraint(max_tokens=max_tokens)],
            mathematical_formulation="Knapsack problem (0/1) formulation, solved with a greedy heuristic."
        )

    def _assemble_context_preserving_structure(self, selected_facts: List[Fact]) -> AssembledContext:
        """Assembles a structured context from the selected facts."""
        context_parts = []
        for fact in selected_facts:
            part = (
                f"- Fact (Type: {fact.type.value}, Confidence: {fact.confidence:.2f}):\n"
                f"  Content: {fact.content}\n"
                f"  Properties: {fact.mathematical_properties}"
            )
            context_parts.append(part)

        context_text = "\n".join(context_parts)
        return AssembledContext(text=context_text, selected_facts=selected_facts)

    def _verify_context_consistency(self, assembled_context: AssembledContext) -> Any:
        """Verifies the internal consistency of the assembled context."""
        if not assembled_context.selected_facts:
            return {"consistent": True, "details": "No facts to check."}

        # Create a temporary knowledge graph with the selected facts
        temp_graph = QuantumKnowledgeGraph()
        for fact in assembled_context.selected_facts:
            temp_graph.create_knowledge_node(fact)

        # Check each fact against the temporary graph containing the others
        all_violations = []
        for fact in assembled_context.selected_facts:
            result = self.consistency_engine.verify_consistency(fact, temp_graph)
            if not result.consistent:
                all_violations.extend(result.violations)

        if not all_violations:
            return {"consistent": True, "details": "All selected facts are internally consistent."}
        else:
            return {"consistent": False, "details": "Inconsistencies found in context.", "violations": all_violations}

    def assemble_context(self, query: str, max_tokens: int) -> OptimizedContext:
        """Assembles optimal context with information-theoretic guarantees."""
        relevant_fact_nodes = self.constellation.query_facts(ConstellationQuery(
            text=query,
            max_results=100,  # Retrieve a larger pool for better optimization
            similarity_threshold=0.7
        )).facts

        if not relevant_fact_nodes:
            return OptimizedContext(
                context_text="",
                selected_facts=[],
                information_content=0,
                token_usage=0,
                mathematical_consistency={"consistent": True, "details": "No relevant facts found."},
                optimization_proof="No facts to optimize."
            )

        optimization_problem = self._formulate_context_optimization(relevant_fact_nodes, max_tokens)
        solution = self.information_optimizer.solve(optimization_problem)

        assembled_context = self._assemble_context_preserving_structure(solution.selected_facts)
        consistency_verification = self._verify_context_consistency(assembled_context)

        token_usage = len(assembled_context.text.split())

        return OptimizedContext(
            context_text=assembled_context.text,
            selected_facts=solution.selected_facts,
            information_content=solution.total_information,
            token_usage=token_usage,
            mathematical_consistency=consistency_verification,
            optimization_proof=solution.optimality_proof
        )
