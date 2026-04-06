"""
Sentiment analysis service.
Использует blanchefort/rubert-base-cased-sentiment через transformers.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


if TYPE_CHECKING:
    from app.models.review import Review

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Модель загружается один раз при старте приложения (singleton)
# ---------------------------------------------------------------------------
_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        import os
        if os.getenv("USE_ML_SENTIMENT", "false").lower() != "true":
            return None
        from transformers import pipeline
        logger.info("Loading sentiment model...")
        _classifier = pipeline(
            "text-classification",
            model="blanchefort/rubert-base-cased-sentiment",
        )
        logger.info("Sentiment model loaded.")
    return _classifier


# ---------------------------------------------------------------------------
# Анализ одного текста
# ---------------------------------------------------------------------------
LABEL_MAP = {
    "POSITIVE": "positive",
    "NEGATIVE": "negative",
    "NEUTRAL":  "neutral",
}


def _analyze_heuristic(rating: float | None) -> dict:
    """Эвристика по рейтингу — используется когда USE_ML_SENTIMENT=false."""
    if rating is None:
        return {"label": "neutral", "positive": 0.0, "negative": 0.0, "neutral": 1.0}
    if rating >= 4:
        return {"label": "positive", "positive": 0.9, "negative": 0.05, "neutral": 0.05}
    if rating == 3:
        return {"label": "neutral", "positive": 0.2, "negative": 0.2, "neutral": 0.6}
    return {"label": "negative", "positive": 0.05, "negative": 0.9, "neutral": 0.05}


def analyze_text(text: str, rating: float | None = None) -> dict:
    """
    Возвращает dict с ключами: label, positive, negative, neutral.
    Если USE_ML_SENTIMENT=true — используем rubert модель.
    Если USE_ML_SENTIMENT=false — эвристика по рейтингу.
    """
    import os
    use_ml = os.getenv("USE_ML_SENTIMENT", "false").lower() == "true"

    if not use_ml:
        return _analyze_heuristic(rating)

    if not text or not text.strip():
        return {
            "label": "neutral",
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
        }

    classifier = get_classifier()
    results = classifier(text[:512], top_k=3)

    scores = {"POSITIVE": 0.0, "NEGATIVE": 0.0, "NEUTRAL": 0.0}
    for item in results:
        scores[item["label"]] = round(item["score"], 6)

    best_label = max(scores, key=scores.__getitem__)

    return {
        "label":    LABEL_MAP[best_label],
        "positive": scores["POSITIVE"],
        "negative": scores["NEGATIVE"],
        "neutral":  scores["NEUTRAL"],
    }


# ---------------------------------------------------------------------------
# Пакетная обработка отзывов бренда
# ---------------------------------------------------------------------------
async def run_sentiment_for_brand(
    brand_id: int,
    db: AsyncSession,
    overwrite: bool = False,
) -> dict:
    """
    Прогоняет sentiment для всех отзывов бренда у которых нет метки
    (или overwrite=True — перезаписать всё).

    Возвращает статистику: сколько обработано / пропущено.
    """
    from app.models.review import Review  # локальный импорт во избежание цикла

    stmt = select(Review).where(Review.brand_id == brand_id)
    result = await db.execute(stmt)
    reviews: list[Review] = list(result.scalars().all())

    processed = 0
    skipped = 0

    for review in reviews:
        # Пропускаем уже размеченные если overwrite=False
        if not overwrite and review.sentiment_label is not None:
            skipped += 1
            continue

        if not review.text:
            skipped += 1
            continue

        sentiment = analyze_text(review.text, rating=review.rating)

        review.sentiment_label    = sentiment["label"]
        review.sentiment_positive = sentiment["positive"]
        review.sentiment_negative = sentiment["negative"]
        review.sentiment_neutral  = sentiment["neutral"]

        processed += 1

    await db.commit()

    logger.info(
        "Sentiment done for brand_id=%s: processed=%s skipped=%s",
        brand_id, processed, skipped,
    )

    return {"processed": processed, "skipped": skipped, "total": len(reviews)}


# ---------------------------------------------------------------------------
# Агрегация метрик по бренду
# ---------------------------------------------------------------------------
async def get_sentiment_summary(brand_id: int, db: AsyncSession) -> dict:
    """
    Возвращает агрегированные метрики тональности для бренда.
    """
    from app.models.review import Review

    stmt = select(Review).where(
        Review.brand_id == brand_id,
        Review.sentiment_label.is_not(None),
    )
    result = await db.execute(stmt)
    reviews: list[Review] = list(result.scalars().all())

    if not reviews:
        return {
            "brand_id":        brand_id,
            "total_analyzed":  0,
            "positive_count":  0,
            "negative_count":  0,
            "neutral_count":   0,
            "positive_pct":    0.0,
            "negative_pct":    0.0,
            "neutral_pct":     0.0,
            "avg_positive":    0.0,
            "avg_negative":    0.0,
            "avg_neutral":     0.0,
            "avg_rating":      None,
        }

    total = len(reviews)
    pos = sum(1 for r in reviews if r.sentiment_label == "positive")
    neg = sum(1 for r in reviews if r.sentiment_label == "negative")
    neu = sum(1 for r in reviews if r.sentiment_label == "neutral")

    avg_pos = sum(r.sentiment_positive or 0 for r in reviews) / total
    avg_neg = sum(r.sentiment_negative or 0 for r in reviews) / total
    avg_neu = sum(r.sentiment_neutral  or 0 for r in reviews) / total

    rated = [r.rating for r in reviews if r.rating is not None]
    avg_rating = round(sum(rated) / len(rated), 2) if rated else None

    return {
        "brand_id":       brand_id,
        "total_analyzed": total,
        "positive_count": pos,
        "negative_count": neg,
        "neutral_count":  neu,
        "positive_pct":   round(pos / total * 100, 1),
        "negative_pct":   round(neg / total * 100, 1),
        "neutral_pct":    round(neu / total * 100, 1),
        "avg_positive":   round(avg_pos, 4),
        "avg_negative":   round(avg_neg, 4),
        "avg_neutral":    round(avg_neu, 4),
        "avg_rating":     avg_rating,
    }
