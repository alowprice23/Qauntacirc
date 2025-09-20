from core.chaos_types import ChaosScenario

def get_all_scenarios():
    """
    Returns a list of predefined chaos testing scenarios.
    This is a placeholder. In a real system, this might load from a config file.
    """
    return [
        ChaosScenario(
            name="default_scenario",
            description="A default mock scenario.",
            target_components=["default_component"],
            fault_injection=lambda: "Injected default fault!",
            expected_behavior="System should recover.",
            recovery_criteria={"metric": "latency", "threshold": 200},
            blast_radius=0.2,
            duration_seconds=30
        )
    ]
