import time
import random
import requests

URL = 'http://localhost:8080/humidity'

def simulate_humidity_sensor():
    while True:
        humidity = round(random.uniform(30.0, 70.0), 2)
        data = {'data': humidity}
        try:
            response = requests.post(URL, json=data)
            print(f"Sent humidity data: {humidity}% - Response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")
        time.sleep(0.01)

if __name__ == "__main__":
    simulate_humidity_sensor()
