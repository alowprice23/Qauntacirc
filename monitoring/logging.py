import logging
import sys

def setup_logging(level: str = "INFO"):
    """
    Set up structured logging for the application.

    Args:
        level: The logging level to set (e.g., "INFO", "DEBUG").
    """
    level = level.upper()
    numeric_level = getattr(logging, level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger().setLevel(numeric_level)
    print(f"Logging configured with level {level}")
