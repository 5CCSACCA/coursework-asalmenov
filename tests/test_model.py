from pathlib import Path
from services.yolo.model import YoloService


def test_yolo_predict_returns_expected_structure():
    svc = YoloService()
    sample = Path("docs/examples/apple.jpg")
    out = svc.predict(sample.read_bytes())

    assert isinstance(out, dict)
    assert "detections" in out
    assert "meta" in out
    assert isinstance(out["detections"], list)

    if out["detections"]:
        first = out["detections"][0]
        assert "label" in first
        assert "confidence" in first
        assert "box" in first