class ServerError(Exception):
    """Base class for all server errors."""
    pass


# -----------------------------
# Connection errors
# -----------------------------
class ConnectionClosedError(ServerError):
    pass


class ConnectionResetError(ServerError):
    pass


# -----------------------------
# Protocol errors
# -----------------------------
class ProtocolError(ServerError):
    pass


class InvalidMagicError(ProtocolError):
    pass


class MessageTooLargeError(ProtocolError):
    pass


# -----------------------------
# Backend errors
# -----------------------------
class BackendUnavailableError(ServerError):
    pass


class BackendConnectionError(ServerError):
    pass


# -----------------------------
# Timeout errors
# -----------------------------
class TimeoutError(ServerError):
    pass