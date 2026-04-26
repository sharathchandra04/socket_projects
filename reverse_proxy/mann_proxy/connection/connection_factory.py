from connection.client_connection import ClientConn
from connection.backend_connection import BackendConn

from protocol.request_parser import RequestParser
from protocol.response_parser import ResponseParser

from io.socket_utils import create_backend_socket


def create_client_connection(sock):
    parser = RequestParser()
    return ClientConn(sock, parser)


def create_backend_connection(host, port):
    sock = create_backend_socket(host, port)
    sock.setblocking(False)

    parser = ResponseParser()
    return BackendConn(sock, parser)