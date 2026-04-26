import socket


def create_listening_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen()

    return sock


def create_backend_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))   # blocking connect (acceptable for now)
    return sock