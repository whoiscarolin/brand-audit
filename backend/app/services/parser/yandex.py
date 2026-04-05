"""
app/services/parser/yandex.py — парсер отзывов с Яндекс Карт (HTML).

Парсим HTML страницы организации на Яндекс Картах.
Яндекс вставляет первые 3 отзыва прямо в HTML — их и берём.
Остальные грузятся через JS (для портфолио 3 отзыва достаточно).

Как найти URL организации:
1. Открой yandex.com/maps
2. Найди заведение
3. Скопируй URL вида: yandex.com/maps/org/{name}/{id}/
"""
import logging
from datetime import datetime

from bs4 import BeautifulSoup

from app.services.parser.base import BaseParser, ParsedReview

logger = logging.getLogger(__name__)


class YandexMapsParser(BaseParser):
    """
    Парсер отзывов с Яндекс Карт через HTML (BeautifulSoup).

    Принимает полный URL страницы организации на Яндекс Картах.

    Пример:
        parser = YandexMapsParser(
            org_url="https://yandex.com/maps/org/ludilove/157741958403/"
        )
        reviews = parser.run()
    """

    SOURCE = "yandex_maps"

    def __init__(self, org_url: str, max_reviews: int = 50):
        super().__init__(brand_url=org_url, max_reviews=max_reviews)
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })

    def fetch_reviews(self) -> list[ParsedReview]:
        try:
            response = self._get(self.brand_url)
        except Exception as e:
            logger.error(f"[Yandex] Не удалось загрузить страницу: {e}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(".business-review-view")

        if not items:
            logger.warning("[Yandex] Отзывы не найдены — возможно структура страницы изменилась")
            return []

        logger.info(f"[Yandex] Найдено отзывов в HTML: {len(items)}")

        reviews = []
        for item in items:
            parsed = self._parse_item(item)
            if parsed:
                reviews.append(parsed)

        return reviews

    def _parse_item(self, item) -> ParsedReview | None:
        """Парсит один блок .business-review-view."""
        try:
            author_tag = item.select_one("[itemprop=name]")
            author = author_tag.get_text(strip=True) if author_tag else None

            rating_tag = item.select_one("[itemprop=ratingValue]")
            rating = float(rating_tag.get("content")) if rating_tag else None

            text_tag = item.select_one("[itemprop=reviewBody]") or \
                       item.select_one(".business-review-view__body-text") or \
                       item.select_one(".business-review-view__comment")
            text = text_tag.get_text(strip=True) if text_tag else None

            reviewed_at = None
            date_tag = item.select_one("[itemprop=datePublished]")
            if date_tag:
                date_str = date_tag.get("content")
                if date_str:
                    try:
                        reviewed_at = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

            return ParsedReview(
                source=self.SOURCE,
                text=text,
                rating=rating,
                author=author,
                reviewed_at=reviewed_at,
            )
        except Exception as e:
            logger.warning(f"[Yandex] Ошибка парсинга отзыва: {e}")
            return None
