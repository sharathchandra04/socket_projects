import socket
import threading
import signal
import sys
# Backend servers (host, port)
BACKENDS = [
    ("127.0.0.1", 5000),
    ("127.0.0.1", 5001),
    ("127.0.0.1", 5002),
]

backend_index = 0
lock = threading.Lock()
# Global server socket
server_socket = None
running = True

def signal_handler(sig, frame):
    global running, server_socket
    print("\nSignal received, shutting down...")
    running = False
    if server_socket:
        server_socket.close()
    sys.exit(0)


def get_next_backend():
    global backend_index
    with lock:
        backend = BACKENDS[backend_index]
        backend_index = (backend_index + 1) % len(BACKENDS)
    return backend

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def handle_client(client_socket, thread_count):
    print(f"thread-{thread_count} start ")
    try:
        # Receive request from client
        request = b""
        while True:
            chunk = client_socket.recv(4096)
            request += chunk
            if len(chunk) < 4096:
                break
        print("request --> ", request)
        if not request:
            client_socket.close()
            return

        backend_host, backend_port = get_next_backend()
        print(f"Forwarding to {backend_host}:{backend_port}")

        # Connect to backend
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect((backend_host, backend_port))

        # Send request to backend
        backend_socket.sendall(request)

        # Receive response from backend and send back to client
        print(' --- before response ---')
        while True:
            response = backend_socket.recv(4096)
            print('response --> ', response)
            if not response:
                break
            client_socket.sendall(response)
        print(' --- after response ---')
        backend_socket.close()
        client_socket.close()
        print("thread end")
    except Exception as e:
        print("Error:", e)
        client_socket.close()


def start_proxy(host="0.0.0.0", port=8080):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(100)
    server_socket.settimeout(1)
    print(f"Reverse proxy running on {host}:{port}")
    thread_count = 0
    while running:
        try:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,thread_count)).start()
            thread_count = thread_count + 1
        except socket.timeout:
            continue  # loop back and check running flag
        except OSError:
            break  # socket closed

    # while running:
    #     client_socket, addr = server_socket.accept()
    #     print(f"Connection from {addr}")
    #
    #     thread = threading.Thread(target=handle_client, args=(client_socket,))
    #     thread.start()


if __name__ == "__main__":
    start_proxy()