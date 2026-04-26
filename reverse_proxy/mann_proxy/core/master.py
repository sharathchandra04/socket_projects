import os
import signal
import time

from observability.logger import get_logger
from core.worker import Worker
from io.socket_utils import create_listening_socket


logger = get_logger(__name__)


class Master:

    def __init__(self, config):
        self.config = config
        self.workers = {}
        self.running = False
        self.listen_sock = None
    # -----------------------------
    def start(self):
        self.running = True
        logger.info(f"Master starting {self.config.num_workers} workers")

        self.listen_sock = create_listening_socket(
            self.config.host,
            self.config.port
        )
        self.listen_sock.setblocking(False)

        for wid in range(self.config.num_workers):
            self._spawn(wid)

        self._monitor()

    # -----------------------------
    def shutdown(self):
        logger.info("Master shutting down")
        self.running = False

        for pid in list(self.workers.keys()):
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

        while self.workers:
            pid, _ = os.wait()
            self.workers.pop(pid, None)

    # -----------------------------
    def _spawn(self, worker_id):
        pid = os.fork()

        if pid == 0:
            # Worker(worker_id, self.config).start()
            Worker(
                worker_id,
                self.config,
                self.listen_sock  # inherited fd
            ).start()
            os._exit(0)

        self.workers[pid] = worker_id
        logger.info(f"Spawned worker {worker_id} pid={pid}")

    # -----------------------------
    def _monitor(self):
        while self.running:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)

                if pid > 0:
                    wid = self.workers.pop(pid, None)
                    if wid is not None:
                        logger.warning(f"Worker {wid} died → respawning")
                        self._spawn(wid)

                time.sleep(1)

            except ChildProcessError:
                time.sleep(1)