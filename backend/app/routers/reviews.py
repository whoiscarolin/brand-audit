"""
app/routers/reviews.py — эндпоинты для отзывов.

Эндпоинты:
    GET    /reviews              — список отзывов (фильтры: brand_id, source)
    POST   /reviews              — создать один отзыв
    POST   /reviews/bulk         — массовое создание (для парсера)
    GET    /reviews/{id}         — отзыв по ID
    DELETE /reviews/{id}         — удалить отзыв
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.review import ReviewCreate, ReviewRead
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewRead], summary="Список отзывов")
async def list_reviews(
    brand_id: int | None = Query(None, description="Фильтр по бренду"),
    source: str | None = Query(None, description="Фильтр по источнику: 2gis, yandex_maps..."),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ReviewRead]:
    """
    Возвращает отзывы с пагинацией.
    Примеры: /reviews?brand_id=1  /reviews?source=2gis&limit=20
    """
    reviews = await review_service.get_reviews(db, brand_id, source, limit, offset)
    return [ReviewRead.model_validate(r) for r in reviews]


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED, summary="Создать отзыв")
async def create_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
) -> ReviewRead:
    """Создаёт один отзыв. Для массовой загрузки используй /reviews/bulk."""
    review = await review_service.create_review(db, data)
    return ReviewRead.model_validate(review)


@router.post(
    "/bulk",
    response_model=list[ReviewRead],
    status_code=status.HTTP_201_CREATED,
    summary="Массовое создание отзывов",
)
async def create_reviews_bulk(
    items: list[ReviewCreate],
    db: AsyncSession = Depends(get_db),
) -> list[ReviewRead]:
    """
    Принимает список отзывов и сохраняет все в одной транзакции.
    Используется парсером после сбора данных.
    """
    if not items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Список отзывов не может быть пустым",
        )
    reviews = await review_service.create_reviews_bulk(db, items)
    return [ReviewRead.model_validate(r) for r in reviews]


@router.get("/{review_id}", response_model=ReviewRead, summary="Отзыв по ID")
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReviewRead:
    review = await review_service.get_review_by_id(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail=f"Отзыв с id={review_id} не найден")
    return ReviewRead.model_validate(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить отзыв")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await review_service.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Отзыв с id={review_id} не найден")
