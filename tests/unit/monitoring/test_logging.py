import logging
import pytest
from unittest.mock import patch

from monitoring.logging import setup_logging

def test_setup_logging_valid_level():
    """
    Tests that setup_logging configures the root logger with the correct level.
    """
    with patch('logging.basicConfig') as mock_basic_config:
        setup_logging("DEBUG")
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        assert kwargs['level'] == logging.DEBUG

def test_setup_logging_invalid_level():
    """
    Tests that setup_logging raises a ValueError for an invalid log level.
    """
    with pytest.raises(ValueError, match="Invalid log level: FAKELEVEL"):
        setup_logging("FAKELEVEL")

def test_setup_logging_default_level():
    """
    Tests that setup_logging uses INFO as the default level.
    """
    with patch('logging.basicConfig') as mock_basic_config:
        setup_logging()
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        assert kwargs['level'] == logging.INFO
