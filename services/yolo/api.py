from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.yolo.db import init_db, log_prediction, list_predictions
from services.yolo.model import YoloService
from services.yolo.storage import init_firebase, save_output, list_outputs, update_output, delete_output
from datetime import datetime
from typing import Any, Dict

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
    init_firebase()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(400, "Unsupported file type")

    data = await file.read()
    result = svc.predict(data)

    firebase_id = None

    if result.get("detections"):
        top = result["detections"][0]
        filename = file.filename or "uploaded"
        label = top.get("label", "unknown")
        confidence = float(top.get("confidence", 0.0))
        created_at = datetime.utcnow().isoformat()

        # 1) Local SQLite log (Stage 4)
        log_prediction(
            filename=filename,
            label=label,
            confidence=confidence,
        )

        # 2) Firebase log (Stage 5)
        firebase_payload = {
            "filename": filename,
            "label": label,
            "confidence": confidence,
            "created_at": created_at,
            "raw_result": result,  # full YOLO output if you want
        }
        firebase_id = save_output(firebase_payload)

    # attach firebase_id so clients can later update/delete
    response_body = dict(result)
    if firebase_id is not None:
        response_body["firebase_id"] = firebase_id

    return JSONResponse(content=response_body)

@app.get("/predictions")
def get_predictions(limit: int = 50):
    """
    Return the most recent logged predictions.
    """
    return list_predictions(limit=limit)

@app.get("/firebase/predictions")
def get_firebase_predictions(limit: int = 50):
    """
    List model outputs stored in Firebase.
    """
    return list_outputs(limit=limit)


@app.put("/firebase/predictions/{doc_id}")
def update_firebase_prediction(doc_id: str, updates: Dict[str, Any]):
    """
    Update a stored model output in Firebase.
    For example, to correct a label or add notes.
    """
    if not updates:
        raise HTTPException(400, "No updates provided")
    update_output(doc_id, updates)
    return {"status": "updated", "id": doc_id}


@app.delete("/firebase/predictions/{doc_id}")
def delete_firebase_prediction(doc_id: str):
    """
    Delete a stored model output from Firebase.
    """
    delete_output(doc_id)
    return {"status": "deleted", "id": doc_id}