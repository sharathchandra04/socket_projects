import errno


class Writer:
    def write(self, sock, buffer):
        """
        Attempts to send buffer.
        Returns remaining buffer (if partial send).
        """

        if not buffer:
            return b""

        try:
            sent = sock.send(buffer)
            return buffer[sent:]

        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return buffer  # try again later

            return b""  # treat as fatal failure