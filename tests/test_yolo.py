from pathlib import Path
from services.yolo.model import YoloService

def test_yolo_inference_runs_on_cpu():
    svc = YoloService()
    sample = Path("docs/examples/apple.jpg")
    out = svc.predict(sample.read_bytes())
    assert "detections" in out
    assert isinstance(out["detections"], list)