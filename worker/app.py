import socket
import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pika
import json
import paho.mqtt.client as mqtt_client
import os
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)


# --------------------------------------------- Variables ------------------------------------------------
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE_NAME = "iot_queue"
TCP_HOST = "0.0.0.0"
TCP_PORT_TEMP = 65432
TCP_PORT_SMOKE = 65433
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = 1883
MQTT_TOPIC = "home/motion"
MQTT_CLIENT_ID = "subscriber"
HTTP_PORT = 8080


# --------------------------------------------- RabbitMQ Setup ------------------------------------------------
def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE_NAME)
    return channel, connection


def publish_message(device, value, channel):
    message = {"device": device, "value": value}
    channel.basic_publish(
        exchange="", routing_key=RABBITMQ_QUEUE_NAME, body=json.dumps(message)
    )

def publish_message_smoke(device,value1,value2,channel):
    message = {"device": device, "value1": value1, "value2":value2}
    channel.basic_publish(
        exchange="", routing_key=RABBITMQ_QUEUE_NAME, body=json.dumps(message)
    )

# --------------------------------------------- TCP Servers  ------------------------------------------------
def start_temperature_server():
    # Create a separate RabbitMQ connection and channel for this thread
    channel, connection = connect_rabbitmq()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((TCP_HOST, TCP_PORT_TEMP))
        s.listen()
        logging.info(f"Temperature server listening on {TCP_HOST}:{TCP_PORT_TEMP}...")
        while True:
            conn, addr = s.accept()
            logging.info(f"Connected by {addr}")
            handle_client(conn, "temperature_sensor", channel)

    # Close connection after thread ends
    connection.close()


def handle_client(conn, sensor_type, channel):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    logging.warning("Client disconnected.")
                    break
                value = data.decode("utf-8")
                publish_message(sensor_type, float(value), channel)
            except ConnectionResetError:
                logging.error("Connection reset by client.")
                break

def handle_client_smoke(conn, sensor_type, channel):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    logging.warning("Client disconnected.")
                    break
                value = data.decode("utf-8").split(',')
                publish_message_smoke(sensor_type, float(value[0]), float(value[1]), channel)
            except ConnectionResetError:
                logging.error("Connection reset by client.")
                break


def start_smoke_server():
    # Create a separate RabbitMQ connection and channel for this thread
    channel, connection = connect_rabbitmq()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((TCP_HOST, TCP_PORT_SMOKE))
        s.listen()
        logging.info(f"Smoke server listening on {TCP_HOST}:{TCP_PORT_SMOKE}...")

        while True:
            conn, addr = s.accept()
            logging.info(f"Connected by {addr}")
            handle_client_smoke(conn, "smoke_sensor", channel)

    # Close connection after thread ends
    connection.close()


# --------------------------------------------- HTTP Server (FastAPI) ------------------------------------------------
resource = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create a single RabbitMQ connection and channel for the FastAPI app
    channel, connection = connect_rabbitmq()
    resource["channel"] = channel
    resource["connection"] = connection
    yield
    # Close connection after the app ends
    connection.close()
    resource.clear()


app = FastAPI(lifespan=lifespan)


# Define the data model for incoming humidity data
class HumidityData(BaseModel):
    data: float


@app.post("/humidity")
async def receive_humidity(data: HumidityData):
    channel = resource["channel"]
    connection = resource["connection"]
    # Get the channel from the lifespan context
    publish_message("humidity_sensor", float(data.data), channel)
    return {"message": "Data received", "data": data.data}


# --------------------------------------------- MQTT  ------------------------------------------------
def connect_mqtt() -> mqtt_client.Client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client


def mqtt_run():
    # Create a separate RabbitMQ connection and channel for this thread
    channel, connection = connect_rabbitmq()

    client = connect_mqtt()

    def on_message(client, userdata, msg):
        value = msg.payload.decode()
        logging.info(f"Received `{float(value)}` from `{msg.topic}` topic")
        publish_message("motion_sensor", float(value), channel)

    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message
    client.loop_forever()

    # Close connection after thread ends
    connection.close()


# --------------------------------------------- Main  ------------------------------------------------

if __name__ == "__main__":
    # Start each server and MQTT listener in its own thread, each with its own RabbitMQ connection
    http_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host=TCP_HOST, port=HTTP_PORT)
    )
    tcp_thread_1 = threading.Thread(target=start_temperature_server)
    tcp_thread_2 = threading.Thread(target=start_smoke_server)
    mqtt_thread = threading.Thread(target=mqtt_run)

    # Start threads
    http_thread.start()
    tcp_thread_1.start()
    tcp_thread_2.start()
    mqtt_thread.start()

    # Join threads
    http_thread.join()
    tcp_thread_1.join()
    tcp_thread_2.join()
    mqtt_thread.join()
