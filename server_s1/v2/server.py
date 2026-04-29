# proxy_server.py
import socket
import select
from collections import deque

HOST = "127.0.0.1"
PORT = 9090

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 9091

MSG_SIZE = 10
POOL_SIZE = 10


def create_backend_conn():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(False)
    try:
        s.connect((BACKEND_HOST, BACKEND_PORT))
    except BlockingIOError:
        pass
    return s


def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(100)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    # frontend
    clients = {}
    client_buf = {}

    # backend
    backend_conns = {}
    backend_buf = {}
    backend_busy = {}
    backend_to_client = {}

    free_backends = deque()

    # 🔹 Initialize backend pool (NO EPOLLOUT HERE)
    for _ in range(POOL_SIZE):
        b = create_backend_conn()
        fd = b.fileno()

        backend_conns[fd] = b
        backend_buf[fd] = b""
        backend_busy[fd] = False

        free_backends.append(fd)

        # Only listen for reads initially
        epoll.register(fd, select.EPOLLIN | select.EPOLLET)
    print("backedn connection --> ", free_backends)
    try:
        while True:
            events = epoll.poll(1)

            for fileno, event in events:

                # 🔹 Accept client
                if fileno == server.fileno():
                    conn, _ = server.accept()
                    conn.setblocking(False)

                    fd = conn.fileno()
                    clients[fd] = conn
                    client_buf[fd] = b""
                    print("accept connection --> ", conn, fd)
                    epoll.register(fd, select.EPOLLIN | select.EPOLLET)

                # 🔹 Client READ
                elif fileno in clients and event & select.EPOLLIN:
                    conn = clients[fileno]

                    while True:
                        try:
                            data = conn.recv(1)
                            if not data:
                                raise Exception()

                            client_buf[fileno] += data
                            print("read data from client --> ", data)
                            if len(client_buf[fileno]) >= MSG_SIZE:
                                print("received full message")
                                msg = client_buf[fileno][:MSG_SIZE]

                                if not free_backends:
                                    cleanup_client(epoll, clients, client_buf, fileno)
                                    break
                                
                                # 🔹 assign backend
                                bfd = free_backends.popleft()
                                print("received free backend --> ", bfd)
                                backend_busy[bfd] = True
                                backend_to_client[bfd] = fileno

                                backend_buf[bfd] = msg

                                # ✅ NOW enable write
                                epoll.modify(bfd,
                                    select.EPOLLOUT | select.EPOLLET)
                                break

                        except BlockingIOError:
                            break
                        except Exception:
                            cleanup_client(epoll, clients, client_buf, fileno)
                            break

                # 🔹 Backend WRITE
                elif fileno in backend_conns and event & select.EPOLLOUT:
                    conn = backend_conns[fileno]
                    outb = backend_buf[fileno]

                    while outb:
                        try:
                            sent = conn.send(outb)
                            print("sent data to backend --> ", outb[:sent])
                            outb = outb[sent:]
                        except BlockingIOError:
                            break

                    backend_buf[fileno] = outb

                    if not outb:
                        # switch to read response
                        epoll.modify(fileno,
                            select.EPOLLIN | select.EPOLLET)

                # 🔹 Backend READ
                elif fileno in backend_conns and event & select.EPOLLIN:
                    conn = backend_conns[fileno]

                    while True:
                        try:
                            data = conn.recv(1)
                            if not data:
                                raise Exception()

                            backend_buf[fileno] += data
                            print("read data from backend--> ", data)
                            if len(backend_buf[fileno]) >= MSG_SIZE:
                                resp = backend_buf[fileno][:MSG_SIZE]
                                backend_buf[fileno] = b""

                                # send to client
                                cfd = backend_to_client[fileno]
                                client_buf[cfd] = resp

                                epoll.modify(cfd,
                                    select.EPOLLOUT | select.EPOLLET)

                                # free backend
                                backend_busy[fileno] = False
                                free_backends.append(fileno)
                                del backend_to_client[fileno]

                                break

                        except BlockingIOError:
                            break
                        except Exception:
                            break

                # 🔹 Client WRITE
                elif fileno in clients and event & select.EPOLLOUT:
                    conn = clients[fileno]
                    outb = client_buf[fileno]

                    while outb:
                        try:
                            sent = conn.send(outb)
                            print("write data to the client --> ", outb[:sent])
                            outb = outb[sent:]
                        except BlockingIOError:
                            break

                    client_buf[fileno] = outb

                    if not outb:
                        cleanup_client(epoll, clients, client_buf, fileno)

    finally:
        epoll.close()
        server.close()


def cleanup_client(epoll, clients, buffers, fd):
    print("clean up client connection ---> ", fd)
    print('\n\n############################\n\n')
    try:
        epoll.unregister(fd)
    except:
        pass
    try:
        clients[fd].close()
    except:
        pass
    clients.pop(fd, None)
    buffers.pop(fd, None)


if __name__ == "__main__":
    run()