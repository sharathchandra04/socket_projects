from request.request import Request


class RequestManager:

    def __init__(self):
        # Since 1 request per client, simple mapping
        self.active_requests = {}   # client_fd → Request

    # -----------------------------
    # Create new request
    # -----------------------------
    def create_request(self, client_conn, payload):
        req = Request(client_conn, payload)

        self.active_requests[client_conn.fd] = req
        client_conn.current_request = req

        return req

    # -----------------------------
    # Assign backend
    # -----------------------------
    def assign_backend(self, req, backend_conn):
        req.assign_backend(backend_conn)

        backend_conn.current_client = req.client_conn
        req.client_conn.current_backend = backend_conn

    # -----------------------------
    # Complete request
    # -----------------------------
    def complete_request(self, backend_conn, response_payload):
        client_conn = backend_conn.current_client
        req = self.active_requests.get(client_conn.fd)

        if not req:
            return None

        req.complete(response_payload)

        # Attach response to client
        client_conn.write_buffer = response_payload
        client_conn.state = "WRITING"

        return req

    # -----------------------------
    # Cleanup request
    # -----------------------------
    def cleanup(self, client_conn):
        req = self.active_requests.pop(client_conn.fd, None)

        if not req:
            return

        # break links
        if req.backend_conn:
            req.backend_conn.current_client = None

        client_conn.current_request = None
        client_conn.current_backend = None