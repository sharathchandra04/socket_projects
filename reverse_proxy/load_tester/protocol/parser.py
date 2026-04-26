import struct
import json
from protocol.protocol import (
    MAGIC_BYTES,
    HEADER_SIZE,
    TYPE_RESPONSE,
)


class Parser:
    def __init__(self):
        self.buffer = b""

    # -----------------------------
    def feed(self, data: bytes):
        """
        Add incoming bytes
        """
        self.buffer += data

    # -----------------------------
    def parse(self):
        """
        Returns:
            list of complete messages
        """

        messages = []

        while True:
            if len(self.buffer) < HEADER_SIZE:
                break

            magic, msg_type, length = struct.unpack(
                "!2sHI",
                self.buffer[:HEADER_SIZE]
            )

            if magic != MAGIC_BYTES:
                raise ValueError("Invalid protocol magic bytes")

            total_len = HEADER_SIZE + length

            if len(self.buffer) < total_len:
                break  # wait for more data

            payload = self.buffer[HEADER_SIZE:total_len]

            # remove consumed bytes
            self.buffer = self.buffer[total_len:]

            # decode payload
            try:
                decoded = json.loads(payload.decode())
            except Exception:
                decoded = payload

            messages.append({
                "type": msg_type,
                "data": decoded
            })

        return messages