import { render, screen } from '@testing-library/react'
import { ProductCard } from '../components/ProductCard'
import type { Product } from '../types'

const product: Product = {
  product_id: 'B001', product_name: 'USB Lightning Cable',
  category: 'Computers&Accessories|Cables',
  discounted_price: 399, actual_price: 1099, discount_percentage: 64,
  rating: 4.2, rating_count: 24269, about_product: 'Fast charging',
  img_link: '', product_link: 'https://amazon.in/B001',
}

describe('ProductCard', () => {
  it('renders product name', () => {
    render(<ProductCard product={product} rank={1} />)
    expect(screen.getByText('USB Lightning Cable')).toBeInTheDocument()
  })

  it('renders discounted price', () => {
    render(<ProductCard product={product} rank={1} />)
    expect(screen.getByText(/₹399/)).toBeInTheDocument()
  })

  it('renders rating', () => {
    render(<ProductCard product={product} rank={1} />)
    expect(screen.getByText(/4\.2/)).toBeInTheDocument()
  })

  it('links to product page', () => {
    render(<ProductCard product={product} rank={1} />)
    expect(screen.getByRole('link')).toHaveAttribute('href', 'https://amazon.in/B001')
  })
})
