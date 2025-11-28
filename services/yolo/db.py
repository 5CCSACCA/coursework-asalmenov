import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = "data/predictions.db"


def _get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename   TEXT NOT NULL,
            label      TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_prediction(filename: str, label: str, confidence: float) -> None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO predictions (filename, label, confidence, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (filename, label, float(confidence), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def list_predictions(limit: int = 50) -> List[Dict[str, Any]]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, filename, label, confidence, created_at
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]