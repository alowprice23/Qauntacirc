import z3
from typing import List, Dict, Any, Optional

from core.exceptions import SMTSolvingError

class SMTConstraintSolver:
    """
    A constraint solver using the Z3 SMT solver.

    This solver can handle a variety of arithmetic and logical constraints.
    """
    def __init__(self):
        self.solver = z3.Solver()
        self.variables: Dict[str, Any] = {}

    def declare_variable(self, name: str, var_type: str = 'Int'):
        """
        Declares a variable for the SMT solver.
        Supported types: 'Int', 'Real', 'Bool'.
        If the variable already exists, this method does nothing.
        """
        if name in self.variables:
            return

        if var_type == 'Int':
            self.variables[name] = z3.Int(name)
        elif var_type == 'Real':
            self.variables[name] = z3.Real(name)
        elif var_type == 'Bool':
            self.variables[name] = z3.Bool(name)
        else:
            raise SMTSolvingError(f"Unsupported variable type: {var_type}")

    def add_constraint(self, constraint_str: str):
        """
        Adds a constraint to the solver from a string.
        Example: "x > 10", "y + z == 5"
        """
        try:
            # This is a simplified parser. A real implementation would need
            # a more robust parsing mechanism (e.g., using a parsing library).
            constraint = eval(constraint_str, {}, self.variables)
            self.solver.add(constraint)
        except Exception as e:
            raise SMTSolvingError(f"Failed to parse or add constraint: '{constraint_str}'. Error: {e}")

    def solve(self) -> Optional[Dict[str, Any]]:
        """
        Solves the current set of constraints.

        Returns:
            A dictionary with the variable assignments if a solution is found (sat).
            None if the constraints are unsatisfiable (unsat) or if the solver times out.
        """
        result = self.solver.check()

        if result == z3.sat:
            model = self.solver.model()
            solution = {}
            for var_name, var in self.variables.items():
                val = model.eval(var)
                if z3.is_int_value(val):
                    solution[var_name] = val.as_long()
                elif z3.is_real_value(val):
                    solution[var_name] = val.as_decimal(10)
                elif z3.is_bool_value(val):
                    solution[var_name] = bool(val)
                else:
                    solution[var_name] = str(val)
            return solution
        elif result == z3.unsat:
            return None
        else: # z3.unknown
            return None

    def check_property(self, property_str: str) -> bool:
        """
        Checks if a given property is entailed by the existing constraints.

        This is done by adding the negation of the property and checking for
        unsatisfiability.

        Returns:
            True if the property holds, False otherwise.
        """
        try:
            prop = eval(property_str, {}, self.variables)
        except Exception as e:
            raise SMTSolvingError(f"Failed to parse property: '{property_str}'. Error: {e}")

        self.solver.push()
        self.solver.add(z3.Not(prop))
        result = self.solver.check()
        self.solver.pop()

        return result == z3.unsat

# Example Usage:
if __name__ == '__main__':
    solver = SMTConstraintSolver()

    # Declare variables
    solver.declare_variable('x', 'Int')
    solver.declare_variable('y', 'Int')

    # Add constraints
    solver.add_constraint("x > 10")
    solver.add_constraint("y < 20")
    solver.add_constraint("x + y == 25")

    # Solve for a model
    solution = solver.solve()
    if solution:
        print(f"Solution found: {solution}")
    else:
        print("No solution found.")

    # Check a property
    property_holds = solver.check_property("x > 5")
    print(f"Is 'x > 5' guaranteed? {property_holds}") # Expected: True

    property_holds_2 = solver.check_property("y > 10")
    print(f"Is 'y > 10' guaranteed? {property_holds_2}") # Expected: False, because y could be e.g. 9 if x is 16