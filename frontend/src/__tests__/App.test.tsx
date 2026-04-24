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
    delete (window as unknown as Record<string, unknown>).shopbotDesktop
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

  it('shows desktop service status when Electron bridge is available', async () => {
    Object.defineProperty(window, 'shopbotDesktop', {
      value: {
        getStatus: vi.fn().mockResolvedValue({
          backend: { name: 'backend', state: 'ready', url: 'http://127.0.0.1:8000' },
          n8n: { name: 'n8n', state: 'starting', url: 'http://127.0.0.1:5678' },
        }),
        onStatusChange: vi.fn(() => vi.fn()),
        openWorkflow: vi.fn(),
        restoreDefaultWorkflow: vi.fn(),
        retryServices: vi.fn(),
      },
      configurable: true,
    })

    render(<App />)

    expect(await screen.findByText(/Backend: ready/i)).toBeInTheDocument()
    expect(await screen.findByText(/Workflow: starting/i)).toBeInTheDocument()
  })

  it('renders workflow controls in desktop mode', async () => {
    Object.defineProperty(window, 'shopbotDesktop', {
      value: {
        getStatus: vi.fn().mockResolvedValue({
          backend: { name: 'backend', state: 'ready', url: 'http://127.0.0.1:8000' },
          n8n: { name: 'n8n', state: 'ready', url: 'http://127.0.0.1:5678' },
        }),
        onStatusChange: vi.fn(() => vi.fn()),
        openWorkflow: vi.fn(),
        restoreDefaultWorkflow: vi.fn().mockResolvedValue({ ok: true, message: 'Default workflow restored.' }),
        retryServices: vi.fn(),
      },
      configurable: true,
    })

    render(<App />)

    expect(await screen.findByRole('button', { name: /Workflow/i })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /Restore/i })).toBeInTheDocument()
  })
})
