"""
tests/test_parser.py — тесты парсера и эндпоинта /parser/run.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_db
from app.services.parser.base import ParsedReview
from app.services.parser.yandex import YandexMapsParser

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(
        bind=engine, class_=AsyncSession,
        expire_on_commit=False, autocommit=False, autoflush=False,
    )

    async def override_get_db():
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
async def client(test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
async def brand_id(client):
    r = await client.post("/brands", json={"name": "Тестовое кафе"})
    return r.json()["id"]


# ── Юнит-тесты парсера ───────────────────────────────────────────────────────

def _make_review_html(author="Иван", rating="5.0", text="Отлично!", date="2024-03-15T12:00:00Z"):
    """Генерирует HTML-блок отзыва Яндекс Карт для тестов."""
    return f"""
    <div class="business-review-view" itemprop="review">
        <div itemprop="name">{author}</div>
        <div class="business-review-view__rating">
            <span itemprop="reviewRating" itemscope>
                <meta content="{rating}" itemprop="ratingValue"/>
            </span>
        </div>
        <span itemprop="reviewBody">{text}</span>
        <meta content="{date}" itemprop="datePublished"/>
    </div>
    """


def test_yandex_parse_item():
    """YandexMapsParser корректно парсит HTML-блок отзыва."""
    from bs4 import BeautifulSoup
    parser = YandexMapsParser(org_url="https://yandex.com/maps/org/test/123/")
    html = _make_review_html(author="Мария", rating="4.0", text="Хороший кофе")
    soup = BeautifulSoup(html, "lxml")
    item = soup.select_one(".business-review-view")

    result = parser._parse_item(item)
    assert result is not None
    assert result.source == "yandex_maps"
    assert result.author == "Мария"
    assert result.rating == 4.0
    assert result.text == "Хороший кофе"
    assert result.reviewed_at is not None


def test_yandex_parse_item_no_text():
    """Парсер справляется с отзывом без текста."""
    from bs4 import BeautifulSoup
    parser = YandexMapsParser(org_url="https://yandex.com/maps/org/test/123/")
    html = _make_review_html(text="")
    soup = BeautifulSoup(html, "lxml")
    item = soup.select_one(".business-review-view")

    result = parser._parse_item(item)
    assert result is not None
    assert result.text == "" or result.text is None


def test_yandex_parse_item_rating_float():
    """Рейтинг корректно конвертируется в float."""
    from bs4 import BeautifulSoup
    parser = YandexMapsParser(org_url="https://yandex.com/maps/org/test/123/")
    html = _make_review_html(rating="3.0")
    soup = BeautifulSoup(html, "lxml")
    item = soup.select_one(".business-review-view")

    result = parser._parse_item(item)
    assert result.rating == 3.0
    assert isinstance(result.rating, float)


# ── Интеграционные тесты /parser/run ─────────────────────────────────────────

def _make_fake_reviews(count: int) -> list[ParsedReview]:
    return [
        ParsedReview(
            source="yandex_maps",
            text=f"Отзыв {i}",
            rating=float(i % 5 + 1),
            author=f"Автор {i}",
            reviewed_at=datetime(2024, 1, (i % 28) + 1, tzinfo=timezone.utc),
        )
        for i in range(count)
    ]


async def test_parser_run_no_url(client, brand_id):
    """Запрос без URL → 422."""
    r = await client.post("/parser/run", json={"brand_id": brand_id})
    assert r.status_code == 422


async def test_parser_run_brand_not_found(client):
    """Несуществующий бренд → 404."""
    r = await client.post("/parser/run", json={
        "brand_id": 999,
        "yandex_org_url": "https://yandex.com/maps/org/test/123/",
    })
    assert r.status_code == 404


async def test_parser_run_saves_reviews(client, brand_id):
    """Парсинг сохраняет отзывы в БД."""
    fake = _make_fake_reviews(3)

    with patch.object(YandexMapsParser, "run", return_value=fake):
        r = await client.post("/parser/run", json={
            "brand_id": brand_id,
            "yandex_org_url": "https://yandex.com/maps/org/ludilove/157741958403/",
        })

    assert r.status_code == 200
    data = r.json()
    assert data["total_parsed"] == 3
    assert data["saved"] == 3
    assert data["sources"]["yandex_maps"] == 3
    assert data["errors"] == []

    reviews_r = await client.get(f"/reviews?brand_id={brand_id}")
    assert len(reviews_r.json()) == 3


async def test_parser_run_message(client, brand_id):
    """Поле message содержит количество сохранённых отзывов."""
    fake = _make_fake_reviews(3)
    with patch.object(YandexMapsParser, "run", return_value=fake):
        r = await client.post("/parser/run", json={
            "brand_id": brand_id,
            "yandex_org_url": "https://yandex.com/maps/org/test/123/",
        })
    assert "3" in r.json()["message"]
