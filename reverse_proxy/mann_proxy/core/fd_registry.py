class FDRegistry:

    def __init__(self):
        self.map = {}

    def add(self, conn):
        self.map[conn.fd] = conn

    def get(self, fd):
        return self.map.get(fd)

    def remove(self, fd):
        self.map.pop(fd, None)