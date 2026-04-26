import signal
import sys

from config.config import load_config
from observability.logger import get_logger
from core.master import Master


logger = get_logger(__name__)

master = None


def _handle_signal(signum, frame):
    global master
    logger.info(f"Signal received: {signum}")

    if master:
        master.shutdown()

    sys.exit(0)


def _setup_signals():
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)


def main():
    global master

    config = load_config()
    _setup_signals()

    logger.info("Starting server...")

    master = Master(config)
    master.start()


if __name__ == "__main__":
    main()