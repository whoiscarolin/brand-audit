"""
Pydantic v2 схемы для sentiment эндпоинтов.
"""
from pydantic import BaseModel, Field


class SentimentResult(BaseModel):
    """Результат анализа одного текста."""
    label: str = Field(..., examples=["positive"])
    positive: float = Field(..., ge=0.0, le=1.0)
    negative: float = Field(..., ge=0.0, le=1.0)
    neutral: float = Field(..., ge=0.0, le=1.0)


class SentimentRunResponse(BaseModel):
    """Ответ после запуска sentiment pipeline для бренда."""
    brand_id: int
    processed: int
    skipped: int
    total: int


class SentimentSummary(BaseModel):
    """Агрегированная аналитика тональности по бренду."""
    brand_id: int
    total_analyzed: int
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_pct: float = Field(..., description="% позитивных отзывов")
    negative_pct: float = Field(..., description="% негативных отзывов")
    neutral_pct: float = Field(..., description="% нейтральных отзывов")
    avg_positive: float = Field(..., description="Средний score позитивности")
    avg_negative: float = Field(..., description="Средний score негативности")
    avg_neutral: float = Field(..., description="Средний score нейтральности")
    avg_rating: float | None = Field(None, description="Средний рейтинг (если есть)")
