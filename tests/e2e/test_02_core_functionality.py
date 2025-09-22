import pytest
from typer.testing import CliRunner
from pathlib import Path
import os
import shutil
from unittest.mock import patch, MagicMock, AsyncMock

from cli.main import app
from core.types import QuantizedTasks, TaskQuantum

runner = CliRunner()

@pytest.fixture(scope="function")
def temp_project(tmp_path):
    """
    Creates a temporary, initialized QuantaCirc project for testing.
    This fixture changes the current working directory to the project root.
    """
    original_cwd = Path.cwd()
    project_name = "test_project"
    project_path = tmp_path / project_name

    # Use the CLI to create a project to ensure it's set up correctly
    os.chdir(tmp_path)
    result = runner.invoke(app, ["init", "create", project_name], catch_exceptions=False)
    assert result.exit_code == 0, f"Failed to create temp project: {result.stdout}"

    os.chdir(project_path)
    yield project_path
    os.chdir(original_cwd)


class TestCoreFunctionality:
    """
    Tests the fundamental software design capabilities of the application.
    Category 2 of the user-provided test plan.
    """
    def get_mock_quantized_tasks(self, num_tasks: int = 1) -> MagicMock:
        """Helper to create a mock QuantizedTasks object."""
        mock_tasks = MagicMock(spec=QuantizedTasks)
        mock_tasks.success = True
        mock_tasks.quanta = [MagicMock(spec=TaskQuantum) for _ in range(num_tasks)]
        mock_tasks.message = "OK"
        return mock_tasks

    # Test 1: Minimalistic Design Spec - "Hello World"
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_minimalistic_hello_world(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests the system's ability to handle a very simple request.
        We mock the orchestrator to simulate a successful generation.
        """
        # Mock PlanckForge to return a successful quantization
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(
            return_value=self.get_mock_quantized_tasks()
        )

        # Mock Orchestrator to return a successful generation
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(
            return_value={
                "success": True,
                "modified_files": ["src/main.py"],
                "proofs": []
            }
        )

        requirement = "a 'hello world' console app"
        result = runner.invoke(app, ["generate", "requirement", requirement], catch_exceptions=False)

        assert result.exit_code == 0
        # Check that the CLI reports success based on the mocked orchestrator result
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: src/main.py" in result.stdout

        # Verify that the orchestrator was called with the correct requirement
        # This requires inspecting the mock call arguments.
        # This part of the code is commented out in generate.py, so we can't test it yet.
        # mock_instance.execute_pipeline.assert_called_once()


    # Test 2: Hyper-Complex Design Spec
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_hyper_complex_spec_graceful_handling(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests that the system handles a hyper-complex request gracefully.
        The system should not crash and ideally should produce a high-level plan
        or ask for clarification rather than attempting to generate everything.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())

        # Simulate the system creating a plan instead of failing
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={
            "success": True,
            "modified_files": ["PLAN.md", "architecture.md"],
            "proofs": []
        })

        requirement = "a distributed, real-time bidding platform with machine learning-based fraud detection"
        result = runner.invoke(app, ["generate", "requirement", requirement], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: PLAN.md, architecture.md" in result.stdout

    # Test 6: Unsupported Request (Non-Software)
    @patch('cli.commands.generate.PlanckForgeAgent')
    def test_unsupported_non_software_request(self, mock_planck_forge, temp_project):
        """
        Tests the system's response to a request that is not about software.
        The system should identify this and respond gracefully.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(
            side_effect=Exception("Request is not related to software engineering. My capabilities are focused on code and system design.")
        )

        requirement = "design a car"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 1

        clean_stdout = " ".join(result.stdout.split())
        assert "Requirement decomposition failed" in clean_stdout
        assert "not related to software engineering" in clean_stdout

    # Test 7: Multi-Language Project Request
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_multi_language_project_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests the ability to handle a request for a project with multiple languages.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={
            "success": True,
            "modified_files": ["backend/main.py", "frontend/index.js", "docs/api.md"],
            "proofs": []
        })

        requirement = "a web app with a Python backend and a JavaScript frontend"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: backend/main.py, frontend/index.js, docs/api.md" in result.stdout

    # Test 11: Requesting a specific dependency version
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_specific_dependency_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request that includes a specific library and version.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["requirements.txt"], "proofs": []})

        requirement = "a project that uses requests version 2.27.1"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: requirements.txt" in result.stdout

    # Test 12: Requesting test generation for existing code
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_test_generation_for_existing_code(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests asking the agent to write tests for code that already exists.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "module.py").write_text("def add(a, b): return a + b")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["tests/test_module.py"], "proofs": []})

        requirement = "write pytest tests for the code in src/module.py"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: tests/test_module.py" in result.stdout

    # Test 16: Requesting code translation
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_code_translation_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request to translate code from one language to another.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "source.py").write_text("print('hello from python')")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["src/source.js"], "proofs": []})

        requirement = "translate the python code in src/source.py to javascript"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: src/source.js" in result.stdout

    # Test 17: Requesting a complex algorithm
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_complex_algorithm_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request to generate a well-known, complex algorithm.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["src/dijkstra.py", "tests/test_dijkstra.py"], "proofs": ["Proof of optimality"]})

        requirement = "implement Dijkstra's shortest path algorithm in python, including unit tests and a proof of correctness"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: src/dijkstra.py, tests/test_dijkstra.py" in result.stdout

    # Test 18: Requesting a change based on a CVE report
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_cve_remediation_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request to update a dependency based on a security advisory.
        """
        (temp_project / "requirements.txt").write_text("requests==2.20.0")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["requirements.txt"], "proofs": []})

        requirement = "update the requests library to fix CVE-2023-32681"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: requirements.txt" in result.stdout

    # Test 19: Requesting a change from user feedback
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_user_feedback_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request that simulates acting on user feedback.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "ui.py").write_text("def render(): print('Welcome!')")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["src/ui.py"], "proofs": []})

        requirement = "a user said the welcome message is too boring. make it more exciting."
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: src/ui.py" in result.stdout

    # Test 20: Requesting a tutorial
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_tutorial_generation_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request to generate a tutorial for a feature.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "api.py").write_text("# API code here")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["docs/tutorial.md"], "proofs": []})

        requirement = "write a tutorial on how to use the api in src/api.py"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: docs/tutorial.md" in result.stdout

    # Test 13: Requesting a bug fix
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_bug_fix_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests how the system handles a request to fix a bug.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        buggy_code = "def add(a, b): return a - b # This is wrong"
        (temp_project / "src" / "buggy.py").write_text(buggy_code)
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["src/buggy.py"], "proofs": ["Proof of correctness"]})

        requirement = "fix the bug in the add function in src/buggy.py"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout

    # Test 14: Requesting a feature addition
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_feature_addition_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests adding a new feature to an existing component.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "calculator.py").write_text("def add(a,b): return a+b")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["src/calculator.py"], "proofs": []})

        requirement = "add a subtract function to the calculator.py module"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: src/calculator.py" in result.stdout

    # Test 15: Requesting a performance analysis report
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_performance_analysis_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request for a performance analysis, which should result in a report.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "code.py").write_text("import time\\ndef slow_function(): time.sleep(1)")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": ["reports/performance_report.md"], "proofs": []})

        requirement = "analyze the performance of src/code.py and generate a report"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Modified files: reports/performance_report.md" in result.stdout

    # Test 8: Requesting a Refactor
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_refactor_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request to refactor existing code.
        """
        # First, create a file to be refactored
        (temp_project / "src").mkdir(exist_ok=True)
        original_code = "def my_func(x,y): return x+y"
        (temp_project / "src" / "original.py").write_text(original_code)
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={
            "success": True,
            "modified_files": ["src/original.py"], # It modifies the existing file
            "proofs": []
        })

        requirement = "refactor the code in src/original.py to be more readable and add type hints"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: src/original.py" in result.stdout

    # Test 9: Requesting Documentation
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_documentation_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request to generate documentation for existing code.
        """
        (temp_project / "src").mkdir(exist_ok=True)
        (temp_project / "src" / "code.py").write_text("def important_function(): pass")
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={
            "success": True,
            "modified_files": ["docs/code.md"], # Creates a new documentation file
            "proofs": []
        })

        requirement = "generate markdown documentation for the function in src/code.py"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: docs/code.md" in result.stdout

    # Test 10: Requesting a Specific Architecture
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_specific_architecture_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests a request that specifies a particular software architecture.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={
            "success": True,
            "modified_files": ["domain/user.py", "application/user_service.py", "infrastructure/user_repo.py"],
            "proofs": []
        })

        requirement = "generate a hexagonal architecture for a user service"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout

        clean_stdout = " ".join(result.stdout.split())
        assert "Modified files: domain/user.py, application/user_service.py, infrastructure/user_repo.py" in clean_stdout

    # Test 3: Contradictory Requirements
    @patch('cli.commands.generate.PlanckForgeAgent')
    def test_contradictory_requirements(self, mock_planck_forge, temp_project):
        """
        Tests the system's ability to detect and handle contradictory requirements.
        The ideal response is to ask for clarification.
        """
        # Simulate the PlanckForge agent detecting a contradiction
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(
            side_effect=Exception("Contradiction detected: Requirement specifies both 'stateless' and 'remember user preferences'.")
        )

        requirement = "The system must be stateless but also remember user preferences"
        result = runner.invoke(app, ["generate", "requirement", requirement], catch_exceptions=False)

        # The CLI should catch the exception from the agent and report it gracefully.
        assert result.exit_code == 1
        assert "Requirement decomposition failed" in result.stdout
        assert "Contradiction detected" in result.stdout

    # Test 4: Ambiguous Requirements
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_ambiguous_requirements_interactive(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests how the system handles ambiguous requirements in interactive mode.
        It should ask clarifying questions.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={"success": True, "modified_files": [], "proofs": []})

        requirement = "make a good application"
        result = runner.invoke(app, ["generate", "requirement", requirement, "--interactive"], input="y\n")

        assert result.exit_code == 0
        assert "Processing requirement: make a good application" in result.stdout

    # Test 5: Niche Technology Request
    @patch('cli.commands.generate.ConstellationMemory')
    @patch('cli.commands.generate.PlanckForgeAgent')
    @patch('cli.commands.generate.AgentOrchestrator')
    def test_niche_technology_request(self, mock_orchestrator, mock_planck_forge, mock_constellation_memory, temp_project):
        """
        Tests the system's response to a request for a less common technology.
        A good response would be to acknowledge the request and either attempt it
        or state its limitations clearly.
        """
        mock_planck_forge.return_value.quantize_requirement = AsyncMock(return_value=self.get_mock_quantized_tasks())
        mock_orchestrator.return_value.execute_pipeline = AsyncMock(return_value={
            "success": True,
            "modified_files": ["src/main.pas", "project.lpr"],
            "proofs": []
        })

        requirement = "a simple command-line calculator written in Pascal"
        result = runner.invoke(app, ["generate", "requirement", requirement])

        assert result.exit_code == 0
        assert "Generation completed successfully!" in result.stdout
        assert "Modified files: src/main.pas, project.lpr" in result.stdout
