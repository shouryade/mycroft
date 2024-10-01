import time
import random
from paho.mqtt import client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "home/motion"
CLIENT_ID = "motion-sensor"


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        print("client")
        if rc == 0:
            print("Connected to MQTT Broker")
        else:
            print("Failed to connect, retry again")

    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client


def publish_motion_data(client):
    while True:
        motion = random.choice([0, 1])
        client.publish(TOPIC, str(motion))
        print(f"Published motion data: {motion}")
        time.sleep(0.01)  # 100 Hz (0.01 seconds delay)


def run():
    client = connect_mqtt()
    client.loop_start()
    publish_motion_data(client)


if __name__ == "__main__":
    run()
