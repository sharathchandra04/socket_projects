# server.py
import socket
import select

HOST = "127.0.0.1"
PORT = 9090
MSG_SIZE = 10

def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(10)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    conns = {}
    buffers = {}
    out_buffers = {}

    try:
        while True:
            events = epoll.poll(1)

            for fileno, event in events:

                # Accept
                if fileno == server.fileno():
                    conn, _ = server.accept()
                    conn.setblocking(False)

                    fd = conn.fileno()
                    conns[fd] = conn
                    buffers[fd] = b""
                    out_buffers[fd] = b""

                    epoll.register(fd, select.EPOLLIN | select.EPOLLET)

                # Read
                elif event & select.EPOLLIN:
                    conn = conns[fileno]

                    while True:
                        try:
                            data = conn.recv(1024)
                            if not data:
                                raise Exception()

                            buffers[fileno] += data

                            # process exactly 1 message (10 bytes)
                            if len(buffers[fileno]) >= MSG_SIZE:
                                msg = buffers[fileno][:MSG_SIZE]
                                buffers[fileno] = buffers[fileno][MSG_SIZE:]

                                out_buffers[fileno] = msg

                                epoll.modify(fileno,
                                    select.EPOLLOUT | select.EPOLLET)
                                break

                        except BlockingIOError:
                            break
                        except Exception:
                            cleanup(epoll, conns, buffers, out_buffers, fileno)
                            break

                # Write
                elif event & select.EPOLLOUT:
                    conn = conns[fileno]
                    outb = out_buffers[fileno]

                    while outb:
                        try:
                            sent = conn.send(outb)
                            outb = outb[sent:]
                        except BlockingIOError:
                            break

                    out_buffers[fileno] = outb

                    if not outb:
                        # close after one request-response
                        cleanup(epoll, conns, buffers, out_buffers, fileno)

    finally:
        epoll.close()
        server.close()


def cleanup(epoll, conns, buffers, out_buffers, fd):
    try:
        epoll.unregister(fd)
    except:
        pass
    try:
        conns[fd].close()
    except:
        pass
    conns.pop(fd, None)
    buffers.pop(fd, None)
    out_buffers.pop(fd, None)


if __name__ == "__main__":
    run()