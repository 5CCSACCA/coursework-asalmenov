FROM python:3.10-slim

WORKDIR /app

# System deps (opencv + torch CPU runtime)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# 1) Install CPU-only Torch from official index
RUN pip install --no-cache-dir \
    torch==2.3.1 \
    --index-url https://download.pytorch.org/whl/cpu

# 2) Install other dependencies (ultralytics, fastapi, uvicorn, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your code
COPY services/ ./services/
COPY docs/ ./docs/

# 4) Expose the API port
EXPOSE 8000

# 5) Run FastAPI YOLO service
CMD ["uvicorn", "services.yolo.api:app", "--host", "0.0.0.0", "--port", "8000"]
