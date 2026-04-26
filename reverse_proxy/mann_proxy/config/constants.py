# -----------------------------
# Server defaults
# -----------------------------
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080

DEFAULT_NUM_WORKERS = 4


# -----------------------------
# Backend defaults
# -----------------------------
DEFAULT_BACKEND_HOST = "127.0.0.1"
DEFAULT_BACKEND_PORT = 9000

DEFAULT_BACKEND_POOL_SIZE = 10


# -----------------------------
# Buffer sizes
# -----------------------------
READ_BUFFER_SIZE = 4096
WRITE_BUFFER_SIZE = 4096


# -----------------------------
# Timeouts (seconds)
# -----------------------------
DEFAULT_TIMEOUT = 30


# -----------------------------
# State values (optional centralization)
# -----------------------------
CLIENT_STATES = {
    "READING",
    "WAIT_BACKEND",
    "WRITING",
    "CLOSED",
}

BACKEND_STATES = {
    "IDLE",
    "BUSY",
    "CLOSED",
}