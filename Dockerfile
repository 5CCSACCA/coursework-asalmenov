FROM pytorch/pytorch:2.1.0-cpu

WORKDIR /app

# system deps (opencv needs these sometimes)
RUN apt-get update && apt-get install -y libglib2.0-0 libgl1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ ./services/
COPY docs/ ./docs/

# default run: smoke test on apple
CMD ["python", "-m", "services.yolo.cli", "--image", "docs/examples/apple.jpg"]