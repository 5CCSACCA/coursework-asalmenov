

# FoodVisionAI — Intelligent Recipe Generator
https://github.com/5CCSACCA/coursework-asalmenov
## Project Description

FoodVisionAI is a cloud-based application that identifies food items from images and suggests creative recipe ideas using those detected ingredients. The system combines computer vision and natural language processing to help users reduce food waste and discover new meal ideas.

The system is fully containerised and designed to run locally or on a virtual machine using Docker Compose.

## System Overview

- YOLOv11n (Ultralytics): Detects and classifies food items from user-provided images.

- BitNet (Microsoft): Generates recipe suggestions and cooking instructions based on the ingredients detected by YOLO.

- FastAPI: Hosts the application as a RESTful API, allowing users to upload images and receive text-based recipe ideas.

- Docker & Docker Compose: Enable simple containerized deployment with one command for building and one for running.

## Architecture

The system is implemented as a set of containerised microservices:

- **YOLO Service**: FastAPI service that performs image inference, logs predictions to SQLite, publishes detection results to RabbitMQ, and forwards results to Firebase Firestore for storage.
- **RabbitMQ**: Message queue used to decouple inference from post-processing.
- **BitNet Service**: Worker service that consumes detection messages and generates recipe suggestions.

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

## Security and Monitoring

- All sensitive API endpoints are protected using Firebase Authentication.
- Unauthorized requests are rejected with HTTP 401.
- Firebase credentials are mounted at runtime and not stored in the repository.
- RabbitMQ uses non-default credentials.
- A `/health` endpoint is provided for service monitoring.
- YOLO inference latency is logged for performance monitoring.


## Setup on a Fresh Linux Machine

The system can be set up and explored on a fresh Linux machine using Docker.

### Requirements
- Linux (e.g. Ubuntu)
- Docker
- Docker Compose
- Firebase project with Authentication enabled

### Steps

1. Install Docker and Docker Compose following the official Docker documentation.
2. Clone the repository:
   ```bash
   git clone https://github.com/5CCSACCA/coursework-asalmenov.git
   cd coursework-asalmenov
   ```
3. Place the Firebase Admin SDK service account JSON at:
   ```
   config/firebase-service-account.json
   ```
4. Build and start the services:
   ```
   docker compose up --build
   ```
5. Test the system using the provided example image:
   ```bash
    curl -X POST http://localhost:8000/predict \
      -H "Authorization: Bearer <FIREBASE_ID_TOKEN>" \
      -H "Content-Type: multipart/form-data" \
      -F "file=@docs/examples/apple.jpg"
   ```

## Technologies Used

- Python

- FastAPI

- Ultralytics YOLOv11n

- Firebase Authentication & Firestore

- Microsoft BitNet

- RabbitMQ

- SQLite

- Docker & Docker Compose
