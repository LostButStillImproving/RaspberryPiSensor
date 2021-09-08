import RPi.GPIO as GPIO
import dht11
import datetime
import json
import socket
import sys
import time
from _thread import start_new_thread

IP = "10.200.130.32"
PORT = 1234

SENSOR_INTERVAL = 1
time_of_measurement = datetime.datetime.utcnow().strftime("%H:%M:%S")
location = "Home"
data = {"time": time_of_measurement,
        "location": location,
        "temperature": 0,
        "humidity": 0}


def record_data():
    start_new_thread(get_measurement, ())


def get_measurement():
    while True:
        time.sleep(SENSOR_INTERVAL)
        data["time"] = get_time()
        result = poll_sensor()
        if hasattr(result, "error_code"):
            data["temperature"] = result.temperature
            data["humidity"] = result.humidity


def get_time():
    return datetime.datetime.utcnow().strftime("%H:%M:%S")


def poll_sensor():
    instance = dht11.DHT11(pin=17)
    result = instance.read()
    if result.is_valid():
        return result
    else:
        print("Error: %d" % result.error_code)


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
    print(f"Server is running on {IP}:{PORT}")
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen(5)
        s, address = s.accept()
        print(f"connection from {address} has been made at time: {get_time()}")
        msg = s.recv(1024).decode("utf-8")
        handle_connection(s, msg)


def sensor_setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()


if __name__ == "__main__":
    sensor_setup()
    record_data()
    listen_for_connection()
