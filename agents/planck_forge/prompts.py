# agents/planck_forge/prompts.py
"""
Prompts for the PlanckForge Agent, designed to translate natural language
requirements into formal, verifiable task specifications.
"""

from agents.base.prompts import PromptSpec

# V1 of the high-level goal decomposition prompt
DECOMPOSE_GOALS_V1 = PromptSpec(
    name="planck_forge_decompose_goals",
    version="1.0",
    template="""\
You are an expert systems engineer. Your task is to decompose a complex, multi-step command into a short list of high-level goals.

Complex Command:
"{complex_command}"

Decomposition Rules:
1.  **Identify Major Stages**: Break down the command into the primary stages of a software project (e.g., "Build Microservices", "Generate Tests", "Optimize for Production").
2.  **Sequential Order**: List the goals in a logical, sequential order.
3.  **Clarity**: Each goal should be a clear, high-level objective.

Output Format:
Provide the output as a JSON object with a single key "goals", which is a list of strings.

Example:
Complex Command: "Build microservices with auth, rate limiting, monitoring, deployment automation, then generate comprehensive tests and optimize for 10k RPS"
Output:
{{
  "goals": [
    "Build microservices with authentication, rate limiting, monitoring, and deployment automation.",
    "Generate comprehensive tests for the microservices.",
    "Optimize the microservices for 10,000 requests per second."
  ]
}}

Now, decompose the provided complex command into high-level goals.
""",
    variables=["complex_command"]
)


# V1 of the goal-to-tasks decomposition prompt
DECOMPOSE_GOAL_TO_TASKS_V1 = PromptSpec(
    name="planck_forge_decompose_goal_to_tasks",
    version="1.0",
    template="""\
You are an expert systems engineer. Your task is to decompose a high-level goal into a structured set of formal tasks.

High-Level Goal:
"{goal_text}"

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
High-Level Goal: "Build a user authentication system."
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

Now, decompose the provided high-level goal.
""",
    variables=["goal_text"]
)

# A central registry of all prompts for this agent
# This makes it easy to manage and access different versions
PROMPT_REGISTRY = {
    "decompose_goals": {
        "1.0": DECOMPOSE_GOALS_V1
    },
    "decompose_goal_to_tasks": {
        "1.0": DECOMPOSE_GOAL_TO_TASKS_V1
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
