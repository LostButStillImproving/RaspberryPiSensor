import RPi.GPIO as GPIO
import os
import dht11
import datetime
import json
import socket
import time
from _thread import start_new_thread

IP_HOME = "192.168.1.118"
IP_SCHOOL = "10.200.130.32"
IP_LOCAL = "127.0.0.1"
PORT = 1233

SENSOR_INTERVAL = 1
is_recording = True
data = {"time": datetime.datetime.utcnow().strftime("%H:%M:%S"),
        "location": "Home",
        "temperature": 0,
        "humidity": 0}


def listen_for_connection():
    print(f"Server is running on {IP_SCHOOL}:{PORT}")
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP_SCHOOL, PORT))
        s.listen(5)
        s, address = s.accept()
        print(f"connection from {address} has been made at time: {get_time()}")
        start_new_thread(handle_connection, (s,))


def handle_connection(client_socket):
    global is_recording
    msg = client_socket.recv(1024).decode("utf-8")
    if msg == "get":
        send_data(client_socket)
    if "interval" in msg:
        interval = int(msg.strip("interval"))
        set_sensor_interval(interval)
    if msg == "stop":
        is_recording = False
    if msg == "start":
        record_data()
    if msg == "reboot":
        os.system("sudo reboot")


def send_data(client_socket):
    client_socket.send(bytes(
        json.dumps(data), "utf-8"))


def set_sensor_interval(interval):
    global SENSOR_INTERVAL
    SENSOR_INTERVAL = interval
    print(f'sensor interval changed to {SENSOR_INTERVAL}')


def get_measurement():
    global is_recording
    while is_recording:
        time.sleep(SENSOR_INTERVAL)
        data["time"] = get_time()
        result = poll_sensor()
        if hasattr(result, "error_code"):
            data["temperature"] = result.temperature
            data["humidity"] = result.humidity


def get_time():
    return datetime.datetime.utcnow().strftime("%H:%M:%S")


def sensor_setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()


def record_data():
    start_new_thread(get_measurement, ())


def poll_sensor():
    instance = dht11.DHT11(pin=17)
    result = instance.read()
    if result.is_valid():
        return result
    else:
        print("Error: %d" % result.error_code)


if __name__ == "__main__":
    sensor_setup()
    record_data()
    listen_for_connection()
