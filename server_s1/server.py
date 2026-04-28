# server.py
import socket
import select
from time import sleep

HOST = "127.0.0.1"
PORT = 9090
MSG_SIZE = 20

def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(10)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)
    print("server 1")

    conns = {}
    buffers = {}
    out_buffers = {}

    try:
        while True:
            print("server")
            events = epoll.poll(10)
            print("server: inside poll loop events: ", events)
            for fileno, event in events:
                print("server: inside the event loop")

                # Accept
                if fileno == server.fileno():
                    print("2. server :: inside the event loop :: accept connection")
                    conn, _ = server.accept()
                    conn.setblocking(False)

                    fd = conn.fileno()
                    conns[fd] = conn
                    buffers[fd] = b""
                    out_buffers[fd] = b""
                    print('###############')
                    print(fd)
                    print(buffers)
                    print(out_buffers)
                    print(conns)
                    print('###############')
                    epoll.register(fd, select.EPOLLIN | select.EPOLLET)

                # Read
                elif event & select.EPOLLIN:
                    print("3. server :: inside the event loop :: Read message")
                    conn = conns[fileno]

                    while True:
                        try:
                            data = conn.recv(2)
                            if not data:
                                print("3.1. inside the not data block while reading which means the conenction is closed")
                                raise Exception()

                            print("read data once --> ", data)
                            buffers[fileno] += data

                            # process exactly 1 message (10 bytes)
                            if len(buffers[fileno]) >= MSG_SIZE:
                                msg = buffers[fileno][:MSG_SIZE]
                                buffers[fileno] = buffers[fileno][MSG_SIZE:]

                                out_buffers[fileno] = msg

                                epoll.modify(fileno,
                                    select.EPOLLOUT | select.EPOLLET)
                                break

                        except BlockingIOError:
                            print("3.2 finished reading and got the blockingIoError")
                            break
                        except Exception:
                            print("3.3 got Exception while reading the messagge")                            
                            cleanup(epoll, conns, buffers, out_buffers, fileno)
                            break

                # Write
                elif event & select.EPOLLOUT:
                    print("4. after reading now write to the client back")
                    conn = conns[fileno]
                    outb = out_buffers[fileno]
                    print("4.1 outb before writing --> ", outb)
                    while outb:
                        try:
                            sent = conn.send(outb)
                            outb = outb[sent:]
                        except BlockingIOError:
                            print('BlockingIOError --> ')
                            break
                    
                    out_buffers[fileno] = outb
                    print("4.2 outb before reading --> ", outb)
                    if not outb:
                        print("4.3 cleaning the connection --> ", outb)
                        # close after one request-response
                        sleep(10)
                        cleanup(epoll, conns, buffers, out_buffers, fileno)

    finally:
        epoll.close()
        server.close()


def cleanup(epoll, conns, buffers, out_buffers, fd):
    try:
        epoll.unregister(fd)
    except:
        pass
    try:
        conns[fd].close()
    except:
        pass
    conns.pop(fd, None)
    buffers.pop(fd, None)
    out_buffers.pop(fd, None)


if __name__ == "__main__":
    run()