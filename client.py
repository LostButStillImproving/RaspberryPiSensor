import socket
import time

IP = "localhost"
PORT = 1234


def connect_to_server():
    while True:
        time.sleep(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((IP, PORT))
            msg_rec = s.recv(1024).decode("utf-8")
            print(msg_rec)

if __name__ == "__main__":
    connect_to_server()
