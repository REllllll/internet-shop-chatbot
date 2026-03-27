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
})
