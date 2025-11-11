import argparse
from pathlib import Path
from services.yolo.model import YoloService

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    args = ap.parse_args()

    data = Path(args.image).read_bytes()
    svc = YoloService()
    print(svc.predict(data))

if __name__ == "__main__":
    main()