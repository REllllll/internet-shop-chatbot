export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

export interface Product {
  product_id: string
  product_name: string
  category: string
  discounted_price: number | null
  actual_price: number | null
  discount_percentage: number | null
  rating: number | null
  rating_count: number | null
  about_product: string
  img_link: string
  product_link: string
}

export interface ComparisonRow {
  attribute: string
  values: string[]
}

export interface RecommendationResult {
  products: Product[]
  comparison: ComparisonRow[]
  fallback?: boolean
}