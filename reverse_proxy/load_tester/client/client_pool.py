from client.client_connection import ClientConnection
from client.client_generator import ClientGenerator


class ClientPool:
    def __init__(self, config, worker):
        self.config = config
        self.worker = worker

        self.clients = []
        self.generator = ClientGenerator()

    # -----------------------------
    def create_clients(self):
        host = self.config.server_host
        port = self.config.server_port

        for _ in range(self.config.m_clients):
            conn = ClientConnection(host, port, self.generator)
            self.clients.append(conn)

    # -----------------------------
    def get_active_clients(self):
        return [c for c in self.clients if c.state != "DONE"]