"""
app/routers/report.py
Endpoint: GET /brands/{brand_id}/report/download
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.brand import Brand
from app.models.review import Review
from app.services.report_service import generate_pdf
from app.services.sentiment_service import get_sentiment_summary

router = APIRouter(prefix="/brands", tags=["report"])


@router.get(
    "/{brand_id}/report/download",
    summary="Скачать PDF-отчёт по бренду",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF-отчёт по бренду",
        },
        404: {"description": "Бренд не найден"},
    },
)
async def download_report(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Генерирует и возвращает PDF-отчёт по бренду.
    Включает сводку, анализ тональности и таблицу отзывов.
    """
    # Получаем бренд
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Бренд {brand_id} не найден.")

    # Получаем отзывы
    result = await db.execute(
        select(Review).where(Review.brand_id == brand_id)
    )
    reviews = list(result.scalars().all())

    if not reviews:
        raise HTTPException(
            status_code=404,
            detail=f"Отзывы для бренда {brand_id} не найдены.",
        )

    # Получаем агрегацию тональности
    summary = await get_sentiment_summary(brand_id, db)

    # Генерируем PDF
    pdf_bytes = generate_pdf(brand, reviews, summary)

    filename = f"brand_audit_{brand_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf",
        },
    )