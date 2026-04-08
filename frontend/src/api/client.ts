const BASE_URL = 'https://brand-audit-a753.onrender.com'
const API_KEY = 'brandaudit_secret_2026'

const USE_MOCK = false

const MOCK_BRANDS = [
  { id: 1, name: 'Кафе Пушкин', rating: 4.7, reviews_count: 128 },
  { id: 2, name: 'Burger Heroes', rating: 4.2, reviews_count: 94 },
  { id: 3, name: 'Тануки', rating: 3.9, reviews_count: 76 },
]

const MOCK_REVIEWS: Record<number, any[]> = {
  1: [
    { id: 1, text: 'Отличное место, очень вкусно!', rating: 5, sentiment: 'positive' },
    { id: 2, text: 'Атмосфера просто волшебная', rating: 5, sentiment: 'positive' },
    { id: 3, text: 'Долго ждали заказ, но еда норм', rating: 3, sentiment: 'neutral' },
  ],
  2: [
    { id: 4, text: 'Лучшие бургеры в городе!', rating: 5, sentiment: 'positive' },
    { id: 5, text: 'Шумно, но вкусно', rating: 3, sentiment: 'neutral' },
    { id: 6, text: 'Бургер был холодный', rating: 2, sentiment: 'negative' },
  ],
  3: [
    { id: 7, text: 'Суши свежие, всё понравилось', rating: 4, sentiment: 'positive' },
    { id: 8, text: 'Ужасное обслуживание', rating: 1, sentiment: 'negative' },
    { id: 9, text: 'Цены высокие для такого качества', rating: 2, sentiment: 'negative' },
  ],
}

export async function getBrands() {
  if (USE_MOCK) return MOCK_BRANDS
  const response = await fetch(`${BASE_URL}/brands`)
  return response.json()
}

export async function getReviews(brandId: number) {
  if (USE_MOCK) return MOCK_REVIEWS[brandId] || []
  const response = await fetch(`${BASE_URL}/reviews?brand_id=${brandId}`)
  return response.json()
}

export async function getSentiment(brandId: number) {
  const response = await fetch(`${BASE_URL}/brands/${brandId}/sentiment`)
  return response.json()
}

export async function runParser(brandId: number) {
  const response = await fetch(`${BASE_URL}/parser/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({ brand_id: brandId })
  })
  return response.json()
}

export async function runSentiment(brandId: number) {
  const response = await fetch(`${BASE_URL}/brands/${brandId}/sentiment/run`, {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY }
  })
  return response.json()
}

export async function downloadReport(brandId: number) {
  const response = await fetch(`${BASE_URL}/brands/${brandId}/report/download`)
  return response.blob()
}