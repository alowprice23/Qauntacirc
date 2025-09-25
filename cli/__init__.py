"""QuantaCirc CLI Package."""

import re
from pathlib import Path

# Read version from version.py without importing it
try:
    project_root = Path(__file__).resolve().parents[1]
    version_file = project_root / "version.py"
    with version_file.open("r") as f:
        version_content = f.read()
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", version_content, re.M)
    if version_match:
        __version__ = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")
except (FileNotFoundError, RuntimeError):
    __version__ = "0.0.0.dev0" # Fallback version

from .main import app as cli_app

__all__ = ["cli_app", "__version__"]
