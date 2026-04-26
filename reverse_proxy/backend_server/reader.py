import errno
from backend.handlers import handle_request


def handle_read(conn, server):
    try:
        data = conn.sock.recv(server.config.read_buffer_size)

        if not data:
            server.close(conn)
            return

        response = conn.parser.parse(data)

        if not response:
            return

        # Process request
        resp_obj = handle_request(response)

        # Serialize response
        conn.write_buffer = server.serializer.serialize(resp_obj)

        # Switch to write
        server.switch_to_write(conn)

    except OSError as e:
        if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
            server.close(conn)