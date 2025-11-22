# services/yolo/api.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.yolo.model import YoloService

app = FastAPI(
    title="YOLO11n Inference API",
    version="0.1.0",
    description="Stage 3 FastAPI YOLO inference service"
)

# Load YOLO once at startup
svc = YoloService()


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accept an uploaded image and return YOLO detections.
    """
    # ensure correct image type
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(400, "Unsupported file type")

    # read bytes
    data = await file.read()

    # run inference using YOUR SAME LOGIC as CLI
    result = svc.predict(data)

    return JSONResponse(content=result)
