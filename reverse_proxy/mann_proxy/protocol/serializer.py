from protocol.protocol_constants import MAGIC, VERSION


def serialize(msg_type, payload: bytes):
    length = len(payload)

    header = (
        MAGIC +
        bytes([VERSION]) +
        bytes([msg_type]) +
        length.to_bytes(4, byteorder="big")
    )

    return header + payload