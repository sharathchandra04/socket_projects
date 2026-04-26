from enum import Enum


class ClientState(Enum):
    CONNECTING = "CONNECTING"
    WRITING = "WRITING"
    READING = "READING"
    DONE = "DONE"
    ERROR = "ERROR"