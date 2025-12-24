"""
Logging module for TimeGuard
Stores logs in ./logs/ directory next to the executable
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Determine the base directory (where exe or main.py is located)
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'timeguard.log')

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger('TimeGuard')
logger.setLevel(logging.DEBUG)

# File handler with rotation (5 MB max, keep 3 backups)
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=3,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Format: timestamp - level - message
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger():
    """Get the TimeGuard logger instance."""
    return logger

def log_info(message):
    """Log an info message."""
    logger.info(message)

def log_debug(message):
    """Log a debug message."""
    logger.debug(message)

def log_warning(message):
    """Log a warning message."""
    logger.warning(message)

def log_error(message):
    """Log an error message."""
    logger.error(message)

def log_blocked_key(key_combo):
    """Log a blocked key combination (debug level to avoid spam)."""
    logger.debug(f"Blocked: {key_combo}")

# Log startup
logger.info(f"={'='*50}")
logger.info(f"TimeGuard started")
logger.info(f"Log directory: {LOGS_DIR}")
