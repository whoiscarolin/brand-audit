import { useEffect, useState } from 'react'
import { getBrands, getReviews } from './api/client'
import BrandCard from './components/BrandCard'
import ReviewTable from './components/ReviewTable'
import { CardSkeleton } from './components/Skeleton'
import './App.css'

function App() {
  const [brands, setBrands] = useState<any[]>([])
  const [reviews, setReviews] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedBrand, setSelectedBrand] = useState<number | null>(null)

  useEffect(() => {
    getBrands().then(data => {
      setBrands(data)
      if (data.length > 0) {
        setSelectedBrand(data[0].id)
      }
      setLoading(false)
    })
  }, [])

  useEffect(() => {
    if (selectedBrand !== null) {
      getReviews(selectedBrand).then(setReviews)
    }
  }, [selectedBrand])

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
              <div key={brand.id} onClick={() => setSelectedBrand(brand.id)}>
                <BrandCard brand={brand} />
              </div>
            ))
          }
        </div>

        {/* Таблица отзывов */}
        {reviews.length > 0 && <ReviewTable reviews={reviews} />}

        {/* Кнопка PDF */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
          <button style={{ background: '#6c63ff', color: '#e8e8f0', border: 'none', borderRadius: '8px', padding: '12px 24px', fontSize: '14px', cursor: 'pointer' }}>
            Скачать PDF
          </button>
        </div>

      </div>
    </div>
  )
}

export default App