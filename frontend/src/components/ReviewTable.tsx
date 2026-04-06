interface Review {
  id: number
  text: string
  rating: number
  sentiment: string
}

function sentimentColor(sentiment: string) {
  if (sentiment === 'positive') return '#00c9a7'
  if (sentiment === 'negative') return '#ff6b6b'
  return '#f5c542'
}

function sentimentLabel(sentiment: string) {
  if (sentiment === 'positive') return 'позитив'
  if (sentiment === 'negative') return 'негатив'
  return 'нейтраль'
}

function ReviewTable({ reviews }: { reviews: Review[] }) {
  return (
    <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
      <div style={{ color: '#e8e8f0', fontSize: '18px', marginBottom: '20px' }}>Последние отзывы</div>
      {reviews.map(review => (
        <div key={review.id} style={{ color: '#6b6b80', fontSize: '13px', padding: '12px 0', borderBottom: '1px solid #2a2a35' }}>
          {'⭐'.repeat(review.rating)} &nbsp; {review.text} &nbsp;
          <span style={{ color: sentimentColor(review.sentiment) }}>
            {sentimentLabel(review.sentiment)}
          </span>
        </div>
      ))}
    </div>
  )
}

export default ReviewTable