import logging
import os

# Define custom log levels for user and system messages.
USER_LEVEL_NUM = 25  # Above INFO, below WARNING
SYSTEM_LEVEL_NUM = 15  # Above DEBUG, below INFO

logging.addLevelName(USER_LEVEL_NUM, "USER")
logging.addLevelName(SYSTEM_LEVEL_NUM, "SYSTEM")


def log_user(self, message, *args, **kws):
    """Logs a message with level USER."""
    if self.isEnabledFor(USER_LEVEL_NUM):
        self._log(USER_LEVEL_NUM, message, args, **kws)


def log_system(self, message, *args, **kws):
    """Logs a message with level SYSTEM."""
    if self.isEnabledFor(SYSTEM_LEVEL_NUM):
        self._log(SYSTEM_LEVEL_NUM, message, args, **kws)


# Add the custom level methods to the Logger class.
logging.Logger.user = log_user
logging.Logger.system = log_system


def setup_logger(
    log_level_str: str = os.environ.get("A1FACTS_LOG_LEVEL", "1"),
    log_file: str = os.environ.get("A1FACTS_LOG_FILE", "a1facts.log"),
):
    """
    Configures and returns a logger instance.
    Log levels:
    - 0: No logs are recorded.
    - 1: Only user-level logs are recorded.
    - 2: System-level and user-level logs are recorded.
    """
    logger = logging.getLogger("a1facts")

    try:
        log_level = int(log_level_str)
    except ValueError:
        log_level = 1  # Default to user-level logs on invalid input.

    if log_level == 0:
        logger.setLevel(logging.CRITICAL + 1)
        handler = logging.NullHandler()
    else:
        if log_level == 1:
            logger.setLevel(USER_LEVEL_NUM)
        elif log_level >= 2:
            logger.setLevel(SYSTEM_LEVEL_NUM)
        else:
            logger.setLevel(USER_LEVEL_NUM)

        if not logger.handlers:
            handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    logger.propagate = False
    return logger


# Initialize and export a default logger instance.
logger = setup_logger()
