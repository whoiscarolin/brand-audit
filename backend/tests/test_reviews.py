"""
tests/test_reviews.py — тесты для /reviews.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_db

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
async def brand(client):
    """Создаёт тестовый бренд и возвращает его id."""
    r = await client.post("/brands", json={"name": "Тестовое кафе", "city": "Москва"})
    return r.json()["id"]


# ── Тесты ────────────────────────────────────────────────────────────────────

async def test_list_reviews_empty(client):
    """Пустой список отзывов при чистой БД."""
    r = await client.get("/reviews")
    assert r.status_code == 200
    assert r.json() == []


async def test_create_review(client, brand):
    """POST /reviews создаёт отзыв и возвращает 201."""
    payload = {
        "brand_id": brand,
        "source": "2gis",
        "text": "Очень вкусный кофе, рекомендую!",
        "rating": 5.0,
        "author": "Иван",
    }
    r = await client.post("/reviews", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["brand_id"] == brand
    assert data["source"] == "2gis"
    assert data["rating"] == 5.0
    assert data["sentiment_label"] is None  # заполнится в Фазе 3


async def test_create_review_invalid_rating(client, brand):
    """Рейтинг вне диапазона 1-5 → 422."""
    r = await client.post("/reviews", json={
        "brand_id": brand, "source": "2gis", "rating": 6.0
    })
    assert r.status_code == 422


async def test_filter_by_brand_id(client, brand):
    """Фильтрация по brand_id возвращает только нужные отзывы."""
    # Создаём второй бренд
    r2 = await client.post("/brands", json={"name": "Другое место"})
    brand2 = r2.json()["id"]

    await client.post("/reviews", json={"brand_id": brand, "source": "2gis", "text": "Хорошо"})
    await client.post("/reviews", json={"brand_id": brand2, "source": "2gis", "text": "Плохо"})

    r = await client.get(f"/reviews?brand_id={brand}")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["brand_id"] == brand


async def test_filter_by_source(client, brand):
    """Фильтрация по source."""
    await client.post("/reviews", json={"brand_id": brand, "source": "2gis"})
    await client.post("/reviews", json={"brand_id": brand, "source": "yandex_maps"})

    r = await client.get("/reviews?source=2gis")
    assert r.status_code == 200
    assert all(rv["source"] == "2gis" for rv in r.json())


async def test_get_review_by_id(client, brand):
    """GET /reviews/{id} возвращает конкретный отзыв."""
    created = await client.post("/reviews", json={
        "brand_id": brand, "source": "2gis", "text": "Норм"
    })
    review_id = created.json()["id"]

    r = await client.get(f"/reviews/{review_id}")
    assert r.status_code == 200
    assert r.json()["id"] == review_id


async def test_get_review_not_found(client):
    """GET /reviews/999 → 404."""
    r = await client.get("/reviews/999")
    assert r.status_code == 404


async def test_bulk_create(client, brand):
    """POST /reviews/bulk создаёт несколько отзывов за один запрос."""
    items = [
        {"brand_id": brand, "source": "2gis", "text": f"Отзыв {i}", "rating": float(i % 5 + 1)}
        for i in range(10)
    ]
    r = await client.post("/reviews/bulk", json=items)
    assert r.status_code == 201
    assert len(r.json()) == 10


async def test_bulk_create_empty_fails(client):
    """Пустой список → 422."""
    r = await client.post("/reviews/bulk", json=[])
    assert r.status_code == 422


async def test_delete_review(client, brand):
    """DELETE /reviews/{id} удаляет отзыв."""
    created = await client.post("/reviews", json={"brand_id": brand, "source": "2gis"})
    review_id = created.json()["id"]

    r = await client.delete(f"/reviews/{review_id}")
    assert r.status_code == 204

    r2 = await client.get(f"/reviews/{review_id}")
    assert r2.status_code == 404


async def test_pagination(client, brand):
    """Пагинация через limit/offset работает корректно."""
    for i in range(5):
        await client.post("/reviews", json={"brand_id": brand, "source": "2gis", "text": str(i)})

    r = await client.get("/reviews?limit=2&offset=0")
    assert len(r.json()) == 2

    r2 = await client.get("/reviews?limit=2&offset=4")
    assert len(r2.json()) == 1
