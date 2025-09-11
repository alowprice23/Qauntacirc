import pytest
from agents.schrodinger_dev.ops import (
    load_code_template,
    extract_python_code,
    validate_python_syntax,
    create_code_and_proof_files,
    CodeGenerationError,
)

def test_load_code_template():
    template = load_code_template("default_function")
    assert template == "def {{function_name}}():\n    \"\"\"\n    {{docstring}}\n    \"\"\"\n    ...\n"
    assert load_code_template("nonexistent") is None

@pytest.mark.parametrize("llm_output, expected_code", [
    ("```python\nprint('hello')\n```", "print('hello')"),
    ("```\nprint('hello')\n```", "print('hello')"),
    ("print('hello')", "print('hello')"),
    ("Some text\n```python\ncode\n```\nmore text", "code"),
])
def test_extract_python_code(llm_output, expected_code):
    assert extract_python_code(llm_output) == expected_code

def test_validate_python_syntax_success():
    validate_python_syntax("def f(): pass") # Should not raise

def test_validate_python_syntax_failure():
    with pytest.raises(CodeGenerationError, match="syntax error"):
        validate_python_syntax("def f():")

def test_create_code_and_proof_files():
    code = "def f(): pass"
    proof = "assert f() is None"
    task_id = "T01"

    file_map = create_code_and_proof_files(code, proof, task_id)

    expected_paths = [
        "src/generated/t01_code.py",
        "proofs/generated/prove_t01_code.py"
    ]
    assert set(file_map.keys()) == set(expected_paths)
    assert file_map["src/generated/t01_code.py"] == code
    assert file_map["proofs/generated/prove_t01_code.py"] == proof
