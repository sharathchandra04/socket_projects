import logging
import sys


_LOGGER_INITIALIZED = False


def _setup_root_logger():
    global _LOGGER_INITIALIZED

    if _LOGGER_INITIALIZED:
        return

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    _LOGGER_INITIALIZED = True


def get_logger(name: str):
    _setup_root_logger()
    return logging.getLogger(name)