import pytest
from agents.planck_forge.prompts import get_prompt, DECOMPOSE_REQUIREMENT_V1

def test_get_prompt_latest():
    prompt = get_prompt("decompose_requirement", "latest")
    assert prompt is not None
    assert prompt.version == "1.0"
    assert prompt.name == "planck_forge_decompose_requirement"

def test_get_prompt_specific_version():
    prompt = get_prompt("decompose_requirement", "1.0")
    assert prompt is not None
    assert prompt.version == "1.0"

def test_get_prompt_nonexistent_name():
    with pytest.raises(KeyError):
        get_prompt("nonexistent_prompt")

def test_get_prompt_nonexistent_version():
    with pytest.raises(KeyError):
        get_prompt("decompose_requirement", "0.1")

def test_decompose_requirement_v1_format():
    requirement = "Create a new user"
    formatted_prompt = DECOMPOSE_REQUIREMENT_V1.format(requirement_text=requirement)
    assert requirement in formatted_prompt
    assert "{requirement_text}" not in formatted_prompt
