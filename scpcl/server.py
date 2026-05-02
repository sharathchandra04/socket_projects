import socket
import select
import os

HOST = "0.0.0.0"
PORT = 9000
BASE_DIR = "./server_files"
os.makedirs(BASE_DIR, exist_ok=True)

CHUNK_SIZE = 64 * 1024
MAX_OUT_BUFFER = 1 * 1024 * 1024  # 1 MB safety


class Connection:
    def __init__(self, sock):
        self.sock = sock
        self.sock.setblocking(False)

        self.in_buffer = b""
        self.out_buffer = b""

        self.state = "READ_CMD"
        self.file = None


def safe_path(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.abspath(path).startswith(os.path.abspath(BASE_DIR)):
        return None
    return path


def handle_read(conn):
    try:
        data = conn.sock.recv(65536)
        if not data:
            return False  # client closed
        conn.in_buffer += data
    except BlockingIOError:
        # when willl we get BlockingIoError ?
        return True

    # Process command
    if conn.state == "READ_CMD":
        if b"\n" in conn.in_buffer:
            line, conn.in_buffer = conn.in_buffer.split(b"\n", 1)
            process_command(conn, line.decode().strip())

    return True


def process_command(conn, line):
    parts = line.split()

    if parts[0] == "GET" and len(parts) == 2:
        path = safe_path(parts[1])

        if not path or not os.path.exists(path):
            conn.out_buffer += b"ERR File not found\n"
            return

        size = os.path.getsize(path)
        conn.out_buffer += f"OK {size}\n".encode()

        conn.file = open(path, "rb")
        conn.state = "SEND_FILE"

    else:
        conn.out_buffer += b"ERR Invalid command\n"


def handle_write(conn):
    try:
        # First flush pending buffer
        if conn.out_buffer:
            sent = conn.sock.send(conn.out_buffer)
            conn.out_buffer = conn.out_buffer[sent:]

    except BlockingIOError:
        return True

    # If buffer empty, send file data
    if conn.state == "SEND_FILE" and not conn.out_buffer:
        chunk = conn.file.read(CHUNK_SIZE)

        if chunk:
            conn.out_buffer += chunk
        else:
            conn.file.close()
            conn.state = "READ_CMD"

    return True


def close_connection(epoll, fd, connections):
    conn = connections[fd]
    epoll.unregister(fd)
    conn.sock.close()
    if conn.file:
        conn.file.close()
    del connections[fd]


def run_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setblocking(False)
    server_sock.bind((HOST, PORT))
    server_sock.listen()

    epoll = select.epoll()
    epoll.register(server_sock.fileno(), select.EPOLLIN)

    connections = {}

    print(f"Server running on {HOST}:{PORT}")

    while True:
        events = epoll.poll(1)

        for fd, event in events:

            # 🔹 New connection
            if fd == server_sock.fileno():
                client_sock, addr = server_sock.accept()
                client_sock.setblocking(False)

                conn = Connection(client_sock)
                connections[client_sock.fileno()] = conn

                epoll.register(client_sock.fileno(), select.EPOLLIN)
                print("New client:", addr)

            # 🔹 Existing client
            else:
                conn = connections[fd]

                # READ event
                if event & select.EPOLLIN:
                    if not handle_read(conn): # close if returned false
                        close_connection(epoll, fd, connections)
                        continue

                # WRITE event
                if event & select.EPOLLOUT:
                    if not handle_write(conn):
                        close_connection(epoll, fd, connections)
                        continue

                # 🔥 Backpressure protection
                if len(conn.out_buffer) > MAX_OUT_BUFFER:
                    print("Client too slow, dropping")
                    close_connection(epoll, fd, connections)
                    continue

                # 🔥 Dynamic interest
                mask = select.EPOLLIN
                if conn.out_buffer or conn.state == "SEND_FILE":
                    mask |= select.EPOLLOUT

                epoll.modify(fd, mask)


if __name__ == "__main__":
    run_server()