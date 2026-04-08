"""
app/routers/brands.py — CRUD-эндпоинты для брендов.

Роутер отвечает только за HTTP-слой:
принять запрос → вызвать сервис → вернуть ответ.
Вся логика — в services/brand_service.py.

Эндпоинты:
    GET    /brands          — список всех брендов
    POST   /brands          — создать бренд
    GET    /brands/{id}     — бренд по ID
    PATCH  /brands/{id}     — обновить бренд
    DELETE /brands/{id}     — удалить бренд
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.brand import BrandCreate, BrandUpdate, BrandRead, BrandSummary
from app.services import brand_service

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get(
    "",
    response_model=list[BrandSummary],
    summary="Список всех брендов",
)
async def list_brands(db: AsyncSession = Depends(get_db)) -> list[BrandSummary]:
    """Возвращает все бренды с количеством отзывов, сортировка по дате добавления."""
    rows = await brand_service.get_all_brands(db)
    result = []
    for brand, review_count, avg_rating in rows:
        summary = BrandSummary.model_validate(brand)
        summary.review_count = review_count
        summary.avg_rating = round(avg_rating, 2) if avg_rating else None
        result.append(summary)
    return result
        



@router.post(
    "",
    response_model=BrandRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бренд",
)
async def create_brand(
    data: BrandCreate,
    db: AsyncSession = Depends(get_db),
) -> BrandRead:
    """Создаёт новый бренд. Используется парсером и (в будущем) формой на дашборде."""
    brand = await brand_service.create_brand(db, data)
    return BrandRead.model_validate(brand)


@router.get(
    "/{brand_id}",
    response_model=BrandRead,
    summary="Получить бренд по ID",
)
async def get_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
) -> BrandRead:
    """Возвращает полную информацию о бренде включая количество отзывов."""
    row = await brand_service.get_brand_by_id(db, brand_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бренд с id={brand_id} не найден",
        )
    brand, review_count = row
    result = BrandRead.model_validate(brand)
    result.review_count = review_count
    return result


@router.patch(
    "/{brand_id}",
    response_model=BrandRead,
    summary="Обновить бренд",
)
async def update_brand(
    brand_id: int,
    data: BrandUpdate,
    db: AsyncSession = Depends(get_db),
) -> BrandRead:
    """Частичное обновление — передавай только те поля, которые нужно изменить."""
    brand = await brand_service.update_brand(db, brand_id, data)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бренд с id={brand_id} не найден",
        )
    return BrandRead.model_validate(brand)


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить бренд",
)
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Удаляет бренд и каскадно все его отзывы."""
    deleted = await brand_service.delete_brand(db, brand_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бренд с id={brand_id} не найден",
        )
