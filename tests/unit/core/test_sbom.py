import os
import json
import pytest
from core.sbom_generator import SBOMGenerator

@pytest.fixture
def project_root(tmpdir):
    # Create a dummy requirements.txt
    req_file = tmpdir.join("requirements.txt")
    req_file.write("pydantic==2.5.2\nnumpy>=1.20.0\n")

    # Create a dummy pyproject.toml
    pyproject_file = tmpdir.join("pyproject.toml")
    pyproject_file.write("""
[project]
name = "my-test-project"
dependencies = [
    "flask",
    "gunicorn"
]
""")

    # Create a dummy package-lock.json
    lock_file = tmpdir.join("package-lock.json")
    lock_file.write(json.dumps({
        "name": "my-node-project",
        "version": "1.0.0",
        "lockfileVersion": 2,
        "requires": True,
        "packages": {
            "": {
                "name": "my-node-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "4.17.1"
                }
            },
            "node_modules/express": {
                "version": "4.17.1",
                "resolved": "https://registry.npmjs.org/express/-/express-4.17.1.tgz",
                "integrity": "sha512-..."
            }
        },
        "dependencies": {
            "express": {
                "version": "4.17.1"
            }
        }
    }))
    return str(tmpdir)

def test_sbom_generator_parses_requirements_txt(project_root):
    generator = SBOMGenerator()
    sbom = generator.generate_sbom(project_root)

    packages = sbom["packages"]
    package_names = {p["name"] for p in packages}

    assert "pydantic" in package_names
    assert "numpy" in package_names

def test_sbom_generator_parses_pyproject_toml(project_root):
    generator = SBOMGenerator()
    sbom = generator.generate_sbom(project_root)

    packages = sbom["packages"]
    package_names = {p["name"] for p in packages}

    assert "flask" in package_names
    assert "gunicorn" in package_names

def test_sbom_generator_finds_correct_versions_from_requirements(project_root):
    generator = SBOMGenerator()
    sbom = generator.generate_sbom(project_root)

    packages = sbom["packages"]
    pydantic_pkg = next((p for p in packages if p["name"] == "pydantic"), None)

    assert pydantic_pkg is not None
    assert pydantic_pkg["version"] == "2.5.2"

def test_sbom_generator_parses_nodejs_dependencies(project_root):
    generator = SBOMGenerator()
    sbom = generator.generate_sbom(project_root)

    packages = sbom["packages"]
    package_names = {p["name"] for p in packages}

    assert "express" in package_names
    express_pkg = next((p for p in packages if p["name"] == "express"), None)
    assert express_pkg is not None
    assert express_pkg["version"] == "4.17.1"

def test_sbom_generator_creates_relationships(project_root):
    generator = SBOMGenerator()
    sbom = generator.generate_sbom(project_root)

    relationships = sbom["relationships"]
    assert len(relationships) > 0

    project_name = os.path.basename(project_root)
    project_spdx_id = f"SPDXRef-{project_name}"

    # Check that all relationships are from the main project component
    for rel in relationships:
        assert rel["spdxElementId"] == project_spdx_id
        assert rel["relationshipType"] == "DEPENDS_ON"
        assert "relatedSpdxElement" in rel

def test_sbom_generator_handles_empty_files(tmpdir):
    project_root = str(tmpdir)
    # Create empty files
    tmpdir.join("requirements.txt").write("")
    tmpdir.join("pyproject.toml").write("")
    tmpdir.join("package-lock.json").write("invalid json")

    generator = SBOMGenerator()
    sbom = generator.generate_sbom(project_root)

    # We expect the project component itself, and any installed packages from pkg_resources
    project_package_found = False
    for pkg in sbom["packages"]:
        if pkg["name"] == os.path.basename(project_root):
            project_package_found = True
            break
    assert project_package_found

    # No relationships should be generated if there are no dependencies
    if len(sbom["packages"]) <= 1:
        assert sbom["relationships"] == []
