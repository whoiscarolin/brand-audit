"""
app/main.py — точка входа FastAPI-приложения.

Запуск:
    uvicorn app.main:app --reload --port 8000

Swagger UI доступен по адресу: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.db.session import Base, engine
from app.routers import health, brands, reviews, parser, sentiment, report

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-хук: выполняется при старте и остановке приложения.
    При старте — создаём таблицы в БД если их ещё нет.
    """
    # Импортируем модели, чтобы Base.metadata их видел
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # приложение работает

    # При остановке — закрываем движок
    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "REST API для сервиса автоматизированного аудита цифрового следа брендов. "
        "Портфолио-проект: парсинг отзывов, sentiment analysis, PDF-отчёты."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — разрешаем фронтенду (Vite dev server) делать запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(health.router)
app.include_router(brands.router)
app.include_router(reviews.router)
app.include_router(parser.router)

app.include_router(sentiment.router)
app.include_router(report.router)


# Здесь будем подключать роутеры следующих фаз:
# app.include_router(report.router, prefix="/report")

