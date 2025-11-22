from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.yolo.db import init_db, log_prediction, list_predictions
from services.yolo.model import YoloService

app = FastAPI(
    title="YOLO11n Inference API",
    version="0.1.0",
    description="Stage 3 FastAPI YOLO inference service"
)

# Load YOLO once at startup
svc = YoloService()

@app.on_event("startup")
def on_startup() -> None:
    init_db()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(400, "Unsupported file type")

    data = await file.read()
    result = svc.predict(data)

    if result.get("detections"):
        top = result["detections"][0]
        log_prediction(
            filename=file.filename or "uploaded",
            label=top.get("label", "unknown"),
            confidence=float(top.get("confidence", 0.0)),
        )

    return JSONResponse(content=result)

@app.get("/predictions")
def get_predictions(limit: int = 50):
    """
    Return the most recent logged predictions.
    """
    return list_predictions(limit=limit)