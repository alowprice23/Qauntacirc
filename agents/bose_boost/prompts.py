# agents/bose_boost/prompts.py
"""
Prompts for the BoseBoost Agent, which optimizes code performance by
refactoring identified bottlenecks.
"""

from agents.base.prompts import PromptSpec

# V1 for generating an optimized version of a code block.
OPTIMIZE_CODE_V1 = PromptSpec(
    name="bose_boost_optimize_code",
    version="1.0",
    template="""\
You are a world-class expert in high-performance computing and Python optimization. Your task is to refactor the given code block to improve its performance, based on the provided profiling data.

Original Code Block (`{file_path}`):
```python
{code_block}
```

Profiling Data / Bottleneck Description:
"{profiling_summary}"

Optimization Rules:
1.  **Algorithmic Improvement**: Prioritize improvements to the underlying algorithm (e.g., changing from O(n^2) to O(n log n)).
2.  **Efficient Data Structures**: Use more efficient data structures where appropriate (e.g., sets for fast lookups, deques for fast appends/pops).
3.  **Resource Awareness**: Consider both CPU and memory performance. The new code should not use excessively more memory unless it provides a significant speedup.
4.  **Preserve Functionality**: The optimized code must produce the exact same output as the original code for all valid inputs.
5.  **Clarity**: The refactored code should remain clear and readable. Add comments to explain complex optimizations.

Output Format:
Provide the output as a JSON object with the following structure:
- "file_to_modify": The path of the file that should be changed.
- "original_code": The exact code block to be replaced.
- "optimized_code": The new, high-performance version of the code.
- "explanation": A brief explanation of the optimization strategy you used.

Example:
... (A full JSON example would be too verbose, but the structure is defined above)

Now, generate the optimized code and refactoring plan.
""",
    variables=["file_path", "code_block", "profiling_summary"]
)

PROMPT_REGISTRY = {
    "optimize_code": { "1.0": OPTIMIZE_CODE_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
