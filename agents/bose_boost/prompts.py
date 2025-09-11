"""
Prompts for the BoseBoost Agent.
"""
from agents.base.prompts import PromptSpec

GENERATE_SCALING_PLAN_V1 = PromptSpec(
    name="bose_boost_generate_scaling_plan",
    version="1.0",
    template="""\
You are an expert DevOps engineer. Your task is to analyze the following deployment plan and provide a summary of the scaling strategy.

Deployment Manifest:
```yaml
{deployment_manifest}
```

Analysis Guidelines:
1.  **Summarize the Replica Count**: State the number of replicas for the deployment.
2.  **Explain the Rationale**: Briefly explain that the replica count was determined by a model based on the task's energy (complexity).
3.  **Suggest Monitoring**: Recommend key metrics to monitor for this deployment (e.g., CPU, memory, latency).

Output Format:
Provide the output as a JSON object with the following keys: "summary", "rationale", "monitoring_recommendations".

Example:
...

Now, analyze the provided deployment manifest.
""",
    variables=["deployment_manifest"]
)

PROMPT_REGISTRY = {
    "generate_scaling_plan": {
        "1.0": GENERATE_SCALING_PLAN_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
