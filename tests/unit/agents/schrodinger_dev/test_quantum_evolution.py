import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock

from agents.schrodinger_dev.hamiltonian import HamiltonianBuilder
from agents.schrodinger_dev.code_generator import QuantumCodeGenerator
from agents.schrodinger_dev.agent import SchrodingerDevAgent
from core.types import SystemState, EnergyBreakdown, LyapunovMetrics, Status, SoftwareState

@pytest.fixture
def hamiltonian_builder():
    weights = {'complexity': 1.0, 'length': 0.01, 'similarity': 0.5}
    return HamiltonianBuilder(weights=weights)

@pytest.fixture
def mock_llm_client_variations():
    client = AsyncMock()
    client.complete.side_effect = [
        {
            "content": """
```python
def func_a():
    # A slightly more complex implementation
    x = [1, 2, 3]
    y = 0
    for i in x:
        y += i
    return y
```
```python
def func_b():
    # A more complex implementation
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    if a > b:
        return c * d
    else:
        return e
```
```python
def func_c():
    # The simplest implementation (lowest energy)
    return 0
```
```python
def func_d():
    # Syntactically correct, but complex
    return 1 * 2 * 3 * 4 * 5 * 6
```
"""
        },
        {
            "content": """
```python
from z3 import Solver, Int
s = Solver()
x = Int('x')
s.add(x > 0)
print(s.check())
```
"""
        }
    ]
    return client

@pytest.fixture
def quantum_code_generator(mock_llm_client_variations):
    return QuantumCodeGenerator(llm_client=mock_llm_client_variations, num_superpositions=4)

def test_hamiltonian_construction(hamiltonian_builder):
    implementations = [
        "def f(): return 1",
        "def f(): return 1+2",
        "def f(): return 1+2+3"
    ]
    spec = {"constraints": []}
    H = hamiltonian_builder.from_specification(implementations, spec)

    assert H.shape == (3, 3)
    assert np.all(np.diag(H) > 0)
    assert np.all(H[np.triu_indices(3, 1)] < 0)

def test_state_evolution_and_collapse(quantum_code_generator):
    psi_0 = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.complex128)
    H = np.array([
        [10, -1, -1, -1],
        [-1, 5, -1, -1],
        [-1, -1, 1, -1], # Lowest energy
        [-1, -1, -1, 8]
    ])

    psi_final = quantum_code_generator.evolve_state(psi_0, H, time_step=1.0)

    assert np.abs(psi_final[2])**2 > np.abs(psi_0[2])**2

    implementations = ["code1", "code2", "code3", "code4"]
    collapsed_code = quantum_code_generator.collapse_to_implementation(implementations, psi_final)
    assert collapsed_code == "code3"

@pytest.mark.asyncio
async def test_agent_end_to_end_quantum_flow(mock_llm_client_variations):
    agent = SchrodingerDevAgent(
        state_space=MagicMock(),
        energy_calculator=MagicMock(),
        metrics_logger=MagicMock(),
        policy_engine=MagicMock(),
        agent_memory=MagicMock(),
        llm_client=mock_llm_client_variations
    )

    energy_breakdown = EnergyBreakdown(total=100.0, complexity=100.0, coupling=0.0, constraint=0.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
    initial_state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
        metadata={
            "planck_forge_output": {
                "tasks": [{"id": "task_quantum", "description": "d1", "verification_criteria": ["vc1"]}]
            },
            "task_dag": {"task_quantum": []}
        }
    )

    proposal = agent.analyze_state(initial_state)

    assert proposal.status == Status.SUCCESS
    assert "code_evolution" in proposal.payload
