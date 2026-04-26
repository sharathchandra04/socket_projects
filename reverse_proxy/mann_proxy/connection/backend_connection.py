class BackendConn:

    def __init__(self, sock, parser):
        self.sock = sock
        self.fd = sock.fileno()

        # State: IDLE → BUSY
        self.state = "IDLE"

        # Buffers
        self.read_buffer = b""
        self.write_buffer = b""

        # Parser (same protocol or different if needed)
        self.parser = parser

        # Link to client
        self.current_client = None

    def reset(self):
        self.read_buffer = b""
        self.write_buffer = b""
        self.parser.reset()
        self.current_client = None
        self.state = "IDLE"