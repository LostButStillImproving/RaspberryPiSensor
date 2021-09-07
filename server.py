import random
import socket
import datetime
import json
import time

from _thread import start_new_thread
import client

SENSOR_INTERVAL = 1
IP = "localhost"
PORT = 1234

temp = 5
humidity = 0
time_of_measurement = datetime.datetime.utcnow().strftime("%H:%M:%S")
location = "Home"

data = {"time": time_of_measurement,
        "location": location,
        "temperature": temp,
        "humidity": humidity}


def get_time():
    return datetime.datetime.utcnow().strftime("%H:%M:%S")


def get_temperature():
    return random.randint(1, 10)


def get_humidity():
    return random.randint(1, 100)


def record_data():
    global time_of_measurement
    global temp
    global humidity
    while True:
        time.sleep(SENSOR_INTERVAL)
        data["time"] = get_time()
        data["temperature"] = get_temperature()
        data["humidity"] = get_humidity()
        temp = get_temperature()
        humidity = get_humidity()


def handle_connection(client_socket):
    print(f"connection from {address} has been made at time: {get_time()}")
    client_socket.send(bytes(
        json.dumps(data), "utf-8"))


def listen_for_connection():
    global address
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((IP, PORT))
            s.listen(5)
            s, address = s.accept()
            start_new_thread(handle_connection, (s,))


if __name__ == "__main__":
    start_new_thread(record_data, ())
    listen_for_connection()


