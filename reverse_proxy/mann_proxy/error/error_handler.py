from observability.logger import get_logger

from error.exceptions import (
    ProtocolError,
    BackendConnectionError,
    BackendUnavailableError,
    TimeoutError,
)


logger = get_logger(__name__)


class ErrorHandler:

    def __init__(self, worker):
        self.worker = worker

    # -----------------------------
    def handle(self, conn, error):
        """
        Main entry point
        """

        if isinstance(error, ProtocolError):
            self._handle_protocol_error(conn, error)

        elif isinstance(error, BackendConnectionError):
            self._handle_backend_error(conn, error)

        elif isinstance(error, BackendUnavailableError):
            self._handle_backend_unavailable(conn)

        elif isinstance(error, TimeoutError):
            self._handle_timeout(conn)

        else:
            self._handle_generic(conn, error)

    # -----------------------------
    def _handle_protocol_error(self, conn, error):
        logger.warning(f"Protocol error on fd={conn.fd}: {error}")
        self.worker.close_connection(conn)

    # -----------------------------
    def _handle_backend_error(self, conn, error):
        logger.error(f"Backend error: {error}")

        # backend connection failure
        if hasattr(conn, "current_client") and conn.current_client:
            client_conn = conn.current_client
            self.worker.close_connection(client_conn)

        self.worker.backend_pool.discard(conn)

    # -----------------------------
    def _handle_backend_unavailable(self, conn):
        logger.warning("No backend available")

        # current design → just close client
        self.worker.close_connection(conn)

    # -----------------------------
    def _handle_timeout(self, conn):
        logger.warning(f"Timeout on fd={conn.fd}")
        self.worker.close_connection(conn)

    # -----------------------------
    def _handle_generic(self, conn, error):
        logger.exception(f"Unhandled error: {error}")
        self.worker.close_connection(conn)