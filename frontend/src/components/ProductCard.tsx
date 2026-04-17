import type { Product } from '../types'
import type { CurrencyCode } from '../utils/currency'
import { convertPrice } from '../utils/currency'

export function ProductCard({
  product,
  rank,
  currency = 'USD',
}: {
  product: Product
  rank: number
  currency?: CurrencyCode
}) {
  return (
    <div style={{
      border: rank === 1 ? '1px solid #2563eb' : '1px solid #334155',
      borderRadius: 8, padding: 12, marginBottom: 10, background: '#0f172a',
    }}>
      {rank === 1 && (
        <div style={{ fontSize: 11, color: '#2563eb', fontWeight: 700, marginBottom: 4 }}>TOP PICK</div>
      )}
      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 6, color: '#f1f5f9' }}>
        {product.product_name}
      </div>
      <div style={{ display: 'flex', gap: 12, fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>
        <span>{convertPrice(product.discounted_price, currency)}</span>
        {product.actual_price && product.actual_price > (product.discounted_price ?? 0) && (
          <span style={{ textDecoration: 'line-through', opacity: 0.5 }}>
            {convertPrice(product.actual_price, currency)}
          </span>
        )}
        {product.discount_percentage && (
          <span style={{ color: '#22c55e' }}>{product.discount_percentage}% off</span>
        )}
      </div>
      <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 8 }}>
        ⭐ {product.rating?.toFixed(1)} · {product.rating_count?.toLocaleString()} reviews
      </div>
      <a href={product.product_link} target="_blank" rel="noopener noreferrer"
        style={{ fontSize: 12, color: '#2563eb' }}>
        View on Amazon →
      </a>
    </div>
  )
}
