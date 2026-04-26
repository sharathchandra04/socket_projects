from collections import deque


class PendingQueue:

    def __init__(self):
        self.queue = deque()

    # -----------------------------
    # Add request
    # -----------------------------
    def push(self, client_conn, payload):
        self.queue.append((client_conn, payload))

    # -----------------------------
    # Get next request
    # -----------------------------
    def pop(self):
        if self.queue:
            return self.queue.popleft()
        return None

    # -----------------------------
    # Check if empty
    # -----------------------------
    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)