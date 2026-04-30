import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
CHUNK_SIZE = 64 * 1024


def download_file(filename, save_as=None):
    if save_as is None:
        save_as = filename

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_HOST, SERVER_PORT))

    try:
        # 1️⃣ Send request
        s.sendall(f"GET {filename}\n".encode())

        # 2️⃣ Read response header (OK <size>\n)
        header = b""
        while not header.endswith(b"\n"):
            chunk = s.recv(1)
            if not chunk:
                raise Exception("Server closed connection")
            header += chunk

        header = header.decode().strip()
        print("Header:", header)

        if not header.startswith("OK"):
            print("Error from server:", header)
            return

        _, size = header.split()
        size = int(size)

        # 3️⃣ Receive file
        received = 0
        with open(save_as, "wb") as f:
            while received < size:
                data = s.recv(min(CHUNK_SIZE, size - received))
                if not data:
                    raise Exception("Connection lost during transfer")

                f.write(data)
                received += len(data)

        print(f"Downloaded {save_as} ({received} bytes)")

    finally:
        s.close()


if __name__ == "__main__":
    download_file("test.txt")