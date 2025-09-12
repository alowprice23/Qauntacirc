from typing import Dict, Any, List, Tuple
import re

from typing import Dict, Any, List, Tuple
import re

from core.types import TaskQuanta
from cli.state import SessionState

# --- Constants for mock physics calculations ---
# Planck's constant in a mock unit system
H_NU = 0.1
MAX_PLAN_ENERGY = 0.5 # Arbitrary threshold for the energy gate

class CommandRouter:
    """
    Processes natural language input through a physics-based transformation pipeline.
    Handles the CNL -> DSL -> Gallina -> Quantized Task pipeline.
    """

    def __init__(self):
        self.MAX_PLAN_ENERGY = MAX_PLAN_ENERGY

    def process_input(self, raw_input: str, session: SessionState) -> Dict[str, Any]:
        """
        Runs the full intent processing pipeline.
        """
        # 1. CNL Translation (simulated and now context-aware)
        cnl_translation = self._to_cnl(raw_input, session)

        # 2. Intent Extraction & DSL Generation
        dsl = self._extract_intent_to_dsl(raw_input)

        if not dsl:
            raise ValueError("Could not extract a valid intent from the input.")

        # 3. Gallina Generation (mocked)
        gallina_spec = self._generate_gallina(dsl)

        # 4. Task Quantization
        quanta, obligations = self._quantize_task(dsl, session)

        # 5. Energy-Guided Routing Gate
        plan_energy = sum(q.energy for q in quanta)
        print(f"[DEBUG] Checking energy {plan_energy} against threshold {self.MAX_PLAN_ENERGY}")
        if plan_energy > self.MAX_PLAN_ENERGY:
            raise ValueError(
                f"Proposed plan energy ({plan_energy:.2f}) exceeds threshold "
                f"({self.MAX_PLAN_ENERGY:.2f}). Please try a less complex command."
            )

        # 6. Δ-closure verification (simulated)
        # For now, we just return the obligations we generated.
        # A real system would have a loop to ensure all are met.

        # 6. Generate a canonical AST from the DSL
        canonical_ast = self._dsl_to_ast(dsl)

        return {
            "cnl_translation": cnl_translation,
            "dsl": dsl,
            "gallina_spec": gallina_spec,
            "task_quanta": quanta,
            "delta_closure_obligations": obligations,
            "canonical_ast": canonical_ast,
        }

    def _to_cnl(self, text: str, session: SessionState) -> str:
        """
        Translates raw text to a more structured Controlled Natural Language format.
        This is a simplified simulation that is now context-aware.
        """
        text = text.lower()
        lang_match = re.search(r'\b(python|typescript|go|rust)\b', text)
        project_type_match = re.search(r'\b(web api|cli|library|service)\b', text)
        action_match = re.search(r'\b(create|make|build|generate)\b', text)

        lang = lang_match.group(0) if lang_match else "unknown"
        p_type = project_type_match.group(0) if project_type_match else "unknown"
        action = action_match.group(0) if action_match else "unknown"

        # Use the git context
        git_context = session.context.get("git", {})
        branch = git_context.get("active_branch", "unknown-branch")
        is_dirty = git_context.get("is_dirty", False)

        dirty_status = "dirty" if is_dirty else "clean"

        return f"On git branch '{branch}' (status: {dirty_status}), it is asserted that the user wants to {action} a new software artifact. The artifact is of type '{p_type}' and is implemented in the language '{lang}'."

    def _extract_intent_to_dsl(self, text: str) -> Dict[str, Any]:
        """
        Parses text to extract a structured intent and converts it to a DSL.
        This is a simple pattern-matching implementation.
        """
        text = text.lower()
        if "create" in text and "project" in text:
            dsl = {"command": "create_project", "params": {}}

            lang_match = re.search(r'\b(python|typescript|go|rust)\b', text)
            if lang_match:
                dsl["params"]["language"] = lang_match.group(0)

            type_match = re.search(r'\b(web api|cli|library|service)\b', text)
            if type_match:
                dsl["params"]["type"] = type_match.group(0)

            return dsl
        return {}

    def _generate_gallina(self, dsl: Dict[str, Any]) -> str:
        """
        Generates a mock Coq/Gallina specification from the DSL.
        """
        if dsl.get("command") == "create_project":
            params = dsl.get("params", {})
            lang = params.get("language", "Python")
            p_type = params.get("type", "WebApp")

            # Capitalize for Gallina record names
            lang_record = lang.capitalize()
            type_record = p_type.replace(" ", "").capitalize()

            return f"""
(* Auto-generated Gallina Specification *)
Require Import String.

(* Define project properties *)
Record ProjectSpec : Type := {{
  language : string;
  project_type : string;
  has_readme : bool;
  has_license : bool;
}}.

(* Define the specific instance for this request *)
Definition MyProject : ProjectSpec := {{
  language := "{lang_record}";
  project_type := "{type_record}";
  has_readme := true;
  has_license := true;
}}.

(* Proof Obligation: Show that the generated project meets the spec *)
Theorem project_conforms_to_spec :
  (language MyProject = "{lang_record}") /\\
  (project_type MyProject = "{type_record}").
Proof.
  (* To be proven by the generation agent *)
Admitted.
"""
        return "(* Could not generate Gallina spec for the given DSL *)"

    def _quantize_task(self, dsl: Dict[str, Any], session: SessionState) -> Tuple[List[TaskQuanta], List[str]]:
        """
        Breaks a DSL task into discrete TaskQuanta with energy levels.
        It also registers the obligations in the session state.
        """
        quanta = []
        new_obligations = []

        if dsl.get("command") == "create_project":
            lang = dsl.get("params", {}).get("language", "python")

            # Create quanta for the project creation task
            quanta.append(TaskQuanta(
                id="init_dir",
                description="Initialize project directory structure",
                verification_criteria=["Directory created"],
                energy=1 * H_NU # Low energy task
            ))
            quanta.append(TaskQuanta(
                id="create_readme",
                description="Generate README.md file",
                dependencies=["init_dir"],
                verification_criteria=["README.md exists"],
                energy=1 * H_NU
            ))
            quanta.append(TaskQuanta(
                id="setup_build_tool",
                description=f"Configure build tool for {lang}",
                dependencies=["init_dir"],
                verification_criteria=["pyproject.toml or package.json exists"],
                energy=2 * H_NU # Higher energy
            ))
            quanta.append(TaskQuanta(
                id="add_hello_world",
                description="Add a 'hello world' entry point",
                dependencies=["setup_build_tool"],
                verification_criteria=["Main file compiles and runs"],
                energy=3 * H_NU # Highest energy
            ))

            # Create and register corresponding obligations
            for q in quanta:
                obligation = f"Verify task '{q.id}' ({q.description}) is complete."
                new_obligations.append(obligation)
                if obligation not in session.qc_state.open_obligations:
                    session.qc_state.open_obligations.append(obligation)

        return quanta, new_obligations

    def _dsl_to_ast(self, dsl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a Canonical AST from a DSL.
        The AST represents the proposed structure of the software artifact.
        """
        if dsl.get("command") != "create_project":
            return {"type": "unknown"}

        params = dsl.get("params", {})
        lang = params.get("language", "python")
        archetype = params.get("type", "library")

        ast = {
            "type": "project",
            "language": lang,
            "archetype": archetype,
            "files": [],
            "dependencies": [],
            "properties": {},
        }

        # Mock structure based on archetype
        if archetype == "web api" and lang == "python":
            ast["files"] = [
                {"name": "pyproject.toml", "size": 350, "type": "config"},
                {"name": "README.md", "size": 600, "type": "doc"},
                {"name": "src/main.py", "size": 1200, "type": "source", "imports": ["fastapi", "uvicorn"]},
                {"name": "src/test_main.py", "size": 900, "type": "test", "imports": ["fastapi.testclient"]},
            ]
            ast["dependencies"] = ["fastapi", "uvicorn", "pytest"]
        else: # Default for other project types
            ast["files"] = [
                {"name": "pyproject.toml", "size": 250, "type": "config"},
                {"name": "README.md", "size": 400, "type": "doc"},
                {"name": "src/lib.py", "size": 500, "type": "source", "imports": []},
            ]
            ast["dependencies"] = ["pytest"]

        ast["properties"] = {
            "num_files": len(ast["files"]),
            "num_source_files": len([f for f in ast["files"] if f["type"] == "source"]),
            "num_dependencies": len(ast["dependencies"]),
            "total_size_bytes": sum(f["size"] for f in ast["files"]),
        }

        return ast
