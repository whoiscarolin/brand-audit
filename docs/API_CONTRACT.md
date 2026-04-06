# API Contract — Brand Audit
> Версия: 1.0 | Дата: 2026-04-05  
> Этот документ — единственный источник правды для фронтенда.  
> Михаил работает по нему, Богдан не меняет сигнатуры без обновления этого файла.

---

## Base URL

```
Development:  http://localhost:8000
Production:   https://TBD (после деплоя на VPS)
```

---

## Общие правила

- Все ответы — JSON
- Даты — ISO 8601: `"2024-03-15T12:00:00"`
- Пагинация: параметры `skip` (default 0) и `limit` (default 20, max 100)
- Ошибки — стандартный FastAPI формат:
  ```json
  { "detail": "Not found" }
  ```

---

## Эндпоинты

### 🟢 Health

#### `GET /health`
Проверка живости сервера.

**Response 200:**
```json
{ "status": "ok" }
```

---

### 🏢 Brands

#### `GET /brands`
Список всех брендов.

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Кофейня Буше",
    "url": "https://2gis.ru/...",
    "created_at": "2024-03-15T12:00:00"
  }
]
```

#### `POST /brands`
Создать бренд.

**Request body:**
```json
{
  "name": "Кофейня Буше",
  "url": "https://2gis.ru/..."
}
```

**Response 201:**
```json
{
  "id": 1,
  "name": "Кофейня Буше",
  "url": "https://2gis.ru/...",
  "created_at": "2024-03-15T12:00:00"
}
```

#### `GET /brands/{id}`
Один бренд по ID.

**Response 200** — объект бренда (см. выше)  
**Response 404** — `{ "detail": "Brand not found" }`

#### `DELETE /brands/{id}`
Удалить бренд (каскадно удаляет все его отзывы).

**Response 204** — пустой ответ

---

### 📝 Reviews

#### `GET /reviews`
Список отзывов с фильтрацией и пагинацией.

**Query params:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `brand_id` | int | нет | Фильтр по бренду |
| `source` | string | нет | Фильтр по источнику (`"2gis"`, `"yandex"`) |
| `sentiment` | string | нет | Фильтр по тональности (`"positive"`, `"negative"`, `"neutral"`) — **заполняется в Фазе 3** |
| `skip` | int | нет | Смещение (default: 0) |
| `limit` | int | нет | Лимит (default: 20) |

**Response 200:**
```json
[
  {
    "id": 42,
    "brand_id": 1,
    "source": "yandex",
    "author": "Иван П.",
    "text": "Отличный кофе, приятная атмосфера",
    "rating": 5,
    "published_at": "2024-02-10T00:00:00",
    "sentiment": null,
    "sentiment_score": null,
    "created_at": "2024-03-15T12:00:00"
  }
]
```

> ⚠️ Поля `sentiment` и `sentiment_score` сейчас всегда `null` — заполнятся после Фазы 3.

#### `POST /reviews`
Создать один отзыв вручную.

**Request body:**
```json
{
  "brand_id": 1,
  "source": "yandex",
  "author": "Иван П.",
  "text": "Отличный кофе",
  "rating": 5,
  "published_at": "2024-02-10T00:00:00"
}
```

**Response 201** — созданный объект отзыва

#### `POST /reviews/bulk`
Создать отзывы пачкой (используется парсером).

**Request body:**
```json
[
  { "brand_id": 1, "source": "yandex", "author": "...", "text": "...", "rating": 4 },
  { "brand_id": 1, "source": "yandex", "author": "...", "text": "...", "rating": 2 }
]
```

**Response 201:**
```json
{ "created": 2 }
```

#### `DELETE /reviews/{id}`
Удалить один отзыв.

**Response 204** — пустой ответ

---

### 🔍 Parser (Фаза 2 Step 2 — частично готово)

#### `POST /parse`
Запустить парсинг для бренда.

**Request body:**
```json
{
  "brand_id": 1,
  "source": "yandex"
}
```

**Response 202:**
```json
{
  "status": "started",
  "brand_id": 1,
  "source": "yandex"
}
```

> ⚠️ Эндпоинт в разработке. Пока использовать mock (см. ниже).

---

### 📊 Sentiment (Фаза 3 — ещё не готово)

#### `GET /sentiment/{brand_id}`
Агрегированная аналитика по бренду.

**Response 200 (планируемый формат):**
```json
{
  "brand_id": 1,
  "total_reviews": 47,
  "average_rating": 4.2,
  "sentiment_distribution": {
    "positive": 31,
    "neutral": 10,
    "negative": 6
  },
  "sentiment_by_month": [
    { "month": "2024-01", "positive": 8, "neutral": 2, "negative": 1 }
  ]
}
```

> ⚠️ Заглушить через mock до готовности Фазы 3.

---

## Mock-данные для фронтенда

Файл `frontend/src/api/mocks.ts` — использовать когда `VITE_USE_MOCK=true`.

```typescript
export const mockBrands = [
  { id: 1, name: "Кофейня Буше", url: "https://2gis.ru/spb/buhe", created_at: "2024-03-01T10:00:00" },
  { id: 2, name: "Теремок", url: "https://yandex.ru/maps/teremok", created_at: "2024-03-05T10:00:00" },
];

export const mockReviews = [
  { id: 1, brand_id: 1, source: "yandex", author: "Анна К.", text: "Прекрасный кофе и уютная обстановка, буду возвращаться", rating: 5, published_at: "2024-02-01T00:00:00", sentiment: null, sentiment_score: null, created_at: "2024-03-10T00:00:00" },
  { id: 2, brand_id: 1, source: "yandex", author: "Дмитрий С.", text: "Долго ждали заказ, персонал невнимательный", rating: 2, published_at: "2024-02-05T00:00:00", sentiment: null, sentiment_score: null, created_at: "2024-03-10T00:00:00" },
  { id: 3, brand_id: 1, source: "2gis", author: "Мария В.", text: "Нормально, ничего особенного", rating: 3, published_at: "2024-02-10T00:00:00", sentiment: null, sentiment_score: null, created_at: "2024-03-10T00:00:00" },
  { id: 4, brand_id: 2, source: "yandex", author: "Павел О.", text: "Вкусные блины, быстрое обслуживание", rating: 4, published_at: "2024-02-12T00:00:00", sentiment: null, sentiment_score: null, created_at: "2024-03-10T00:00:00" },
  { id: 5, brand_id: 2, source: "yandex", author: "Елена Т.", text: "Цены выросли, качество упало", rating: 2, published_at: "2024-02-15T00:00:00", sentiment: null, sentiment_score: null, created_at: "2024-03-10T00:00:00" },
];

export const mockSentiment = {
  brand_id: 1,
  total_reviews: 5,
  average_rating: 3.2,
  sentiment_distribution: { positive: 2, neutral: 1, negative: 2 },
  sentiment_by_month: [
    { month: "2024-02", positive: 2, neutral: 1, negative: 2 }
  ]
};
```
