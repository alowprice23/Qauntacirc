import pytest
import json

from agents.planck_forge.ops import (
    parse_llm_output,
    validate_task_set,
    generate_spec_stub,
    TaskValidationError,
)
from core.types import TaskQuanta

@pytest.fixture
def llm_output_json_str():
    return json.dumps({
        "tasks": [
            {"id": "task1", "description": "First task", "verification_criteria": ["vc1"]},
            {"id": "task2", "description": "Second task", "verification_criteria": ["vc2"], "dependencies": ["task1"]},
        ]
    })

def test_parse_llm_output_success(llm_output_json_str):
    tasks = parse_llm_output(llm_output_json_str)
    assert len(tasks) == 2
    assert isinstance(tasks[0], TaskQuanta)
    assert tasks[0].id == "task1"
    assert tasks[1].dependencies == ["task1"]

def test_parse_llm_output_quantization_and_stub(llm_output_json_str):
    tasks = parse_llm_output(llm_output_json_str)
    assert tasks[0].energy > 0
    assert tasks[1].energy > 0
    assert "Theorem task1_correct" in tasks[0].spec_stub
    assert "Theorem task2_correct" in tasks[1].spec_stub

def test_parse_llm_output_invalid_json():
    with pytest.raises(TaskValidationError, match="Failed to decode"):
        parse_llm_output("not json")

def test_parse_llm_output_missing_tasks_key():
    with pytest.raises(TaskValidationError, match="missing a 'tasks' list"):
        parse_llm_output('{"other_key": []}')

def test_validate_task_set_success():
    tasks = [
        TaskQuanta(id="1", description="d", verification_criteria=["v"]),
        TaskQuanta(id="2", description="d", verification_criteria=["v"], dependencies=["1"]),
    ]
    validate_task_set(tasks) # Should not raise

def test_validate_task_set_empty():
    with pytest.raises(TaskValidationError, match="Task set cannot be empty"):
        validate_task_set([])

def test_validate_task_set_duplicate_ids():
    tasks = [
        TaskQuanta(id="1", description="d", verification_criteria=["v"]),
        TaskQuanta(id="1", description="d", verification_criteria=["v"]),
    ]
    with pytest.raises(TaskValidationError, match="Task IDs must be unique"):
        validate_task_set(tasks)

def test_validate_task_set_missing_fields():
    with pytest.raises(Exception): # Pydantic validation error
        TaskQuanta(id="1")

def test_validate_task_set_invalid_dependency():
    tasks = [
        TaskQuanta(id="1", description="d", verification_criteria=["v"], dependencies=["3"]),
        TaskQuanta(id="2", description="d", verification_criteria=["v"]),
    ]
    with pytest.raises(TaskValidationError, match="has an invalid dependency"):
        validate_task_set(tasks)

def test_generate_spec_stub():
    task = TaskQuanta(
        id="test_spec",
        description="A test for spec generation",
        verification_criteria=["Criterion A", "Criterion B"]
    )
    stub = generate_spec_stub(task)
    assert "Theorem test_spec_correct" in stub
    assert "Criterion A" in stub
    assert "Criterion B" in stub
