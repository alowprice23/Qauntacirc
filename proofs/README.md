# Formal Proof System

This directory contains the formal verification proofs for the core algorithms
of the QuantaCirc system. The purpose of this proof system is to provide
mathematical guarantees of correctness, stability, and convergence through
formal, machine-checkable verification.

## 1. Overview of the Proof System

Our formal verification strategy is built on a multi-modal approach, using
several state-of-the-art proof assistants and technologies to leverage the
unique strengths of each:

-   **Coq**: For expressive, constructive proofs of algorithmic correctness,
    convergence, and stability. Coq's Gallina language allows us to write
    theorems and proofs about complex data structures and properties.

-   **Agda**: For dependent type verification, particularly for ensuring the
    correctness of contracts, interfaces, and compositional systems. Agda's
    type system can capture deep properties of programs.

-   **SMT (Satisfiability Modulo Theories)**: For constraint solving and
    verification of properties that can be expressed in logical formulas. We use
    SMT solvers like Z3 to check for the satisfiability of system invariants
    and constraints.

## 2. Mathematical Foundations

The proofs in this directory provide formal guarantees for several key
mathematical foundations of the system:

-   **Annealing Convergence**: Proof that the simulated annealing algorithm
    converges to a global minimum energy state. See `coq/convergence.v`.

-   **Lyapunov Stability**: Formal analysis of system stability using Lyapunov's
    direct method, ensuring that the system remains in a stable state. See
    `coq/stability.v`.

-   **Energy Function Properties**: Proofs about the properties of the energy
    function, such as the Polyak-Łojasiewicz (PL) inequality, which guarantees
    linear convergence for gradient-based optimization. See `coq/energy.v`.

-   **Functor Correctness**: Proofs from category theory that the mappings between
    different system representations (e.g., software to quantum state) are
    structure-preserving. See `agda/functor.agda`.

-   **System Constraints**: Formalization of system-wide invariants and
    constraints that must hold for correct operation. See `smt/constraints.smt2`.

## 3. Proof Structure

The proofs are organized by proof system:

-   `coq/`: Contains all Coq proofs (`.v` files).
-   `agda/`: Contains all Agda proofs (`.agda` files).
-   `smt/`: Contains all SMT-LIB constraint files (`.smt2` files).
-   `certificates/`: Stores generated proof certificates and artifacts from
    the verification pipeline (currently a placeholder).
-   `validators.py`: The main script for running all proof validations.

## 4. Verification Procedures

To ensure the continuous validity of all formal proofs, we use an automated
verification script. This script invokes the command-line tools for each proof
system and checks that all proofs are still valid.

### Prerequisites

To run the validators, you must have the following tools installed and available
in your system's PATH:

-   `coqc` (the Coq compiler)
-   `agda` (the Agda type checker)
-   `z3` (the Z3 SMT solver)

### Running the Validators

You can run all proof checks by executing the `validators.py` script from the
root of the repository:

```bash
python3 proofs/validators.py
```

The script will automatically discover all proof files in this directory, run
the appropriate validator, and report a summary of the results. If any proof
fails, the script will exit with a non-zero status code, which can be used to
gate CI/CD pipelines.
