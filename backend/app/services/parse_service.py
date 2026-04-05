"""
app/services/parse_service.py — оркестратор парсинга.

Источники:
- Яндекс Карты (HTML, BS4) — рабочий
- 2GIS API — временно недоступен (403), оставлен как заглушка
"""
import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.review import ReviewCreate
from app.services import review_service
from app.services.parser.yandex import YandexMapsParser

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    brand_id: int
    total_parsed: int
    saved: int
    sources: dict[str, int]
    errors: list[str]


async def run_parsing(
    db: AsyncSession,
    brand_id: int,
    yandex_org_url: str | None = None,
    max_per_source: int = 50,
) -> ParseResult:
    """
    Запускает парсинг для бренда.

    Args:
        db: AsyncSession
        brand_id: ID бренда в нашей БД
        yandex_org_url: полный URL организации на Яндекс Картах
        max_per_source: максимум отзывов с каждого источника
    """
    all_reviews: list[ReviewCreate] = []
    sources_count: dict[str, int] = {}
    errors: list[str] = []

    # ── Яндекс Карты ──────────────────────────────────────────────────────────
    if yandex_org_url:
        try:
            parser = YandexMapsParser(org_url=yandex_org_url, max_reviews=max_per_source)
            parsed = parser.run()
            converted = _to_review_create(parsed, brand_id)
            all_reviews.extend(converted)
            sources_count["yandex_maps"] = len(converted)
            logger.info(f"Яндекс: собрано {len(converted)} отзывов")
        except Exception as e:
            msg = f"Яндекс парсер упал: {e}"
            logger.error(msg)
            errors.append(msg)

    # ── Сохраняем в БД ────────────────────────────────────────────────────────
    saved = 0
    if all_reviews:
        try:
            created = await review_service.create_reviews_bulk(db, all_reviews)
            saved = len(created)
            logger.info(f"Сохранено в БД: {saved} отзывов для brand_id={brand_id}")
        except Exception as e:
            msg = f"Ошибка сохранения в БД: {e}"
            logger.error(msg)
            errors.append(msg)

    return ParseResult(
        brand_id=brand_id,
        total_parsed=len(all_reviews),
        saved=saved,
        sources=sources_count,
        errors=errors,
    )


def _to_review_create(parsed_reviews, brand_id: int) -> list[ReviewCreate]:
    result = []
    for pr in parsed_reviews:
        try:
            result.append(ReviewCreate(
                brand_id=brand_id,
                source=pr.source,
                text=pr.text,
                rating=pr.rating,
                author=pr.author,
                reviewed_at=pr.reviewed_at,
            ))
        except Exception as e:
            logger.warning(f"Не удалось конвертировать отзыв: {e}")
    return result
