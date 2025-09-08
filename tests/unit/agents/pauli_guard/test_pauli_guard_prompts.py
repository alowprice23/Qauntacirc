import pytest
from agents.pauli_guard.prompts import get_prompt, GENERATE_REFACTORING_PLAN_V1

def test_get_prompt_latest():
    prompt = get_prompt("generate_refactoring_plan", "latest")
    assert prompt is not None
    assert prompt.version == "1.0"
    assert prompt.name == "pauli_guard_generate_refactoring_plan"

def test_get_prompt_specific_version():
    prompt = get_prompt("generate_refactoring_plan", "1.0")
    assert prompt is not None
    assert prompt.version == "1.0"

def test_get_prompt_nonexistent():
    with pytest.raises(KeyError):
        get_prompt("nonexistent_prompt")

def test_generate_refactoring_plan_v1_format():
    formatted = GENERATE_REFACTORING_PLAN_V1.format(
        file_path_1="file1.py",
        code_block_1="code1",
        file_path_2="file2.py",
        code_block_2="code2",
    )
    assert "file1.py" in formatted
    assert "code1" in formatted
    assert "file2.py" in formatted
    assert "code2" in formatted
