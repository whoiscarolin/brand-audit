"""
app/services/brand_service.py — бизнес-логика работы с брендами.

Роутер вызывает сервис, сервис работает с БД.
Такое разделение позволяет легко тестировать логику отдельно от HTTP-слоя.
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.models.review import Review
from app.schemas.brand import BrandCreate, BrandUpdate


async def get_all_brands(db: AsyncSession) -> list[tuple[Brand, int]]:
    """
    Возвращает список всех брендов с количеством отзывов каждого.
    Использует LEFT JOIN + COUNT — один запрос вместо N+1.
    """
    stmt = (
        select(Brand, func.count(Review.id).label("review_count"))
        .outerjoin(Review, Review.brand_id == Brand.id)
        .group_by(Brand.id)
        .order_by(Brand.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.all()


async def get_brand_by_id(db: AsyncSession, brand_id: int) -> tuple[Brand, int] | None:
    """Возвращает бренд по ID с количеством отзывов. None если не найден."""
    stmt = (
        select(Brand, func.count(Review.id).label("review_count"))
        .outerjoin(Review, Review.brand_id == Brand.id)
        .where(Brand.id == brand_id)
        .group_by(Brand.id)
    )
    result = await db.execute(stmt)
    return result.first()


async def create_brand(db: AsyncSession, data: BrandCreate) -> Brand:
    """Создаёт новый бренд и сохраняет в БД."""
    brand = Brand(**data.model_dump())
    db.add(brand)
    await db.flush()   # получаем id до commit
    await db.refresh(brand)
    return brand


async def update_brand(
    db: AsyncSession, brand_id: int, data: BrandUpdate
) -> Brand | None:
    """
    Частичное обновление бренда (PATCH-семантика).
    Обновляем только те поля, которые явно переданы (не None).
    """
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if brand is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)

    await db.flush()
    await db.refresh(brand)
    return brand


async def delete_brand(db: AsyncSession, brand_id: int) -> bool:
    """Удаляет бренд. Возвращает True если удалён, False если не найден."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if brand is None:
        return False
    await db.delete(brand)
    return True
