export type CurrencyCode = 'USD' | 'INR' | 'EUR'

export const CURRENCIES: Record<CurrencyCode, { symbol: string; rateFromINR: number }> = {
  USD: { symbol: '$', rateFromINR: 0.012 },
  INR: { symbol: '₹', rateFromINR: 1 },
  EUR: { symbol: '€', rateFromINR: 0.011 },
}

export function convertPrice(priceInINR: number | null, currency: CurrencyCode): string {
  if (priceInINR == null || Number.isNaN(priceInINR)) return 'N/A'
  const converted = priceInINR * CURRENCIES[currency].rateFromINR
  return `${CURRENCIES[currency].symbol}${converted.toFixed(2)}`
}

export function formatComparisonValue(attribute: string, value: string, currency: CurrencyCode): string {
  const priceAttrs = ['price', 'cost']
  const isPriceRow = priceAttrs.some(a => attribute.toLowerCase().includes(a))
  if (!isPriceRow) return value

  const num = parseFloat(value.replace(/[^\d.]/g, ''))
  if (Number.isNaN(num)) return value
  return `${CURRENCIES[currency].symbol}${(num * CURRENCIES[currency].rateFromINR).toFixed(2)}`
}
