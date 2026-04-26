class Request:

    def __init__(self, client_conn, payload):
        self.client_conn = client_conn
        self.backend_conn = None

        self.request_payload = payload
        self.response_payload = None

        # INIT → SENT → DONE
        self.state = "INIT"

    # -----------------------------
    def assign_backend(self, backend_conn):
        self.backend_conn = backend_conn
        self.state = "SENT"

    # -----------------------------
    def complete(self, response_payload):
        self.response_payload = response_payload
        self.state = "DONE"

    # -----------------------------
    def reset(self):
        self.backend_conn = None
        self.response_payload = None
        self.state = "INIT"