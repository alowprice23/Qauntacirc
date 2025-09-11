"""
Prompts for the FluctuaTest Agent.
"""
from agents.base.prompts import PromptSpec

GENERATE_CHAOS_EXPERIMENT_V1 = PromptSpec(
    name="fluctuatest_generate_chaos_experiment",
    version="1.0",
    template="""\
You are a chaos engineer. Your task is to design a chaos experiment for the following system component.

Component Description:
"{component_description}"

Experiment Design Guidelines:
1.  **Hypothesis**: State a clear hypothesis about how the system will behave under a specific failure condition (e.g., "The system will remain available, with latency under 200ms, when the database connection is lost for 30 seconds.").
2.  **Experiment Type**: Propose a specific type of chaos experiment (e.g., latency injection, error injection, resource exhaustion).
3.  **Magnitude**: Specify the magnitude of the experiment (e.g., "inject 100ms of latency", "terminate 1 out of 3 pods").
4.  **Duration**: Specify the duration of the experiment.

Output Format:
Provide the output as a JSON object with the following keys: "hypothesis", "experiment_type", "magnitude", "duration_seconds".

Now, design a chaos experiment for the provided component.
""",
    variables=["component_description"]
)

PROMPT_REGISTRY = {
    "generate_chaos_experiment": {
        "1.0": GENERATE_CHAOS_EXPERIMENT_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
