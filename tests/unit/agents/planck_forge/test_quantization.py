import pytest
from agents.planck_forge.quantization import EnergyQuantizer
from core.data_models import TaskQuanta

@pytest.fixture
def sample_tasks():
    """A fixture for a sample task graph."""
    return [
        TaskQuanta(id="a", description="Task A", verification_criteria=["vc_a"], dependencies=[]),
        TaskQuanta(id="b", description="Task B", verification_criteria=["vc_b1", "vc_b2"], dependencies=["a"]),
        TaskQuanta(id="c", description="Task C", verification_criteria=["vc_c"], dependencies=["b"]),
        TaskQuanta(id="d", description="Task D", verification_criteria=["vc_d"], dependencies=["a"]),
    ]

def test_quantize_batch_default_params(sample_tasks):
    """
    Tests the energy quantization with default Planck constant (1.0) and weights.
    """
    quantizer = EnergyQuantizer()
    quantized_tasks = quantizer.quantize_batch(sample_tasks)
    task_map = {task.id: task for task in quantized_tasks}

    weights = quantizer.base_frequency_weights
    h = quantizer.planck_constant

    # Expected levels: a=1, b=2, d=2, c=3
    # Expected frequencies (v):
    v_a = len("Task A") * weights["description_len"] + 1 * weights["verification_criteria_count"] + 0 * weights["dependencies_count"]
    v_b = len("Task B") * weights["description_len"] + 2 * weights["verification_criteria_count"] + 1 * weights["dependencies_count"]
    v_c = len("Task C") * weights["description_len"] + 1 * weights["verification_criteria_count"] + 1 * weights["dependencies_count"]
    v_d = len("Task D") * weights["description_len"] + 1 * weights["verification_criteria_count"] + 1 * weights["dependencies_count"]

    # Expected energies (E = n * h * v):
    e_a = 1 * h * v_a
    e_b = 2 * h * v_b
    e_c = 3 * h * v_c
    e_d = 2 * h * v_d

    assert task_map["a"].energy == pytest.approx(e_a)
    assert task_map["b"].energy == pytest.approx(e_b)
    assert task_map["c"].energy == pytest.approx(e_c)
    assert task_map["d"].energy == pytest.approx(e_d)

def test_quantize_batch_custom_planck_constant(sample_tasks):
    """
    Tests the energy quantization with a custom Planck constant.
    """
    h = 2.5
    quantizer = EnergyQuantizer(planck_constant=h)
    quantized_tasks = quantizer.quantize_batch(sample_tasks)
    task_map = {task.id: task for task in quantized_tasks}

    weights = quantizer.base_frequency_weights

    v_a = len("Task A") * weights["description_len"] + 1 * weights["verification_criteria_count"] + 0 * weights["dependencies_count"]
    e_a = 1 * h * v_a
    assert task_map["a"].energy == pytest.approx(e_a)

    v_c = len("Task C") * weights["description_len"] + 1 * weights["verification_criteria_count"] + 1 * weights["dependencies_count"]
    e_c = 3 * h * v_c
    assert task_map["c"].energy == pytest.approx(e_c)


def test_quantize_batch_custom_weights(sample_tasks):
    """
    Tests the energy quantization with custom base frequency weights.
    """
    h = 1.0
    custom_weights = {
        "description_len": 1.0,
        "verification_criteria_count": 2.0,
        "dependencies_count": 3.0,
        "spec_stub_len": 0.0, # Not testing spec stub here
    }
    quantizer = EnergyQuantizer(planck_constant=h, base_frequency_weights=custom_weights)
    quantized_tasks = quantizer.quantize_batch(sample_tasks)
    task_map = {task.id: task for task in quantized_tasks}

    v_b = len("Task B") * custom_weights["description_len"] + 2 * custom_weights["verification_criteria_count"] + 1 * custom_weights["dependencies_count"]
    e_b = 2 * h * v_b
    assert task_map["b"].energy == pytest.approx(e_b)

def test_quantize_batch_empty_list():
    """
    Tests that quantizing an empty list of tasks returns an empty list.
    """
    quantizer = EnergyQuantizer()
    assert quantizer.quantize_batch([]) == []
