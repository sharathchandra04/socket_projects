import errno


class Reader:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size

    def read(self, sock):
        """
        Returns:
            bytes data or None
        """
        try:
            data = sock.recv(self.buffer_size)

            if not data:
                return None  # connection closed

            return data

        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return b""  # no data available right now
            return None