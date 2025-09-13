import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from deployment.mathematical_deployment_automation_system import MathematicalDeploymentAutomationSystem
from deployment.data_models import SystemState, DeploymentTarget

@pytest.fixture(autouse=True)
def mock_k8s_config():
    with patch('kubernetes.config.load_incluster_config') as mock_incluster, \
         patch('kubernetes.config.load_kube_config') as mock_kubeconfig:
        yield

@pytest.fixture
def mock_kubernetes_manager():
    mock = MagicMock()
    mock.apply_manifest.return_value = None
    mock.get_deployment_status.return_value = "Running"
    return mock

@pytest.fixture
def mock_iac_engine(mock_kubernetes_manager):
    from deployment.iac_engine import InfrastructureAsCodeEngine
    engine = InfrastructureAsCodeEngine(mock_kubernetes_manager)
    mock_status = MagicMock()
    mock_status.available_replicas = 1
    engine.apply_infrastructure_with_verification = MagicMock(return_value={
        "infrastructure": {},
        "status": mock_status
    })
    return engine

@pytest.fixture
def mock_capacity_planner():
    from deployment.capacity_planner import MathematicalCapacityPlanner
    planner = MathematicalCapacityPlanner()
    planner.generate_optimal_deployment_config = MagicMock(return_value={
        "name": "test-app",
        "replicas": 3,
        "cpu_per_replica": 0.5,
        "mem_per_replica": 256,
        "image": "test-image:1.0",
        "port": 8080,
    })
    return planner

@pytest.fixture
def mock_deployment_verifier():
    from deployment.deployment_verifier import DeploymentMathematicalVerifier
    verifier = DeploymentMathematicalVerifier()
    verifier.verify_deployment_mathematics = AsyncMock(return_value={
        "verification_certificate": {"verified": True}
    })
    return verifier

@pytest.fixture
def mock_monitoring_engine(mock_kubernetes_manager):
    from deployment.monitoring_engine import MonitoringSetupEngine
    engine = MonitoringSetupEngine(mock_kubernetes_manager)
    engine.setup_monitoring_with_mathematical_alerts = AsyncMock(return_value={
        "monitoring_setup_successful": True
    })
    return engine

@pytest.mark.asyncio
async def test_deployment_automation_system(
    mock_kubernetes_manager,
    mock_iac_engine,
    mock_capacity_planner,
    mock_deployment_verifier,
    mock_monitoring_engine,
):
    # Arrange
    system = SystemState(
        requirements={
            "name": "test-app",
            "cpu_per_replica": 0.5,
            "mem_per_replica": 256,
            "image": "test-image:1.0",
            "port": 8080,
        },
        artifacts=[],
    )
    deployment_target = DeploymentTarget(
        environment="staging",
        resource_constraints={
            "max_total_cpu": 4,
            "max_total_mem": 1024,
            "min_replicas": 2,
            "max_replicas": 5,
        },
        performance_targets={},
        optimization_objectives={},
        alerting_config={},
    )

    automation_system = MathematicalDeploymentAutomationSystem()
    automation_system.kubernetes_manager = mock_kubernetes_manager
    automation_system.infrastructure_as_code_engine = mock_iac_engine
    automation_system.mathematical_capacity_planner = mock_capacity_planner
    automation_system.deployment_verifier = mock_deployment_verifier
    automation_system.monitoring_setup_engine = mock_monitoring_engine

    # Act
    result = await automation_system.deploy_system_with_mathematical_guarantees(
        system, deployment_target
    )

    # Assert
    assert result.deployment_successful
    assert result.infrastructure_result["status"] != "Not Found"
    assert result.deployment_verification["verification_certificate"]["verified"]
    assert result.monitoring_setup["monitoring_setup_successful"]
    assert "mathematical_deployment_certificate" in result.model_dump()
