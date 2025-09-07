# core/edit_distance.py

"""
Provides utilities for computing the "edit distance" between system states.

This is not a geometric distance in the state space, but rather a measure
of how many discrete changes (e.g., version changes, config updates)
separate two classical software states.
"""

from __future__ import annotations

from core.types import SoftwareState, QCState

def software_state_edit_distance(state_a: SoftwareState, state_b: SoftwareState) -> int:
    """
    Computes the edit distance between two SoftwareState objects.

    The distance is defined as the number of differing items in their
    component versions and configuration hashes.

    Args:
        state_a: The first SoftwareState.
        state_b: The second SoftwareState.

    Returns:
        An integer representing the number of "edits" between the two states.
    """
    distance = 0

    # Compare component versions
    versions_a = state_a.component_versions
    versions_b = state_b.component_versions
    all_components = set(versions_a.keys()) | set(versions_b.keys())

    for comp in all_components:
        if versions_a.get(comp) != versions_b.get(comp):
            distance += 1

    # Compare config hashes
    hashes_a = state_a.config_hashes
    hashes_b = state_b.config_hashes
    all_configs = set(hashes_a.keys()) | set(hashes_b.keys())

    for conf in all_configs:
        if hashes_a.get(conf) != hashes_b.get(conf):
            distance += 1

    # Compare status
    if state_a.status != state_b.status:
        distance += 1

    return distance

def qcstate_edit_distance(state_a: QCState, state_b: QCState) -> int:
    """
    Computes the edit distance between the classical software parts of two QCStates.

    This is a convenience wrapper around `software_state_edit_distance`.

    Args:
        state_a: The first QCState.
        state_b: The second QCState.

    Returns:
        The edit distance between the two underlying software states.
    """
    return software_state_edit_distance(state_a.software_state, state_b.software_state)

# Example Usage
if __name__ == '__main__':
    state1 = SoftwareState(
        component_versions={"compA": "1.0", "compB": "2.0"},
        config_hashes={"conf1": "hashA", "conf2": "hashB"},
        status="nominal"
    )

    state2 = SoftwareState(
        component_versions={"compA": "1.1", "compB": "2.0"}, # 1 change
        config_hashes={"conf1": "hashA", "conf2": "hashC"}, # 1 change
        status="nominal"
    )

    state3 = SoftwareState(
        component_versions={"compA": "1.1", "compC": "3.0"}, # compB removed, compC added -> 2 changes
        config_hashes={"conf1": "hashA"}, # conf2 removed -> 1 change
        status="degraded" # 1 change
    )

    dist_1_2 = software_state_edit_distance(state1, state2)
    print(f"Edit distance between state 1 and state 2: {dist_1_2}") # Expected: 2
    assert dist_1_2 == 2

    dist_1_3 = software_state_edit_distance(state1, state3)
    print(f"Edit distance between state 1 and state 3: {dist_1_3}") # Expected: 4
    assert dist_1_3 == 4

    dist_2_3 = software_state_edit_distance(state2, state3)
    # compA: same, compB vs compC: 2, conf1: same, conf2 vs missing: 1, status: 1 -> 4
    print(f"Edit distance between state 2 and state 3: {dist_2_3}") # Expected: 4
    assert dist_2_3 == 4
