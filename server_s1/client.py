# client.py
import socket
import select

HOST = "127.0.0.1"
PORT = 9090
MSG_SIZE = 20

def pad(msg: str) -> bytes:
    return msg.encode().ljust(MSG_SIZE, b'@')[:MSG_SIZE]

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)

    try:
        sock.connect((HOST, PORT))
    except BlockingIOError:
        pass

    epoll = select.epoll()
    fd = sock.fileno()

    epoll.register(fd, select.EPOLLOUT | select.EPOLLET)

    outb = pad("hello123")
    print(outb)
    inb = b""

    try:
        while True:
            events = epoll.poll(1)

            for fileno, event in events:
                print('event loop --> ', fileno, event)
                # Write
                if event & select.EPOLLOUT:
                    while outb:
                        try:
                            sent = sock.send(outb)
                            outb = outb[sent:]
                        except BlockingIOError:
                            break

                    if not outb:
                        epoll.modify(fd,
                            select.EPOLLIN | select.EPOLLET)

                # Read
                elif event & select.EPOLLIN:
                    while True:
                        print("inside while")
                        try:
                            # print("before sock recv")
                            data = sock.recv(1)
                            # print("ater sock recv")
                            print("data --> ", data)
                            if not data:
                                break
                            
                            inb += data

                            if len(inb) >= MSG_SIZE:
                                print("inside the close block")
                                msg = inb[:MSG_SIZE]
                                print("Received:", msg.decode().strip())

                                epoll.unregister(fd)
                                sock.close()
                                return

                        except BlockingIOError:
                            print("blocking IO Error")
                            break
                    print("loop break")

    finally:
        epoll.close()


if __name__ == "__main__":
    run()