"""
app/routers/parser.py — эндпоинт запуска парсинга.

POST /parser/run — запускает парсинг для бренда и сохраняет отзывы в БД.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import brand_service
from app.services.parse_service import run_parsing

router = APIRouter(prefix="/parser", tags=["parser"])


class ParseRequest(BaseModel):
    brand_id: int
    yandex_org_url: str | None = None
    max_per_source: int = 50


class ParseResponse(BaseModel):
    brand_id: int
    total_parsed: int
    saved: int
    sources: dict[str, int]
    errors: list[str]
    message: str


@router.post("/run", response_model=ParseResponse, summary="Запустить парсинг для бренда")
async def run_parser(
    data: ParseRequest,
    db: AsyncSession = Depends(get_db),
) -> ParseResponse:
    """
    Запускает парсинг отзывов для указанного бренда.

    - **brand_id** — ID бренда в нашей БД
    - **yandex_org_url** — полный URL организации на Яндекс Картах
    - **max_per_source** — максимум отзывов с каждого источника

    Пример yandex_org_url:
        https://yandex.com/maps/org/ludilove/157741958403/
    """
    brand_row = await brand_service.get_brand_by_id(db, data.brand_id)
    if brand_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бренд с id={data.brand_id} не найден",
        )

    if not data.yandex_org_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Укажи yandex_org_url",
        )

    result = await run_parsing(
        db=db,
        brand_id=data.brand_id,
        yandex_org_url=data.yandex_org_url,
        max_per_source=data.max_per_source,
    )

    message = f"Готово: собрано {result.total_parsed}, сохранено {result.saved}"
    if result.errors:
        message += f" | Ошибки: {len(result.errors)}"

    return ParseResponse(
        brand_id=result.brand_id,
        total_parsed=result.total_parsed,
        saved=result.saved,
        sources=result.sources,
        errors=result.errors,
        message=message,
    )
