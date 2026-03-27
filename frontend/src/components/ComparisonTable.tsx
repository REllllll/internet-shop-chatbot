import type { ComparisonRow, Product } from '../types'

export function ComparisonTable({ products, rows }: { products: Product[]; rows: ComparisonRow[] }) {
  return (
    <div style={{ overflowX: 'auto', marginTop: 12 }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: '6px 8px', color: '#64748b', width: '30%' }}>
              Feature
            </th>
            {products.map(p => (
              <th key={p.product_id} style={{ textAlign: 'center', padding: '6px 8px', color: '#f1f5f9' }}>
                {p.product_name.split(' ').slice(0, 3).join(' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.attribute} style={{ background: i % 2 === 0 ? '#0f172a' : '#1e293b' }}>
              <td style={{ padding: '6px 8px', color: '#94a3b8' }}>{row.attribute}</td>
              {row.values.map((val, j) => (
                <td key={j} style={{ textAlign: 'center', padding: '6px 8px', color: '#f1f5f9' }}>{val}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
