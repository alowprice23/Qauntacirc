"""
Prompts for the LondonLink Agent, which optimizes internal module dependencies
based on the principles of London dispersion forces.
"""

from agents.base.prompts import PromptSpec

REFACTOR_COUPLED_MODULES_V1 = PromptSpec(
    name="london_link_refactor_coupled_modules",
    version="1.0",
    template="""\
You are a senior software architect focused on creating modular and maintainable systems. Your task is to resolve a problematic coupling between two modules.

Analysis:
- Module A: `{module_a}`
- Module B: `{module_b}`
- These two modules have been identified as having a strong "attraction" (high coupling potential) but are far apart in the codebase's dependency graph. This suggests they might contain related logic that should be centralized or that their interface is too chatty.

Refactoring Task:
Propose a refactoring to address this issue. You can either:
1.  **Centralize Logic**: Extract the shared or related logic into a new, shared module that both modules can depend on.
2.  **Decouple**: Introduce a proper interface (e.g., using an abstract base class or a message bus) to reduce the direct, "improper" coupling between them.

Provide the refactored code for ONE of the modules, and explain your reasoning.

Output Format:
Provide the output as a JSON object with the following structure:
- "refactored_module_path": The full path of the module you chose to refactor (e.g., "src/module/a.py").
- "refactored_code": The complete, refactored Python code for that module.
- "explanation": A brief explanation of your change and how it resolves the long-distance coupling.

Now, generate the refactoring plan for the modules described above.
""",
    variables=["module_a", "module_b"]
)

PROMPT_REGISTRY = {
    "refactor_coupled_modules": { "1.0": REFACTOR_COUPLED_MODULES_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
