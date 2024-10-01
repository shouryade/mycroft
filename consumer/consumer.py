import pika
import json
import asyncpg
import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO)


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5432/postgres"
)

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "iot_queue")

DEVICE_TABLE_MAP = {
    "motion_sensor": "motion_sensor_data",
    "temperature_sensor": "temperature_sensor_data",
    "humidity_sensor": "humidity_sensor_data",
    "smoke_sensor": "smoke_sensor_data",
}


async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)


async def insert_data(pool, device, value):
    table_name = DEVICE_TABLE_MAP.get(device)

    if not table_name:
        print(f"Unknown device: {device}")
        return

    query = f"INSERT INTO {table_name} (value) VALUES ($1)"
    logging.info(query)

    async with pool.acquire() as connection:
        await connection.execute(query, value)
        logging.info(f"Inserted {value} into {table_name}")


# Callback function for processing RabbitMQ messages
async def process_message(pool, body):
    try:
        message = json.loads(body)
        device = message.get("device")
        value = message.get("value")

        if device:
            await insert_data(pool, device, float(value))
        else:
            print(f"Invalid message format: {message}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")


# Synchronous function to handle RabbitMQ message delivery
def callback(ch, method, properties, body, loop, pool):
    asyncio.run_coroutine_threadsafe(process_message(pool, body), loop)


# Function to start RabbitMQ consumer
def consume_messages(loop, pool):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE_NAME)

    # Pass the event loop and pool to the callback
    on_message_callback = lambda ch, method, properties, body: callback(
        ch, method, properties, body, loop, pool
    )

    channel.basic_consume(
        queue=RABBITMQ_QUEUE_NAME,
        on_message_callback=on_message_callback,
        auto_ack=True,
    )

    print(f"Listening for messages on {RABBITMQ_QUEUE_NAME}...")

    channel.start_consuming()


async def main():
    loop = asyncio.get_event_loop()
    pool = await get_db_pool()
    await loop.run_in_executor(None, consume_messages, loop, pool)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
