# agents/uncertain_ai/prompts.py
"""
Prompts for the UncertainAI Agent, which identifies and mitigates risk
by generating targeted test cases.
"""

from agents.base.prompts import PromptSpec

# V1 for identifying potential risks in a code block.
IDENTIFY_RISKS_V1 = PromptSpec(
    name="uncertain_ai_identify_risks",
    version="1.0",
    template="""\
You are an expert software quality assurance engineer with a specialization in risk analysis and security. Your task is to analyze the following Python code and identify potential risks.

Code Block:
```python
{code_block}
```

Code Description:
"{code_description}"

Risk Analysis Guidelines:
1.  **Edge Cases**: Consider inputs at the boundaries of their valid ranges (e.g., 0, -1, max_int, empty strings, empty lists).
2.  **Error Handling**: How does the code behave when errors occur? Does it handle exceptions gracefully?
3.  **Security Vulnerabilities**: Look for common vulnerabilities like injection attacks, improper data sanitization, or insecure handling of secrets (even in this small snippet).
4.  **Assumptions**: What implicit assumptions does the code make about its inputs or environment?
5.  **Complexity**: Is any part of the logic overly complex or hard to understand? This can be a source of hidden bugs.

Output Format:
Provide the output as a JSON object with a single key "identified_risks", which is a list of strings. Each string should be a concise description of a potential risk.

Example:
Code Block: `def divide(a, b): return a / b`
Code Description: "A function to divide two numbers."
Output:
{{
  "identified_risks": [
    "Division by zero is not handled and will raise an unhandled ZeroDivisionError.",
    "The function does not validate the input types; non-numeric inputs will raise a TypeError."
  ]
}}

Now, identify the risks for the provided code block.
""",
    variables=["code_block", "code_description"]
)

# V1 for generating test cases to mitigate a specific risk.
GENERATE_TEST_CASES_FOR_RISK_V1 = PromptSpec(
    name="uncertain_ai_generate_test_cases",
    version="1.0",
    template="""\
You are an expert test engineer. Your task is to write a Python `unittest` test case to mitigate a specific, identified risk in a block of code.

Code Block Under Test:
```python
{code_block}
```

Risk to Mitigate:
"{risk_description}"

Test Case Generation Rules:
1.  **Targeted**: The test case must directly address the specified risk.
2.  **Specific Assertions**: Use specific assertions (e.g., `assertRaises`, `assertEqual`) to clearly verify the expected outcome.
3.  **Self-Contained**: The test should be self-contained and ready to run.
4.  **Clarity**: Name the test method clearly to reflect the risk it covers.

Output Format:
Provide the output as a single Python code block containing the `unittest.TestCase` class. Do not include the `if __name__ == '__main__':` block.

Example:
Code Block: `def divide(a, b): return a / b`
Risk to Mitigate: "Division by zero is not handled."

Output:
```python
import unittest
# from my_module import divide

class TestDivisionRisk(unittest.TestCase):
    def test_division_by_zero_raises_error(self):
        \"\"\"Verifies that dividing by zero raises a ZeroDivisionError.\"\"\"
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)
```

Now, generate the test case for the provided risk.
""",
    variables=["code_block", "risk_description"]
)

PROMPT_REGISTRY = {
    "identify_risks": { "1.0": IDENTIFY_RISKS_V1 },
    "generate_test_cases": { "1.0": GENERATE_TEST_CASES_FOR_RISK_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
