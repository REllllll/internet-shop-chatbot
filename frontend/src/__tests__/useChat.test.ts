import { renderHook, act } from '@testing-library/react'
import { useChat } from '../hooks/useChat'

const mockSSE = (events: string[]) => {
  const enc = new TextEncoder()
  let i = 0
  const stream = new ReadableStream({
    pull(ctrl) {
      if (i < events.length) ctrl.enqueue(enc.encode(events[i++]))
      else ctrl.close()
    },
  })
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' } })
}

describe('useChat', () => {
  beforeEach(() => vi.resetAllMocks())

  it('starts with a welcome message', () => {
    const { result } = renderHook(() => useChat())
    expect(result.current.messages).toHaveLength(1)
    expect(result.current.messages[0].role).toBe('assistant')
  })

  it('adds user message on sendMessage', async () => {
    global.fetch = vi.fn().mockResolvedValue(
      mockSSE([`data: ${JSON.stringify({ type: 'done' })}\n\n`])
    )
    const { result } = renderHook(() => useChat())
    await act(async () => { await result.current.sendMessage('hello') })
    expect(result.current.messages.some(m => m.role === 'user' && m.content === 'hello')).toBe(true)
  })

  it('sets recommendations when products event received', async () => {
    const products = [{ product_id: 'B001', product_name: 'Cable' }]
    global.fetch = vi.fn().mockResolvedValue(
      mockSSE([
        `data: ${JSON.stringify({ type: 'products', data: { products, comparison: [] } })}\n\n`,
        `data: ${JSON.stringify({ type: 'done' })}\n\n`,
      ])
    )
    const { result } = renderHook(() => useChat())
    await act(async () => { await result.current.sendMessage('show me products') })
    expect(result.current.recommendations?.products).toEqual(products)
  })

  it('clears previous recommendations when a new message is sent', async () => {
    const products = [{ product_id: 'B001', product_name: 'Cable' }]
    global.fetch = vi.fn()
      .mockResolvedValueOnce(
        mockSSE([
          `data: ${JSON.stringify({ type: 'products', data: { products, comparison: [] } })}\n\n`,
          `data: ${JSON.stringify({ type: 'done' })}\n\n`,
        ])
      )
      .mockResolvedValueOnce(
        mockSSE([`data: ${JSON.stringify({ type: 'done' })}\n\n`])
      )

    const { result } = renderHook(() => useChat())

    await act(async () => { await result.current.sendMessage('show me products') })
    expect(result.current.recommendations?.products).toEqual(products)

    await act(async () => { await result.current.sendMessage('try something else') })
    expect(result.current.recommendations).toBeNull()
  })
})
