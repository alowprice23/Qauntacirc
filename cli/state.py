import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import git
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field

from core.types import QCState, SoftwareState, EnergyComponents

# --- Configuration for persistence ---
SESSION_DIR = Path.home() / ".quantacirc" / "sessions"
KEY_FILE = Path.home() / ".quantacirc" / "session.key"

# --- Helper functions for security ---

def get_or_create_key() -> bytes:
    """
    Retrieves the encryption key from the key file, or creates it if it doesn't exist.
    """
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    if not KEY_FILE.exists():
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
    else:
        key = KEY_FILE.read_bytes()
    return key

# --- Pydantic Models for State Structure ---

class HistoryItem(BaseModel):
    """
    Represents a single turn in the conversation history.
    """
    role: str  # "user" or "agent"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SessionState(BaseModel):
    """
    Manages the state of a conversational session, including history,
    permissions, and the core quantum system state.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    history: List[HistoryItem] = Field(default_factory=list)
    permissions: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict) # For git status, env vars, etc.

    qc_state: QCState = Field(default_factory=lambda: QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        energy=0.0,
        energy_components=EnergyComponents(static=0.0, dynamic=0.0, interaction=0.0),
        lyapunov_potential=0.0,
        contraction_factor=1.0,
    ))

    # --- Persistence and Security ---

    @classmethod
    def load(cls, session_id: str) -> "SessionState":
        """
        Loads a session from a cryptographically secured file.
        """
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        session_file = SESSION_DIR / f"{session_id}.session"
        if not session_file.exists():
            raise FileNotFoundError(f"Session with ID '{session_id}' not found.")

        key = get_or_create_key()
        fernet = Fernet(key)

        encrypted_data = session_file.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)

        data = json.loads(decrypted_data)

        instance = cls(**data)
        instance.last_accessed = datetime.utcnow()
        instance.save()
        return instance

    def save(self) -> None:
        """
        Saves the current session state to a cryptographically secured file.
        """
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        session_file = SESSION_DIR / f"{self.session_id}.session"

        self.last_accessed = datetime.utcnow()

        data_json = self.model_dump_json(indent=2)

        key = get_or_create_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data_json.encode('utf-8'))

        session_file.write_bytes(encrypted_data)

    def add_history(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Adds a new item to the conversation history.
        """
        self.history.append(HistoryItem(role=role, content=content, metadata=metadata or {}))

    def aggregate_context(self) -> None:
        """
        Aggregates context from the environment, such as git status and env vars.
        """
        context_data = {
            "environment": {},
            "git": {}
        }

        # 1. Aggregate environment variables
        relevant_vars = ["USER", "PWD", "HOME"]
        for var in relevant_vars:
            if var in os.environ:
                context_data["environment"][var] = os.environ[var]

        # Add any custom QUANTA_ vars
        for key, value in os.environ.items():
            if key.startswith("QUANTA_"):
                context_data["environment"][key] = value

        # 2. Aggregate git repository information
        try:
            repo = git.Repo(search_parent_directories=True)
            context_data["git"]["active_branch"] = repo.active_branch.name
            context_data["git"]["is_dirty"] = repo.is_dirty()
            context_data["git"]["head_commit"] = repo.head.commit.hexsha

            # Get untracked files
            untracked_files = repo.untracked_files
            if untracked_files:
                 context_data["git"]["untracked_files"] = untracked_files[:10] # Limit to 10

        except git.InvalidGitRepositoryError:
            context_data["git"]["error"] = "Not a git repository."
        except Exception as e:
            context_data["git"]["error"] = f"An error occurred: {str(e)}"

        self.context = context_data

    def resolve_obligation(self, obligation_id: str) -> bool:
        """
        Moves an obligation from the open to the completed list.
        Returns True if the obligation was found and moved, False otherwise.
        """
        if obligation_id in self.qc_state.open_obligations:
            self.qc_state.open_obligations.remove(obligation_id)
            self.qc_state.completed_obligations.append(obligation_id)
            return True
        return False
