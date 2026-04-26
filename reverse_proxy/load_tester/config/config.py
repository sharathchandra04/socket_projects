class Config:
    def __init__(self):
        # Server (proxy / backend under test)
        self.server_host = "127.0.0.1"
        self.server_port = 9000

        # Load settings
        self.m_clients = 1000   # M concurrent clients per worker

        # Network tuning
        self.buffer_size = 4096
        self.connect_timeout = 5

        # Protocol limits
        self.max_payload_size = 10 * 1024 * 1024  # 10 MB

        # Debug / observability
        self.enable_logging = True