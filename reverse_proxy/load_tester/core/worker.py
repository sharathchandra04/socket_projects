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
        print("self.client_pool.clients --> ", len(self.client_pool.clients))
        for conn in self.client_pool.clients:
            self.fd_registry.add(conn)
            print("registreing event on connection --> ", select.EPOLLIN, select.EPOLLOUT, select.EPOLLIN | select.EPOLLOUT)
            self.event_loop.register(
                conn.sock,
                self._handle_event,
                select.EPOLLIN | select.EPOLLOUT
            )

        self._run_loop()

    # -----------------------------
    def _run_loop(self):
        while self.running:
            print(" $$$$$$$ self.event_loop.poll(timeout=10)")
            self.event_loop.poll(timeout=10)

    # -----------------------------
    def _handle_event(self, fd, event):
        conn = self.fd_registry.get(fd)
        print("inside handle event fd, event --> ", fd, event, conn)
        print("iswrite --> ", event, select.EPOLLOUT, event & select.EPOLLOUT)
        print("isread --> ", event, select.EPOLLIN, event & select.EPOLLIN)

        if not conn:
            return

        if event & (select.EPOLLERR | select.EPOLLHUP):
            # close connection
            print(" select.EPOLLERR | select.EPOLLHUP ")
            return
        # READ
        if event & select.EPOLLIN:
            print("now read it")
            conn.on_read(self)

        # WRITE
        if event & select.EPOLLOUT:
            print("now write it")
            conn.on_write(self)

    # -----------------------------
    def stop(self):
        self.logger.info("Stopping worker")
        self.running = False