import pytest
import yaml
import hashlib
from agents.base.prompts import PromptSpec, PromptRegistry

def test_prompt_spec_checksum():
    spec = PromptSpec(name="test", template="Hello, {name}!", version="1.0")
    expected_checksum = hashlib.sha256(b"1.0:Hello, {name}!").hexdigest()
    assert spec.checksum == expected_checksum
    assert spec.validate() is True

def test_prompt_spec_format():
    spec = PromptSpec(
        name="test",
        template="Hello, {name}!",
        version="1.0",
        variables=["name"]
    )
    formatted = spec.format(name="World")
    assert formatted == "Hello, World!"

def test_prompt_spec_format_missing_variable():
    spec = PromptSpec(
        name="test",
        template="Hello, {name}!",
        version="1.0",
        variables=["name"]
    )
    with pytest.raises(ValueError):
        spec.format()

@pytest.fixture
def prompt_yaml_file(tmp_path):
    content = """
- name: greeting
  version: "1.0"
  template: "Hello, {name}!"
  variables: ["name"]
- name: greeting
  version: "1.2"
  template: "Hi, {name}!"
  variables: ["name"]
- name: farewell
  version: "1.0"
  template: "Goodbye, {name}."
  variables: ["name"]
"""
    file_path = tmp_path / "prompts.yaml"
    file_path.write_text(content)
    return file_path

def test_prompt_registry_load_from_yaml(prompt_yaml_file):
    registry = PromptRegistry()
    registry.load_from_yaml(prompt_yaml_file)

    spec = registry.get("greeting", "1.0")
    assert spec is not None
    assert spec.template == "Hello, {name}!"

    spec2 = registry.get("farewell")
    assert spec2 is not None
    assert spec2.version == "1.0"

def test_prompt_registry_get_latest():
    registry = PromptRegistry()
    spec1 = PromptSpec(name="test", template="v1", version="1.0")
    spec2 = PromptSpec(name="test", template="v2", version="2.0")
    spec3 = PromptSpec(name="test", template="v1.5", version="1.5")

    registry.register(spec1)
    registry.register(spec2)
    registry.register(spec3)

    latest_spec = registry.get("test", "latest")
    assert latest_spec.version == "2.0"

def test_prompt_registry_get_specific_version():
    registry = PromptRegistry()
    spec1 = PromptSpec(name="test", template="v1", version="1.0")
    spec2 = PromptSpec(name="test", template="v2", version="2.0")

    registry.register(spec1)
    registry.register(spec2)

    spec = registry.get("test", "1.0")
    assert spec.version == "1.0"

def test_prompt_registry_get_nonexistent():
    registry = PromptRegistry()
    assert registry.get("nonexistent") is None
