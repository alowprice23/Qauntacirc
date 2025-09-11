"""
Prompts for the TunnelFix Agent.
"""
from agents.base.prompts import PromptSpec

GENERATE_OPTIMIZATION_V1 = PromptSpec(
    name="tunnelfix_generate_optimization",
    version="1.0",
    template="""\
You are an expert performance engineer. Your task is to analyze the following Python code and suggest a simple, rule-based optimization.

Code Block:
```python
{code_block}
```

Optimization Guidelines:
1.  **Simple Refactoring**: Suggest a simple refactoring that is likely to improve performance (e.g., replace a loop with a list comprehension, use a more efficient data structure, etc.).
2.  **No Semantic Changes**: The optimization must not change the semantics of the code.
3.  **Provide the Refactored Code**: Provide the full, refactored code block.

Output Format:
Provide the output as a JSON object with a single key "refactored_code".

Example:
Code Block: `squares = []\nfor i in range(10):\n    squares.append(i*i)`
Output:
{{
  "refactored_code": "squares = [i*i for i in range(10)]"
}}

Now, suggest an optimization for the provided code block.
""",
    variables=["code_block"]
)

PROMPT_REGISTRY = {
    "generate_optimization": {
        "1.0": GENERATE_OPTIMIZATION_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
