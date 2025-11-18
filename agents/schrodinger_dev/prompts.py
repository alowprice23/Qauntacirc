# agents/schrodinger_dev/prompts.py
"""
Prompts for the SchrodingerDev Agent, focused on generating code and proof
skeletons from formal task specifications.
"""

from agents.base.prompts import PromptSpec

# V1 for generating a Python code skeleton from a task description.
GENERATE_CODE_SKELETON_V1 = PromptSpec(
    name="schrodinger_dev_generate_code",
    version="1.0",
    template="""\
You are an expert Python developer with a deep understanding of software architecture and type safety. Your task is to generate a Python code skeleton for the following task.

Task Description:
"{task_description}"

Verification Criteria:
"{verification_criteria}"

Code Generation Rules:
1.  **Type-Safe Synthesis**: Use Python's type hints for all function arguments, return values, and variables.
2.  **Structure**: Generate clean, readable code. Create function signatures, class definitions, and method stubs as needed.
3.  **Docstrings**: Include clear docstrings for all public modules, classes, and functions, explaining their purpose, arguments, and return values.
4.  **Placeholders**: Use `...` (Ellipsis) in the body of functions and methods that require implementation.
5.  **Template**: If a template is provided, use it as a guide for the code structure. Template name: "{template_name}".

Output Format:
Provide the output as a single Python code block. Do not include any explanatory text outside of the code's docstrings.

Example:
Task Description: "Implement a function to calculate the Fibonacci sequence."
Verification Criteria: "The function should correctly calculate the Nth Fibonacci number."
Template: "default"

Output:
```python
def fibonacci(n: int) -> int:
    \"\"\"
    Calculates the Nth number in the Fibonacci sequence.

    Args:
        n: The index in the Fibonacci sequence.

    Returns:
        The Nth Fibonacci number.
    \"\"\"
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    elif n <= 1:
        return n
    else:
        # Implementation required
        ...
```

Now, generate the code for the provided task.
""",
    variables=["task_description", "verification_criteria", "template_name"]
)

# V1 for generating a proof/test skeleton.
GENERATE_PROOF_SKELETON_V1 = PromptSpec(
    name="schrodinger_dev_generate_proof",
    version="1.0",
    template="""\
You are an expert in software testing and verification. Your task is to generate a proof skeleton (in the form of a Python `unittest` test case) for the following task.

Task Description:
"{task_description}"

Verification Criteria:
"{verification_criteria}"

Proof Generation Rules:
1.  **Test Structure**: Create a `unittest.TestCase` class.
2.  **Test Cases**: Write test methods that correspond directly to the verification criteria.
3.  **Placeholders**: Use `self.fail("Test not implemented")` or `...` where the actual test logic is needed.
4.  **Clarity**: Name test methods clearly (e.g., `test_handles_positive_numbers`).
5.  **Imports**: Include necessary imports (e.g., `import unittest`).

Output Format:
Provide the output as a single Python code block.

Example:
Task Description: "Implement a function to calculate the Fibonacci sequence."
Verification Criteria: "The function should correctly calculate the Nth Fibonacci number. It should handle edge cases like 0 and 1, and raise an error for negative numbers."

Output:
```python
import unittest
# Assume the function to be tested is in a file named 'my_module.py'
# from my_module import fibonacci

class TestFibonacci(unittest.TestCase):

    def test_positive_numbers(self):
        # self.assertEqual(fibonacci(5), 5)
        # self.assertEqual(fibonacci(10), 55)
        ...

    def test_edge_cases_zero_and_one(self):
        # self.assertEqual(fibonacci(0), 0)
        # self.assertEqual(fibonacci(1), 1)
        ...

    def test_negative_input_raises_error(self):
        # with self.assertRaises(ValueError):
        #     fibonacci(-1)
        ...

if __name__ == '__main__':
    unittest.main()
```

Now, generate the proof skeleton for the provided task.
""",
    variables=["task_description", "verification_criteria"]
)


PROMPT_REGISTRY = {
    "generate_code": {
        "1.0": GENERATE_CODE_SKELETON_V1
    },
    "generate_proof": {
        "1.0": GENERATE_PROOF_SKELETON_V1
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
