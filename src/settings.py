import logging

# Basic settings
PATH = "C:\Programming\excel-xml"

# Logger settings
LOG_LEVEL = logging.DEBUG
FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

def get_logger(log_file_name: str) -> object:
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Create a custom format
    formatter = logging.Formatter(FORMAT)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file_name)
    c_handler.setLevel(LOG_LEVEL)
    f_handler.setLevel(LOG_LEVEL)

    # Create formatters and add it to handlers
    c_handler.setLevelsetFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger