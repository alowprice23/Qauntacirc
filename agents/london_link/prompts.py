# agents/london_link/prompts.py
"""
Prompts for the LondonLink Agent, which manages and optimizes the
system's external dependencies.
"""

from agents.base.prompts import PromptSpec

# V1 for optimizing a set of dependencies.
OPTIMIZE_DEPENDENCIES_V1 = PromptSpec(
    name="london_link_optimize_dependencies",
    version="1.0",
    template="""\
You are a security researcher and expert in software supply chain management. Your task is to analyze a list of project dependencies and recommend optimizations to improve security, stability, and performance.

Project Dependencies:
```
{dependency_list}
```

Known Vulnerabilities:
```
{vulnerability_report}
```

Optimization Guidelines:
1.  **Update Vulnerable Packages**: For any package with a known vulnerability, suggest updating to the minimum safe version.
2.  **Update Outdated Packages**: Suggest updating packages that are significantly behind the latest stable version, as long as the update is not a major breaking change.
3.  **Remove Unused Dependencies**: If a dependency is identified as unused (this information would be provided in a real analysis), recommend its removal.
4.  **Consolidate Redundancy**: If multiple packages serve the same purpose (e.g., two different HTTP clients), suggest consolidating to one.

Output Format:
Provide the output as a JSON object with a single key "optimization_actions". This should be a list of objects, where each object has:
- "package": The name of the dependency.
- "current_version": The current version.
- "recommended_version": The suggested new version (or "remove" if it should be removed).
- "reason": A brief justification for the change.

Example:
... (Example is omitted for brevity, the structure is defined above)

Now, generate the dependency optimization plan.
""",
    variables=["dependency_list", "vulnerability_report"]
)

PROMPT_REGISTRY = {
    "optimize_dependencies": { "1.0": OPTIMIZE_DEPENDENCIES_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
