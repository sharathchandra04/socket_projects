import select


class EventLoop:
    def __init__(self, logger):
        self.epoll = select.epoll()
        self.handlers = {}
        self.logger = logger

    def register(self, sock, handler, eventmask=select.EPOLLIN):
        fd = sock.fileno()
        print("inside register of eventloop --> ", fd, eventmask)
        self.epoll.register(fd, eventmask)
        self.handlers[fd] = handler

    def modify(self, sock, eventmask, handler=None):
        fd = sock.fileno()
        self.epoll.modify(fd, eventmask)
        if handler:
            self.handlers[fd] = handler

    def unregister(self, sock):
        fd = sock.fileno()
        try:
            self.epoll.unregister(fd)
        except Exception:
            pass
        self.handlers.pop(fd, None)

    def poll(self, timeout=1):
        events = self.epoll.poll(timeout)
        print('events ---> ', events)
        for fd, event in events:
            handler = self.handlers.get(fd)

            if handler:
                try:
                    print("fd, handler --> ", fd, handler)
                    handler(fd, event)
                except Exception as e:
                    self.logger.error(f"Handler error fd={fd}: {e}")