"""
app/services/review_service.py — бизнес-логика работы с отзывами.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import ReviewCreate


async def get_reviews(
    db: AsyncSession,
    brand_id: int | None = None,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Review]:
    """
    Возвращает отзывы с опциональной фильтрацией по brand_id и source.
    Поддерживает пагинацию через limit/offset.
    """
    stmt = select(Review).order_by(Review.created_at.desc())

    if brand_id is not None:
        stmt = stmt.where(Review.brand_id == brand_id)
    if source is not None:
        stmt = stmt.where(Review.source == source)

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_review_by_id(db: AsyncSession, review_id: int) -> Review | None:
    """Возвращает отзыв по ID или None."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    return result.scalar_one_or_none()


async def create_review(db: AsyncSession, data: ReviewCreate) -> Review:
    """Создаёт один отзыв."""
    review = Review(**data.model_dump())
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


async def create_reviews_bulk(
    db: AsyncSession, items: list[ReviewCreate]
) -> list[Review]:
    """
    Массовое создание отзывов — используется парсером.
    Все записи добавляются в одной транзакции.
    """
    reviews = [Review(**item.model_dump()) for item in items]
    db.add_all(reviews)
    await db.flush()
    for r in reviews:
        await db.refresh(r)
    return reviews


async def delete_review(db: AsyncSession, review_id: int) -> bool:
    """Удаляет отзыв. Возвращает True если удалён."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if review is None:
        return False
    await db.delete(review)
    return True
