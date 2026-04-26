def safe_close(sock):
    """
    Safely close a socket
    """
    try:
        sock.close()
    except Exception:
        pass


def safe_remove(mapping, key):
    """
    Remove key from dict safely
    """
    try:
        mapping.pop(key, None)
    except Exception:
        pass


def chunk_bytes(data: bytes, size: int):
    """
    Yield chunks of given size
    """
    for i in range(0, len(data), size):
        yield data[i:i + size]


def is_socket_closed(data):
    """
    Helper to check if recv() indicates closed connection
    """
    return not data