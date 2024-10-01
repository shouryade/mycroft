import socket
import time
import random

HOST = 'localhost'
PORT = 65433

def simulate_temperature_sensor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            smoke_level = round(random.uniform(0.0, 1.0), 3)
            co_level = round(random.uniform(0.0, 1.0), 3)
            s.sendall(f'{str(smoke_level)},{str(co_level)}'.encode('utf-8'))
            print(f"Sent Smoke data: {smoke_level} CO-Level:{co_level}")
            time.sleep(0.01)

if __name__ == "__main__":
    simulate_temperature_sensor()
