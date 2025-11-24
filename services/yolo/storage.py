# services/yolo/storage.py

import os
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore

# We’ll use Firestore to store model outputs as documents
_db: Optional[firestore.Client] = None


def init_firebase() -> None:
    """
    Initialise Firebase Admin SDK and Firestore client.
    Expects:
      - GOOGLE_APPLICATION_CREDENTIALS env var pointing to service account JSON
      - (optional) FIREBASE_PROJECT_ID if needed
    """
    global _db

    if _db is not None:
        return  # already initialised

    # If an app is already initialised (e.g. by tests), reuse it
    if not firebase_admin._apps:
        cred_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "config/firebase-service-account.json",  # default path inside container
        )
        if not os.path.exists(cred_path):
            # In case the marker doesn’t mount real credentials, fail gracefully
            raise RuntimeError(
                f"Firebase credentials not found at {cred_path}. "
                "Set GOOGLE_APPLICATION_CREDENTIALS or mount the JSON file."
            )

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()


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