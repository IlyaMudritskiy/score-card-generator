import logging
from dataclasses import dataclass


@dataclass
class Settings:
    """Basic settings."""

    # How to generate report fields:
    # "standard" - for using in NSTM by hand (/Application/CDA[@CDAISACTIVE='Active']/CDAScore/CDAScoreParam[@CDASPNAME='{param}']/@CDASPVALUE)
    # "advanced" - for using in NSTM config file (\#Limit_min=/Application/CDA[@CDAISACTIVE='Active']/CDAScore/CDAScoreParam[@CDASPNAME='#Limit_min']/@CDASPVALUE;1;1;1;101)
    REPORT_FIELDS_TYPE: str = "standard"
    REPORT_LINE_START: str = 0
    SHEET_NAME: str = "Data"


settings = Settings()

# Logger settings
LOG_LEVEL = logging.DEBUG
FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

def get_logger(log_file_name: str) -> object:

    with open("log/other.log", "a"):
        pass

    filename = f"log/{log_file_name}"

    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Create a custom format
    formatter = logging.Formatter(FORMAT)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filename)
    c_handler.setLevel(LOG_LEVEL)
    f_handler.setLevel(LOG_LEVEL)

    # Create formatters and add it to handlers
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger