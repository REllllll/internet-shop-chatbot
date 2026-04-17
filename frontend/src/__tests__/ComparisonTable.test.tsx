import { render, screen } from '@testing-library/react'
import { ComparisonTable } from '../components/ComparisonTable'
import type { ComparisonRow, Product } from '../types'

const products = [
  { product_id: 'B001', product_name: 'Cable A' },
  { product_id: 'B002', product_name: 'Cable B' },
  { product_id: 'B003', product_name: 'Cable C' },
] as Product[]

const rows: ComparisonRow[] = [
  { attribute: 'Price', values: ['399', '299', '499'] },
  { attribute: 'Rating',    values: ['4.2', '4.0', '4.5'] },
]

describe('ComparisonTable', () => {
  it('renders product names as headers', () => {
    render(<ComparisonTable products={products} rows={rows} />)
    expect(screen.getByText('Cable A')).toBeInTheDocument()
    expect(screen.getByText('Cable B')).toBeInTheDocument()
  })

  it('renders attribute row labels', () => {
    render(<ComparisonTable products={products} rows={rows} />)
    expect(screen.getByText('Price')).toBeInTheDocument()
    expect(screen.getByText('Rating')).toBeInTheDocument()
  })

  it('renders cell values', () => {
    render(<ComparisonTable products={products} rows={rows} />)
    expect(screen.getByText('4.5')).toBeInTheDocument()
  })

  it('converts price values to USD by default', () => {
    render(<ComparisonTable products={products} rows={rows} />)
    expect(screen.getByText('$4.79')).toBeInTheDocument()
  })

  it('converts price values to INR when selected', () => {
    render(<ComparisonTable products={products} rows={rows} currency="INR" />)
    expect(screen.getByText('₹399.00')).toBeInTheDocument()
  })
})
