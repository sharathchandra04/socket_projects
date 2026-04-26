class ClientConn:

    def __init__(self, sock, parser):
        self.sock = sock
        self.fd = sock.fileno()

        # State: READING → WAIT_BACKEND → WRITING → CLOSED
        self.state = "READING"

        # Buffers
        self.read_buffer = b""
        self.write_buffer = b""

        # Parser (protocol-specific)
        self.parser = parser

        # Link to backend
        self.current_backend = None

    def reset(self):
        self.read_buffer = b""
        self.write_buffer = b""
        self.parser.reset()
        self.current_backend = None