from protocol.protocol_constants import (
    MAGIC, HEADER_SIZE, MAX_PAYLOAD_SIZE
)


class RequestParser:

    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer = b""
        self.expected_length = None

    def parse(self, data):
        self.buffer += data

        # Step 1: Need header
        if len(self.buffer) < HEADER_SIZE:
            return None

        # Step 2: Parse header
        magic = self.buffer[0:2]
        if magic != MAGIC:
            # simple strategy: drop buffer (can improve later with resync)
            self.reset()
            return None

        version = self.buffer[2]
        msg_type = self.buffer[3]
        length = int.from_bytes(self.buffer[4:8], byteorder="big")

        # Validate
        if length > MAX_PAYLOAD_SIZE:
            self.reset()
            return None

        total_size = HEADER_SIZE + length

        # Step 3: Wait for full payload
        if len(self.buffer) < total_size:
            return None

        payload = self.buffer[HEADER_SIZE:total_size]

        # Step 4: Consume buffer
        self.buffer = self.buffer[total_size:]

        return payload