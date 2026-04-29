# client.py
import socket
import select

HOST = "127.0.0.1"
PORT = 9090


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


def run():
    sock = socket.socket()
    sock.setblocking(False)

    try:
        sock.connect((HOST, PORT))
    except BlockingIOError:
        pass

    epoll = select.epoll()
    fd = sock.fileno()

    epoll.register(fd, select.EPOLLOUT | select.EPOLLET)

    outb = encode_msg(b"hello variable length world")
    print('outb --> ', outb)
    inb = b""

    while True:
        for f, ev in epoll.poll(1):

            if ev & select.EPOLLOUT:
                while outb:
                    try:
                        sent = sock.send(outb)
                        outb = outb[sent:]
                    except BlockingIOError:
                        break

                if not outb:
                    epoll.modify(fd, select.EPOLLIN | select.EPOLLET)

            elif ev & select.EPOLLIN:
                while True:
                    try:
                        data = sock.recv(1024)
                        if not data:
                            return
                        inb += data

                        msg, inb = try_parse(inb)
                        if msg:
                            print("Received:", msg.decode())
                            return

                    except BlockingIOError:
                        break


if __name__ == "__main__":
    run()