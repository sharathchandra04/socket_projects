import time


class TimeoutManager:
    """
    Tracks connection activity and closes stale connections.
    """

    def __init__(self, timeout_seconds=30):
        self.timeout = timeout_seconds

        # fd → last_active_timestamp
        self.last_active = {}

    # -----------------------------
    def register(self, conn):
        self.last_active[conn.fd] = time.time()

    # -----------------------------
    def update(self, conn):
        self.last_active[conn.fd] = time.time()

    # -----------------------------
    def unregister(self, conn):
        self.last_active.pop(conn.fd, None)

    # -----------------------------
    def get_expired(self):
        now = time.time()
        expired = []

        for fd, ts in list(self.last_active.items()):
            if now - ts > self.timeout:
                expired.append(fd)

        return expired