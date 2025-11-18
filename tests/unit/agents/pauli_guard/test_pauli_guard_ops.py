import pytest
from agents.pauli_guard.ops import (
    levenshtein_distance,
    normalize_code,
    detect_duplicates,
    parse_refactoring_plan,
    RefactoringPlanError,
)

def test_levenshtein_distance():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("hello", "hello") == 0
    assert levenshtein_distance("", "abc") == 3

def test_normalize_code():
    code = "def my_func(a, b):\n    return a + b"
    expected = "def _func_(_arg_, _arg_):\n    return _var_ + _var_"
    assert normalize_code(code) == expected

def test_detect_exact_duplicates():
    files = {
        "file1.py": "def f(a, b):\n    return a + b",
        "file2.py": "def f(x, y):\n    return x + y", # Semantically identical
    }
    duplicates = detect_duplicates(files, min_lines=2)
    assert len(duplicates) == 1
    assert duplicates[0]["type"] == "exact"

def test_detect_similar_duplicates():
    files = {
        "file1.py": "def f(a, b):\n    return a + b",
        "file2.py": "def f(a, b):\n    return a * b", # Different operator
    }
    duplicates = detect_duplicates(files, min_lines=2, similarity_threshold=0.9)
    assert len(duplicates) == 1
    assert duplicates[0]["type"] == "similar"

def test_no_duplicates():
    files = {"file1.py": "a = 1", "file2.py": "b = 2"}
    duplicates = detect_duplicates(files)
    assert len(duplicates) == 0

def test_parse_refactoring_plan_success():
    llm_output = '{"shared_component_path": "p", "refactored_code": "c", "replacement_plan": [1, 2]}'
    plan = parse_refactoring_plan(llm_output)
    assert plan["shared_component_path"] == "p"

def test_parse_refactoring_plan_invalid_json():
    with pytest.raises(RefactoringPlanError, match="Failed to decode"):
        parse_refactoring_plan("not json")

def test_parse_refactoring_plan_missing_keys():
    with pytest.raises(RefactoringPlanError, match="missing required keys"):
        parse_refactoring_plan('{"refactored_code": "c"}')
