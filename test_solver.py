import z3

print("--- Direct Z3 Proof Test ---")
s = z3.Solver()
s.set(proof=True)
a = z3.Bool('a')
s.add(a)
s.add(z3.Not(a))
result = s.check()
print("Check result:", result)
if result == z3.unsat:
    try:
        proof = s.proof()
        print("Proof generated successfully (direct test).")
    except z3.Z3Exception as e:
        print("Direct test failed to generate proof:", e)

print("\n--- Testing ConstraintSolver Wrapper ---")
from core.constraint_solver import ConstraintSolver

def main():
    print("--- Satisfiable Example ---")
    solver_sat = ConstraintSolver()
    solver_sat.add_variable('x', 'Int')
    solver_sat.add_variable('y', 'Int')
    x = solver_sat.get_variable('x')
    y = solver_sat.get_variable('y')
    solver_sat.add_constraint(x > 0)
    solver_sat.add_constraint(y > x)
    solver_sat.add_constraint(y < 5)
    result = solver_sat.check_satisfiability()
    print(f"Is satisfiable? {result.satisfiable}")
    if result.satisfiable:
        print(f"Model: {result.model}")

    print("\n--- Unsatisfiable Example with Proof ---")
    solver_unsat = ConstraintSolver(proof_generation=True)
    solver_unsat.add_variable('a', 'Bool')
    a = solver_unsat.get_variable('a')
    solver_unsat.add_constraint(a)
    solver_unsat.add_constraint(z3.Not(a))

    result_unsat = solver_unsat.check_satisfiability()
    print(f"Is satisfiable? {result_unsat.satisfiable}")

    if not result_unsat.satisfiable:
        proof = solver_unsat.generate_proof_certificate()
        if proof:
            print("Proof certificate generated successfully.")
        else:
            print("Failed to generate proof certificate.")

if __name__ == '__main__':
    main()
