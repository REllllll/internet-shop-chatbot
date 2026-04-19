import { useState } from 'react'
import { useChat } from './hooks/useChat'
import { ChatWindow } from './components/ChatWindow'
import { ProductCard } from './components/ProductCard'
import { ComparisonTable } from './components/ComparisonTable'
import { CURRENCIES, type CurrencyCode } from './utils/currency'

export default function App() {
  const { messages, recommendations, isLoading, sendMessage } = useChat()
  const [currency, setCurrency] = useState<CurrencyCode>('USD')
  const hasRecommendations = Boolean(recommendations)
  const hasProducts = (recommendations?.products.length ?? 0) > 0

  return (
    <div style={{
      display: 'flex', height: '100vh',
      background: '#020617', color: '#f1f5f9',
      fontFamily: 'system-ui, sans-serif',
    }}>
      {/* Left: chat */}
      <div style={{ flex: '0 0 50%', display: 'flex', flexDirection: 'column', borderRight: '1px solid #1e293b' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #1e293b', fontWeight: 700, fontSize: 18 }}>
          ShopBot
        </div>
        <ChatWindow messages={messages} isLoading={isLoading} onSend={sendMessage} />
      </div>

      {/* Right: products */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
          <select
            value={currency}
            onChange={e => setCurrency(e.target.value as CurrencyCode)}
            style={{
              padding: '6px 10px',
              borderRadius: 6,
              border: '1px solid #334155',
              background: '#1e293b',
              color: '#f1f5f9',
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            {Object.entries(CURRENCIES).map(([code, { symbol }]) => (
              <option key={code} value={code}>
                {symbol} {code}
              </option>
            ))}
          </select>
        </div>
        {hasRecommendations ? (
          <>
            {hasProducts ? (
              <>
                <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 16, color: '#94a3b8' }}>
                  {recommendations?.fallback ? 'Products found (pipeline unavailable)' : `Top ${recommendations?.products.length} Picks`}
                </div>
                {recommendations?.products.map((p, i) => (
                  <ProductCard key={p.product_id} product={p} rank={i + 1} currency={currency} />
                ))}
                {(recommendations?.comparison.length ?? 0) > 0 && (
                  <>
                    <div style={{ fontWeight: 600, fontSize: 14, marginTop: 20, marginBottom: 8, color: '#64748b' }}>
                      COMPARISON
                    </div>
                    <ComparisonTable products={recommendations!.products} rows={recommendations!.comparison} currency={currency} />
                  </>
                )}
              </>
            ) : (
              <div style={{
                height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: '#94a3b8', fontSize: 14, textAlign: 'center',
              }}>
                No products matched your request.
                <br />
                Try a higher budget, fewer keywords, or a broader category.
              </div>
            )}
          </>
        ) : (
          <div style={{
            height: '100%', display: 'flex', alignItems: 'center',
            justifyContent: 'center', color: '#334155', fontSize: 14, textAlign: 'center',
          }}>
            Product recommendations will<br />appear here after your conversation.
          </div>
        )}
      </div>
    </div>
  )
}
