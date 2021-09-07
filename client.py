import socket
import time

IP = "192.168.1.118"
PORT = 1234

while True:
    time.sleep(1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))
        msgRec = s.recv(1024).decode("utf-8")
        print(msgRec)
