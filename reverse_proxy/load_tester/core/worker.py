import select

from core.event_loop import EventLoop
from core.fd_registry import FDRegistry

from client.client_pool import ClientPool
from metrics.stats import Stats
from utils.logger import Logger


class Worker:
    def __init__(self, config):
        self.config = config

        self.logger = Logger("WORKER", config.enable_logging)

        self.event_loop = EventLoop(self.logger)
        self.fd_registry = FDRegistry()

        self.stats = Stats()

        self.client_pool = ClientPool(config, self)

        self.running = False

    # -----------------------------
    def start(self):
        self.logger.info(f"Starting worker with M={self.config.m_clients}")

        self.running = True

        # create clients
        self.client_pool.create_clients()

        # register all clients in epoll
        for conn in self.client_pool.clients:
            self.fd_registry.add(conn)

            self.event_loop.register(
                conn.sock,
                self._handle_event,
                select.EPOLLIN | select.EPOLLOUT
            )

        self._run_loop()

    # -----------------------------
    def _run_loop(self):
        while self.running:
            self.event_loop.poll(timeout=1)

    # -----------------------------
    def _handle_event(self, fd, event):
        conn = self.fd_registry.get(fd)

        if not conn:
            return

        # READ
        if event & select.EPOLLIN:
            conn.on_read(self)

        # WRITE
        if event & select.EPOLLOUT:
            conn.on_write(self)

    # -----------------------------
    def stop(self):
        self.logger.info("Stopping worker")
        self.running = False