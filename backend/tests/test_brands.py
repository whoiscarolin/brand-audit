"""
tests/test_brands.py — интеграционные тесты CRUD для /brands.

Каждый тест работает с чистой in-memory SQLite БД — изоляция гарантирована.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_db

# In-memory SQLite для тестов — не трогает файл brand_audit.db
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Создаёт чистую БД для каждого теста и удаляет после."""
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
    """HTTP-клиент с подменённой тестовой БД."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


# ── Тесты ────────────────────────────────────────────────────────────────────

async def test_list_brands_empty(client):
    """Пустой список брендов при чистой БД."""
    r = await client.get("/brands")
    assert r.status_code == 200
    assert r.json() == []


async def test_create_brand(client):
    """POST /brands создаёт бренд и возвращает 201."""
    payload = {"name": "Кофейня Прага", "category": "cafe", "city": "Москва"}
    r = await client.post("/brands", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == 1
    assert data["name"] == "Кофейня Прага"
    assert data["category"] == "cafe"
    assert data["city"] == "Москва"
    assert data["review_count"] == 0


async def test_create_brand_minimal(client):
    """Только name — остальные поля опциональны."""
    r = await client.post("/brands", json={"name": "Рестик"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Рестик"
    assert data["category"] is None


async def test_create_brand_empty_name_fails(client):
    """Пустое имя — 422 Unprocessable Entity."""
    r = await client.post("/brands", json={"name": ""})
    assert r.status_code == 422


async def test_get_brand_by_id(client):
    """GET /brands/{id} возвращает созданный бренд."""
    await client.post("/brands", json={"name": "Пиццерия Рим", "city": "СПб"})
    r = await client.get("/brands/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Пиццерия Рим"


async def test_get_brand_not_found(client):
    """GET /brands/999 — 404."""
    r = await client.get("/brands/999")
    assert r.status_code == 404


async def test_list_brands_returns_all(client):
    """После создания двух брендов список содержит оба."""
    await client.post("/brands", json={"name": "Бренд А"})
    await client.post("/brands", json={"name": "Бренд Б"})
    r = await client.get("/brands")
    assert r.status_code == 200
    names = [b["name"] for b in r.json()]
    assert "Бренд А" in names
    assert "Бренд Б" in names


async def test_update_brand(client):
    """PATCH /brands/{id} обновляет только переданные поля."""
    await client.post("/brands", json={"name": "Старое имя", "city": "Москва"})
    r = await client.patch("/brands/1", json={"name": "Новое имя"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Новое имя"
    assert data["city"] == "Москва"  # не тронуто


async def test_update_brand_not_found(client):
    """PATCH /brands/999 — 404."""
    r = await client.patch("/brands/999", json={"name": "X"})
    assert r.status_code == 404


async def test_delete_brand(client):
    """DELETE /brands/{id} удаляет бренд, повторный GET → 404."""
    await client.post("/brands", json={"name": "Удали меня"})
    r = await client.delete("/brands/1")
    assert r.status_code == 204
    r2 = await client.get("/brands/1")
    assert r2.status_code == 404


async def test_delete_brand_not_found(client):
    """DELETE /brands/999 — 404."""
    r = await client.delete("/brands/999")
    assert r.status_code == 404
