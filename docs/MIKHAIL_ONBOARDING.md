# Онбординг для Михаила — Brand Audit Frontend

Привет! Здесь всё что нужно чтобы начать работать над проектом.

---

## 1. Клонируй репозиторий

```bash
git clone <URL репозитория>
cd brand-audit
```

---

## 2. Структура проекта

```
brand-audit/
├── backend/          ← Богдан (не трогай)
├── frontend/         ← твоя зона
├── docs/
│   └── API_CONTRACT.md   ← читай это перед работой с API
├── docker-compose.yml
└── .env.example
```

---

## 3. Запуск через Docker (рекомендуется)

Тебе не нужен Python. Docker запустит бэкенд автоматически.

```bash
# Установи Docker Desktop если нет: https://docker.com/products/docker-desktop

# Запусти всё одной командой из корня проекта:
docker compose up
```

После запуска:
- **Бэкенд:** http://localhost:8000
- **Swagger (документация API):** http://localhost:8000/docs
- **Твой фронт:** http://localhost:5173

---

## 4. Запуск фронтенда без Docker

Если не хочешь Docker — можно запускать фронт отдельно:

```bash
cd frontend
npm install
npm run dev
```

Но тогда бэкенд нужно запускать отдельно (спроси Богдана).

---

## 5. Переменные окружения

Создай файл `frontend/.env.local`:

```env
# URL бэкенда
VITE_API_URL=http://localhost:8000

# Режим моков (true = работать без бэкенда, false = реальный API)
VITE_USE_MOCK=false
```

> Поставь `VITE_USE_MOCK=true` если хочешь работать совсем без бэкенда — есть готовые тестовые данные.

---

## 6. Scaffold фронтенда

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install axios
```

### Структура папок которую нужно создать:

```
frontend/src/
├── api/
│   ├── client.ts       ← axios instance
│   ├── brands.ts       ← функции для /brands
│   ├── reviews.ts      ← функции для /reviews
│   └── mocks.ts        ← тестовые данные
├── types/
│   └── api.ts          ← TypeScript типы
├── components/
│   ├── BrandCard/
│   ├── ReviewTable/
│   └── SentimentChart/ ← позже, в Фазе 3
├── pages/
│   ├── Dashboard.tsx
│   └── BrandDetail.tsx
└── App.tsx
```

---

## 7. Задачи по фазам

### Фаза 1 (сейчас — синхронизация)

- [ ] Scaffold: `npm create vite` + TypeScript
- [ ] Создать `src/api/client.ts` (axios с baseURL из env)
- [ ] Создать `src/types/api.ts` (типы Brand, Review, Sentiment)
- [ ] Создать `src/api/mocks.ts` (тестовые данные — см. API_CONTRACT.md)
- [ ] Убедиться что `GET /health` проходит → вывести статус в App.tsx

**Критерий:** React запускается, `/health` опрашивается, статус виден в UI.

### Фаза 2 (параллельно с парсером Богдана)

- [ ] `BrandCard` — карточка бренда (название, кол-во отзывов, средний рейтинг)
- [ ] `ReviewTable` — таблица отзывов с пагинацией (`skip` / `limit`)
- [ ] Скелетоны загрузки для обоих компонентов
- [ ] Страница Dashboard — список брендов
- [ ] Страница BrandDetail — отзывы конкретного бренда

**Критерий:** дашборд показывает бренды и отзывы (mock или реальные).

### Фаза 3 (после готовности `/sentiment` от Богдана)

- [ ] `SentimentChart` — диаграмма позитив/нейтраль/негатив
- [ ] Интеграция с `/sentiment/{brand_id}`
- [ ] Фильтр отзывов по тональности

### Фаза 4 (финал)

- [ ] Кнопка "Скачать PDF отчёт" → `GET /report/download/{brand_id}`
- [ ] Финальный дизайн-полировка
- [ ] README для портфолио

---

## 8. Правила синхронизации с Богданом

1. **Не меняй сигнатуры API** — если нужен новый эндпоинт, сначала обсудите и обновите `docs/API_CONTRACT.md`
2. **Ветки:** `main` — только рабочий код; твои задачи — в ветках `feat/mikhail-*`
3. **Swagger всегда актуален:** http://localhost:8000/docs — генерируй типы отсюда
4. **Mock-режим** — используй когда бэкенд ещё не готов, не блокируйся

---

## 9. Генерация TypeScript типов из Swagger

Когда бэкенд запущен:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

Типы обновятся автоматически из реальных Pydantic-схем Богдана.

---

## Вопросы?

- По API и бэкенду → Богдан
- По дизайну и UI → сам решаешь
- Swagger: http://localhost:8000/docs
- API-контракт: `docs/API_CONTRACT.md`
