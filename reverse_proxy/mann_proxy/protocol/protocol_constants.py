# Magic value to identify start of message
MAGIC = b'\xab\xcd'

# Header format:
# MAGIC (2 bytes) + VERSION (1 byte) + TYPE (1 byte) + LENGTH (4 bytes)
HEADER_SIZE = 8

VERSION = 1

# Message types
TYPE_REQUEST = 1
TYPE_RESPONSE = 2

# Limits
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB