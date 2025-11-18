import pytest
import json

from agents.planck_forge.ops import (
    parse_llm_output,
    validate_task_set,
    validate_dag,
    generate_task_dag,
    TaskValidationError,
)

def test_parse_llm_output_success():
    llm_output = '{"tasks": [{"task_id": "1"}, {"task_id": "2"}]}'
    tasks = parse_llm_output(llm_output)
    assert len(tasks) == 2
    assert tasks[0]["task_id"] == "1"

def test_parse_llm_output_invalid_json():
    with pytest.raises(TaskValidationError, match="Failed to decode"):
        parse_llm_output("not json")

def test_parse_llm_output_missing_tasks_key():
    with pytest.raises(TaskValidationError, match="missing a 'tasks' list"):
        parse_llm_output('{"other_key": []}')

def test_validate_task_set_success():
    tasks = [
        {"task_id": "1", "description": "d", "verification_criteria": "v"},
        {"task_id": "2", "description": "d", "verification_criteria": "v", "dependencies": ["1"]},
    ]
    validate_task_set(tasks) # Should not raise

def test_validate_task_set_empty():
    with pytest.raises(TaskValidationError, match="Task set cannot be empty"):
        validate_task_set([])

def test_validate_task_set_missing_id():
    tasks = [{"description": "d", "verification_criteria": "v"}]
    with pytest.raises(TaskValidationError, match="All tasks must have a 'task_id'"):
        validate_task_set(tasks)

def test_validate_task_set_duplicate_ids():
    tasks = [
        {"task_id": "1", "description": "d", "verification_criteria": "v"},
        {"task_id": "1", "description": "d", "verification_criteria": "v"},
    ]
    with pytest.raises(TaskValidationError, match="Task IDs must be unique"):
        validate_task_set(tasks)

def test_validate_task_set_missing_fields():
    tasks = [{"task_id": "1"}]
    with pytest.raises(TaskValidationError, match="is missing description or verification criteria"):
        validate_task_set(tasks)

def test_validate_task_set_invalid_dependency():
    tasks = [
        {"task_id": "1", "description": "d", "verification_criteria": "v", "dependencies": ["3"]},
        {"task_id": "2", "description": "d", "verification_criteria": "v"},
    ]
    with pytest.raises(TaskValidationError, match="has an invalid dependency"):
        validate_task_set(tasks)

def test_validate_dag_success():
    tasks = [
        {"task_id": "1"},
        {"task_id": "2", "dependencies": ["1"]},
        {"task_id": "3", "dependencies": ["1"]},
        {"task_id": "4", "dependencies": ["2", "3"]},
    ]
    validate_dag(tasks) # Should not raise

def test_validate_dag_cycle():
    tasks = [
        {"task_id": "1", "dependencies": ["3"]},
        {"task_id": "2", "dependencies": ["1"]},
        {"task_id": "3", "dependencies": ["2"]},
    ]
    with pytest.raises(TaskValidationError, match="A cycle was detected"):
        validate_dag(tasks)

def test_generate_task_dag():
    tasks = [
        {"task_id": "1"},
        {"task_id": "2", "dependencies": ["1"]},
    ]
    dag = generate_task_dag(tasks)
    assert dag == {"1": [], "2": ["1"]}
