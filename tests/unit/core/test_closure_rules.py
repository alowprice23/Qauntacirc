import pytest
from core.closure_rules import ClosureRuleEngine
from core.types import Requirement, Obligation, ObligationType, ObligationStatus

def test_closure_engine_derives_obligations():
    """
    Tests that the ClosureRuleEngine correctly derives new obligations
    based on matching rules against requirements.
    """
    engine = ClosureRuleEngine()

    requirements: set[Requirement] = {
        "The system must have secure user authentication required."
    }

    initial_obligations: set[Obligation] = {
        Obligation(
            id="ob1",
            description="Implement login endpoint.",
            type=ObligationType.FUNCTIONAL,
            status=ObligationStatus.OPEN,
            energy_impact=1.0
        )
    }

    result = engine.verify_closure(requirements, initial_obligations)

    assert result.is_closed, "The closure process should result in a closed set."
    assert result.derived_obligations > 0, "New obligations should have been derived."

    closed_set_descs = {ob.description for ob in result.closed_set}

    # Check that obligations from the 'auth_implies_authz' rule were added
    assert "authorization_system" in closed_set_descs
    assert "session_management" in closed_set_descs
    assert "access_control" in closed_set_descs

    # Check that the initial obligation is still there
    assert "Implement login endpoint." in closed_set_descs

def test_closure_engine_no_new_obligations():
    """
    Tests that the engine does not derive new obligations if no rules match.
    """
    engine = ClosureRuleEngine()

    requirements: set[Requirement] = {
        "The system should have a nice color scheme."
    }
    initial_obligations: set[Obligation] = set()

    result = engine.verify_closure(requirements, initial_obligations)

    assert result.is_closed
    assert result.derived_obligations == 0
    assert len(result.closed_set) == 0

def test_closure_idempotency():
    """
    Tests that running closure on an already closed set produces no new changes.
    """
    engine = ClosureRuleEngine()

    requirements: set[Requirement] = {
        "A secure payment gateway is needed."
    }
    initial_obligations: set[Obligation] = set()

    # First run
    result1 = engine.verify_closure(requirements, initial_obligations)
    assert result1.is_closed
    assert result1.derived_obligations > 0

    # Second run on the output of the first
    result2 = engine.verify_closure(requirements, result1.closed_set)
    assert result2.is_closed
    assert result2.derived_obligations == 0
    assert result1.closed_set == result2.closed_set
