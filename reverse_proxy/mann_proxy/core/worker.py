import signal

from observability.logger import get_logger
from core.event_loop import EventLoop
from core.fd_registry import FDRegistry

from pool.backend_pool import BackendPool
from pool.pending_queue import PendingQueue

from request.request_manager import RequestManager

from state.state_machine import StateMachine
from state.timeout_manager import TimeoutManager

from error.error_handler import ErrorHandler

from io.socket_utils import create_listening_socket


logger = get_logger(__name__)


class Worker:

    def __init__(self, worker_id, config, listen_sock):
        self.worker_id = worker_id
        self.config = config
        self.running = True

        # Core systems
        self.event_loop = EventLoop()
        self.fd_registry = FDRegistry()

        self.backend_pool = BackendPool(config)
        self.pending_queue = PendingQueue()

        self.request_manager = RequestManager()

        self.state_machine = StateMachine()
        self.timeout_manager = TimeoutManager(config.timeout)

        self.error_handler = ErrorHandler(self)

        # Socket
        # self.listen_sock = create_listening_socket(
        #     config.host, config.port
        # )
        self.listen_sock = listen_sock


    # -----------------------------
    def start(self):
        logger.info(f"Worker {self.worker_id} started")

        signal.signal(signal.SIGTERM, self._shutdown)

        self.event_loop.register(
            self.listen_sock,
            self._accept_handler
        )

        self._run()

    # -----------------------------
    def _run(self):
        while self.running:
            self.event_loop.poll()
            self._check_timeouts()

    # -----------------------------
    def _accept_handler(self, fd, event):
        from connection.connection_factory import create_client_connection

        while True:
            try:
                client_sock, _ = self.listen_sock.accept()
                client_sock.setblocking(False)

                conn = create_client_connection(client_sock)

                self.fd_registry.add(conn)
                self.timeout_manager.register(conn)

                self.event_loop.register(
                    client_sock,
                    self._client_read_handler
                )

            except BlockingIOError:
                break

    # -----------------------------
    def _client_read_handler(self, fd, event):
        from io.reader import handle_client_read

        conn = self.fd_registry.get(fd)
        handle_client_read(conn, self)

    # -----------------------------
    def _client_write_handler(self, fd, event):
        from io.writer import handle_client_write

        conn = self.fd_registry.get(fd)
        handle_client_write(conn, self)

    # -----------------------------
    def _backend_read_handler(self, fd, event):
        from io.reader import handle_backend_read

        conn = self.fd_registry.get(fd)
        handle_backend_read(conn, self)

    # -----------------------------
    def _backend_write_handler(self, fd, event):
        from io.writer import handle_backend_write

        conn = self.fd_registry.get(fd)
        handle_backend_write(conn, self)

    # -----------------------------
    def switch_to_read(self, conn, is_backend=False):
        import select

        if is_backend:
            handler = self._backend_read_handler
        else:
            handler = self._client_read_handler

        # 🔥 Change epoll interest to READ
        self.event_loop.modify(
            conn.sock,
            select.EPOLLIN,
            handler
        )

        # Optional but good
        conn.state = "READING"
    # -----------------------------

    def switch_to_write(self, conn, is_backend=False):
        import select

        if is_backend:
            handler = self._backend_write_handler
        else:
            handler = self._client_write_handler

        # 🔥 Enable write readiness notifications
        self.event_loop.modify(
            conn.sock,
            select.EPOLLOUT,
            handler
        )

        conn.state = "WRITING"

    def _check_timeouts(self):
        expired = self.timeout_manager.get_expired()

        for fd in expired:
            conn = self.fd_registry.get(fd)
            if conn:
                self.error_handler.handle(conn, Exception("Timeout"))

    # -----------------------------
    def close_connection(self, conn):
        self.event_loop.unregister(conn.sock)
        self.fd_registry.remove(conn.fd)

        try:
            conn.sock.close()
        except Exception:
            pass

    # -----------------------------
    def _shutdown(self, signum, frame):
        logger.info(f"Worker {self.worker_id} shutting down")
        self.running = False
        self.event_loop.close()