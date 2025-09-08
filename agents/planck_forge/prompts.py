# agents/planck_forge/prompts.py
"""
Prompts for the PlanckForge Agent, designed to translate natural language
requirements into formal, verifiable task specifications.
"""

from agents.base.prompts import PromptSpec

# V1 of the requirement decomposition prompt
# This prompt guides the LLM to break down a high-level requirement
# into a series of smaller, more manageable tasks.
DECOMPOSE_REQUIREMENT_V1 = PromptSpec(
    name="planck_forge_decompose_requirement",
    version="1.0",
    template="""\
You are an expert systems engineer. Your task is to decompose a high-level natural language requirement into a structured set of formal tasks.

Requirement:
"{requirement_text}"

Decomposition Rules:
1.  **Atomicity**: Each task should be atomic and represent a single, verifiable unit of work.
2.  **Clarity**: Task descriptions must be clear, unambiguous, and written in a formal style.
3.  **Dependencies**: Identify any dependencies between tasks. If Task B depends on Task A, Task A must be completed before Task B can start.
4.  **Verifiability**: Each task must have a clear verification criterion. How will we know this task is done correctly?

Output Format:
Provide the output as a JSON object containing a list of tasks. Each task should have the following fields:
- "task_id": A unique identifier for the task (e.g., "T01", "T02").
- "description": A concise, formal description of the task.
- "dependencies": A list of task_ids that this task depends on.
- "verification_criteria": A clear statement of what constitutes successful completion.

Example:
Requirement: "Build a user authentication system."
Output:
{{
  "tasks": [
    {{
      "task_id": "T01",
      "description": "Design the database schema for user credentials.",
      "dependencies": [],
      "verification_criteria": "The database schema is approved and documented."
    }},
    {{
      "task_id": "T02",
      "description": "Implement the user registration endpoint.",
      "dependencies": ["T01"],
      "verification_criteria": "The endpoint successfully creates new users in the database."
    }}
  ]
}}

Now, decompose the provided requirement.
""",
    variables=["requirement_text"]
)

# A central registry of all prompts for this agent
# This makes it easy to manage and access different versions
PROMPT_REGISTRY = {
    "decompose_requirement": {
        "1.0": DECOMPOSE_REQUIREMENT_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """
    Retrieves a prompt by name and version.

    Args:
        name (str): The name of the prompt.
        version (str): The desired version.

    Returns:
        The requested PromptSpec.

    Raises:
        KeyError: If the prompt name or version is not found.
    """
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]

    return PROMPT_REGISTRY[name][version]
