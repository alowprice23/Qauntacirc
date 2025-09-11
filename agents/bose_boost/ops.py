"""
Operations for the BoseBoost Agent.

This module provides utilities for generating deployment manifests based on
Bose-Einstein statistics, which determine resource allocation (e.g., replicas)
based on the "energy" of task quanta.
"""
import math
import yaml
from typing import Dict, Any, List
from core.types import TaskQuanta

def bose_einstein_distribution(energy: float, chemical_potential: float, temperature: float) -> float:
    """
    Calculates the expected number of "particles" (e.g., replicas) for a given
    energy level, based on Bose-Einstein statistics.
    """
    if temperature <= 0:
        return 1.0 # Avoid division by zero, default to 1 replica

    exponent = (energy - chemical_potential) / temperature

    # Avoid overflow
    if exponent > 700:
        return 0.0

    denominator = math.exp(exponent) - 1

    if denominator <= 0:
        # This happens when energy is less than or equal to the chemical potential,
        # suggesting a high number of replicas are needed. We cap it.
        return 10.0

    return 1.0 / denominator

def generate_deployment_manifest(task: TaskQuanta, num_replicas: int) -> str:
    """
    Generates a mock Kubernetes deployment manifest for a given task.
    """
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{task.id}-deployment",
        },
        "spec": {
            "replicas": num_replicas,
            "selector": {
                "matchLabels": {
                    "app": task.id,
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": task.id,
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": task.id,
                            "image": f"my-registry/{task.id}:latest",
                            "ports": [{"containerPort": 8080}],
                        }
                    ]
                }
            }
        }
    }
    return yaml.dump(manifest)
