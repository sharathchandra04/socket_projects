import socket


def create_nonblocking_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    return sock


def safe_connect(sock, addr):
    try:
        sock.connect(addr)
    except BlockingIOError:
        pass  # expected for non-blocking connect


def safe_close(sock):
    try:
        sock.close()
    except Exception:
        pass