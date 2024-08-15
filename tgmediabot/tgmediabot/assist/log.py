import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_logger(name=__name__):
    return logging.getLogger(name)
