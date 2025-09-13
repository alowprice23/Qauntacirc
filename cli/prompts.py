from agents.base.prompts import PromptSpec

GENERATE_SUGGESTION_V1 = PromptSpec(
    name="cli_generate_suggestion",
    version="1.0",
    template="""\
You are an intelligent command line assistant. Your task is to complete a partial command based on a successful historical pattern.

Partial Command:
"{partial_input}"

Successful Historical Pattern:
"{pattern_content}"

Based on the historical pattern, provide a likely completion for the partial command.

Output Format:
Provide the output as a JSON object with a single key "suggestion".

Example:
Partial Command: "Build a user auth"
Successful Historical Pattern: "Built a user authentication system with JWT and rate limiting."
Output:
{{
  "suggestion": "Build a user authentication system with JWT and rate limiting"
}}

Now, generate a suggestion for the provided partial command.
""",
    variables=["partial_input", "pattern_content"]
)

PROMPT_REGISTRY = {
    "generate_suggestion": {
        "1.0": GENERATE_SUGGESTION_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """
    Retrieves a prompt by name and version.
    """
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
