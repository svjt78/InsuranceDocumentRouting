import pika
from .config import RABBITMQ_URL


def get_rabbitmq_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    # disable AMQP-level heartbeats so pika.BlockingConnection isn't closed by RabbitMQ
    params.heartbeat = 0
    # increase the blocked connection timeout to prevent unexpected closures
    params.blocked_connection_timeout = 300
    connection = pika.BlockingConnection(params)
    return connection


def publish_message(queue_name: str, message: str):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
