"""Loads the YOLO model once and runs inference on images."""

import logging
import threading
import time

from PIL import Image
from ultralytics import YOLO

from . import settings

logger = logging.getLogger("detector")


class Detector:
    def __init__(self) -> None:
        if settings.MODEL_PATH.exists():
            self.weights = str(settings.MODEL_PATH)
            self.is_drone_model = True
        else:
            logger.warning(
                "Drone weights not found at %s - falling back to generic '%s'. "
                "Detections will NOT be drone-specific until you add trained weights.",
                settings.MODEL_PATH,
                settings.FALLBACK_WEIGHTS,
            )
            self.weights = settings.FALLBACK_WEIGHTS
            self.is_drone_model = False

        self.model = YOLO(self.weights)
        self._lock = threading.Lock()  # run one inference at a time on the shared model

    def predict(self, image: Image.Image, conf: float) -> tuple[list[dict], float]:
        """Return (objects, inference_ms). Each object has label, confidence and box."""
        with self._lock:
            start = time.perf_counter()
            result = self.model.predict(
                image, conf=conf, imgsz=settings.IMG_SIZE, verbose=False
            )[0]
            elapsed_ms = (time.perf_counter() - start) * 1000

        objects = []
        for box in result.boxes:
            x1, y1, x2, y2 = (round(v, 1) for v in box.xyxy[0].tolist())
            objects.append(
                {
                    "label": result.names[int(box.cls[0])],
                    "confidence": round(float(box.conf[0]), 4),
                    "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                }
            )
        return objects, round(elapsed_ms, 1)

    @staticmethod
    def contains_drone(objects: list[dict]) -> bool:
        return any(obj["label"].lower() in settings.DRONE_LABELS for obj in objects)
