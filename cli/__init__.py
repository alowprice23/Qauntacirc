"""QuantaCirc CLI Package."""

from version import __version__
from .main import app as cli_app

__all__ = ["cli_app", "__version__"]
