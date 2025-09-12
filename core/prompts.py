"""
This file contains structured prompts for interacting with the LLM.
Using a centralized prompt store ensures consistency and easy management.
"""

# Prompt for extracting a structured intent from user input.
# The LLM is expected to return a JSON object that can be parsed into TaskQuanta.
# Note: Literal curly braces are escaped by doubling them ({{ and }}).
INTENT_PARSING_PROMPT = """
You are a master software architect. A user has provided the following request.
Your task is to analyze the request and break it down into a structured list of
"Task Quanta". Each quantum should be a self-contained, verifiable task.
For each task, provide an ID, a clear description, a list of dependencies (by ID),
and a list of verification criteria.

User Request: "{user_input}"

Return the result as a JSON object with a single key "quanta", which is a list
of task quantum objects. For example:
{{
  "quanta": [
    {{
      "id": "TASK-001",
      "description": "Set up the basic project structure with a README file.",
      "dependencies": [],
      "verification_criteria": ["Project directory exists.", "README.md is present."]
    }},
    {{
      "id": "TASK-002",
      "description": "Implement the user authentication endpoint.",
      "dependencies": ["TASK-001"],
      "verification_criteria": ["Users can register.", "Users can log in.", "JWT tokens are issued."]
    }}
  ]
}}
"""

# Prompt for generating a plan from a list of task quanta.
# The LLM is expected to return a JSON object that can be parsed into AgentTasks.
# Note: Literal curly braces are escaped by doubling them ({{ and }}).
PLANNING_PROMPT = """
You are a project manager AI. Given a list of task quanta, you must create a
plan of execution. The plan should be a sequence of "Agent Tasks".
Each agent task specifies which agent should handle it and includes the
necessary payload (e.g., the task quanta).

The available agents are: {agent_names}

Task Quanta:
{task_quanta_json}

Return the result as a JSON object with a single key "plan", which is a list
of agent task objects. For example:
{{
  "plan": [
    {{
      "agent_name": "PlanckForge",
      "task_type": "setup_project",
      "payload": {{ "id": "API-001", "description": "...", "dependencies": [], "verification_criteria": [] }}
    }},
    {{
      "agent_name": "SchrodingerDev",
      "task_type": "implement_feature",
      "payload": {{ "id": "API-003", "description": "...", "dependencies": [], "verification_criteria": [] }}
    }}
  ]
}}
"""

# Other prompts can be added here as the system evolves.
CONSTRAINT_EXTRACTION_PROMPT = ""
CLARIFICATION_PROMPT = ""
VERIFICATION_PROMPT = ""
