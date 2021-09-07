import datetime
import json
import random
import socket
import sys
import time
from _thread import start_new_thread

SENSOR_INTERVAL = 1
IP = "localhost"
PORT = 1234
temp = 0
humidity = 0
time_of_measurement = datetime.datetime.utcnow().strftime("%H:%M:%S")
location = "Home"
data = {"time": time_of_measurement,
        "location": location,
        "temperature": temp,
        "humidity": humidity}


def record_data():
    start_new_thread(get_measurement, ())


def get_measurement():
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


def get_time():
    return datetime.datetime.utcnow().strftime("%H:%M:%S")


def get_temperature():
    return random.randint(1, 10)


def get_humidity():
    return random.randint(1, 100)


def send_data(client_socket):
    client_socket.send(bytes(
        json.dumps(data), "utf-8"))


def handle_connection(s, msg):
    global SENSOR_INTERVAL
    if msg == "shutdown":
        sys.exit()
    if msg == "get":
        start_new_thread(send_data, (s,))
    if "interval" in msg:
        SENSOR_INTERVAL = int(msg.strip("interval"))
        print(SENSOR_INTERVAL)


def listen_for_connection():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen(5)
        s, address = s.accept()
        print(f"connection from {address} has been made at time: {get_time()}")
        msg = s.recv(1024).decode("utf-8")
        handle_connection(s, msg)


if __name__ == "__main__":
    record_data()
    listen_for_connection()
