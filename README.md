

# FoodVisionAI — Intelligent Recipe Generator
https://github.com/5CCSACCA/coursework-asalmenov
## Project Description

FoodVisionAI is a cloud-based application that identifies food items from images and suggests creative recipe ideas using those detected ingredients. The system combines computer vision and natural language processing to help users reduce food waste and discover new meal ideas.


## System Overview

- YOLOv8n (Ultralytics): Detects and classifies food items from user-provided images or a live camera feed.

- BitNet (Microsoft): Generates recipe suggestions and cooking instructions based on the ingredients detected by YOLO.

- FastAPI: Hosts the application as a RESTful API, allowing users to upload images and receive text-based recipe ideas.

- Docker & Docker Compose: Enable simple containerized deployment with one command for building and one for running.

## Workflow

1. The user uploads or captures an image of food.

2. YOLO detects visible ingredients (e.g., tomato, pasta, cheese).

3. The list of detected ingredients is sent to BitNet.

4. BitNet generates a recipe idea and instructions in natural language.

### Example
#### Input: 

Image containing tomatoes, onions, and garlic 

#### Output:

```
Detected ingredients: tomato, onion, garlic  
Suggested recipe: Roasted Tomato Soup  
Instructions: Roast tomatoes and garlic with olive oil, blend, and simmer with vegetable stock.
```


## Technologies

- Python

- FastAPI

- Ultralytics YOLOv8n

- Microsoft BitNet

- Docker & Docker Compose

## Future Additions

- User authentication and recipe history via Firebase

- RabbitMQ integration for scalable message handling

- Infrastructure cost estimation and system monitoring
