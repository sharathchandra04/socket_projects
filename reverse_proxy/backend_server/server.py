import select
import socket

from core.event_loop import EventLoop
from core.fd_registry import FDRegistry

from backend.connection import BackendClientConnection
from backend.reader import handle_read
from backend.writer import handle_write

from protocol.request_parser import RequestParser
from protocol.serializer import Serializer


class BackendServer:

    def __init__(self, config):
        self.config = config

        self.event_loop = EventLoop()
        self.fd_registry = FDRegistry()

        self.serializer = Serializer()

        self.listen_sock = self._create_socket()

    # -----------------------------
    def _create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.backend_host, self.config.backend_port))
        sock.listen()
        sock.setblocking(False)
        return sock

    # -----------------------------
    def start(self):
        self.event_loop.register(
            self.listen_sock,
            self._accept_handler
        )

        while True:
            self.event_loop.poll()

    # -----------------------------
    def _accept_handler(self, fd, event):
        while True:
            try:
                client_sock, addr = self.listen_sock.accept()
                client_sock.setblocking(False)

                conn = BackendClientConnection(client_sock, addr)
                conn.parser = RequestParser()

                self.fd_registry.add(conn)

                self.event_loop.register(
                    client_sock,
                    self._read_handler
                )

            except BlockingIOError:
                break

    # -----------------------------
    def _read_handler(self, fd, event):
        conn = self.fd_registry.get(fd)
        handle_read(conn, self)

    # -----------------------------
    def _write_handler(self, fd, event):
        conn = self.fd_registry.get(fd)
        handle_write(conn, self)

    # -----------------------------
    def switch_to_write(self, conn):
        self.event_loop.modify(
            conn.sock,
            select.EPOLLOUT,
            self._write_handler
        )
        conn.state = "WRITING"

    # -----------------------------
    def close(self, conn):
        self.event_loop.unregister(conn.sock)
        self.fd_registry.remove(conn.fd)

        try:
            conn.sock.close()
        except Exception:
            pass