import socket

IP = "localhost"
PORT = 1234


def get_data():
    server_socket = connect_to_server()
    server_socket.connect((IP, PORT))
    server_socket.send(bytes("get", "utf-8"))
    msg_recv = server_socket.recv(1024).decode("utf-8")
    print(msg_recv)


def shutdown_server():
    server_socket = connect_to_server()
    server_socket.connect((IP, PORT))
    server_socket.send(bytes("shutdown", "utf-8"))


def set_sensor_interval(seconds):
    server_socket = connect_to_server()
    server_socket.connect((IP, PORT))
    server_socket.send(bytes(f"interval{seconds}", "utf-8"))


def connect_to_server():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


if __name__ == "__main__":
    set_sensor_interval(1)
    get_data()
    set_sensor_interval(5)
    get_data()
