import errno


def handle_write(conn, server):
    try:
        if conn.write_buffer:
            sent = conn.sock.send(conn.write_buffer)
            conn.write_buffer = conn.write_buffer[sent:]

        if not conn.write_buffer:
            # simple model → close after response
            server.close(conn)

    except OSError as e:
        if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
            server.close(conn)