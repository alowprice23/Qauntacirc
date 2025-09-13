from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SystemState(BaseModel):
    """
    Represents the state of the system to be deployed.
    """
    requirements: Dict[str, Any] = Field(..., description="The requirements of the system.")
    artifacts: List[str] = Field(..., description="The artifacts of the system.")

class DeploymentTarget(BaseModel):
    """
    Represents the target for the deployment.
    """
    environment: str = Field(..., description="The deployment environment (e.g., 'staging', 'production').")
    resource_constraints: Dict[str, Any] = Field(..., description="The resource constraints of the target environment.")
    performance_targets: Dict[str, Any] = Field(..., description="The performance targets for the deployment.")
    optimization_objectives: Dict[str, Any] = Field(..., description="The mathematical optimization objectives.")
    verification_timeout: int = Field(600, description="The timeout for deployment verification in seconds.")
    alerting_config: Dict[str, Any] = Field({}, description="The configuration for alerts.")

class DeploymentResult(BaseModel):
    """
    Represents the result of a deployment.
    """
    deployment_successful: bool
    infrastructure_result: Dict[str, Any]
    deployment_execution: Dict[str, Any]
    deployment_verification: Dict[str, Any]
    monitoring_setup: Dict[str, Any]
    mathematical_deployment_certificate: Dict[str, Any]
