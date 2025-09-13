import pytest
from agents.planck_forge.prompts import get_prompt, DECOMPOSE_GOAL_TO_TASKS_V1

def test_get_prompt_latest():
    prompt = get_prompt("decompose_goal_to_tasks", "latest")
    assert prompt is not None
    assert prompt.version == "1.0"
    assert prompt.name == "planck_forge_decompose_goal_to_tasks"

def test_get_prompt_specific_version():
    prompt = get_prompt("decompose_goal_to_tasks", "1.0")
    assert prompt is not None
    assert prompt.version == "1.0"

def test_get_prompt_nonexistent_name():
    with pytest.raises(KeyError):
        get_prompt("nonexistent_prompt")

def test_get_prompt_nonexistent_version():
    with pytest.raises(KeyError):
        get_prompt("decompose_goal_to_tasks", "0.1")

def test_decompose_goal_to_tasks_v1_format():
    goal = "Create a new user"
    formatted_prompt = DECOMPOSE_GOAL_TO_TASKS_V1.format(goal_text=goal)
    assert goal in formatted_prompt
    assert "{goal_text}" not in formatted_prompt
