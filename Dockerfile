FROM python:3.10-slim

WORKDIR /app

# system deps (opencv + some torch bits like libgomp)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# 1) Install CPU-only torch from the official PyTorch CPU index
RUN pip install --no-cache-dir \
    torch==2.3.1 \
    --index-url https://download.pytorch.org/whl/cpu

# 2) Install the rest of your deps (ultralytics etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your code
COPY services/ ./services/
COPY docs/ ./docs/

# 4) Default command: smoke test on apple image
CMD ["python", "-m", "services.yolo.cli", "--image", "docs/examples/apple.jpg"]