import yaml
from pathlib import Path
from typing import Optional
import logging

from .types import QuantaCircConfig
from .exceptions import QuantaCircError

log = logging.getLogger(__name__)

def load_config(config_path: Optional[Path] = None) -> QuantaCircConfig:
    """
    Loads configuration from a YAML file and merges it with defaults.

    Args:
        config_path: The path to the configuration file. If not provided,
                     it looks for 'quantacirc.yml' in the current directory.

    Returns:
        A QuantaCircConfig object.
    """
    if config_path is None:
        config_path = Path.cwd() / "quantacirc.yml"

    if not config_path.exists():
        log.warning(f"Configuration file not found at {config_path}. Using default settings.")
        return QuantaCircConfig()

    log.info(f"Loading configuration from {config_path}")
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        if not config_data:
            log.warning(f"Configuration file {config_path} is empty. Using default settings.")
            return QuantaCircConfig()

        return QuantaCircConfig.model_validate(config_data)

    except yaml.YAMLError as e:
        raise QuantaCircError(
            f"Error parsing YAML file at {config_path}: {e}",
            suggested_fix="Please check the YAML syntax of your configuration file."
        )
    except Exception as e:
        raise QuantaCircError(
            f"Failed to load or validate configuration from {config_path}: {e}",
            suggested_fix="Ensure the configuration file structure matches the required schema in core/types.py."
        )
