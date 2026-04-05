"""
app/schemas/review.py — Pydantic-схемы для отзывов.

ReviewCreate  — входные данные (от парсера или клиента)
ReviewRead    — исходящие данные (клиенту)
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    brand_id: int
    source: str = Field(..., max_length=50, examples=["2gis", "yandex_maps"])
    text: str | None = Field(None)
    rating: float | None = Field(None, ge=1.0, le=5.0)
    author: str | None = Field(None, max_length=255)
    reviewed_at: datetime | None = None


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    source: str
    text: str | None
    rating: float | None
    author: str | None
    reviewed_at: datetime | None
    sentiment_label: str | None
    sentiment_positive: float | None
    sentiment_negative: float | None
    sentiment_neutral: float | None
    created_at: datetime
