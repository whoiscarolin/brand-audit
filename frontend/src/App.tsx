import { useEffect, useState } from 'react'
import { getBrands, getReviews } from './api/client'
import BrandCard from './components/BrandCard'
import ReviewTable from './components/ReviewTable'
import { CardSkeleton } from './components/Skeleton'
import SentimentChart from './components/SentimentChart'
import './App.css'

function App() {
  const [brands, setBrands] = useState<any[]>([])
  const [reviews, setReviews] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedBrand, setSelectedBrand] = useState<number | null>(null)

  useEffect(() => {
    getBrands()
      .then(data => {
        setBrands(data)
        if (data.length > 0) setSelectedBrand(data[0].id)
        setLoading(false)
      })
      .catch(() => {
        setError('Не удалось загрузить данные. Проверьте подключение к API.')
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    if (selectedBrand !== null) {
      getReviews(selectedBrand)
        .then(data => setReviews(Array.isArray(data) ? data : []))
        .catch(() => setReviews([]))
    }
  }, [selectedBrand])

  const safeReviews = Array.isArray(reviews) ? reviews : []
  const positive = safeReviews.filter(r => r.sentiment_label === 'positive').length
  const neutral = safeReviews.filter(r => r.sentiment_label === 'neutral').length
  const negative = safeReviews.filter(r => r.sentiment_label === 'negative').length
  const selectedBrandData = brands.find(b => b.id === selectedBrand)

  return (
    <div style={{ background: '#0d0d0f', minHeight: '100vh', fontFamily: "'DM Mono', monospace" }}>

      {/* Шапка */}
      <div className="animate animate-1" style={{
        background: '#16161a',
        padding: '0 32px',
        height: '64px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #2a2a35'
      }}>
        <span style={{ color: '#e8e8f0', fontSize: '22px', fontWeight: 'bold', letterSpacing: '-0.5px' }}>
          Brand<span style={{ color: '#6c63ff' }}>Audit</span>
        </span>
        <span style={{ color: '#6b6b80', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1.5px' }}>
          portfolio project
        </span>
      </div>

      <div style={{ padding: '32px' }}>

        {/* Ошибка */}
        {error && (
          <div className="error-box animate animate-1" style={{ marginBottom: '24px' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Карточки брендов */}
        <div className="grid-3 animate animate-2" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '20px',
          marginBottom: '24px'
        }}>
          {loading
            ? [1, 2, 3].map(i => <CardSkeleton key={i} />)
            : brands.map(brand => (
              <div
                key={brand.id}
                className="card-hover"
                onClick={() => setSelectedBrand(brand.id)}
                style={{
                  outline: selectedBrand === brand.id ? '2px solid #6c63ff' : '2px solid transparent',
                  borderRadius: '10px',
                  cursor: 'pointer'
                }}
              >
                <BrandCard brand={brand} reviewsCount={selectedBrand === brand.id ? reviews.length : undefined} />
              </div>
            ))
          }
        </div>

        {/* Метрики */}
        {selectedBrandData && (
          <div className="grid-3 animate animate-3" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '20px',
            marginBottom: '24px'
          }}>
            {[
              { label: 'Средний рейтинг', value: reviews.length > 0 ? `⭐ ${(reviews.reduce((sum: number, r: any) => sum + r.rating, 0) / reviews.length).toFixed(1)}` : '—', color: '#e8e8f0' },
              { label: 'Всего отзывов', value: reviews.length, color: '#e8e8f0' },
              { label: 'Позитивных', value: `${Math.round(positive / (safeReviews.length || 1) * 100)}%`, color: '#00c9a7' },
            ].map((metric, i) => (
              <div key={i} style={{
                background: '#16161a',
                borderRadius: '10px',
                padding: '24px',
                border: '1px solid #2a2a35'
              }}>
                <div style={{ color: '#6b6b80', fontSize: '12px', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  {metric.label}
                </div>
                <div style={{ color: metric.color, fontSize: '28px', fontWeight: 'bold' }}>
                  {metric.value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* График и отзывы */}
        <div className="grid-2 animate animate-4" style={{
          display: 'grid',
          gridTemplateColumns: '1fr 2fr',
          gap: '20px',
          marginBottom: '24px'
        }}>
          <SentimentChart positive={positive} neutral={neutral} negative={negative} />
          {safeReviews.length > 0 && <ReviewTable reviews={safeReviews} />}
        </div>

        {/* Кнопка PDF */}
        <div className="animate animate-5" style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            className="pdf-btn"
            disabled
            title="Будет доступно после деплоя бэкенда"
            style={{
              background: '#6c63ff',
              color: '#e8e8f0',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 28px',
              fontSize: '13px',
              cursor: 'pointer',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}
          >
            Скачать PDF
          </button>
        </div>

      </div>
    </div>
  )
}

export default App