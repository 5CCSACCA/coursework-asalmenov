import json
import os
import time
from typing import Any, Dict

import pika
from pika.exceptions import AMQPConnectionError

print("[BitNet] Module imported.")

def get_rabbitmq_url() -> str:
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def fake_bitnet_postprocess(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stand-in for a BitNet-style LLM.

    Takes YOLO detections of food items and generates a simple recipe
    using those ingredients.
    """
    detections = message.get("detections", [])
    if not detections:
        return {
            "recipe_title": "No recipe available",
            "ingredients": [],
            "steps": [
                "No food items were detected in the image, so a recipe could not be generated."
            ],
            "used_labels": [],
            "original_meta": message.get("meta", {}),
        }

    labels = [d.get("label", "ingredient") for d in detections]
    unique_labels = sorted(set(labels))

    main_ingredient = unique_labels[0]
    extra_ingredients = unique_labels[1:]

    title = f"Quick {main_ingredient.capitalize()} Dish"

    ingredients = [f"{main_ingredient} (as the main ingredient)"]
    for ing in extra_ingredients:
        ingredients.append(f"{ing} (supporting ingredient)")

    ingredients.extend([
        "Salt, to taste",
        "Pepper, to taste",
        "1 tbsp olive oil (or any cooking oil)",
    ])

    steps = [
        f"1. Prepare the ingredients: wash and cut the {', '.join(unique_labels)} as needed.",
        f"2. Heat a pan with a little oil over medium heat.",
        f"3. Start by cooking the {main_ingredient} until it softens or browns slightly.",
    ]

    if extra_ingredients:
        steps.append(
            f"4. Add the remaining ingredients ({', '.join(extra_ingredients)}) and cook for a few more minutes."
        )
    else:
        steps.append(
            "4. Season with salt and pepper, adjusting the taste as you go."
        )

    steps.extend([
        "5. Once everything is cooked through and well combined, remove from the heat.",
        "6. Serve warm, optionally with bread, rice, or a simple salad on the side.",
    ])

    return {
        "recipe_title": title,
        "ingredients": ingredients,
        "steps": steps,
        "used_labels": unique_labels,
        "original_meta": message.get("meta", {}),
    }

def start_worker() -> None:
    url = get_rabbitmq_url()
    params = pika.URLParameters(url)

    while True:
        try:
            print(f"[BitNet] Connecting to RabbitMQ at {url} ...")
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
                    print(f"[BitNet] Generated recipe: {processed['recipe_title']}")
                    print(f"[BitNet] Ingredients: {processed['ingredients']}")
                    print(f"[BitNet] Steps: {processed['steps']}")
                except Exception as e:
                    print(f"[BitNet] Error processing message: {e}")
                finally:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=callback)

            channel.start_consuming()
        except AMQPConnectionError as e:
            print(f"[BitNet] Could not connect to RabbitMQ ({e}). Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("[BitNet] Shutting down.")
            try:
                connection.close()
            except Exception:
                pass
            break
        except Exception as e:
            print(f"[BitNet] Unexpected error in worker: {e}. Retrying in 5 seconds...")
            time.sleep(5)


def main() -> None:
    print("[BitNet] main() starting.")
    start_worker()


if __name__ == "__main__":
    main()