# backend_server.py
import socket
import select

HOST = "127.0.0.1"
PORT = 9091


def encode_msg(data):
    return len(data).to_bytes(4, "big") + data


def try_parse(buf):
    if len(buf) < 4:
        return None, buf
    length = int.from_bytes(buf[:4], "big")
    print("message length --> ", length) 
    if len(buf) < 4 + length:
        return None, buf
    msg = buf[4:4+length]
    return msg, buf[4+length:]


def run():
    server = socket.socket()
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(100)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    conns, inb, outb = {}, {}, {}

    while True:
        for fd, ev in epoll.poll(1):

            if fd == server.fileno():
                while True:
                    try:
                        c, _ = server.accept()
                        c.setblocking(False)
                        conns[c.fileno()] = c
                        inb[c.fileno()] = b""
                        outb[c.fileno()] = b""
                        epoll.register(c.fileno(), select.EPOLLIN | select.EPOLLET)
                    except BlockingIOError:
                        break

            elif ev & select.EPOLLIN:
                c = conns[fd]
                while True:
                    try:
                        data = c.recv(1)
                        if not data:
                            raise Exception()
                        inb[fd] += data

                        while True:
                            msg, inb[fd] = try_parse(inb[fd])
                            if not msg:
                                break
                            outb[fd] += encode_msg(msg)

                        if outb[fd]:
                            epoll.modify(fd, select.EPOLLOUT | select.EPOLLET)

                    except BlockingIOError:
                        break
                    except:
                        c.close()
                        epoll.unregister(fd)
                        break

            elif ev & select.EPOLLOUT:
                c = conns[fd]
                while outb[fd]:
                    try:
                        sent = c.send(outb[fd])
                        outb[fd] = outb[fd][sent:]
                    except BlockingIOError:
                        break

                if not outb[fd]:
                    epoll.modify(fd, select.EPOLLIN | select.EPOLLET)


if __name__ == "__main__":
    run()