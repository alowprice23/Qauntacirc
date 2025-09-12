import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from core.types import (
    Plan, PlanNode, PlanEdge, Intent, CNLValidation, CNLValidationStatus,
    IntentContext, QCState, EnergyEstimate, RiskBound, QuantumSignatures,
    Priority, EffortLevel, PlanMetadata, VerificationPoint, EnergyMetrics,
    ConvergenceProof, LyapunovCertificate, Permission, SoftwareState, EnergyComponents
)
import uuid

# --- Helper to create a mock intent ---
# This is complex and doesn't need to be generated every time.
def get_mock_intent():
    return Intent(
        goal="Test",
        cnl_translation="Test",
        cnl_validation=CNLValidation(status=CNLValidationStatus.AUTO_ACCEPT, confidence=1.0),
        constraints={},
        context=IntentContext(session_id=uuid.uuid4(), user_profile={}, system_state=QCState(software_state=SoftwareState(component_versions={}, config_hashes={}), energy=0, energy_components=EnergyComponents(static=0,dynamic=0,interaction=0), lyapunov_potential=0, contraction_factor=0.5)),
        priority=Priority.LOW,
        acceptance_criteria=[],
        energy_estimate=EnergyEstimate(e_complexity=1, e_coupling=1, e_constraint=1, e_debt=1, total_estimated_energy=4),
        risk_assessment=RiskBound(confidence_level=1, failure_probability=0, details=""),
        requires_approval=False,
        estimated_effort=EffortLevel.TRIVIAL,
        quantum_signatures=QuantumSignatures(semantic_hash="", constraint_hash="")
    )

# --- Helper function to detect cycles in a graph ---
def has_cycle(nodes, edges) -> bool:
    adj = {node.id: [] for node in nodes}
    node_ids = {node.id for node in nodes}
    for edge in edges:
        if edge.from_node in node_ids and edge.to_node in node_ids:
            adj[edge.from_node].append(edge.to_node)

    path = set()
    visited = set()

    def dfs_check_cycle(node_id):
        visited.add(node_id)
        path.add(node_id)
        for neighbor in adj.get(node_id, []):
            if neighbor in path:
                return True
            if neighbor not in visited:
                if dfs_check_cycle(neighbor):
                    return True
        path.remove(node_id)
        return False

    for node_id in adj:
        if node_id not in visited:
            if dfs_check_cycle(node_id):
                return True
    return False

# --- Property-Based Test for Plan DAG Validation ---
@given(data=st.data())
def test_plan_dag_property(data):
    """
    Tests that the Plan model's DAG validation correctly identifies cycles
    for a wide range of generated graphs.
    """
    # 1. Generate a list of unique nodes
    nodes = data.draw(st.lists(
        st.builds(PlanNode, id=st.text(alphabet="ABCDE", min_size=1, max_size=1)),
        min_size=1, max_size=5, unique_by=lambda n: n.id
    ))
    node_ids = [n.id for n in nodes]

    # 2. Generate a list of edges connecting the generated nodes
    edges = data.draw(st.lists(
        st.builds(
            PlanEdge,
            from_node=st.sampled_from(node_ids),
            to_node=st.sampled_from(node_ids),
            transition_probability=st.floats(0, 1)
        ),
        max_size=5
    ))

    # 3. Determine if the generated graph is cyclic
    is_cyclic = has_cycle(nodes, edges)
    mock_intent = get_mock_intent()

    # 4. Assert that the Pydantic model validation matches our cycle check
    if is_cyclic:
        with pytest.raises(ValidationError, match="Plan contains a cycle, it is not a valid DAG."):
            Plan(
                intent=mock_intent,
                nodes=nodes,
                edges=edges,
                metadata=PlanMetadata(required_capabilities=set(), estimated_time_seconds=0, risk_assessment=mock_intent.risk_assessment),
                verification_points=[],
                energy_impact=EnergyMetrics(initial_energy=0, predicted_final_energy=0, delta_e=0),
                convergence_proof=ConvergenceProof(proof_sketch=""),
                lyapunov_certificate=LyapunovCertificate(function_definition="", descent_guarantee="")
            )
    else:
        # This should not raise an exception
        Plan(
            intent=mock_intent,
            nodes=nodes,
            edges=edges,
            metadata=PlanMetadata(required_capabilities=set(), estimated_time_seconds=0, risk_assessment=mock_intent.risk_assessment),
            verification_points=[],
            energy_impact=EnergyMetrics(initial_energy=0, predicted_final_energy=0, delta_e=0),
            convergence_proof=ConvergenceProof(proof_sketch=""),
            lyapunov_certificate=LyapunovCertificate(function_definition="", descent_guarantee="")
        )

@given(
    e_complexity=st.floats(0, 1e6),
    e_coupling=st.floats(0, 1e6),
    e_constraint=st.floats(0, 1e6),
    e_debt=st.floats(0, 1e6),
)
def test_energy_estimate_property(e_complexity, e_coupling, e_constraint, e_debt):
    """
    Tests that the total_estimated_energy is always the sum of its components.
    """
    total = e_complexity + e_coupling + e_constraint + e_debt

    # Test success case
    estimate = EnergyEstimate(
        e_complexity=e_complexity,
        e_coupling=e_coupling,
        e_constraint=e_constraint,
        e_debt=e_debt,
        total_estimated_energy=total
    )
    assert estimate.total_estimated_energy == total

    # Test failure case
    with pytest.raises(ValidationError):
        EnergyEstimate(
            e_complexity=e_complexity,
            e_coupling=e_coupling,
            e_constraint=e_constraint,
            e_debt=e_debt,
            total_estimated_energy=total + 1.0 # Mismatch
        )
