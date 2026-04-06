function Skeleton({ width = '100%', height = '20px' }: { width?: string, height?: string }) {
  return (
    <div style={{
      width,
      height,
      background: '#2a2a35',
      borderRadius: '6px',
      animation: 'pulse 1.5s ease-in-out infinite'
    }} />
  )
}

export function CardSkeleton() {
  return (
    <div style={{ background: '#16161a', borderRadius: '10px', padding: '20px', border: '1px solid #2a2a35' }}>
      <Skeleton height='20px' width='60%' />
      <div style={{ marginTop: '10px' }}>
        <Skeleton height='14px' width='40%' />
      </div>
    </div>
  )
}

export default Skeleton