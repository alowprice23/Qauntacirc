# agents/test_agent/prompts.py
"""
Prompts for the TestAgent Agent.
"""

from agents.base.prompts import PromptSpec

# Example prompt
EXAMPLE_PROMPT_V1 = PromptSpec(
    name="test_agent_example",
    version="1.0",
    template="""\
You are the TestAgent Agent. Your task is to {task_description}.

Input data:
{input_data}

Please generate the required output in JSON format.
""",
    variables=["task_description", "input_data"]
)

PROMPT_REGISTRY = {
    "example": {
        "1.0": EXAMPLE_PROMPT_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """
    Retrieves a prompt by name and version.
    """
    if name not in PROMPT_REGISTRY:
        raise ValueError(f"Prompt '{name}' not found in registry.")

    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]

    if version not in PROMPT_REGISTRY[name]:
        raise ValueError(f"Version '{version}' for prompt '{name}' not found.")

    return PROMPT_REGISTRY[name][version]