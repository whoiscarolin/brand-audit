interface Brand {
  id: number
  name: string
  rating?: number
  review_count?: number
  reviews_count?: number
  category?: string
  city?: string
  reviewsLoaded?: number
}

function BrandCard({ brand, reviewsCount }: { brand: Brand, reviewsCount?: number }) {
  const count = reviewsCount ?? brand.review_count ?? brand.reviews_count ?? 0
  const rating = brand.avg_rating ? brand.avg_rating.toFixed(1) : '—'

  return (
    <div style={{
      background: '#16161a',
      borderRadius: '10px',
      padding: '20px',
      border: '1px solid #2a2a35',
      cursor: 'pointer'
    }}>
      <div style={{ color: '#e8e8f0', fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
        {brand.name}
      </div>
      <div style={{ color: '#6b6b80', fontSize: '13px', marginBottom: '4px' }}>
        {brand.city} · {brand.category}
      </div>
      <div style={{ color: '#6b6b80', fontSize: '13px' }}>
        ⭐ {rating} · {count} отзывов
      </div>
    </div>
  )
}

export default BrandCard