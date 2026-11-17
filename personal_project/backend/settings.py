"""Settings, read from environment variables (or a .env file in the project root)."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]  # project root (the folder that contains backend/)
load_dotenv(BASE_DIR / ".env")


def _csv(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


# Trained drone weights. If this file is missing, the app falls back to generic YOLO
# weights so you can test the API, but those will NOT detect drones reliably.
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "models" / "drone.pt"))
FALLBACK_WEIGHTS = os.getenv("FALLBACK_WEIGHTS", "yolov8n.pt")

# Larger values (960, 1280) help with small, distant drones but run slower.
IMG_SIZE = int(os.getenv("IMG_SIZE", "640"))
DEFAULT_CONFIDENCE = float(os.getenv("DEFAULT_CONFIDENCE", "0.25"))

# Class names in your trained model that count as a drone (case-insensitive).
DRONE_LABELS = {label.lower() for label in _csv("DRONE_LABELS", "drone,uav")}

DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'drone_detection.db').as_posix()}"
)

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

# Which origins may call the API from a browser. "*" is fine for local development.
CORS_ORIGINS = _csv("CORS_ORIGINS", "*")