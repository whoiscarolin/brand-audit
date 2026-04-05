import './App.css'

function App() {
  return (
    <div style={{ background: '#0d0d0f', minHeight: '100vh', padding: '0', fontFamily: 'monospace' }}>
      
      {/* Шапка */}
      <div style={{ background: '#16161a', padding: '0 32px', height: '64px', display: 'flex', alignItems: 'center' }}>
        <span style={{ color: '#e8e8f0', fontSize: '24px', fontWeight: 'bold' }}>
          Brand<span style={{ color: '#6c63ff' }}>Audit</span>
        </span>
      </div>

      <div style={{ padding: '32px' }}>

        {/* Карточки метрик */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
          
          <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
            <div style={{ color: '#6b6b80', fontSize: '14px', marginBottom: '8px' }}>Средний рейтинг</div>
            <div style={{ color: '#e8e8f0', fontSize: '28px' }}>4.7 ⭐</div>
          </div>

          <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
            <div style={{ color: '#6b6b80', fontSize: '14px', marginBottom: '8px' }}>Всего отзывов</div>
            <div style={{ color: '#e8e8f0', fontSize: '28px' }}>128</div>
          </div>

          <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
            <div style={{ color: '#6b6b80', fontSize: '14px', marginBottom: '8px' }}>Тональность</div>
            <div style={{ color: '#e8e8f0', fontSize: '28px' }}>74% позитив</div>
          </div>

        </div>

        {/* Блок отзывов */}
        <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35', marginBottom: '24px' }}>
          <div style={{ color: '#e8e8f0', fontSize: '18px', marginBottom: '20px' }}>Последние отзывы</div>
          
          <div style={{ color: '#6b6b80', fontSize: '13px', padding: '12px 0', borderBottom: '1px solid #2a2a35' }}>
            ⭐⭐⭐⭐⭐ &nbsp; Отличное место, очень вкусно! &nbsp;
            <span style={{ color: '#00c9a7' }}>позитив</span>
          </div>
          <div style={{ color: '#6b6b80', fontSize: '13px', padding: '12px 0', borderBottom: '1px solid #2a2a35' }}>
            ⭐⭐⭐ &nbsp; Долго ждали заказ, но еда норм &nbsp;
            <span style={{ color: '#f5c542' }}>нейтраль</span>
          </div>
          <div style={{ color: '#6b6b80', fontSize: '13px', padding: '12px 0' }}>
            ⭐ &nbsp; Ужасное обслуживание, больше не приду &nbsp;
            <span style={{ color: '#ff6b6b' }}>негатив</span>
          </div>
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