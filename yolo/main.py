import io
import os

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from ultralytics import YOLO

MODEL_PATH = "yolov8n.pt"
PORT = 8000

app = FastAPI(
    title="YOLO API",
    description="API REST exposant un modele YOLO pour la detection d'objets sur une image.",
    version="1.0.0",
)
model = YOLO(MODEL_PATH)


def _read_image(raw_bytes: bytes) -> np.ndarray:
    array = np.frombuffer(raw_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Fichier image invalide.")
    return image


@app.get("/")
def root():
    return {
        "message": "API YOLO disponible.",
        "routes": {
            "POST /detect": "renvoie les annotations detectees au format JSON",
            "POST /detect/image": "renvoie l'image annotee (boites + labels) en JPEG",
        },
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    image = _read_image(await file.read())
    results = model(image)[0]

    detections = [
        {
            "class_id": int(box.cls[0]),
            "class_name": model.names[int(box.cls[0])],
            "confidence": round(float(box.conf[0]), 4),
            "bbox": [round(v, 2) for v in box.xyxy[0].tolist()],
        }
        for box in results.boxes
    ]

    return {"count": len(detections), "detections": detections}


@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    image = _read_image(await file.read())
    results = model(image)[0]
    annotated = results.plot()  # image (numpy array BGR) avec boites + labels dessines

    success, buffer = cv2.imencode(".jpg", annotated)
    if not success:
        raise HTTPException(status_code=500, detail="Echec de l'encodage de l'image annotee.")

    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")


def _start_ngrok_tunnel() -> None:
    from pyngrok import ngrok

    tunnel = ngrok.connect(PORT)
    print(f"Tunnel ngrok public : {tunnel.public_url}")


if __name__ == "__main__":
    if os.getenv("USE_NGROK", "false").lower() == "true":
        _start_ngrok_tunnel()

    uvicorn.run(app, host="0.0.0.0", port=PORT)
