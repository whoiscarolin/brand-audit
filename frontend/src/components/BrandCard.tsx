interface Brand {
  id: number
  name: string
  rating: number
  reviews_count: number
}

function BrandCard({ brand }: { brand: Brand }) {
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
      <div style={{ color: '#6b6b80', fontSize: '13px' }}>
        ⭐ {brand.rating} · {brand.reviews_count} отзывов
      </div>
    </div>
  )
}

export default BrandCard