import logging
import os
from pathlib import Path

from src.config import PROJECT_ROOT


# ======================================================================
# LOGGING CONFIGURATION
# ======================================================================

LOGGER_NAME = "vehicle_inspection"

DEFAULT_LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()


# ======================================================================
# LOG DIRECTORY
# ======================================================================

LOGS_DIR = (
    Path(PROJECT_ROOT)
    / "logs"
)

LOG_FILE = (
    LOGS_DIR
    / "inspection.log"
)


# ======================================================================
# LOG FORMAT
# ======================================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


# ======================================================================
# LOGGING SETUP
# ======================================================================

def setup_logging():
    """
    Configure and return the application logger.

    Logging is configured using the project-level configuration
    from src.config.

    Returns:
        logging.Logger:
            Configured vehicle inspection logger.
    """

    # --------------------------------------------------------------
    # Ensure log directory exists
    # --------------------------------------------------------------

    LOGS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------------
    # Resolve log level
    # --------------------------------------------------------------

    log_level = getattr(
        logging,
        DEFAULT_LOG_LEVEL,
        logging.INFO,
    )

    # --------------------------------------------------------------
    # Get application logger
    # --------------------------------------------------------------

    logger = logging.getLogger(
        LOGGER_NAME
    )

    logger.setLevel(
        log_level
    )

    logger.propagate = False

    # --------------------------------------------------------------
    # Prevent duplicate handlers
    # --------------------------------------------------------------

    if logger.handlers:
        return logger

    # --------------------------------------------------------------
    # Formatter
    # --------------------------------------------------------------

    formatter = logging.Formatter(
        LOG_FORMAT
    )

    # --------------------------------------------------------------
    # Console handler
    # --------------------------------------------------------------

    console_handler = (
        logging.StreamHandler()
    )

    console_handler.setLevel(
        log_level
    )

    console_handler.setFormatter(
        formatter
    )

    # --------------------------------------------------------------
    # File handler
    # --------------------------------------------------------------

    file_handler = (
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        )
    )

    file_handler.setLevel(
        log_level
    )

    file_handler.setFormatter(
        formatter
    )

    # --------------------------------------------------------------
    # Register handlers
    # --------------------------------------------------------------

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )

    logger.info(
        "Vehicle Inspection logging initialized."
    )

    logger.info(
        "Log file: %s",
        LOG_FILE,
    )

    return logger


# ======================================================================
# CONVENIENCE ACCESSOR
# ======================================================================

def get_logger():
    """
    Return the configured vehicle inspection logger.

    Returns:
        logging.Logger
    """

    return setup_logging()
