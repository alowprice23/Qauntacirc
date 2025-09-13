import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import UUID
from core.data_models import (
    EnergyComponents,
    SoftwareState,
    QuantumState,
    QCState,
    AgentTask,
    AgentResult,
    RunRecord,
    Plan, PlanNode, PlanEdge, Intent, CNLValidation, CNLValidationStatus,
    IntentContext, EnergyEstimate, RiskBound, QuantumSignatures,
    Priority, EffortLevel, PlanMetadata, VerificationPoint, EnergyMetrics,
    ConvergenceProof, LyapunovCertificate, Permission,
    LyapunovMetrics, EnergyBreakdown
)
import uuid

def test_energy_components_total():
    """Tests the total energy calculation."""
    components = EnergyComponents(total=3.0, complexity=1.0, coupling=2.5, constraint=-0.5, debt=0.0)
    assert components.total == 3.0

def test_qcstate_creation_defaults():
    """Tests the default values for a QCState instance."""
    state = QCState(
        software_state=SoftwareState(
            component_versions={"test_comp": "1.0"},
            config_hashes={"test_conf": "abc"},
        ),
        energy_breakdown=EnergyBreakdown(total=2.0, complexity=1.0, coupling=1.0, constraint=0.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=0.5, energy=2.0, test_penalty=0.0, obligation_penalty=0.0),
        contraction_factor=0.5,
    )
    assert isinstance(state.id, UUID)
    assert isinstance(state.timestamp, datetime)
    assert state.phase == "A"
    assert state.metadata == {}

# This test is no longer valid as the validator was removed.
# def test_qcstate_energy_validator_success():
#     """Tests successful validation of energy components."""
#     state = QCState(
#         software_state=SoftwareState(),
#         energy_breakdown=EnergyBreakdown(total=5.0, complexity=1.5, coupling=2.5, constraint=1.0, debt=0.0),
#         lyapunov_metrics=LyapunovMetrics(phi=0.5, energy=5.0, test_penalty=0.0, obligation_penalty=0.0),
#         contraction_factor=0.5,
#     )
#     assert state.energy_breakdown.total == 5.0

# This test is no longer valid as the validator was removed.
# def test_qcstate_energy_validator_failure():
#     """Tests failed validation when energy components don't sum up."""
#     with pytest.raises(ValidationError, match="Total energy must equal the sum of its components."):
#         QCState(
#             software_state=SoftwareState(),
#             energy_breakdown=EnergyBreakdown(total=2.0, complexity=1.0, coupling=1.0, constraint=1.0, debt=0.0), # Total should be 3.0
#             lyapunov_metrics=LyapunovMetrics(phi=0.5, energy=2.0, test_penalty=0.0, obligation_penalty=0.0),
#             contraction_factor=0.5,
#         )

def test_qcstate_contraction_factor_valid():
    """Tests valid contraction factors."""
    for factor in [0.0, 0.5, 1.0]:
        state = QCState(
            software_state=SoftwareState(),
            energy_breakdown=EnergyBreakdown(total=2.0, complexity=1.0, coupling=1.0, constraint=0.0, debt=0.0),
            lyapunov_metrics=LyapunovMetrics(phi=0.5, energy=2.0, test_penalty=0.0, obligation_penalty=0.0),
            contraction_factor=factor,
        )
        assert state.contraction_factor == factor

def test_qcstate_contraction_factor_invalid():
    """Tests invalid contraction factors."""
    for factor in [-0.1, 1.1]:
        with pytest.raises(ValidationError):
            QCState(
                software_state=SoftwareState(),
                energy_breakdown=EnergyBreakdown(total=2.0, complexity=1.0, coupling=1.0, constraint=0.0, debt=0.0),
                lyapunov_metrics=LyapunovMetrics(phi=0.5, energy=2.0, test_penalty=0.0, obligation_penalty=0.0),
                contraction_factor=factor,
            )

def test_agent_task_defaults():
    """Tests default values for AgentTask."""
    task = AgentTask(
        agent_name="test_agent",
        task_type="test_task",
        payload={"data": "test"},
    )
    assert isinstance(task.id, UUID)
    assert isinstance(task.created_at, datetime)
    assert task.priority == 5
    assert task.quantum_context is None

def test_agent_task_priority_validation():
    """Tests priority validation for AgentTask."""
    with pytest.raises(ValidationError):
        AgentTask(
            agent_name="test_agent",
            task_type="test_task",
            payload={},
            priority=0,
        )
    with pytest.raises(ValidationError):
        AgentTask(
            agent_name="test_agent",
            task_type="test_task",
            payload={},
            priority=11,
        )

def test_run_record_time_validator():
    """Tests the time validator for RunRecord."""
    now = datetime.utcnow()
    earlier = datetime.fromtimestamp(now.timestamp() - 10)

    qc_state = QCState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0),
        contraction_factor=0.5,
    )

    # Valid
    record = RunRecord(
        start_time=earlier,
        end_time=now,
        status="completed",
        initial_state=qc_state,
        final_state=qc_state,
    )
    assert record.end_time > record.start_time

    # Invalid
    with pytest.raises(ValidationError, match="end_time must not be before start_time"):
        RunRecord(
            start_time=now,
            end_time=earlier,
            status="completed",
            initial_state=qc_state,
            final_state=qc_state,
        )

def get_mock_intent():
    return Intent(
        goal="Test",
        cnl_translation="Test",
        cnl_validation=CNLValidation(status=CNLValidationStatus.AUTO_ACCEPT, confidence=1.0),
        constraints={},
        context=IntentContext(session_id=uuid.uuid4(), user_profile={},
                              system_state=QCState(software_state=SoftwareState(),
                                                   energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0),
                                                   lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0),
                                                   contraction_factor=0.5)),
        priority=Priority.LOW,
        acceptance_criteria=[],
        energy_estimate=EnergyEstimate(e_complexity=1, e_coupling=1, e_constraint=1, e_debt=1, total_estimated_energy=4),
        risk_assessment=RiskBound(confidence_level=1, failure_probability=0, details=""),
        requires_approval=False,
        estimated_effort=EffortLevel.TRIVIAL,
        quantum_signatures=QuantumSignatures(semantic_hash="", constraint_hash="")
    )

def test_plan_dag_validation_success():
    """Tests that a valid DAG plan validates successfully."""
    mock_intent = get_mock_intent()

    nodes = [
        PlanNode(id="A", description="", agent_name="", tool_call="", preconditions=[], postconditions=[], energy_barrier=1),
        PlanNode(id="B", description="", agent_name="", tool_call="", preconditions=[], postconditions=[], energy_barrier=1),
        PlanNode(id="C", description="", agent_name="", tool_call="", preconditions=[], postconditions=[], energy_barrier=1),
    ]
    edges = [
        PlanEdge(from_node="A", to_node="B", transition_probability=1.0, condition=""),
        PlanEdge(from_node="B", to_node="C", transition_probability=1.0, condition=""),
    ]

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

def test_plan_dag_validation_failure_cycle():
    """Tests that a plan with a cycle fails validation."""
    mock_intent = get_mock_intent()

    nodes = [
        PlanNode(id="A", description="", agent_name="", tool_call="", preconditions=[], postconditions=[], energy_barrier=1),
        PlanNode(id="B", description="", agent_name="", tool_call="", preconditions=[], postconditions=[], energy_barrier=1),
        PlanNode(id="C", description="", agent_name="", tool_call="", preconditions=[], postconditions=[], energy_barrier=1),
    ]
    edges = [
        PlanEdge(from_node="A", to_node="B", transition_probability=1.0, condition=""),
        PlanEdge(from_node="B", to_node="C", transition_probability=1.0, condition=""),
        PlanEdge(from_node="C", to_node="A", transition_probability=1.0, condition=""),
    ]

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
