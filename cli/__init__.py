import sys
from pathlib import Path

# HACK: Add project root to path to allow sibling imports.
# This is necessary because the project is not structured as a single
# installable package (e.g., with a 'src' layout). This allows
# modules like 'cli' to import from 'core', 'version', etc.
sys.path.insert(0, str(Path(__file__).parent.parent))

from version import __version__
from .main import app as cli_app

__all__ = ["cli_app", "__version__"]
