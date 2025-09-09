# tests/unit/config/test_config.py
import os
import pytest
from config import ConfigLoader
from core.types import QuantaCircConfig

def test_successful_load(tmp_path):
    """Tests that a valid configuration file is loaded correctly."""
    config_content = """
project:
  name: "Test Project"
  version: "1.0.0"
"""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)

    loader = ConfigLoader()
    config = loader.load_config(str(config_file))

    assert isinstance(config, QuantaCircConfig)
    assert config.project.name == "Test Project"
    assert config.project.version == "1.0.0"

def test_env_var_substitution(tmp_path):
    """Tests that environment variables are correctly substituted."""
    os.environ["TEST_VERSION"] = "2.0.0-beta"
    config_content = """
project:
  name: "Env Var Test"
  version: "${TEST_VERSION}"
"""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)

    loader = ConfigLoader()
    config = loader.load_config(str(config_file))

    assert config.project.version == "2.0.0-beta"
    del os.environ["TEST_VERSION"]

def test_hierarchical_merge(tmp_path):
    """Tests that configurations are merged correctly."""
    base_config_content = """
project:
  name: "Base Project"
  version: "1.0.0"
execution:
  default_mode: "simulation"
"""
    dev_config_content = """
project:
  version: "1.1.0-dev"
"""
    base_file = tmp_path / "base.yml"
    base_file.write_text(base_config_content)
    dev_file = tmp_path / "dev.yml"
    dev_file.write_text(dev_config_content)

    loader = ConfigLoader()
    config = loader.load_config(str(base_file), str(dev_file))

    assert config.project.name == "Base Project"
    assert config.project.version == "1.1.0-dev"
    assert config.execution.default_mode == "simulation"

def test_validation_failure(tmp_path):
    """Tests that validation failure raises a ValueError."""
    invalid_config_content = """
project:
  name: "Incomplete Project"
"""
    config_file = tmp_path / "config.yml"
    config_file.write_text(invalid_config_content)

    loader = ConfigLoader()
    with pytest.raises(ValueError) as excinfo:
        loader.load_config(str(config_file))

    assert "Configuration validation failed" in str(excinfo.value)
    assert "'version' is a required property" in str(excinfo.value)

def test_missing_env_var_failure(tmp_path):
    """Tests that a missing environment variable raises a ValueError."""
    config_content = """
project:
  name: "Missing Var Test"
  version: "${MISSING_VAR}"
"""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)

    loader = ConfigLoader()
    with pytest.raises(ValueError) as excinfo:
        loader.load_config(str(config_file))

    assert "Environment variable 'MISSING_VAR' is not set" in str(excinfo.value)
