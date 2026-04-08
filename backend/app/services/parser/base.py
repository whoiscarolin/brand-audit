"""
app/services/parser/base.py — базовый класс для всех парсеров.

Каждый конкретный парсер (2GIS, Яндекс) наследуется отсюда
и реализует только метод fetch_reviews().
Вся общая логика (сессия, заголовки, задержки) — здесь.
"""
import time
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

import requests
from requests import Session

logger = logging.getLogger(__name__)

# Заголовки — имитируем обычный браузер
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class ParsedReview:
    """
    Унифицированный формат отзыва — одинаковый для всех парсеров.
    Потом конвертируется в ReviewCreate для сохранения в БД.
    """
    source: str                        # "2gis" | "yandex_maps"
    text: str | None
    rating: float | None
    author: str | None = None
    reviewed_at: datetime | None = None
    raw: dict = field(default_factory=dict)   # сырые данные для отладки


class BaseParser(ABC):
    """
    Абстрактный базовый парсер.

    Использование:
        parser = TwoGisParser(brand_url="https://2gis.ru/...")
        reviews = parser.run()
    """

    SOURCE: str = ""  # переопределяется в каждом парсере

    def __init__(self, brand_url: str, max_reviews: int = 50):
        self.brand_url = brand_url
        self.max_reviews = max_reviews
        self.session = self._make_session()

    def _make_session(self) -> Session:
        """Создаёт requests.Session с нужными заголовками."""
        s = Session()
        s.headers.update(DEFAULT_HEADERS)
        return s

    MAX_REQUESTS_PER_RUN = 10  # максимум запросов за один запуск парсера

def _get(self, url: str, **kwargs) -> requests.Response:
        if not hasattr(self, '_request_count'):
            self._request_count = 0
        
        if self._request_count >= self.MAX_REQUESTS_PER_RUN:
            raise Exception(
                f"Достигнут лимит запросов ({self.MAX_REQUESTS_PER_RUN}) за один запуск"
            )
        
        delay = random.uniform(1.0, 3.0)
        logger.debug(f"GET {url} (delay={delay:.1f}s, request={self._request_count + 1})")
        time.sleep(delay)
        self._request_count += 1
        response = self.session.get(url, timeout=15, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    def fetch_reviews(self) -> list[ParsedReview]:
        """
        Основной метод — реализуется в каждом парсере.
        Возвращает список ParsedReview.
        """
        ...

    def run(self) -> list[ParsedReview]:
        """
        Запускает парсер и возвращает отзывы.
        Оборачивает fetch_reviews в try/except — ошибка одного
        парсера не роняет весь пайплайн.
        """
        logger.info(f"[{self.SOURCE}] Начинаем парсинг: {self.brand_url}")
        try:
            reviews = self.fetch_reviews()
            trimmed = reviews[:self.max_reviews]
            logger.info(f"[{self.SOURCE}] Собрано {len(trimmed)} отзывов")
            return trimmed
        except Exception as e:
            logger.error(f"[{self.SOURCE}] Ошибка парсинга: {e}")
            return []
