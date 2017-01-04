import logging
from os import path

def get_logger(log_name, log_folder=None):
    if not log_folder:
        log_folder = path.dirname(path.abspath(__file__))

    logger = logging.getLogger(log_name)

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")

    log_file = path.join(log_folder, log_name + '.log')
    print log_file
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
