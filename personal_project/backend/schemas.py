"""Pydantic models that define the JSON the API returns."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class BoundingBox(BaseModel):
    """Pixel coordinates: top-left (x1, y1) and bottom-right (x2, y2)."""

    x1: float
    y1: float
    x2: float
    y2: float


class DetectedObject(BaseModel):
    label: str
    confidence: float
    box: BoundingBox


class DetectionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    filename: Optional[str]
    image_width: int
    image_height: int
    drone_detected: bool
    detection_count: int
    max_confidence: Optional[float]
    inference_ms: float
    objects: list[DetectedObject]

    @field_validator("created_at")
    @classmethod
    def assume_utc(cls, value: datetime) -> datetime:
        # SQLite drops timezone info; timestamps are stored in UTC, so put it back.
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)