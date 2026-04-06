function Skeleton({ width = '100%', height = '20px' }: { width?: string, height?: string }) {
  return (
    <div className="skeleton" style={{ width, height }} />
  )
}

export function CardSkeleton() {
  return (
    <div style={{ background: '#16161a', borderRadius: '10px', padding: '20px', border: '1px solid #2a2a35' }}>
      <Skeleton height='16px' width='50%' />
      <div style={{ marginTop: '12px' }}>
        <Skeleton height='32px' width='70%' />
      </div>
    </div>
  )
}

export default Skeleton