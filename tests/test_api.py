from fastapi.testclient import TestClient

from services.yolo import api
from services.yolo.auth import get_current_user

class DummyYoloService:
    def predict(self, data: bytes):
        return {
            "detections": [
                {
                    "label": "apple",
                    "confidence": 0.99,
                    "box": [0, 0, 10, 10],
                }
            ],
            "meta": {
                "imgsz": 640,
                "conf": 0.25,
                "iou": 0.45,
            },
        }


def test_health_endpoint_works():
    client = TestClient(api.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_protected_endpoint_requires_auth():
    client = TestClient(api.app)
    resp = client.get("/predictions")
    assert resp.status_code == 401


def test_predict_with_dummy_yolo_and_fake_auth(tmp_path, monkeypatch):
    api.app.dependency_overrides[get_current_user] = lambda: {"uid": "test-user"}

    api.svc = DummyYoloService()

    client = TestClient(api.app)

    fake_img_path = tmp_path / "test.jpg"
    fake_img_path.write_bytes(b"fake image bytes")

    with fake_img_path.open("rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        resp = client.post("/predict", files=files)

    assert resp.status_code == 200
    data = resp.json()
    assert "detections" in data
    assert len(data["detections"]) == 1
    assert data["detections"][0]["label"] == "apple"

    api.app.dependency_overrides.clear()