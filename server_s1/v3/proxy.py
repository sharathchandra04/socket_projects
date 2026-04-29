# proxy_server.py
import socket
import select
from collections import deque

HOST = "127.0.0.1"
PORT = 9090

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 9091

POOL_SIZE = 10


def encode_msg(data):
    return len(data).to_bytes(4, "big") + data


def try_parse(buf):
    if len(buf) < 4:
        return None, buf
    length = int.from_bytes(buf[:4], "big")
    if len(buf) < 4 + length:
        return None, buf
    msg = buf[4:4+length]
    return msg, buf[4+length:]


def create_backend():
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect((BACKEND_HOST, BACKEND_PORT))
    except BlockingIOError:
        pass
    return s


def run():
    server = socket.socket()
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(100)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    clients, cin, cout = {}, {}, {}
    backends, binb, bout = {}, {}, {}
    free = deque()
    b2c = {}

    # pool
    for _ in range(POOL_SIZE):
        b = create_backend()
        fd = b.fileno()
        backends[fd] = b
        binb[fd] = b""
        bout[fd] = b""
        free.append(fd)
        epoll.register(fd, select.EPOLLIN | select.EPOLLET)

    while True:
        for fd, ev in epoll.poll(1):

            if fd == server.fileno():
                c, _ = server.accept()
                c.setblocking(False)
                clients[c.fileno()] = c
                cin[c.fileno()] = b""
                cout[c.fileno()] = b""
                epoll.register(c.fileno(), select.EPOLLIN | select.EPOLLET)

            elif fd in clients and ev & select.EPOLLIN:
                c = clients[fd]
                while True:
                    try:
                        data = c.recv(1024)
                        if not data:
                            raise Exception()
                        cin[fd] += data

                        msg, cin[fd] = try_parse(cin[fd])
                        if msg:
                            bfd = free.popleft()
                            b2c[bfd] = fd
                            bout[bfd] = encode_msg(msg)
                            epoll.modify(bfd, select.EPOLLOUT | select.EPOLLET)
                            break

                    except BlockingIOError:
                        break
                    except:
                        c.close()
                        break

            elif fd in backends and ev & select.EPOLLOUT:
                b = backends[fd]
                while bout[fd]:
                    try:
                        sent = b.send(bout[fd])
                        bout[fd] = bout[fd][sent:]
                    except BlockingIOError:
                        break

                if not bout[fd]:
                    epoll.modify(fd, select.EPOLLIN | select.EPOLLET)

            elif fd in backends and ev & select.EPOLLIN:
                b = backends[fd]
                while True:
                    try:
                        data = b.recv(1024)
                        if not data:
                            raise Exception()
                        binb[fd] += data

                        msg, binb[fd] = try_parse(binb[fd])
                        if msg:
                            cfd = b2c[fd]
                            cout[cfd] = encode_msg(msg)
                            epoll.modify(cfd, select.EPOLLOUT | select.EPOLLET)

                            free.append(fd)
                            del b2c[fd]
                            break

                    except BlockingIOError:
                        break

            elif fd in clients and ev & select.EPOLLOUT:
                c = clients[fd]
                while cout[fd]:
                    try:
                        sent = c.send(cout[fd])
                        cout[fd] = cout[fd][sent:]
                    except BlockingIOError:
                        break

                if not cout[fd]:
                    epoll.unregister(fd)
                    c.close()


if __name__ == "__main__":
    run()