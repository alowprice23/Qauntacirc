# agents/tunnel_fix/prompts.py
"""
Prompts for the TunnelFix Agent, which automatically generates patches
for bugs and vulnerabilities.
"""

from agents.base.prompts import PromptSpec

# V1 for generating a patch to fix a bug.
GENERATE_PATCH_V1 = PromptSpec(
    name="tunnel_fix_generate_patch",
    version="1.0",
    template="""\
You are an expert diagnostician and Python programmer. Your task is to analyze a failing test case and the associated source code, then generate a patch to fix the underlying bug.

Source Code (`{file_path}`):
```python
{source_code}
```

Failing Test Case (`{test_file_path}`):
```python
{test_code}
```

Test Error Output:
```
{test_error}
```

Analysis and Patch Generation Rules:
1.  **Root Cause Analysis**: First, determine the root cause of the error based on the source code, test, and error message.
2.  **Minimal Change**: Generate the smallest possible change to fix the bug. Avoid unrelated refactoring.
3.  **Patch Format**: Provide the fix as a patch in the standard unified diff format. The patch should be applicable to the source file (`{file_path}`).

Output Format:
Provide the output as a single code block containing the unified diff.

Example:
Source Code (`src/math.py`):
```python
def divide(a, b):
    return a / b
```
Failing Test (`tests/test_math.py`):
```python
def test_divide_by_zero(self):
    divide(10, 0)
```
Test Error: `ZeroDivisionError: division by zero`

Output:
```diff
--- a/src/math.py
+++ b/src/math.py
@@ -1,2 +1,4 @@
 def divide(a, b):
+    if b == 0:
+        return float('inf') # Or raise an error, depending on desired behavior
     return a / b
```

Now, generate the patch for the provided bug.
""",
    variables=["file_path", "source_code", "test_file_path", "test_code", "test_error"]
)

PROMPT_REGISTRY = {
    "generate_patch": { "1.0": GENERATE_PATCH_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
