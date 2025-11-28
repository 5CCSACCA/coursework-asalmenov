import json
import os
import pika
from typing import Any, Dict


def get_rabbitmq_url() -> str:
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def publish_yolo_output(payload: Dict[str, Any], queue_name: str = "yolo_outputs") -> None:
    """
    Publish YOLO output to a RabbitMQ queue for post-processing.
    Best-effort: if RabbitMQ is not available, just log and continue.
    """
    url = get_rabbitmq_url()
    try:
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        body = json.dumps(payload).encode("utf-8")
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )
        connection.close()
        print(f"[RabbitMQ] Published message to queue '{queue_name}'.")
    except Exception as e:
        print(f"[RabbitMQ] Warning: failed to publish message: {e}")