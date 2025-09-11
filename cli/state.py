import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

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
