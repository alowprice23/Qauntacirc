# core/serialization.py

"""
Handles serialization and deserialization of core data structures.

This module centralizes the logic for converting core objects (like QCState
and RunRecord) to and from persistent formats, primarily JSON. It provides
a layer of abstraction over Pydantic's serialization capabilities, making it
easier to manage custom data types or change serialization formats globally.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Type, TypeVar, Any
import numpy as np

from pydantic import BaseModel
from core.types import QCState, RunRecord

# Generic type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

class NumpyJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that can handle NumPy arrays and data types.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

def object_hook_for_numpy(obj: dict) -> Any:
    """
    A custom object hook for json.load to reconstruct complex numbers.
    """
    if 'real' in obj and 'imag' in obj and len(obj) == 2:
        return obj['real'] + 1j * obj['imag']
    return obj

def serialize_model(model_instance: T) -> str:
    """
    Serializes a Pydantic model instance to a JSON string.

    Args:
        model_instance: The Pydantic model instance to serialize.

    Returns:
        A JSON string representation of the model.
    """
    # model_dump is used to get a dict, then we use our custom encoder
    model_dict = model_instance.model_dump(mode='json')
    return json.dumps(model_dict, indent=4, cls=NumpyJSONEncoder)

def deserialize_model(json_string: str, model_class: Type[T]) -> T:
    """
    Deserializes a JSON string into a Pydantic model instance.

    Args:
        json_string: The JSON string to deserialize.
        model_class: The Pydantic model class to instantiate.

    Returns:
        An instance of the specified model class.
    """
    data = json.loads(json_string, object_hook=object_hook_for_numpy)
    return model_class.model_validate(data)

def save_model_to_json(model_instance: T, file_path: Path | str):
    """
    Saves a Pydantic model instance to a JSON file.

    Args:
        model_instance: The model instance to save.
        file_path: The path to the output JSON file.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    json_string = serialize_model(model_instance)
    file_path.write_text(json_string)

def load_model_from_json(file_path: Path | str, model_class: Type[T]) -> T:
    """
    Loads a Pydantic model instance from a JSON file.

    Args:
        file_path: The path to the input JSON file.
        model_class: The model class to instantiate.

    Returns:
        An instance of the specified model class.
    """
    file_path = Path(file_path)
    json_string = file_path.read_text()
    return deserialize_model(json_string, model_class)


# Example Usage
if __name__ == '__main__':
    from uuid import uuid4
    from datetime import datetime
    from core.types import SoftwareState, EnergyComponents, QuantumState

    # Create a QCState object
    qc_state = QCState(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        software_state=SoftwareState(component_versions={"a":"1"}, config_hashes={"b":"2"}, status="nominal"),
        energy=10.5,
        energy_components=EnergyComponents(static=5.0, dynamic=5.5, interaction=0.0),
        lyapunov_potential=0.5,
        contraction_factor=0.8,
        optimization_phase="exploitation",
        # Create a quantum state with a numpy array to test the custom encoder
        quantum_state=QuantumState(state_vector=np.array([1+2j, 3+4j]) / np.sqrt(30), density_matrix=None)
    )

    print("--- Testing Serialization ---")

    # Serialize the state
    json_str = serialize_model(qc_state)
    print("Serialized QCState (first 200 chars):")
    print(json_str[:200] + "...")

    # Deserialize the state
    deserialized_state = deserialize_model(json_str, QCState)
    print("\nDeserialized QCState successfully.")
    print(f"Original energy: {qc_state.energy}, Deserialized energy: {deserialized_state.energy}")
    assert qc_state.energy == deserialized_state.energy

    # Because of the custom serialization, the deserialized object will have lists, not numpy arrays.
    # We need to convert the original to a list for a fair comparison.
    assert np.allclose(np.array(qc_state.quantum_state.state_vector), np.array(deserialized_state.quantum_state.state_vector))

    print("\n--- Testing File I/O ---")

    temp_file = Path("./temp_qc_state.json")

    # Save to file
    save_model_to_json(qc_state, temp_file)
    print(f"Saved state to {temp_file.resolve()}")
    assert temp_file.exists()

    # Load from file
    loaded_state = load_model_from_json(temp_file, QCState)
    print("Loaded state from file successfully.")
    assert loaded_state.id == qc_state.id

    # Clean up
    temp_file.unlink()
    print(f"Cleaned up {temp_file}.")
