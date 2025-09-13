import pytest
from agents.planck_forge.dependencies import validate_dag, generate_task_dag, TaskValidationError, calculate_node_levels
from core.data_models import TaskQuanta

@pytest.fixture
def valid_dag_tasks():
    return [
        TaskQuanta(id="task1", description="1", verification_criteria=["vc1"]),
        TaskQuanta(id="task2", description="2", verification_criteria=["vc2"], dependencies=["task1"]),
        TaskQuanta(id="task3", description="3", verification_criteria=["vc3"], dependencies=["task1"]),
        TaskQuanta(id="task4", description="4", verification_criteria=["vc4"], dependencies=["task2", "task3"]),
    ]

@pytest.fixture
def cyclic_dag_tasks():
    return [
        TaskQuanta(id="task1", description="1", verification_criteria=["vc1"], dependencies=["task3"]),
        TaskQuanta(id="task2", description="2", verification_criteria=["vc2"], dependencies=["task1"]),
        TaskQuanta(id="task3", description="3", verification_criteria=["vc3"], dependencies=["task2"]),
    ]

@pytest.fixture
def complex_cyclic_dag_tasks():
    return [
        TaskQuanta(id="task1", description="1", verification_criteria=["vc1"]),
        TaskQuanta(id="task2", description="2", verification_criteria=["vc2"], dependencies=["task1"]),
        TaskQuanta(id="task3", description="3", verification_criteria=["vc3"], dependencies=["task2"]),
        TaskQuanta(id="task4", description="4", verification_criteria=["vc4"], dependencies=["task3"]),
        TaskQuanta(id="task5", description="5", verification_criteria=["vc5"], dependencies=["task4"]),
        TaskQuanta(id="task1", description="1", verification_criteria=["vc1"], dependencies=["task5"]), # Cycle back to task1
    ]

def test_validate_dag_valid(valid_dag_tasks):
    try:
        validate_dag(valid_dag_tasks)
    except TaskValidationError:
        pytest.fail("validate_dag raised TaskValidationError unexpectedly for a valid DAG.")

def test_validate_dag_cyclic(cyclic_dag_tasks):
    with pytest.raises(TaskValidationError, match="A cycle was detected"):
        validate_dag(cyclic_dag_tasks)

def test_validate_dag_complex_cyclic(complex_cyclic_dag_tasks):
    with pytest.raises(TaskValidationError, match="A cycle was detected"):
        validate_dag(complex_cyclic_dag_tasks)

def test_generate_task_dag(valid_dag_tasks):
    expected_dag = {
        "task1": [],
        "task2": ["task1"],
        "task3": ["task1"],
        "task4": ["task2", "task3"],
    }
    assert generate_task_dag(valid_dag_tasks) == expected_dag

def test_calculate_node_levels_linear_chain():
    adj_list = {"a": [], "b": ["a"], "c": ["b"]}
    expected_levels = {"a": 1, "b": 2, "c": 3}
    assert calculate_node_levels(adj_list) == expected_levels

def test_calculate_node_levels_multiple_dependencies():
    adj_list = {"a": [], "b": [], "c": ["a", "b"]}
    expected_levels = {"a": 1, "b": 1, "c": 2}
    assert calculate_node_levels(adj_list) == expected_levels

def test_calculate_node_levels_complex_graph():
    adj_list = {
        "a": [],
        "b": ["a"],
        "c": ["a"],
        "d": ["b", "c"],
        "e": ["d"],
    }
    expected_levels = {"a": 1, "b": 2, "c": 2, "d": 3, "e": 4}
    assert calculate_node_levels(adj_list) == expected_levels

def test_calculate_node_levels_multiple_sources():
    adj_list = {"a": [], "b": [], "c": ["a"], "d": ["b"]}
    expected_levels = {"a": 1, "b": 1, "c": 2, "d": 2}
    assert calculate_node_levels(adj_list) == expected_levels

def test_calculate_node_levels_empty_graph():
    adj_list = {}
    expected_levels = {}
    assert calculate_node_levels(adj_list) == expected_levels
