import socket
import select
import errno


class ClientConnection:
    def __init__(self, server_host, server_port, generator):
        self.server_host = server_host
        self.server_port = server_port

        self.sock = self._create_socket()
        self.fd = self.sock.fileno()

        self.state = "CONNECTING"

        self.write_buffer = b""
        self.read_buffer = b""

        self.generator = generator
        self.response = None

    # -----------------------------
    def _create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

        try:
            sock.connect((self.server_host, self.server_port))
        except BlockingIOError:
            pass  # expected in non-blocking mode

        return sock

    # -----------------------------
    def on_read(self, worker):
        try:
            data = self.sock.recv(worker.config.buffer_size)

            if not data:
                self.close(worker)
                return

            self.read_buffer += data

            # try parse response
            if self._is_complete_response():
                self.response = self.read_buffer
                self.read_buffer = b""
                self.state = "DONE"

                worker.metrics.record_success()

                # close in simple model
                self.close(worker)

        except socket.error as e:
            if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                self.close(worker)

    # -----------------------------
    def on_write(self, worker):
        try:
            if self.state == "CONNECTING":
                self.state = "WRITING"
                self.write_buffer = self.generator.generate()

            if self.write_buffer:
                sent = self.sock.send(self.write_buffer)
                self.write_buffer = self.write_buffer[sent:]

            if not self.write_buffer:
                self.state = "READING"

        except socket.error as e:
            if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                self.close(worker)

    # -----------------------------
    def _is_complete_response(self):
        # SIMPLE PROTOCOL RULE:
        # assume newline-terminated response OR fixed format later
        return b"\n" in self.read_buffer

    # -----------------------------
    def close(self, worker):
        try:
            worker.event_loop.unregister(self.sock)
        except Exception:
            pass

        try:
            self.sock.close()
        except Exception:
            pass