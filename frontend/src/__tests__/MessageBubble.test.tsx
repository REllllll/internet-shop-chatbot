import { render, screen } from '@testing-library/react'
import { MessageBubble } from '../components/MessageBubble'

describe('MessageBubble', () => {
  it('renders user message', () => {
    render(<MessageBubble message={{ id: '1', role: 'user', content: 'Hello' }} />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByTestId('bubble-user')).toBeInTheDocument()
  })

  it('renders assistant message', () => {
    render(<MessageBubble message={{ id: '2', role: 'assistant', content: 'Hi' }} />)
    expect(screen.getByTestId('bubble-assistant')).toBeInTheDocument()
  })

  it('shows streaming indicator when isStreaming', () => {
    render(<MessageBubble message={{ id: '3', role: 'assistant', content: '', isStreaming: true }} />)
    expect(screen.getByTestId('streaming-indicator')).toBeInTheDocument()
  })

  it('renders assistant markdown as formatted content', () => {
    const { container } = render(
      <MessageBubble message={{ id: '4', role: 'assistant', content: '**Bold** item' }} />,
    )

    expect(screen.getByText('Bold')).toBeInTheDocument()
    expect(container.querySelector('strong')?.textContent).toBe('Bold')
  })

  it('keeps user markdown-like text as plain text', () => {
    const { container } = render(
      <MessageBubble message={{ id: '5', role: 'user', content: '**Bold** item' }} />,
    )

    expect(screen.getByText('**Bold** item')).toBeInTheDocument()
    expect(container.querySelector('strong')).toBeNull()
  })
})
