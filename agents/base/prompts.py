# agents/base/prompts.py
"""
Prompt management system with versioning, checksums, and YAML loading
for LLM-based agents.
"""

import yaml
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class PromptSpec:
    """
    A specification for a single prompt, including its template, version,
    and metadata for validation.
    """
    name: str
    template: str
    version: str
    checksum: str = field(init=False)
    variables: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculates the checksum after the object is initialized."""
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculates a SHA256 checksum of the prompt template and version."""
        data = f"{self.version}:{self.template}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def validate(self) -> bool:
        """Validates the integrity of the prompt spec."""
        return self.checksum == self._calculate_checksum()

    def format(self, **kwargs) -> str:
        """Formats the prompt template with the given variables."""
        for var in self.variables:
            if var not in kwargs:
                raise ValueError(f"Missing variable '{var}' for prompt '{self.name}'")
        return self.template.format(**kwargs)


class PromptRegistry:
    """
    A registry for managing and versioning prompts for all agents.
    """
    def __init__(self):
        self._prompts: Dict[str, Dict[str, PromptSpec]] = {}  # name -> version -> spec

    def load_from_yaml(self, file_path: str):
        """
        Loads and registers prompt specifications from a YAML file.

        The YAML file should be a list of prompt dictionaries, each with
        'name', 'version', 'template', and optional 'variables'.
        """
        with open(file_path, 'r') as f:
            prompt_configs = yaml.safe_load(f)

        for config in prompt_configs:
            spec = PromptSpec(
                name=config['name'],
                template=config['template'],
                version=config['version'],
                variables=config.get('variables', [])
            )
            if not spec.validate():
                raise ValueError(f"Checksum validation failed for prompt {spec.name} v{spec.version}")

            self.register(spec)

    def register(self, spec: PromptSpec):
        """Registers a single PromptSpec."""
        if spec.name not in self._prompts:
            self._prompts[spec.name] = {}

        if spec.version in self._prompts[spec.name]:
            # This could be an error, a warning, or allow overwriting, depending on policy
            print(f"Warning: Overwriting prompt {spec.name} version {spec.version}")

        self._prompts[spec.name][spec.version] = spec

    def get(self, name: str, version: str = "latest") -> Optional[PromptSpec]:
        """
        Retrieves a prompt by name and version.

        Args:
            name: The name of the prompt.
            version: The desired version. If "latest", it returns the highest semantic version.

        Returns:
            The requested PromptSpec, or None if not found.
        """
        if name not in self._prompts:
            return None

        versions = self._prompts[name]
        if not versions:
            return None

        if version == "latest":
            # Simple "latest" implementation: assumes sortable versions like "1.2.3"
            try:
                latest_version = sorted(versions.keys(), reverse=True)[0]
                return versions[latest_version]
            except (ValueError, IndexError):
                # Fallback for non-standard versioning
                return next(iter(versions.values()))

        return versions.get(version)
