"""FastAPI app: upload an image, get drone detections back, browse the saved history.

Run from the project root:  uvicorn backend.main:app --reload
Interactive docs:           http://127.0.0.1:8000/docs
"""

import io
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import settings
from .database import Base, Detection, engine, get_db
from .detector import Detector
from .schemas import DetectionResult


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # creates the SQLite file and tables on first run
    app.state.detector = Detector()  # load the model once at startup, not on every request
    yield


app = FastAPI(title="Drone Detection API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_detector(request: Request) -> Detector:
    return request.app.state.detector


@app.get("/health")
def health(detector: Detector = Depends(get_detector)):
    """Shows which weights are loaded and whether they are the trained drone model."""
    return {
        "status": "ok",
        "weights": detector.weights,
        "drone_model_loaded": detector.is_drone_model,
    }


# Plain `def` (not `async def`) on purpose: FastAPI runs it in a worker thread,
# so the slow model call doesn't block other requests.
@app.post("/detect", response_model=DetectionResult)
def detect(
    file: UploadFile = File(...),
    conf: float = Query(settings.DEFAULT_CONFIDENCE, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    detector: Detector = Depends(get_detector),
):
    """Run detection on one uploaded image and save the result to the database."""
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    data = file.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413, detail=f"Image is larger than {settings.MAX_UPLOAD_MB} MB"
        )

    try:
        # exif_transpose applies the camera's rotation, so box coordinates match what people see
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status_code=400, detail="File is not a valid image")

    objects, inference_ms = detector.predict(image, conf)

    record = Detection(
        filename=file.filename,
        image_width=image.width,
        image_height=image.height,
        drone_detected=detector.contains_drone(objects),
        detection_count=len(objects),
        max_confidence=max((o["confidence"] for o in objects), default=None),
        inference_ms=inference_ms,
        objects=objects,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/detections", response_model=list[DetectionResult])
def list_detections(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    only_drones: bool = False,
    db: Session = Depends(get_db),
):
    """Saved detections, newest first."""
    stmt = select(Detection)
    if only_drones:
        stmt = stmt.where(Detection.drone_detected.is_(True))
    stmt = stmt.order_by(Detection.id.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@app.get("/detections/{detection_id}", response_model=DetectionResult)
def get_detection(detection_id: int, db: Session = Depends(get_db)):
    record = db.get(Detection, detection_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return record


@app.delete("/detections/{detection_id}", status_code=204)
def delete_detection(detection_id: int, db: Session = Depends(get_db)):
    record = db.get(Detection, detection_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    db.delete(record)
    db.commit()
    return Response(status_code=204)
