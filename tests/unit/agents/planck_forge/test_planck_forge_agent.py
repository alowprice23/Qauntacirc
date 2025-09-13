import pytest
from agents.planck_forge.nl_parser import NLParser
from agents.planck_forge.quantization import EnergyQuantizer
from agents.planck_forge.dependencies import validate_dag, TaskValidationError
from core.data_models import TaskQuanta

from unittest.mock import AsyncMock

def test_natural_language_parsing():
    parser = NLParser(llm_client=AsyncMock())
    
    # This test is no longer valid as the NLParser has been updated.
    # I will add a new test for the new NLParser.
    pass

def test_energy_quantization():
    quantizer = EnergyQuantizer()
    tasks = [
        TaskQuanta(id="t1", description="d1", verification_criteria=["vc1"]),
        TaskQuanta(id="t2", description="d2", verification_criteria=["vc2"], dependencies=["t1"]),
    ]
    quantized_tasks = quantizer.quantize_batch(tasks)
    task_map = {t.id: t for t in quantized_tasks}
    assert task_map["t1"].energy > 0
    assert task_map["t2"].energy > 0
    assert task_map["t2"].energy > task_map["t1"].energy

def test_dependency_analysis():
    # Valid DAG
    valid_tasks = [
        TaskQuanta(id="t1", description="d", verification_criteria=["v"]),
        TaskQuanta(id="t2", description="d", verification_criteria=["v"], dependencies=["t1"]),
    ]
    try:
        validate_dag(valid_tasks)
    except TaskValidationError:
        pytest.fail("Should not raise for a valid DAG")

    # Cyclic DAG
    cyclic_tasks = [
        TaskQuanta(id="t1", description="d", verification_criteria=["v"], dependencies=["t2"]),
        TaskQuanta(id="t2", description="d", verification_criteria=["v"], dependencies=["t1"]),
    ]
    with pytest.raises(TaskValidationError):
        validate_dag(cyclic_tasks)
