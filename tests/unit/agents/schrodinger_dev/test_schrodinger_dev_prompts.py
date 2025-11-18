import pytest
from agents.schrodinger_dev.prompts import (
    get_prompt,
    GENERATE_CODE_SKELETON_V1,
    GENERATE_PROOF_SKELETON_V1,
)

def test_get_prompt_generate_code():
    prompt = get_prompt("generate_code")
    assert prompt is not None
    assert prompt.name == "schrodinger_dev_generate_code"

def test_get_prompt_generate_proof():
    prompt = get_prompt("generate_proof", "1.0")
    assert prompt is not None
    assert prompt.name == "schrodinger_dev_generate_proof"

def test_get_prompt_nonexistent():
    with pytest.raises(KeyError):
        get_prompt("nonexistent_prompt")

def test_generate_code_skeleton_format():
    formatted = GENERATE_CODE_SKELETON_V1.format(
        task_description="test desc",
        verification_criteria="test criteria",
        template_name="test_template"
    )
    assert "test desc" in formatted
    assert "test criteria" in formatted
    assert "test_template" in formatted

def test_generate_proof_skeleton_format():
    formatted = GENERATE_PROOF_SKELETON_V1.format(
        task_description="test desc",
        verification_criteria="test criteria"
    )
    assert "test desc" in formatted
    assert "test criteria" in formatted
