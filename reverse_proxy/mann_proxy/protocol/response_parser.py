from protocol.protocol_constants import (
    MAGIC, HEADER_SIZE, MAX_PAYLOAD_SIZE
)


class ResponseParser:

    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer = b""

    def parse(self, data):
        self.buffer += data

        if len(self.buffer) < HEADER_SIZE:
            return None

        magic = self.buffer[0:2]
        if magic != MAGIC:
            self.reset()
            return None

        length = int.from_bytes(self.buffer[4:8], byteorder="big")

        if length > MAX_PAYLOAD_SIZE:
            self.reset()
            return None

        total_size = HEADER_SIZE + length

        if len(self.buffer) < total_size:
            return None

        payload = self.buffer[HEADER_SIZE:total_size]

        self.buffer = self.buffer[total_size:]

        return payload