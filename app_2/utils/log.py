import logging
import os

def get_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Create and return a reusable logger with:
    - General log file
    - Error-only log file
    - Console output
    """

 
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
 
    base_name = name.replace(".", "_")

    if not log_file:
        log_file = f"{base_name}.log"

    error_log_file = f"{base_name}_error.log"

    log_path = os.path.join(LOG_DIR, log_file)
    error_log_path = os.path.join(LOG_DIR, error_log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

   
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
 
        error_handler = logging.FileHandler(error_log_path)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
 
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

    return logger