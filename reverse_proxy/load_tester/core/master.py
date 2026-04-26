from core.worker import Worker
from utils.logger import Logger


class Master:
    def __init__(self, config):
        self.config = config
        self.logger = Logger("MASTER", config.enable_logging)
        self.worker = None

    def start(self):
        self.logger.info("Starting load tester (N=1 worker)")

        self.worker = Worker(self.config)
        self.worker.start()

    def stop(self):
        self.logger.info("Stopping system")

        if self.worker:
            self.worker.stop()