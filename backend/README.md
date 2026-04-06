# BrandAudit

Сервис автоматизированного аудита цифрового следа для ресторанов, кафе и локальных брендов.

## Что делает сервис

- Парсит отзывы с публичных источников (Отзовик, 2GIS)
- Анализирует тональность отзывов (позитив / нейтраль / негатив)
- Визуализирует метрики на дашборде
- Генерирует PDF-отчёт по бренду

## Стек

### Backend
- Python 3.11, FastAPI, SQLAlchemy, SQLite
- BeautifulSoup4 — парсинг
- Dostoevsky — sentiment analysis на русском
- reportlab — генерация PDF

### Frontend
- React + TypeScript, Vite
- Recharts — графики

## Запуск локально

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Открой http://localhost:5173

## Команда

| Участник | Роль |
|----------|------|
| Богдан | Backend, парсинг, sentiment, деплой |
| Михаил | Frontend, UI/UX, дизайн |
