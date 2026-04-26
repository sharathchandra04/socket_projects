import os

from config.constants import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_NUM_WORKERS,
    DEFAULT_BACKEND_HOST,
    DEFAULT_BACKEND_PORT,
    DEFAULT_BACKEND_POOL_SIZE,
    READ_BUFFER_SIZE,
    DEFAULT_TIMEOUT,
)


class Config:

    def __init__(self):
        # -----------------------------
        # Server config
        # -----------------------------
        self.host = os.getenv("SERVER_HOST", DEFAULT_HOST)
        self.port = int(os.getenv("SERVER_PORT", DEFAULT_PORT))

        self.num_workers = int(
            os.getenv("NUM_WORKERS", DEFAULT_NUM_WORKERS)
        )

        # -----------------------------
        # Backend config
        # -----------------------------
        self.backend_host = os.getenv(
            "BACKEND_HOST", DEFAULT_BACKEND_HOST
        )

        self.backend_port = int(
            os.getenv("BACKEND_PORT", DEFAULT_BACKEND_PORT)
        )

        self.backend_pool_size = int(
            os.getenv("BACKEND_POOL_SIZE", DEFAULT_BACKEND_POOL_SIZE)
        )

        # -----------------------------
        # IO config
        # -----------------------------
        self.read_buffer_size = int(
            os.getenv("READ_BUFFER_SIZE", READ_BUFFER_SIZE)
        )

        # -----------------------------
        # Timeout config
        # -----------------------------
        self.timeout = int(
            os.getenv("TIMEOUT", DEFAULT_TIMEOUT)
        )

    # -----------------------------
    def __repr__(self):
        return (
            f"<Config "
            f"{self.host}:{self.port} "
            f"workers={self.num_workers} "
            f"backend={self.backend_host}:{self.backend_port} "
            f"pool={self.backend_pool_size}>"
        )


# -----------------------------
# Loader
# -----------------------------
def load_config():
    return Config()