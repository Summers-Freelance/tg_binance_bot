import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Setup root logging as `RotatingFileHandler` with custom formater."""
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        "binance.log",
        mode="a",
        maxBytes=5 * 1024 * 1024,  # 5Mb
        # `backupCount` Will create two files when the main log file will exceed the maxBytes.
        # ex. `.log.1`, `.log.2`.
        backupCount=2,
        encoding="utf-8",
        delay=0,
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"),
    )
    logger.addHandler(handler)
    return logger
