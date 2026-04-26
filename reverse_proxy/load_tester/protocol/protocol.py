# Simple custom TCP protocol

MAGIC_BYTES = b"PX"          # 2 bytes to identify protocol
HEADER_SIZE = 8              # fixed header size

# Header layout (fixed size):
# 2 bytes  magic
# 2 bytes  type
# 4 bytes  payload length (int)

MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# Message types
TYPE_PING = 1
TYPE_ECHO = 2
TYPE_SUM = 3
TYPE_RESPONSE = 100