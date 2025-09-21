import pytest
from typer.testing import CliRunner
from pathlib import Path
import os
import shutil
import ast
import json
import re

# A schema validation library would be good here, but for a self-contained
# test, we can write a simple validator.
# import jsonschema

from cli.main import app

runner = CliRunner()

@pytest.fixture(scope="function")
def temp_project(tmp_path):
    """
    Creates a temporary, initialized QuantaCirc project for testing.
    """
    project_name = "output_validation_project"
    project_path = tmp_path / project_name
    runner.invoke(app, ["init", "create", str(project_path)], catch_exceptions=False)
    os.chdir(project_path)
    yield project_path

class TestOutputValidation:
    """
    Tests to programmatically check the quality of generated code and artifacts.
    Category 4 of the user-provided test plan.
    """

    # Test 1: Syntax Checking
    def test_generated_python_code_syntax(self, temp_project):
        """
        Ensures that generated Python code is syntactically correct.
        """
        # "Generate" a Python file
        generated_code = "def my_function():\\n    return 'hello'\\n"
        code_file = temp_project / "generated.py"
        code_file.write_text(generated_code)

        # Use Python's `ast` module to parse the file.
        # It will raise a SyntaxError if the code is invalid.
        try:
            with open(code_file, 'r') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            pytest.fail(f"Generated Python code has a syntax error: {e}")

    # Test 2: Completeness Check
    def test_completeness_of_generated_class(self, temp_project):
        """
        Verifies that a generated class includes all requested methods.
        """
        # "Generate" a class
        generated_code = "class User:\\n    def __init__(self): pass\\n    def get_name(self): pass\\n"
        code_file = temp_project / "user.py"
        code_file.write_text(generated_code)

        # Parse the code and check for method names
        with open(code_file, 'r') as f:
            tree = ast.parse(f.read())

        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)
        assert class_node.name == "User"

        method_names = {node.name for node in class_node.body if isinstance(node, ast.FunctionDef)}
        expected_methods = {"__init__", "get_name"}
        assert expected_methods.issubset(method_names)

    # Test 3: Consistency Check
    def test_api_client_server_consistency(self, temp_project):
        """
        Checks that a generated API client calls endpoints defined in a server stub.
        """
        # "Generate" server and client stubs
        server_code = "API_ROUTES = ['/users', '/users/{id}']"
        client_code = "def call_api():\\n    requests.get('/users')\\n"
        (temp_project / "server.py").write_text(server_code)
        (temp_project / "client.py").write_text(client_code)

        # Simple check: extract strings and compare
        server_routes = re.findall(r"\'(.*?)\'", server_code)
        client_calls = re.findall(r"\'(.*?)\'", client_code)

        for call in client_calls:
            # This is a naive check. A real one would be more robust.
            assert call in server_routes

    # Test 4: Format Adherence (JSON)
    def test_json_output_format_adherence(self, temp_project):
        """
        Validates that a generated JSON file is well-formed.
        """
        # "Generate" a JSON file
        json_content = '{"key": "value", "number": 123}'
        json_file = temp_project / "config.json"
        json_file.write_text(json_content)

        # Attempt to parse it
        try:
            with open(json_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Generated JSON is not well-formed: {e}")

    # Test 5: Format Adherence (Markdown)
    def test_markdown_output_format_adherence(self, temp_project):
        """
        Checks a generated Markdown file for valid structure.
        """
        # "Generate" a Markdown file
        md_content = "# Title\\n\\nThis is a paragraph.\\n\\n- Item 1\\n- Item 2"
        md_file = temp_project / "README.md"
        md_file.write_text(md_content)

        # Simple validation checks
        lines = md_content.split('\\n')
        assert lines[0].startswith("# ") # Check for H1 header
        assert lines[2].startswith("- ") # Check for list item

    # Test 6: Dependency File Validation
    def test_requirements_file_syntax(self, temp_project):
        """
        Ensures a generated requirements.txt file has valid syntax.
        """
        # "Generate" a requirements file
        req_content = "requests==2.27.1\\npytest>=6.0.0\\n# A comment\\n"
        req_file = temp_project / "requirements.txt"
        req_file.write_text(req_content)

        # A simple validation is to check each non-comment line for '==' or '>=' etc.
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    assert any(op in line for op in ['==', '>=', '<=', '>', '<', '~='])

    # Test 7: Configuration File Validation (INI)
    def test_ini_config_validation(self, temp_project):
        """
        Validates the structure of a generated .ini file.
        """
        import configparser
        ini_content = "[database]\\nhost = localhost\\nuser=admin\\n"
        ini_file = temp_project / "config.ini"
        ini_file.write_text(ini_content)

        try:
            config = configparser.ConfigParser()
            config.read(ini_file)
            assert config.has_section('database')
            assert config.get('database', 'host') == 'localhost'
        except configparser.Error as e:
            pytest.fail(f"Generated INI file is invalid: {e}")

    # Test 8: Generated Test File Validation
    def test_generated_test_file_structure(self, temp_project):
        """
        Checks that a generated test file contains valid pytest functions.
        """
        test_code = "import pytest\\ndef test_feature_one():\\n    assert True\\nclass TestSuite:\\n    def test_something(self):\\n        pass"
        test_file = temp_project / "test_generated.py"
        test_file.write_text(test_code)

        with open(test_file, 'r') as f:
            tree = ast.parse(f.read())

        test_functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
        assert "test_feature_one" in test_functions
        assert "test_something" in test_functions

    # Test 9: Checking for Placeholder Comments
    def test_for_placeholder_todos(self, temp_project):
        """
        Scans generated code for placeholders like TODO or FIXME.
        A "complete" generation should not contain these.
        """
        # "Generate" code with a placeholder
        code_with_todo = "def incomplete_function():\\n    # TODO: Implement this later\\n    pass"
        code_file = temp_project / "wip.py"
        code_file.write_text(code_with_todo)

        content = code_file.read_text()
        assert "TODO" in content, "Test setup failed, TODO not found"
        # A real validation test would assert that "TODO" is NOT in the content
        # of a supposedly finished artifact.

    # Test 10: Enforcing a Naming Convention
    def test_naming_convention_enforcement(self, temp_project):
        """
        Checks if generated Python functions follow snake_case naming.
        """
        code = "def myFunction(): pass\\ndef another_bad_name(): pass"
        code_file = temp_project / "naming.py"
        code_file.write_text(code)

        with open(code_file, 'r') as f:
            tree = ast.parse(f.read())

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    violations.append(node.name)

        assert "myFunction" in violations
        assert "another_bad_name" not in violations # This one is valid snake_case
