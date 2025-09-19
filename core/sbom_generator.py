import os
import hashlib
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None

@dataclass
class SBOMComponent:
    """Represents a component in the Software Bill of Materials"""
    name: str
    version: str
    supplier: Optional[str] = None
    download_location: Optional[str] = None
    files_analyzed: List[str] = field(default_factory=list)
    licenses: List[str] = field(default_factory=list)
    copyright_text: Optional[str] = None
    package_verification_code: str = "NOASSERTION"
    checksums: Dict[str, str] = field(default_factory=dict)
    cpe: Optional[str] = None
    purl: Optional[str] = None
    external_refs: List[Dict[str, str]] = field(default_factory=list)
    spdx_id: Optional[str] = None # Used for relationships

def to_spdx_package(component: SBOMComponent) -> Dict[str, Any]:
    """Converts an SBOMComponent to an SPDX package dictionary."""
    pkg = asdict(component)
    # The 'spdx_id' is not part of the SPDX package schema, it's for relationships.
    # The identifier for a package in SPDX is SPDXID.
    pkg["SPDXID"] = pkg.pop("spdx_id", f"SPDXRef-{component.name}-{component.version}")
    return pkg

class SBOMGenerator:
    """Generates SPDX-compliant Software Bill of Materials"""

    def __init__(self):
        self.document_namespace = "https://quantacirc.dev/spdx/"
        self.creators = ["Tool: QuantaCirc-SBOM-Generator"]

    def generate_sbom(self, project_root: str, output_format: str = "json") -> Dict:
        """Generate comprehensive SBOM for project"""
        project_name = os.path.basename(os.path.abspath(project_root))
        project_component = SBOMComponent(name=project_name, version="1.0.0", supplier="Local")

        components = []
        components.extend(self._scan_python_dependencies(project_root))
        components.extend(self._scan_nodejs_dependencies(project_root))

        all_components = [project_component] + components
        relationships = self._generate_relationships(project_component, components)

        sbom_document = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": project_component.name,
            "documentNamespace": f"{self.document_namespace}{project_component.name}-{project_component.version}-{hashlib.sha256(project_root.encode()).hexdigest()[:8]}",
            "creationInfo": {
                "created": datetime.utcnow().isoformat() + "Z",
                "creators": self.creators,
                "licenseListVersion": "3.19"
            },
            "packages": [to_spdx_package(comp) for comp in all_components],
            "relationships": relationships
        }
        return sbom_document

    def _scan_python_dependencies(self, project_root: str) -> List[SBOMComponent]:
        """Scan Python dependencies from various sources"""
        components: Dict[str, SBOMComponent] = {}

        # Scan requirements.txt
        requirements_file = os.path.join(project_root, "requirements.txt")
        if os.path.exists(requirements_file):
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        component = self._parse_requirement_line(line)
                        if component:
                            components[component.name] = component

        # Scan pyproject.toml
        pyproject_file = os.path.join(project_root, "pyproject.toml")
        if os.path.exists(pyproject_file) and tomllib:
            for component in self._scan_pyproject_toml(pyproject_file):
                components[component.name] = component

        # Scan installed packages via pip
        try:
            import pkg_resources
            for pkg in pkg_resources.working_set:
                if pkg.project_name not in components:
                    components[pkg.project_name] = SBOMComponent(
                        name=pkg.project_name,
                        version=pkg.version,
                        supplier="PyPI",
                        purl=f"pkg:pypi/{pkg.project_name}@{pkg.version}"
                    )
        except ImportError:
            logging.warning("`pkg_resources` not found. Installed packages scan will be skipped.")
            pass

        return list(components.values())

    def _scan_nodejs_dependencies(self, project_root: str) -> List[SBOMComponent]:
        """Scan Node.js dependencies from package-lock.json"""
        components: List[SBOMComponent] = []
        lock_file = os.path.join(project_root, "package-lock.json")
        if os.path.exists(lock_file):
            with open(lock_file, 'r') as f:
                try:
                    data = json.load(f)
                    # For package-lock.json v1, dependencies are in "dependencies"
                    # For v2+, they are in "packages"
                    packages = data.get("packages", data.get("dependencies", {}))
                    for name, details in packages.items():
                        if not name: continue # Skip root package
                        package_name = name.split("node_modules/")[-1]
                        components.append(SBOMComponent(
                            name=package_name,
                            version=details.get("version"),
                            supplier="npm",
                            purl=f"pkg:npm/{package_name}@{details.get('version')}"
                        ))
                except json.JSONDecodeError:
                    pass
        return components

    def _parse_requirement_line(self, line: str) -> Optional[SBOMComponent]:
        """Parses a line from requirements.txt to create an SBOMComponent."""
        try:
            name, version = "", "UNKNOWN"
            if "==" in line:
                name, version = line.split("==")[:2]
            elif ">=" in line: name = line.split(">=")[0]
            elif "<=" in line: name = line.split("<=")[0]
            elif "!=" in line: name = line.split("!=")[0]
            elif "~=" in line: name = line.split("~=")[0]
            else: name = line
            return SBOMComponent(name=name.strip(), version=version.strip(), supplier="PyPI", purl=f"pkg:pypi/{name.strip()}")
        except ValueError:
            return SBOMComponent(name=line, version="UNKNOWN", supplier="PyPI", purl=f"pkg:pypi/{line}")

    def _scan_pyproject_toml(self, pyproject_path: str) -> List[SBOMComponent]:
        """Scans dependencies from pyproject.toml."""
        components: List[SBOMComponent] = []
        try:
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)

            dependencies = data.get("project", {}).get("dependencies", [])
            for dep in dependencies:
                name = dep.split(">=")[0].split("==")[0].split("<=")[0].split("!=")[0].split("~=")[0].strip()
                components.append(SBOMComponent(name=name, version="ANY", supplier="PyPI", purl=f"pkg:pypi/{name}"))
        except Exception:
            pass
        return components

    def _generate_relationships(self, main_component: SBOMComponent, dependencies: List[SBOMComponent]) -> list:
        """Generates relationships between the main component and its dependencies."""
        relationships = []
        main_component.spdx_id = f"SPDXRef-{main_component.name}"

        for dep in dependencies:
            dep.spdx_id = f"SPDXRef-{dep.name}-{dep.version}"
            relationships.append({
                "spdxElementId": main_component.spdx_id,
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": dep.spdx_id
            })
        return relationships
