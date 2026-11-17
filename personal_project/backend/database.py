"""SQLAlchemy engine, session dependency, and the table that stores detection history."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .settings import DATABASE_URL

# SQLite needs this flag because FastAPI handles requests in worker threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Detection(Base):
    """One scanned image and what the model found in it (boxes are stored as JSON)."""

    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    filename: Mapped[Optional[str]]
    image_width: Mapped[int]
    image_height: Mapped[int]
    drone_detected: Mapped[bool] = mapped_column(index=True)
    detection_count: Mapped[int]
    max_confidence: Mapped[Optional[float]]
    inference_ms: Mapped[float]
    objects: Mapped[list] = mapped_column(JSON)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()