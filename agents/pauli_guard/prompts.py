# agents/pauli_guard/prompts.py
"""
Prompts for the PauliGuard Agent, which focuses on detecting and
eliminating code duplication to improve system orthogonality.
"""

from agents.base.prompts import PromptSpec

# V1 for generating a refactoring plan for duplicated code.
GENERATE_REFACTORING_PLAN_V1 = PromptSpec(
    name="pauli_guard_generate_refactoring_plan",
    version="1.0",
    template="""\
You are an expert software architect specializing in code quality and refactoring. Your task is to analyze two blocks of duplicated code and create a plan to refactor them into a single, reusable component.

Duplicated Code Block 1 (from `{file_path_1}`):
```python
{code_block_1}
```

Duplicated Code Block 2 (from `{file_path_2}`):
```python
{code_block_2}
```

Refactoring Rules:
1.  **Abstraction**: Identify the common logic and abstract it into a new, reusable function or class. The new component should be placed in a suitable shared module (e.g., `src/shared/utils.py`).
2.  **Parameterization**: The new function/class should be parameterized to handle any minor differences between the two original blocks.
3.  **Clarity**: The refactored code should be clear, well-documented, and easy to understand.
4.  **Replacement Plan**: Provide clear instructions on how to replace the original code blocks with calls to the new, shared component.

Output Format:
Provide the output as a JSON object with the following structure:
- "shared_component_path": The suggested file path for the new, reusable component.
- "refactored_code": The full Python code for the new, shared function or class.
- "replacement_plan": A list of objects, where each object contains:
  - "file_to_modify": The path of the file to be changed.
  - "original_code": The exact code block to be replaced.
  - "new_code": The new code (a call to the shared component) that should replace the original block.

Example:
... (A full JSON example would be too verbose for a prompt, but the structure is defined above)

Now, generate the refactoring plan for the provided code blocks.
""",
    variables=["file_path_1", "code_block_1", "file_path_2", "code_block_2"]
)

# V2 for generating a refactoring plan for a cluster of similar code blocks.
GENERATE_REFACTORING_PLAN_V2 = PromptSpec(
    name="pauli_guard_generate_refactoring_plan",
    version="2.0",
    template="""\
You are an expert software architect specializing in code quality and refactoring. Your task is to analyze a cluster of similar code blocks and create a plan to refactor them into a single, reusable component.

Here is the cluster of similar code blocks:
{code_blocks_section}

Refactoring Rules:
1.  **Abstraction**: Analyze all provided blocks to identify the common, shared logic. Abstract this logic into a new, reusable function or class. The new component should be placed in a suitable shared module (e.g., `src/shared/utils.py`).
2.  **Parameterization**: The new function/class must be parameterized to handle any differences between the original blocks.
3.  **Clarity**: The refactored code must be clear, well-documented, and easy to understand.
4.  **Replacement Plan**: Provide a clear plan to replace each of the original code blocks with a call to the new, shared component.

Output Format:
Provide the output as a single JSON object with the following structure:
- "shared_component_path": The suggested file path for the new, reusable component.
- "refactored_code": The full Python code for the new, shared function or class.
- "replacement_plan": A list of objects, where each object contains:
  - "file_to_modify": The path of the file to be changed.
  - "original_code": The exact code block to be replaced from that file.
  - "new_code": The new code (e.g., a call to the shared component) that should replace the original block.

Now, generate the refactoring plan for the provided cluster of code blocks.
""",
    variables=["code_blocks_section"]
)


PROMPT_REGISTRY = {
    "generate_refactoring_plan": {
        "1.0": GENERATE_REFACTORING_PLAN_V1,
        "2.0": GENERATE_REFACTORING_PLAN_V2,
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
