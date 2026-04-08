"""
app/schemas/brand.py — Pydantic-схемы для бренда.

Разделяем схемы на:
- BrandCreate  — входные данные при создании (от клиента)
- BrandRead    — исходящие данные (клиенту)
- BrandSummary — лёгкая версия для списков (без вложенных отзывов)

Это стандартный паттерн FastAPI: ORM-модель ≠ схема API.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class BrandCreate(BaseModel):
    """Данные для создания нового бренда."""
    name: str = Field(..., min_length=1, max_length=255, examples=["Кофейня Прага"])
    category: str | None = Field(None, max_length=100, examples=["cafe"])
    city: str | None = Field(None, max_length=100, examples=["Москва"])
    source_url: str | None = Field(None, max_length=512, examples=["https://2gis.ru/..."])


class BrandUpdate(BaseModel):
    """Частичное обновление бренда (все поля опциональны)."""
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    source_url: str | None = Field(None, max_length=512)


class BrandSummary(BaseModel):
    """Краткое представление бренда для списков."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str | None
    city: str | None
    created_at: datetime
    review_count: int = 0
    avg_rating: float | None = None

class BrandRead(BrandSummary):
    """Полное представление бренда (используется в GET /brands/{id})."""
    source_url: str | None
    # Количество отзывов — вычисляется в роутере, не в ORM
    review_count: int = 0
