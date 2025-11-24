# services/yolo/storage.py

import os
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore

# We’ll use Firestore to store model outputs as documents
_db: Optional[firestore.Client] = None


def init_firebase() -> None:
    """
    Best-effort Firebase init.
    If credentials file is missing or invalid, just log a warning and skip.
    """
    global _db

    if _db is not None:
        return  # already initialised

    # Reuse existing app if already initialised
    if firebase_admin._apps:
        _db = firestore.client()
        return

    cred_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "config/firebase-service-account.json",
    )

    # If file doesn't exist or is a directory -> skip Firebase
    if not os.path.isfile(cred_path):
        print(f"[Firebase] Warning: credentials file not found at {cred_path}. Skipping Firebase init.")
        return

    # Quick sanity check: is it valid JSON?
    try:
        with open(cred_path, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        print(f"[Firebase] Warning: invalid credentials JSON at {cred_path}: {e}. Skipping Firebase init.")
        return

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("[Firebase] Initialised Firestore client.")
    except Exception as e:
        print(f"[Firebase] Warning: failed to initialise Firebase: {e}. Skipping.")
        _db = None

def _collection():
    if _db is None:
        raise RuntimeError("Firebase not initialised. Call init_firebase() first.")
    return _db.collection("predictions")  # Firestore collection name


def save_output(payload: Dict[str, Any]) -> str:
    """
    Save a model output document to Firebase.
    Returns the Firebase document ID.
    """
    doc_ref = _collection().document()  # auto-id
    doc_ref.set(payload)
    return doc_ref.id


def list_outputs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    List the most recent model outputs from Firebase.
    """
    docs = (
        _collection()
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def update_output(doc_id: str, updates: Dict[str, Any]) -> None:
    """
    Update a stored model output in Firebase.
    """
    _collection().document(doc_id).update(updates)


def delete_output(doc_id: str) -> None:
    """
    Delete a stored model output from Firebase.
    """
    _collection().document(doc_id).delete()