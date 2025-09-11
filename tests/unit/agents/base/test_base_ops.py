import pytest
import ast
import inspect

from agents.base.ops import (
    parse_to_ast,
    get_function_definitions,
    get_class_definitions,
    calculate_cyclomatic_complexity,
    detect_duplicate_code,
    get_docstring,
)

SAMPLE_CODE = """
import os

class MyClass:
    \"\"\"A sample class.\"\"\"
    def __init__(self):
        self.x = 1

    def my_method(self, y):
        \"\"\"A sample method.\"\"\"
        if y > self.x:
            return y
        return self.x

def my_function(a, b):
    \"\"\"A sample function.\"\"\"
    if a and b:
        return a + b
    elif a or b:
        return a - b
    return 0
"""

def test_parse_to_ast():
    tree = parse_to_ast(SAMPLE_CODE)
    assert isinstance(tree, ast.Module)

def test_parse_to_ast_invalid_syntax():
    with pytest.raises(SyntaxError):
        parse_to_ast("invalid code:")

def test_get_function_definitions():
    tree = parse_to_ast(SAMPLE_CODE)
    functions = get_function_definitions(tree)
    assert len(functions) == 1
    assert functions[0].name == "my_function"

def test_get_class_definitions():
    tree = parse_to_ast(SAMPLE_CODE)
    classes = get_class_definitions(tree)
    assert len(classes) == 1
    assert classes[0].name == "MyClass"

def test_calculate_cyclomatic_complexity():
    tree = parse_to_ast(SAMPLE_CODE)
    functions = get_function_definitions(tree)
    # Complexity of my_function: 1 (start) + 1 (if) + 1 (and) + 1 (elif) + 1 (or) = 5
    assert calculate_cyclomatic_complexity(functions[0]) == 5

def test_detect_duplicate_code():
    files = {"file1.py": SAMPLE_CODE, "file2.py": SAMPLE_CODE}
    duplicates = detect_duplicate_code(files)
    assert duplicates == []

def test_get_docstring_function():
    tree = parse_to_ast(SAMPLE_CODE)
    functions = get_function_definitions(tree)
    assert get_docstring(functions[0]) == "A sample function."

def test_get_docstring_class():
    tree = parse_to_ast(SAMPLE_CODE)
    classes = get_class_definitions(tree)
    assert get_docstring(classes[0]) == "A sample class."

def test_get_docstring_method():
    tree = parse_to_ast(SAMPLE_CODE)
    classes = get_class_definitions(tree)
    method = [node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == "my_method"][0]
    assert inspect.cleandoc(get_docstring(method)) == "A sample method."
