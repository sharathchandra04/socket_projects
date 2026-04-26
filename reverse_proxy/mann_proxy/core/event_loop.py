import select


class EventLoop:

    def __init__(self):
        self.epoll = select.epoll()
        self.handlers = {}  # fd → handler

    # -----------------------------
    def register(self, sock, handler):
        fd = sock.fileno()
        self.epoll.register(fd, select.EPOLLIN)
        self.handlers[fd] = handler

    def register_epollout(self, sock, handler):
        fd = sock.fileno()
        self.epoll.register(fd, select.EPOLLOUT)
        self.handlers[fd] = handler

    # -----------------------------
    def modify(self, sock, event_mask, handler):
        fd = sock.fileno()
        self.epoll.modify(fd, event_mask)
        self.handlers[fd] = handler

    # -----------------------------
    def unregister(self, sock):
        fd = sock.fileno()
        try:
            self.epoll.unregister(fd)
        except Exception:
            pass
        self.handlers.pop(fd, None)

    # -----------------------------
    def poll(self):
        events = self.epoll.poll(1)

        for fd, event in events:
            print('event --> ', event)
            handler = self.handlers.get(fd)
            if handler:
                handler(fd, event)

    # -----------------------------
    def close(self):
        self.epoll.close()