import io, os, numpy as np, torch
from PIL import Image
from ultralytics import YOLO

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
torch.set_num_threads(4)

class YoloService:
    def __init__(self, weights: str = "yolo11n.pt"):
        self.model = YOLO(weights)
        self.class_names = self.model.names

    @staticmethod
    def _to_numpy(image_bytes: bytes) -> np.ndarray:
        return np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))

    def predict(self, image_bytes: bytes, conf=0.25, iou=0.45, imgsz=640):
        np_img = self._to_numpy(image_bytes)
        results = self.model.predict(source=np_img, imgsz=imgsz, conf=conf, iou=iou,
                                     device="cpu", verbose=False)
        dets = []
        r = results[0]
        if r.boxes is not None:
            for box, confv, cls in zip(r.boxes.xyxy.cpu().numpy(),
                                       r.boxes.conf.cpu().numpy(),
                                       r.boxes.cls.cpu().numpy().astype(int)):
                dets.append({
                    "label": self.class_names.get(cls, str(cls)),
                    "confidence": float(round(confv, 4)),
                    "box": [float(round(x, 2)) for x in box]
                })
        return {"detections": dets, "meta": {"imgsz": imgsz, "conf": conf, "iou": iou}}