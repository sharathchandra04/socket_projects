import socket
import errno

from observability.logger import get_logger


logger = get_logger(__name__)


# -----------------------------
# CLIENT WRITE
# -----------------------------
def handle_client_write(client_conn, worker):
    try:
        if client_conn.write_buffer:
            sent = client_conn.sock.send(client_conn.write_buffer)
            client_conn.write_buffer = client_conn.write_buffer[sent:]

        if not client_conn.write_buffer:
            # request complete → cleanup
            worker.request_manager.cleanup(client_conn)
            worker.close_connection(client_conn) # --------------------> last step close client connection .

    except socket.error as e:
        if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
            worker.close_connection(client_conn)


# -----------------------------
# BACKEND WRITE
# -----------------------------
def handle_backend_write(backend_conn, worker):
    try:
        if backend_conn.write_buffer:
            sent = backend_conn.sock.send(backend_conn.write_buffer)
            backend_conn.write_buffer = backend_conn.write_buffer[sent:]

        if not backend_conn.write_buffer:
            # switch to read response
            # worker.switch_to_read()
            worker.switch_to_read(backend_conn, is_backend=True)

    except socket.error as e:
        if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
            worker.backend_pool.discard(backend_conn)