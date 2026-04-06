import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'

interface Props {
  positive: number
  neutral: number
  negative: number
}

const COLORS = ['#00c9a7', '#f5c542', '#ff6b6b']

function SentimentChart({ positive, neutral, negative }: Props) {
  const data = [
    { name: 'Позитив', value: positive },
    { name: 'Нейтраль', value: neutral },
    { name: 'Негатив', value: negative },
  ]

  return (
    <div style={{ background: '#16161a', borderRadius: '10px', padding: '24px', border: '1px solid #2a2a35' }}>
      <div style={{ color: '#e8e8f0', fontSize: '18px', marginBottom: '20px' }}>Тональность отзывов</div>
      <PieChart width={300} height={300}>
        <Pie data={data} cx={150} cy={120} outerRadius={80} dataKey="value">
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip contentStyle={{ background: '#16161a', border: '1px solid #2a2a35', color: '#e8e8f0' }} />
        <Legend />
      </PieChart>
    </div>
  )
}

export default SentimentChart
