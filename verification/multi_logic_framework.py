from formal_verification.coq_integration import CoqIntegration
from formal_verification.smt_integration import SMTIntegration
from formal_verification.uppaal_integration import UppaalIntegration
from formal_verification.prism_integration import PrismIntegration
import logging

logger = logging.getLogger(__name__)

class MultiLogicVerificationFramework:
    """
    Integrates multiple formal verification tools into a single framework.
    It orchestrates verification tasks by dispatching them to the appropriate tool
    based on the specified logic.
    """

    def __init__(self):
        """
        Initializes the framework and its supported verification tools.
        """
        self.verifiers = {
            "coq": CoqIntegration(),
            "smt": SMTIntegration(),
            "uppaal": UppaalIntegration(),
            "prism": PrismIntegration(),
        }
        logger.info("Multi-logic verification framework initialized.")

    def verify(self, logic: str, **kwargs) -> (bool, str):
        """
        Dispatches a verification task to the appropriate tool.

        Args:
            logic: The formal logic to be used ('coq', 'smt', 'uppaal', 'prism').
            **kwargs: A dictionary of arguments required by the specific tool.
                      - For 'coq': {'proof_file_path': str}
                      - For 'smt': {'smt_lib_file_path': str}
                      - For 'uppaal': {'model_path': str, 'query_path': str}
                      - For 'prism': {'model_file': str, 'properties_file': str}

        Returns:
            A tuple containing a boolean success status and a message from the tool.
            The meaning of 'success' depends on the tool:
            - Coq: Proof is valid.
            - SMT: Formula is unsatisfiable (proving a property by checking unsatisfiability of its negation).
            - UPPAAL: Property is satisfied.
            - PRISM: Property holds.
        """
        logic = logic.lower()
        if logic not in self.verifiers:
            raise ValueError(f"Unsupported logic: '{logic}'. Supported logics are {list(self.verifiers.keys())}.")

        logger.info(f"Dispatching verification task to {logic.upper()} solver.")

        try:
            if logic == "coq":
                return self.verifiers["coq"].verify_proof(**kwargs)
            elif logic == "smt":
                # For SMT, 'unsat' often means the property is proven (e.g., by checking the negation).
                status, output = self.verifiers["smt"].check_satisfiability(**kwargs)
                return status == "unsat", output
            elif logic == "uppaal":
                return self.verifiers["uppaal"].verify_model(**kwargs)
            elif logic == "prism":
                return self.verifiers["prism"].verify_model(**kwargs)
        except TypeError as e:
            logger.error(f"Incorrect arguments for {logic.upper()} verifier: {e}")
            raise ValueError(f"Missing or incorrect arguments for logic '{logic}'.") from e

        return False, "Logic type matched but no action was executed."
