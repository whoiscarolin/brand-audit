"""
app/services/parser/twogis.py — парсер отзывов с 2GIS.

2GIS грузит отзывы через внутренний API — мы его и используем.
Это публичный незащищённый эндпоинт, без авторизации.

Как найти URL для конкретного заведения:
1. Открой страницу заведения на 2gis.ru
2. F12 → Network → фильтр "reviews"
3. Скопируй URL запроса к API (начинается с api.2gis.ru)

Или используй format: https://2gis.ru/city/firm_id
"""
import logging
from datetime import datetime

from app.services.parser.base import BaseParser, ParsedReview

logger = logging.getLogger(__name__)

# Публичный API 2GIS для отзывов
TWOGIS_API = "https://public-api.reviews.2gis.com/2.0/branches/{branch_id}/reviews"


class TwoGisParser(BaseParser):
    """
    Парсер отзывов с 2GIS через публичный API отзывов.

    Принимает branch_id — числовой ID заведения на 2GIS.
    Найти его можно в URL страницы: 2gis.ru/city/firm/{branch_id}

    Пример:
        parser = TwoGisParser(branch_id="70000001037821488")
        reviews = parser.run()
    """

    SOURCE = "2gis"

    def __init__(self, branch_id: str, max_reviews: int = 50):
        # Передаём brand_url для совместимости с BaseParser
        super().__init__(
            brand_url=TWOGIS_API.format(branch_id=branch_id),
            max_reviews=max_reviews,
        )
        self.branch_id = branch_id

    def fetch_reviews(self) -> list[ParsedReview]:
        reviews = []
        page = 1
        limit = 20  # 2GIS отдаёт по 20 отзывов на страницу

        while len(reviews) < self.max_reviews:
            params = {
                "key": "37ruby",   # публичный ключ 2GIS API
                "limit": limit,
                "offset": (page - 1) * limit,
                "is_advertiser": "false",
                "fields": "meta.providers,meta.branch_rating,meta.branch_reviews_count",
                "sort_by": "date_edited",
                "locale": "ru_RU",
            }

            try:
                response = self._get(self.brand_url, params=params)
                data = response.json()
            except Exception as e:
                logger.warning(f"[2GIS] Ошибка запроса страницы {page}: {e}")
                break

            items = data.get("reviews", [])
            if not items:
                break  # больше отзывов нет

            for item in items:
                parsed = self._parse_item(item)
                if parsed:
                    reviews.append(parsed)

            # Проверяем есть ли следующая страница
            total = data.get("meta", {}).get("branch_reviews_count", 0)
            if page * limit >= total:
                break

            page += 1

        return reviews

    def _parse_item(self, item: dict) -> ParsedReview | None:
        """Конвертирует сырой объект отзыва 2GIS в ParsedReview."""
        try:
            text = item.get("text") or None
            rating = item.get("rating")
            author = item.get("user", {}).get("name") or None

            # Дата в формате ISO — парсим если есть
            reviewed_at = None
            date_str = item.get("date_edited") or item.get("date_created")
            if date_str:
                try:
                    reviewed_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    pass

            return ParsedReview(
                source=self.SOURCE,
                text=text,
                rating=float(rating) if rating is not None else None,
                author=author,
                reviewed_at=reviewed_at,
                raw=item,
            )
        except Exception as e:
            logger.warning(f"[2GIS] Не удалось распарсить отзыв: {e}")
            return None
