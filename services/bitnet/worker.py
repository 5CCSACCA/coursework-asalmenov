import json
import os
import pika
from typing import Any, Dict


def get_rabbitmq_url() -> str:
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def fake_bitnet_postprocess(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stand-in for BitNet LLM.
    Takes YOLO detections and returns a simple natural-language summary.
    """
    detections = message.get("detections", [])
    if not detections:
        summary = "No objects were detected in the image."
    else:
        labels = [d.get("label", "object") for d in detections]
        unique_labels = sorted(set(labels))
        summary = f"The model detected: {', '.join(unique_labels)}."

    return {
        "summary": summary,
        "original_meta": message.get("meta", {}),
    }


def main() -> None:
    url = get_rabbitmq_url()
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    queue_name = "yolo_outputs"
    channel.queue_declare(queue=queue_name, durable=True)

    print(f"[BitNet] Worker started. Listening on queue '{queue_name}'.")

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode("utf-8"))
            print(f"[BitNet] Received message: {message}")
            processed = fake_bitnet_postprocess(message)
            print(f"[BitNet] Post-processed output: {processed}")
        except Exception as e:
            print(f"[BitNet] Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[BitNet] Shutting down.")
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()