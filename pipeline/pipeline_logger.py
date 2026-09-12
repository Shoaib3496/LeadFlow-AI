import logging
import os
from datetime import datetime


LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)


def get_pipeline_logger():

    today = datetime.now().strftime("%Y-%m-%d")

    log_file = os.path.join(
        LOG_DIR,
        f"pipeline_{today}.log"
    )

    logger = logging.getLogger("LeadFlowPipeline")

    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # -------------------------
    # File logging
    # -------------------------

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # -------------------------
    # Console logging
    # -------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger