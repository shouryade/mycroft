# RSE002-Engineer-Smart_H_Integration_Assignmentt_Submission-Divij_Goel

This project is a multi-service application managed with Docker Compose. It includes the following services:  

1. **mqtt-broker**: This service uses the official eclipse-mosquitto image and provides an MQTT broker for managing publish/subscribe communication. It exposes ports 1883 for MQTT and 9001 for WebSocket connections.

2. **rabbitmq-broker**: A RabbitMQ service built from a custom Dockerfile. It manages messaging queues for communication between the producer and consumer. Exposes port 5672 for AMQP protocol and 15672 for the RabbitMQ management UI.

3. **postgres-db**: This service runs a PostgreSQL database using the postgres:15-alpine image. It's used for persisting sensor data. The database is accessible on port 5432 and is pre-configured with initial data using a volume-mounted SQL script.

4. **grafana**: A Grafana instance used for visualizing the sensor data stored in the PostgreSQL database. It connects to the PostgreSQL service and is accessible on port 3000.

5. **producer**: A custom service built from a Dockerfile in the ./worker directory. It simulates an IoT device that publishes sensor data (smoke and CO levels) to MQTT and RabbitMQ.

6. **consumer**: A custom service built from a Dockerfile in the ./consumer directory. It consumes data from RabbitMQ, processes it, and stores it in the PostgreSQL database.

## Getting Started
To get the application up and running, make sure Docker and Docker Compose are installed. Then follow these steps:  

1. Unzip the file.

2. Navigate to the file 
```bash
cd RSE002-Engineer-Smart_H_Integration_Assignmentt
```
3. Build the service
```bash
docker compose up --build
```

## Service Access
After running the application with Docker Compose, the following services will be available:  
- MQTT Broker: Connect to the broker at mqtt://localhost:1883 for MQTT communication.
- RabbitMQ Management UI: Access the RabbitMQ web interface at http://localhost:15672.
- PostgreSQL Database: The PostgreSQL database will be running on localhost:5432 with the following credentials:
    - Username: postgres
    - Password: postgres
    - Database: postgres
- Grafana: Access the Grafana interface at http://localhost:3000 to visualize the sensor data. Grafana is pre-configured to connect to the PostgreSQL database.

## Environment Variables
Each service uses the following environment variables:

- mqtt-broker: Configured via a custom mosquitto.conf file located in the ./configs/ directory.
- rabbitmq-broker: Built from the Dockerfile.rabbitmq file in the ./dockerfiles/ directory.
- postgres-db: The PostgreSQL database uses environment variables to configure the database name, user, and password.
- grafana: Grafana connects to the PostgreSQL database using environment variables specified in the docker-compose.yml file.
- producer: The producer service publishes data to MQTT and RabbitMQ. It uses environment variables for configuring the broker host and port.
- consumer: The consumer service connects to RabbitMQ and PostgreSQL using environment variables to process and store sensor data.

## Simulating Sensors
Run the following commands:  
make sure to install pipenv (pip install pipenv)
```bash
cd playground
pipenv install
```
to run and use one of the following commads:
```bash
python scripts/divij_mqtt.py
python scripts/divij_tcp.py
python scripts/http_client.py
python scripts/smoke_tcp.py
```

## Load Graphana dashboard
open garphana interface at http://localhost:3000  
load graphana dashboard by copying the graphana.json file ./configs 

## Volumes
- postgres-data: Stores PostgreSQL database data.
- grafana: Stores persistent Grafana data, such as dashboards and configurations.

## Monitoring
- RabbitMQ Management UI: You can monitor the RabbitMQ queues and exchanges using the management UI at http://localhost:15672.
- Grafana Dashboards: Visualize the smoke and CO sensor data with Grafana by creating dashboards and connecting to the PostgreSQL database.

## Milestones
- Set up an MQTT broker with Mosquitto.
- Configure RabbitMQ with health checks.
- Set up PostgreSQL database with initial data.
- Set up Grafana for data visualization.
- Build a producer service to simulate IoT devices.
- Build a consumer service to process and store sensor data in PostgreSQL.