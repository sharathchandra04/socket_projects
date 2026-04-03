import socket
import selectors

sel = selectors.DefaultSelector()

BACKENDS = [
    ("127.0.0.1", 5000),
    ("127.0.0.1", 5001),
    ("127.0.0.1", 5002),
]

backend_index = 0

def get_next_backend():
    global backend_index
    backend = BACKENDS[backend_index]
    backend_index = (backend_index + 1) % len(BACKENDS)
    return backend


class Connection:
    def __init__(self, client_sock):
        self.client = client_sock
        self.backend = None
        self.client_buffer = b""
        self.backend_buffer = b""


def accept(sock):
    client, addr = sock.accept()
    print("Accepted:", addr)
    client.setblocking(False)

    conn = Connection(client)
    sel.register(client, selectors.EVENT_READ, data=("client", conn))


def handle_client_read(sock, conn):
    try:
        data = sock.recv(4096)
        if not data:
            close_connection(conn)
            return

        conn.client_buffer += data

        # First time: connect to backend
        if conn.backend is None:
            backend_host, backend_port = get_next_backend()
            backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend.setblocking(False)
            backend.connect_ex((backend_host, backend_port))

            conn.backend = backend
            sel.register(backend, selectors.EVENT_WRITE, data=("backend", conn))

    except Exception as e:
        print("Client read error:", e)
        close_connection(conn)


def handle_backend_write(sock, conn):
    try:
        # Send client request to backend
        if conn.client_buffer:
            sent = sock.send(conn.client_buffer)
            conn.client_buffer = conn.client_buffer[sent:]

        # Switch backend to read mode
        sel.modify(sock, selectors.EVENT_READ, data=("backend", conn))

    except Exception as e:
        print("Backend write error:", e)
        close_connection(conn)


def handle_backend_read(sock, conn):
    try:
        data = sock.recv(4096)
        if not data:
            close_connection(conn)
            return

        conn.backend_buffer += data
        sel.modify(conn.client, selectors.EVENT_WRITE, data=("client", conn))

    except Exception as e:
        print("Backend read error:", e)
        close_connection(conn)


def handle_client_write(sock, conn):
    try:
        if conn.backend_buffer:
            sent = sock.send(conn.backend_buffer)
            conn.backend_buffer = conn.backend_buffer[sent:]

        # Go back to reading backend
        sel.modify(sock, selectors.EVENT_READ, data=("client", conn))

    except Exception as e:
        print("Client write error:", e)
        close_connection(conn)


def close_connection(conn):
    print("Closing connection")
    try:
        sel.unregister(conn.client)
        conn.client.close()
    except:
        pass

    if conn.backend:
        try:
            sel.unregister(conn.backend)
            conn.backend.close()
        except:
            pass


def start_proxy(host="0.0.0.0", port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    server.setblocking(False)

    sel.register(server, selectors.EVENT_READ, data=None)

    print(f"Non-blocking proxy running on {host}:{port}")

    while True:
        events = sel.select()

        for key, mask in events:
            sock = key.fileobj
            data = key.data

            if data is None:
                accept(sock)
            else:
                role, conn = data

                if role == "client":
                    if mask & selectors.EVENT_READ:
                        handle_client_read(sock, conn)
                    if mask & selectors.EVENT_WRITE:
                        handle_client_write(sock, conn)

                elif role == "backend":
                    if mask & selectors.EVENT_READ:
                        handle_backend_read(sock, conn)
                    if mask & selectors.EVENT_WRITE:
                        handle_backend_write(sock, conn)


if __name__ == "__main__":
    start_proxy()