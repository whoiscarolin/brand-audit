"""
Роутер: /brands/{brand_id}/sentiment
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.sentiment import SentimentRunResponse, SentimentSummary
from app.services.sentiment_service import (
    get_sentiment_summary,
    run_sentiment_for_brand,
)

from app.dependencies import get_api_key
from fastapi import Depends

router = APIRouter(
    prefix="/brands",
    tags=["sentiment"],
    dependencies=[Depends(get_api_key)],
)


@router.post(
    "/{brand_id}/sentiment/run",
    response_model=SentimentRunResponse,
    summary="Запустить sentiment analysis для всех отзывов бренда",
)
async def run_sentiment(
    brand_id: int,
    overwrite: bool = Query(False, description="Перезаписать уже размеченные отзывы"),
    db: AsyncSession = Depends(get_db),
):
    """
    Прогоняет все отзывы бренда через модель тональности.
    Сохраняет результат в поля sentiment_* таблицы reviews.
    """
    result = await run_sentiment_for_brand(brand_id, db, overwrite=overwrite)

    if result["total"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Отзывы для бренда {brand_id} не найдены.",
        )

    return SentimentRunResponse(brand_id=brand_id, **result)


@router.get(
    "/{brand_id}/sentiment",
    response_model=SentimentSummary,
    summary="Получить агрегированную аналитику тональности бренда",
)
async def get_sentiment(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает агрегированные метрики тональности:
    счётчики, проценты, средние score, средний рейтинг.
    """
    summary = await get_sentiment_summary(brand_id, db)

    if summary["total_analyzed"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Нет размеченных отзывов для бренда {brand_id}. "
                   f"Сначала вызови POST /brands/{brand_id}/sentiment/run",
        )

    return SentimentSummary(**summary)
