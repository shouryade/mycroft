import socket
import time
import random

HOST = 'localhost'
PORT = 65432

def simulate_temperature_sensor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            # Random temperature data in °C
            temperature = round(random.uniform(20.0, 30.0), 2)
            s.sendall(str(temperature).encode('utf-8'))
            print(f"Sent temperature data: {temperature}°C")
            time.sleep(0.01)  # 100 Hz (0.01 seconds delay)

if __name__ == "__main__":
    simulate_temperature_sensor()
