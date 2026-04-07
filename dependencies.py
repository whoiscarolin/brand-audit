"""
app/dependencies.py
Общие зависимости FastAPI: авторизация по API ключу.
"""
import os
from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """
    Проверяет API ключ из заголовка X-API-Key.
    Если API_KEY не задан в .env — защита отключена (удобно для разработки).
    """
    expected_key = os.getenv("API_KEY", "")

    # Если ключ не задан в окружении — пропускаем всех (dev режим)
    if not expected_key:
        return "dev"

    if api_key == expected_key:
        return api_key

    raise HTTPException(
        status_code=403,
        detail="Неверный или отсутствующий API ключ. Передайте его в заголовке X-API-Key.",
    )
