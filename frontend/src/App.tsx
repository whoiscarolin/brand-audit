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
  const [selectedBrand, setSelectedBrand] = useState<number | null>(null)

  useEffect(() => {
    getBrands().then(data => {
      setBrands(data)
      if (data.length > 0) setSelectedBrand(data[0].id)
      setLoading(false)
    })
  }, [])

  useEffect(() => {
    if (selectedBrand !== null) {
      getReviews(selectedBrand).then(setReviews)
    }
  }, [selectedBrand])

  const positive = reviews.filter(r => r.sentiment === 'positive').length
  const neutral = reviews.filter(r => r.sentiment === 'neutral').length
  const negative = reviews.filter(r => r.sentiment === 'negative').length

  const selectedBrandData = brands.find(b => b.id === selectedBrand)

  return (
    <div style={{ background: '#0d0d0f', minHeight: '100vh', fontFamily: 'monospace' }}>

      {/* Шапка */}
      <div style={{ background: '#16161a', padding: '0 32px', height: '64px', display: 'flex', alignItems: 'center' }}>
        <span style={{ color: '#e8e8f0', fontSize: '24px', fontWeight: 'bold' }}>
          Brand<span style={{ color: '#6c63ff' }}>Audit</span>
        </span>
      </div>

      <div style={{ padding: '32px' }}>

        {/* Карточки брендов */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
          {loading
            ? [1, 2, 3].map(i => <CardSkeleton key={i} />)
            : brands.map(brand => (
              <div key={brand.id} onClick={() => setSelectedBrand(brand.id)}
                style={{ outline: selectedBrand === brand.id ? '2px solid #6c63ff' : 'none', borderRadius: '10px' }}>
                <BrandCard brand={brand} />
              </div>
            ))
          }
        </div>

        {/* Метрики выбранного бренда */}
        {selectedBrandData && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
            <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
              <div style={{ color: '#6b6b80', fontSize: '14px', marginBottom: '8px' }}>Средний рейтинг</div>
              <div style={{ color: '#e8e8f0', fontSize: '28px' }}>⭐ {selectedBrandData.rating}</div>
            </div>
            <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
              <div style={{ color: '#6b6b80', fontSize: '14px', marginBottom: '8px' }}>Всего отзывов</div>
              <div style={{ color: '#e8e8f0', fontSize: '28px' }}>{selectedBrandData.reviews_count}</div>
            </div>
            <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
              <div style={{ color: '#6b6b80', fontSize: '14px', marginBottom: '8px' }}>Позитивных</div>
              <div style={{ color: '#00c9a7', fontSize: '28px' }}>{Math.round(positive / reviews.length * 100) || 0}%</div>
            </div>
          </div>
        )}

        {/* График и отзывы */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px', marginBottom: '24px' }}>
          <SentimentChart positive={positive} neutral={neutral} negative={negative} />
          {reviews.length > 0 && <ReviewTable reviews={reviews} />}
        </div>

        {/* Кнопка PDF */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button style={{ background: '#6c63ff', color: '#e8e8f0', border: 'none', borderRadius: '8px', padding: '12px 24px', fontSize: '14px', cursor: 'pointer' }}>
            Скачать PDF
          </button>
        </div>

      </div>
    </div>
  )
}

export default App