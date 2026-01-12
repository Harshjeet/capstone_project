import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name="healthai", log_file="backend.log", level=logging.INFO):
    """
    Sets up a logger with both console and file handlers.
    """
    # Ensure logs directory exists if path is specified
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # File Handler (with rotation: 1MB per file, keep 5 files)
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # System/Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times if logger is already initialized
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger

# Create a default logger instance
logger = setup_logger()
    
