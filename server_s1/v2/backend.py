# backend_server.py
import socket
import select

HOST = "127.0.0.1"
PORT = 9091
MSG_SIZE = 10


def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(100)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    conns = {}
    in_buf = {}
    out_buf = {}

    try:
        while True:
            events = epoll.poll(1)

            for fileno, event in events:

                # 🔹 Accept new backend connection
                if fileno == server.fileno():
                    while True:
                        try:
                            conn, _ = server.accept()
                            conn.setblocking(False)

                            fd = conn.fileno()
                            conns[fd] = conn
                            in_buf[fd] = b""
                            out_buf[fd] = b""

                            epoll.register(fd, select.EPOLLIN | select.EPOLLET)
                            print("accepted connection --> ", conn, fd)
                        except BlockingIOError:
                            break

                # 🔹 Read request
                elif event & select.EPOLLIN:
                    conn = conns[fileno]

                    while True:
                        try:
                            data = conn.recv(1)
                            if not data:
                                raise Exception()

                            in_buf[fileno] += data

                            # process complete messages (can be multiple)
                            print("received data --> ", data)
                            while len(in_buf[fileno]) >= MSG_SIZE:
                                msg = in_buf[fileno][:MSG_SIZE]
                                in_buf[fileno] = in_buf[fileno][MSG_SIZE:]

                                # echo → append to out buffer
                                out_buf[fileno] += msg

                            # if we have something to send → enable write
                            if out_buf[fileno]:
                                epoll.modify(fileno,
                                    select.EPOLLOUT | select.EPOLLET)

                        except BlockingIOError:
                            break
                        except Exception:
                            cleanup(epoll, conns, in_buf, out_buf, fileno)
                            break

                # 🔹 Write response
                elif event & select.EPOLLOUT:
                    conn = conns[fileno]
                    outb = out_buf[fileno]

                    while outb:
                        try:
                            sent = conn.send(outb)
                            print("sent data --> ", outb[:sent])
                            print('\n\n############################\n\n')
                            outb = outb[sent:]
                        except BlockingIOError:
                            break

                    out_buf[fileno] = outb

                    # once all sent → go back to read mode
                    if not outb:
                        epoll.modify(fileno,
                            select.EPOLLIN | select.EPOLLET)

    finally:
        epoll.close()
        server.close()


def cleanup(epoll, conns, in_buf, out_buf, fd):
    print('cleanup the proxy connection --> ', fd)
    try:
        epoll.unregister(fd)
    except:
        pass
    try:
        conns[fd].close()
    except:
        pass

    conns.pop(fd, None)
    in_buf.pop(fd, None)
    out_buf.pop(fd, None)


if __name__ == "__main__":
    run()