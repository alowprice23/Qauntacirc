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


# V1 for generating multiple diverse code variations for superposition.
GENERATE_CODE_VARIATIONS_V1 = PromptSpec(
    name="schrodinger_dev_generate_code_variations",
    version="1.0",
    template="""\
You are a creative and expert Python developer. Your task is to generate {num_variations} different and diverse implementations for the following task.

Task Description:
"{task_description}"

Verification Criteria:
"{verification_criteria}"

Code Generation Rules:
1.  **Diversity**: Provide distinct approaches. For example, use different algorithms, data structures, or library calls. One might be iterative, another recursive. One might be simple, another highly optimized.
2.  **Completeness**: Each variation should be a complete, runnable piece of code.
3.  **Clarity**: The code should be well-documented with comments and docstrings.
4.  **No Placeholders**: Do not use `...` or `pass`. Provide a full implementation for each variation.

Output Format:
Provide each implementation in its own separate Python code block. Do not include any explanatory text between the blocks.

Example:
Task Description: "Implement a function `is_prime(n)` that checks if a number is prime."
Num Variations: 2

Output:
```python
def is_prime_iterative(n: int) -> bool:
    \"\"\"Checks for primality using trial division.\"\"\"
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

```python
import re

def is_prime_regex(n: int) -> bool:
    \"\"\"Checks for primality using a regular expression. Less efficient but a creative alternative.\"\"\"
    if n <= 1:
        return False
    return not re.fullmatch(r'1?' r'|(11+?)\1+', '1' * n)
```

Now, generate {num_variations} code variations for the provided task.
""",
    variables=["task_description", "verification_criteria", "num_variations"]
)

# V1 for generating a formal proof skeleton using Z3.
GENERATE_PROOF_SKELETON_V1 = PromptSpec(
    name="schrodinger_dev_generate_proof",
    version="1.0",
    template="""\
You are an expert in formal methods and automated theorem proving. Your task is to generate a formal proof skeleton using the Z3 SMT solver's Python API (`z3-solver`) for the following task.

Task Description:
"{task_description}"

Verification Criteria:
"{verification_criteria}"

Proof Generation Rules:
1.  **Z3 Solver**: Use the `z3` library. Import necessary types like `Solver`, `Int`, `Real`, `Bool`, etc.
2.  **Function Modeling**: Model the generated Python function as a Z3 function or relation.
3.  **Translate Criteria to Assertions**: Convert each verification criterion into one or more Z3 assertions. The goal is to create a script that can formally prove the correctness of the code.
4.  **Solver Check**: Include the standard `s.check()` and `s.model()` calls to solve the constraints.
5.  **Placeholders**: Use comments (`# TODO: ...`) to indicate where the generated code's logic needs to be precisely translated into Z3 constraints.

Output Format:
Provide the output as a single, complete Python code block.

Example:
Task Description: "Implement a function `clamp(value, min_val, max_val)` that clamps a value to a given range."
Verification Criteria:
- If value is between min_val and max_val, return value.
- If value is less than min_val, return min_val.
- If value is greater than max_val, return max_val.

Output:
```python
from z3 import Int, Ints, Solver, If, And, Implies, Not

# 1. Model the function to be verified
# This should be replaced by the actual implementation's logic
def clamp(value, min_val, max_val):
    return If(value < min_val, min_val, If(value > max_val, max_val, value))

# 2. Define the specification as Z3 constraints
value, min_val, max_val = Ints('value min_val max_val')
result = Int('result')

# Define the properties of the clamp function
spec = [
    # Pre-condition: min_val is less than or equal to max_val
    min_val <= max_val,
    # The core logic of the clamp function
    result == clamp(value, min_val, max_val)
]

# 3. Define the theorems to be proven based on verification criteria
# Theorem 1: If value is in range, result is value
prop_in_range = Implies(
    And(value >= min_val, value <= max_val),
    result == value
)

# Theorem 2: If value is below range, result is min_val
prop_below_range = Implies(value < min_val, result == min_val)

# Theorem 3: If value is above range, result is max_val
prop_above_range = Implies(value > max_val, result == max_val)

# 4. Setup solver to prove the theorems
s = Solver()
s.add(spec)

# Check if the properties hold
s.push()
s.add(Not(prop_in_range))
print(f"Checking in-range property: {{s.check()}}")
s.pop()

s.push()
s.add(Not(prop_below_range))
print(f"Checking below-range property: {{s.check()}}")
s.pop()

s.push()
s.add(Not(prop_above_range))
print(f"Checking above-range property: {{s.check()}}")
s.pop()

```

Now, generate the formal proof skeleton for the provided task.
""",
    variables=["task_description", "verification_criteria"]
)


PROMPT_REGISTRY = {
    "generate_code": {
        "1.0": GENERATE_CODE_SKELETON_V1
    },
    "generate_proof": {
        "1.0": GENERATE_PROOF_SKELETON_V1
    },
    "generate_code_variations": {
        "1.0": GENERATE_CODE_VARIATIONS_V1
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
