# agents/phonon_flow/prompts.py
"""
Prompts for the PhononFlow Agent, which optimizes code structure to improve
the "speed of sound" in the codebase, enhancing maintainability.
"""

from agents.base.prompts import PromptSpec

# V1 for refactoring a file to reduce coupling and complexity.
REFACTOR_FOR_DECOUPLING_V1 = PromptSpec(
    name="phonon_flow_refactor_for_decoupling",
    version="1.0",
    template="""\
You are an expert software architect who specializes in creating clean, maintainable, and loosely-coupled code. Your task is to refactor the following Python code to improve its structure.

File to Refactor: `{file_path}`

Code Block:
```python
{code_block}
```

Refactoring Goals:
1.  **Reduce Coupling**: Minimize dependencies on other modules. Can you extract interfaces, use dependency injection, or introduce events to decouple this component?
2.  **Increase Cohesion / Reduce Complexity**: Ensure the code in this file has a single, well-defined responsibility. If it's doing too much, suggest how it could be broken down into smaller, more focused components.
3.  **No Semantic Changes**: The public API and behavior of the refactored code must remain the same.

Output Format:
Provide the output as a JSON object with the following structure:
- "refactored_code": The complete, refactored Python code for the file.
- "explanation": A brief explanation of the changes you made and how they improve the code's structure (specifically addressing coupling and complexity).

Example:
File: `src/processing.py`
Code: `import db; import api; def process_data(): data = db.fetch(); api.send(data)`

Output:
{{
  "refactored_code": "class DataProcessor:\\n  def __init__(self, fetcher, sender):\\n    self.fetcher = fetcher\\n    self.sender = sender\\n\\n  def process(self):\\n    data = self.fetcher.fetch()\\n    self.sender.send(data)",
  "explanation": "I used dependency injection to decouple the DataProcessor from the concrete `db` and `api` modules. It now depends on abstractions (a fetcher and a sender), making it more reusable and easier to test."
}}

Now, refactor the provided code block.
""",
    variables=["file_path", "code_block"]
)

PROMPT_REGISTRY = {
    "refactor_for_decoupling": { "1.0": REFACTOR_FOR_DECOUPLING_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
