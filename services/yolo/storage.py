from typing import Any, Dict, List, Optional
import os

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

_db: Optional[firestore.Client] = None


def init_firebase() -> None:
    """
    Best-effort Firebase init.
    If credentials file is missing or invalid, just log a warning and skip.
    """
    global _db

    if _db is not None:
        return

    if firebase_admin._apps:
        _db = firestore.client()
        return

    cred_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "config/firebase-service-account.json",
    )

    if not os.path.isfile(cred_path):
        print(f"[Firebase] Warning: credentials file not found at {cred_path}. Skipping Firebase init.")
        return

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("[Firebase] Initialised Firestore client.")
    except Exception as e:
        print(f"[Firebase] Warning: failed to initialise Firebase: {e}. Skipping.")
        _db = None


def save_output(payload: Dict[str, Any]) -> Optional[str]:
    """
    Save a model output document to Firebase.
    Returns the document ID, or None if Firebase is not available.
    """
    if _db is None:
        print("[Firebase] save_output called but Firebase is not initialised. Skipping.")
        return None

    collection = _db.collection("predictions")
    data = dict(payload)
    data.setdefault("created_at", datetime.utcnow().isoformat())

    doc_ref = collection.document()
    doc_ref.set(data)
    return doc_ref.id


def list_outputs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    List the most recent model outputs from Firebase.
    Returns an empty list if Firebase is not available.
    """
    if _db is None:
        print("[Firebase] list_outputs called but Firebase is not initialised. Returning empty list.")
        return []

    collection = _db.collection("predictions")
    docs = (
        collection
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def update_output(doc_id: str, updates: Dict[str, Any]) -> None:
    """
    Update a stored model output in Firebase.
    No-op if Firebase is not available.
    """
    if _db is None:
        print("[Firebase] update_output called but Firebase is not initialised. Skipping.")
        return

    _db.collection("predictions").document(doc_id).update(updates)


def delete_output(doc_id: str) -> None:
    """
    Delete a stored model output from Firebase.
    No-op if Firebase is not available.
    """
    if _db is None:
        print("[Firebase] delete_output called but Firebase is not initialised. Skipping.")
        return

    _db.collection("predictions").document(doc_id).delete()