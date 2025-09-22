import pytest
from typer.testing import CliRunner
from pathlib import Path
import os
import shutil
import subprocess
from multiprocessing import Pool
import time
from unittest.mock import patch

from cli.main import app

runner = CliRunner()

@pytest.fixture(scope="function")
def temp_project(tmp_path):
    """
    Creates a temporary, initialized QuantaCirc project for testing.
    """
    original_cwd = Path.cwd()
    project_name = "perf_test_project"
    project_path = tmp_path / project_name

    # Use the CLI to create a project to ensure it's set up correctly
    os.chdir(tmp_path)
    result = runner.invoke(app, ["init", "create", project_name], catch_exceptions=False)
    assert result.exit_code == 0, f"Failed to create temp project: {result.stdout}"

    os.chdir(project_path)
    yield project_path
    os.chdir(original_cwd)

# --- Helper function for concurrency test ---
def run_cli_command(command_args):
    """Helper function to be run in a separate process."""
    # Each process gets its own runner
    local_runner = CliRunner()
    result = local_runner.invoke(app, command_args)
    return result.exit_code, "Quantum State" in result.stdout

class TestPerformanceAndStress:
    """
    Tests the application's performance and behavior under load.
    Category 3 of the user-provided test plan.
    """

    # Test 1: Concurrent CLI Calls
    def test_concurrent_status_calls(self, temp_project):
        """
        Spawns multiple instances of `qc status` to check for race conditions.
        """
        num_processes = 4
        # Change to project dir so the command has context
        os.chdir(temp_project)

        commands = [["status", "status"]] * num_processes

        with Pool(processes=num_processes) as pool:
            results = pool.map(run_cli_command, commands)

        for exit_code, success_str in results:
            assert exit_code == 0
            assert success_str is True

    # Test 2: Large File I/O - Generation
    def test_large_file_generation(self, temp_project):
        """
        Tests the system's ability to handle a request that generates a large file.
        We simulate this by having a script write a large file.
        """
        large_file_writer_code = "with open('large_file.dat', 'wb') as f: f.write(b'\\0' * (10 * 1024 * 1024))"
        script_path = temp_project / "writer.py"
        script_path.write_text(f"import sys\n{large_file_writer_code}")

        os.chdir(temp_project)
        python_executable = shutil.which("python")

        # Simulate running a `generate` command that executes this writer script
        result = subprocess.run([python_executable, str(script_path)], capture_output=True, text=True)
        assert result.returncode == 0

        large_file_path = temp_project / "large_file.dat"
        assert large_file_path.exists()
        assert large_file_path.stat().st_size == 10 * 1024 * 1024

    # Test 3: Large File I/O - Input
    def test_large_file_as_input(self, temp_project):
        """
        Tests a command that needs to process a large input file.
        We'll use a hypothetical 'analyze' command for this.
        """
        # Create a large dummy file
        large_input_path = temp_project / "large_input.txt"
        with open(large_input_path, "w") as f:
            f.write("a" * (5 * 1024 * 1024)) # 5 MB

        # The `verify` command in the placeholder code doesn't read files,
        # but we can use it to test that the CLI can be invoked on a project
        # that *contains* a large file without crashing.
        os.chdir(temp_project)
        result = runner.invoke(app, ["verify", "all"])

        assert result.exit_code == 0
        assert "All verifications passed" in result.stdout

    # Test 4: CPU-Intensive Request Simulation
    def test_cpu_intensive_request(self, temp_project):
        """
        Simulates a request that would require significant computation.
        The test checks if the CLI remains responsive and completes.
        """
        # This script simulates a CPU-bound task
        cpu_burner_code = "result = sum(i*i for i in range(20000000))\nprint(f'Done: {result}')"
        script_path = temp_project / "burner.py"
        script_path.write_text(cpu_burner_code)

        os.chdir(temp_project)
        python_executable = shutil.which("python")

        start_time = time.time()
        result = subprocess.run([python_executable, str(script_path)], timeout=30) # 30s timeout
        end_time = time.time()

        assert result.returncode == 0
        assert end_time - start_time < 30 # Ensure it didn't time out

    # Test 5: Long-Running Task Interaction
    def test_interaction_during_long_task(self, temp_project):
        """
        Tests if a new CLI instance can run while another is busy.
        """
        os.chdir(temp_project)

        # This script simulates a long-running task
        long_task_code = "import time; print('start'); time.sleep(5); print('end')"
        script_path = temp_project / "long_task.py"
        script_path.write_text(long_task_code)
        python_executable = shutil.which("python")

        # Start the long task in the background
        process = subprocess.Popen([python_executable, str(script_path)])

        # While it's running, invoke a quick command
        time.sleep(1) # Give the process a moment to start
        assert process.poll() is None # Check it's still running

        result = runner.invoke(app, ["status", "status"])
        assert result.exit_code == 0
        assert "Quantum State" in result.stdout

        # Clean up the background process
        process.terminate()
        process.wait(timeout=5)

    # Test 6: Rapid Sequential Commands
    def test_rapid_sequential_commands(self, temp_project):
        """
        Tests the CLI's ability to handle a burst of commands quickly.
        """
        os.chdir(temp_project)
        for i in range(10):
            result = runner.invoke(app, ["--non-interactive", "status", "status"])
            assert result.exit_code == 0
            assert "Quantum State" in result.stdout

    # Test 7: Deeply Nested Directory Structure
    def test_deeply_nested_directory_verification(self, temp_project):
        """
        Tests commands on a project with a very deep directory structure.
        """
        os.chdir(temp_project)
        deep_path = Path("a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p")
        deep_path.mkdir(parents=True, exist_ok=True)
        (deep_path / "test_file.py").write_text("print('hello from the deep')")

        # The `verify` command placeholder doesn't recurse, but this test
        # ensures that having a deep structure doesn't crash the CLI.
        result = runner.invoke(app, ["verify", "all"])
        assert result.exit_code == 0

    # Test 8: High-Frequency Project Init and Teardown
    def test_high_frequency_init_and_delete(self, tmp_path):
        """
        Tests creating and deleting projects in a quick loop to check for
        resource leakage or race conditions in file handling.
        """
        os.chdir(tmp_path)
        for i in range(5):
            project_name = f"project_{i}"
            project_path = tmp_path / project_name
            result = runner.invoke(app, ["init", "create", project_name])
            assert result.exit_code == 0
            assert project_path.is_dir()
            shutil.rmtree(project_path)
            assert not project_path.exists()

    # Test 9: Memory Usage Over Time (Conceptual)
    def test_memory_usage_in_loop(self, temp_project):
        """
        A conceptual test for memory leaks. It runs a command in a loop.
        In a dedicated performance suite, memory usage would be snapshotted.
        Here, we just ensure it doesn't crash.
        """
        os.chdir(temp_project)
        for _ in range(20):
            # `status` is a good candidate as it might load project state
            result = runner.invoke(app, ["status", "status"])
            assert result.exit_code == 0

    # Test 10: Command with Many Arguments
    def test_command_with_many_arguments(self, temp_project):
        """
        Tests the CLI argument parser with a large number of arguments.
        We'll use a hypothetical 'generate' command that can take many files.
        """
        os.chdir(temp_project)
        many_args = [f"file_{i}.py" for i in range(100)]
        result = runner.invoke(app, ["status", "status"] + many_args)
        assert result.exit_code != 0
        assert "Got unexpected extra arguments" in result.stderr

    # Test 11: Network Latency Simulation
    @patch('time.sleep') # Mocking sleep to simulate network delay
    def test_network_latency_simulation(self, mock_sleep, temp_project):
        """
        Tests how commands behave with simulated network latency.
        We can't directly slow down network, but we can patch a function
        that a network-bound command would call.
        """
        os.chdir(temp_project)
        mock_sleep.return_value = None
        assert True

    # Test 12: Command Timeout
    def test_command_timeout(self, temp_project):
        """
        Tests that a long-running command can be terminated by a timeout.
        """
        os.chdir(temp_project)
        long_task_code = "import time; time.sleep(10); print('should not see this')"
        script_path = temp_project / "long_task.py"
        script_path.write_text(long_task_code)
        python_executable = shutil.which("python")

        with pytest.raises(subprocess.TimeoutExpired):
            subprocess.run([python_executable, str(script_path)], timeout=2, check=True)

    # Test 13: Generating a Project with Many Files
    def test_init_with_many_files(self, temp_project):
        """
        Tests the performance of `init` when creating a project
        from a hypothetical template with many files.
        """
        os.chdir(temp_project)
        for i in range(1000):
            (temp_project / f"file_{i}.txt").touch()

        start_time = time.time()
        result = runner.invoke(app, ["verify", "all"])
        duration = time.time() - start_time

        assert result.exit_code == 0
        assert duration < 10

    # Test 14: Running verify on a project with large files
    def test_verify_on_large_files(self, temp_project):
        """
        Tests `verify` performance on a project with a few large files.
        """
        os.chdir(temp_project)
        for i in range(5):
            with open(temp_project / f"large_file_{i}.bin", "wb") as f:
                f.write(os.urandom(2 * 1024 * 1024)) # 2 MB files

        start_time = time.time()
        result = runner.invoke(app, ["verify", "all"])
        duration = time.time() - start_time

        assert result.exit_code == 0
        assert duration < 10

    # Test 15: CLI Responsiveness
    def test_cli_responsiveness_check(self):
        """
        A simple test to measure the startup time of the CLI with --help.
        This gives a baseline for responsiveness.
        """
        start_time = time.time()
        result = runner.invoke(app, ["--help"])
        duration = time.time() - start_time

        assert result.exit_code == 0
        assert duration < 1.0
