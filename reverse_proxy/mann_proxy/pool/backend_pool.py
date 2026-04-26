from collections import deque

from connection.connection_factory import create_backend_connection
from observability.logger import get_logger


logger = get_logger(__name__)


class BackendPool:

    def __init__(self, config):
        self.host = config.backend_host
        self.port = config.backend_port

        self.max_size = config.backend_pool_size

        self.idle = deque()      # available connections
        self.busy = set()        # in-use connections

        self.current_size = 0

    # -----------------------------
    # Acquire connection
    # -----------------------------
    def acquire(self):
        # Reuse existing idle connection
        if self.idle:
            conn = self.idle.popleft()
            conn.state = "BUSY"
            self.busy.add(conn)
            return conn

        # Create new connection if under limit
        if self.current_size < self.max_size:
            conn = create_backend_connection(self.host, self.port)
            conn.state = "BUSY"

            self.busy.add(conn)
            self.current_size += 1

            return conn

        # Pool exhausted
        return None

    # -----------------------------
    # Release connection
    # -----------------------------
    def release(self, conn):
        if conn in self.busy:
            self.busy.remove(conn)

        conn.reset()

        self.idle.append(conn)

    # -----------------------------
    # Remove broken connection
    # -----------------------------
    def discard(self, conn):
        # Called when backend connection is dead
        if conn in self.busy:
            self.busy.remove(conn)

        try:
            self.idle.remove(conn)
        except ValueError:
            pass

        try:
            conn.sock.close()
        except Exception:
            pass

        self.current_size -= 1

        logger.warning("Backend connection discarded")