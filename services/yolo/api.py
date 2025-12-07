from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from services.yolo.db import init_db, log_prediction, list_predictions
from services.yolo.model import YoloService
from services.yolo.storage import init_firebase, save_output, list_outputs, update_output, delete_output
from datetime import datetime
from typing import Any, Dict
from services.yolo.mq import publish_yolo_output
from services.yolo.auth import get_current_user
import time

app = FastAPI(
    title="YOLO11n Inference API",
    version="0.1.0",
    description="Stage 3 FastAPI YOLO inference service"
)

svc = YoloService()

@app.on_event("startup")
def on_startup() -> None:
    init_db()
    init_firebase()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    user: Dict[str, Any] = Depends(get_current_user),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(400, "Unsupported file type")

    data = await file.read()

    start = time.time()
    result = svc.predict(data)
    duration = time.time() - start
    print(f"[Monitor] YOLO inference time: {duration:.4f} seconds")

    firebase_id = None

    if result.get("detections"):
        top = result["detections"][0]
        filename = file.filename or "uploaded"
        label = top.get("label", "unknown")
        confidence = float(top.get("confidence", 0.0))
        created_at = datetime.utcnow().isoformat()

        log_prediction(
            filename=filename,
            label=label,
            confidence=confidence,
        )

        firebase_payload = {
            "filename": filename,
            "label": label,
            "confidence": confidence,
            "created_at": created_at,
            "raw_result": result,
        }
        firebase_id = save_output(firebase_payload)

    try:
        publish_yolo_output(result)
    except Exception as e:
        print(f"[Stage6] Warning: failed to publish to RabbitMQ: {e}")

    response_body = dict(result)
    if firebase_id is not None:
        response_body["firebase_id"] = firebase_id

    return JSONResponse(content=response_body)

@app.get("/predictions")
def get_predictions(
    limit: int = 50,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Return the most recent logged predictions.
    """
    return list_predictions(limit=limit)

@app.get("/firebase/predictions")
def get_firebase_predictions(
    limit: int = 50,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List model outputs stored in Firebase.
    """
    return list_outputs(limit=limit)


@app.put("/firebase/predictions/{doc_id}")
def update_firebase_prediction(
    doc_id: str,
    updates: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a stored model output in Firebase.
    For example, to correct a label or add notes.
    """
    if not updates:
        raise HTTPException(400, "No updates provided")
    update_output(doc_id, updates)
    return {"status": "updated", "id": doc_id}


@app.delete("/firebase/predictions/{doc_id}")
def delete_firebase_prediction(
    doc_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a stored model output from Firebase.
    """
    delete_output(doc_id)
    return {"status": "deleted", "id": doc_id}