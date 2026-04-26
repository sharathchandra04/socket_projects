import struct
from protocol.protocol import (
    MAGIC_BYTES,
    HEADER_SIZE,
    TYPE_PING,
    TYPE_ECHO,
    TYPE_SUM,
)


class Serializer:

    def encode(self, msg_type, payload: bytes) -> bytes:
        """
        Frame format:
        [MAGIC][TYPE][LENGTH][PAYLOAD]
        """

        if len(payload) > (10 * 1024 * 1024):
            raise ValueError("Payload too large")

        header = struct.pack(
            "!2sHI",
            MAGIC_BYTES,
            msg_type,
            len(payload)
        )

        return header + payload

    # -----------------------------
    def encode_request(self, req: dict) -> bytes:
        import json

        msg_type = {
            "PING": TYPE_PING,
            "ECHO": TYPE_ECHO,
            "SUM": TYPE_SUM
        }[req["type"]]

        payload = json.dumps(req["data"]).encode()

        return self.encode(msg_type, payload)