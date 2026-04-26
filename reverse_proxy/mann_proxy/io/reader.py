import socket
import errno

from observability.logger import get_logger
from request.request_manager import RequestManager


logger = get_logger(__name__)


# -----------------------------
# CLIENT READ
# -----------------------------
def handle_client_read(client_conn, worker):
    try:
        data = client_conn.sock.recv(worker.config.read_buffer_size)

        if not data:
            worker.close_connection(client_conn)
            return

        # parse incoming data
        message = client_conn.parser.parse(data)

        if not message:
            return

        # Create request
        req = worker.request_manager.create_request(client_conn, message)

        # Acquire backend
        backend_conn = worker.backend_pool.acquire()

        if not backend_conn:
            worker.pending_queue.push(client_conn, message)
            return

        worker.request_manager.assign_backend(req, backend_conn)

        # Prepare backend write
        backend_conn.write_buffer = message

        worker.fd_registry.add(backend_conn)

        # this is the correct ussage
        # worker.event_loop.register_epollout(
        #     backend_conn.sock,
        #     worker._backend_write_handler
        # )
        worker.event_loop.register_epollout(
            backend_conn.sock,
            worker._backend_write_handler
        )

        client_conn.state = "WAIT_BACKEND"

    except socket.error as e:
        if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
            worker.close_connection(client_conn)


# -----------------------------
# BACKEND READ
# -----------------------------
def handle_backend_read(backend_conn, worker):
    try:
        data = backend_conn.sock.recv(worker.config.read_buffer_size)

        if not data:
            worker.backend_pool.discard(backend_conn)
            return

        response = backend_conn.parser.parse(data)

        if not response:
            return

        # Complete request
        req = worker.request_manager.complete_request(backend_conn, response)

        client_conn = req.client_conn

        # Switch client to write
        worker.switch_to_write(client_conn, is_backend=False)

        # Release backend
        worker.backend_pool.release(backend_conn)

        # Try to serve pending queue
        _drain_pending(worker)

    except socket.error:
        worker.backend_pool.discard(backend_conn)


# -----------------------------
# Pending queue drain
# -----------------------------
def _drain_pending(worker):
    while not worker.pending_queue.is_empty():
        backend_conn = worker.backend_pool.acquire()
        if not backend_conn:
            return

        client_conn, payload = worker.pending_queue.pop()

        req = worker.request_manager.create_request(client_conn, payload)
        worker.request_manager.assign_backend(req, backend_conn)

        backend_conn.write_buffer = payload

        worker.fd_registry.add(backend_conn)
        worker.event_loop.register(
            backend_conn.sock,
            worker._backend_write_handler
        )