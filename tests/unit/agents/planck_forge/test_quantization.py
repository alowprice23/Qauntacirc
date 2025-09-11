import pytest
from agents.planck_forge.quantization import EnergyQuantizer
from core.types import TaskQuanta

def test_energy_quantizer_default_weights():
    quantizer = EnergyQuantizer()
    task = TaskQuanta(
        id="test_task",
        description="A test task",
        verification_criteria=["criterion1", "criterion2"],
        dependencies=["dep1"],
        spec_stub="spec stub content"
    )

    expected_energy = (
        len(task.description) * 0.1 +
        len(task.verification_criteria) * 0.5 +
        len(task.dependencies) * 1.0 +
        len(task.spec_stub) * 0.2
    )

    assert quantizer.quantize(task) == pytest.approx(expected_energy)

def test_energy_quantizer_custom_weights():
    weights = {
        "description_len": 0.2,
        "verification_criteria_count": 1.0,
        "dependencies_count": 2.0,
        "spec_stub_len": 0.5,
    }
    quantizer = EnergyQuantizer(weights=weights)
    task = TaskQuanta(
        id="test_task",
        description="A test task",
        verification_criteria=["criterion1", "criterion2"],
        dependencies=["dep1"],
        spec_stub="spec stub content"
    )

    expected_energy = (
        len(task.description) * 0.2 +
        len(task.verification_criteria) * 1.0 +
        len(task.dependencies) * 2.0 +
        len(task.spec_stub) * 0.5
    )

    assert quantizer.quantize(task) == pytest.approx(expected_energy)

def test_quantize_batch():
    quantizer = EnergyQuantizer()
    tasks = [
        TaskQuanta(
            id="task1",
            description="First task",
            verification_criteria=["vc1"],
            dependencies=[],
            spec_stub="stub1"
        ),
        TaskQuanta(
            id="task2",
            description="Second task",
            verification_criteria=["vc2", "vc3"],
            dependencies=["task1"],
            spec_stub="longer_stub2"
        ),
    ]

    quantized_tasks = quantizer.quantize_batch(tasks)
    assert len(quantized_tasks) == 2

    energy1 = (len("First task") * 0.1 + 1 * 0.5 + 0 * 1.0 + len("stub1") * 0.2)
    energy2 = (len("Second task") * 0.1 + 2 * 0.5 + 1 * 1.0 + len("longer_stub2") * 0.2)

    assert quantized_tasks[0].energy == pytest.approx(energy1)
    assert quantized_tasks[1].energy == pytest.approx(energy2)
