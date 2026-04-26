class BackendClientConnection:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.fd = sock.fileno()

        self.parser = None  # assigned later
        self.write_buffer = b""
        self.state = "READING"