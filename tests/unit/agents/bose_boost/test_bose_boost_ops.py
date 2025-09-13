import pytest
import yaml
from agents.bose_boost.ops import bose_einstein_distribution, generate_deployment_manifest
from core.data_models import TaskQuanta

def test_bose_einstein_distribution():
    # High energy -> low replicas
    assert bose_einstein_distribution(100, 50, 20) < 1.0
    # Low energy -> high replicas
    assert bose_einstein_distribution(40, 50, 20) > 1.0
    # Energy == chemical potential -> high replicas
    assert bose_einstein_distribution(50, 50, 20) == 10.0

def test_generate_deployment_manifest():
    task = TaskQuanta(id="my-app", description="d", verification_criteria=["v"])
    manifest_str = generate_deployment_manifest(task, 3)
    manifest = yaml.safe_load(manifest_str)

    assert manifest["kind"] == "Deployment"
    assert manifest["metadata"]["name"] == "my-app-deployment"
    assert manifest["spec"]["replicas"] == 3
    assert manifest["spec"]["template"]["spec"]["containers"][0]["image"] == "my-registry/my-app:latest"
