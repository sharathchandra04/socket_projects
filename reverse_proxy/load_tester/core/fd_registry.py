class FDRegistry:
    def __init__(self):
        self._fd_map = {}

    def add(self, conn):
        self._fd_map[conn.fd] = conn

    def get(self, fd):
        return self._fd_map.get(fd)

    def remove(self, fd):
        self._fd_map.pop(fd, None)