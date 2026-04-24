import { render, screen } from '@testing-library/react'
import App from '../App'
import type { RecommendationResult } from '../types'

const mockUseChat = vi.fn()

vi.mock('../hooks/useChat', () => ({
  useChat: () => mockUseChat(),
}))

describe('App', () => {
  beforeEach(() => {
    Element.prototype.scrollIntoView = vi.fn()
    mockUseChat.mockReturnValue({
      messages: [{ id: 'welcome', role: 'assistant', content: 'Hi! I\'m ShopBot.' }],
      recommendations: null,
      isLoading: false,
      sendMessage: vi.fn(),
    })
  })

  it('shows a no-results message when recommendation payload is empty', () => {
    const recommendations: RecommendationResult & { empty: true } = {
      products: [],
      comparison: [],
      fallback: true,
      empty: true,
    }

    mockUseChat.mockReturnValue({
      messages: [{ id: 'welcome', role: 'assistant', content: 'Hi! I\'m ShopBot.' }],
      recommendations,
      isLoading: false,
      sendMessage: vi.fn(),
    })

    render(<App />)

    expect(screen.getByText(/No products matched your request/i)).toBeInTheDocument()
    expect(screen.queryByText(/Products found/i)).not.toBeInTheDocument()
  })

  it('adds accessible name attributes to the chat input', () => {
    render(<App />)

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('id', 'chat-message')
    expect(input).toHaveAttribute('name', 'message')
  })
})
