import type { Message } from '../types'

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  return (
    <div
      data-testid={`bubble-${message.role}`}
      style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: 8 }}
    >
      <div style={{
        maxWidth: '75%', padding: '10px 14px', borderRadius: 12,
        background: isUser ? '#2563eb' : '#1e293b',
        color: '#f1f5f9', fontSize: 14, lineHeight: 1.5,
      }}>
        {message.content}
        {message.isStreaming && (
          <span data-testid="streaming-indicator" style={{ marginLeft: 4, opacity: 0.6 }}>▌</span>
        )}
      </div>
    </div>
  )
}
