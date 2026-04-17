import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '../types'

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  const content = isUser ? (
    message.content
  ) : (
    <div style={{ display: 'grid', gap: 8 }}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ ...props }) => <p style={{ margin: 0 }} {...props} />,
          ul: ({ ...props }) => <ul style={{ margin: 0, paddingLeft: 20 }} {...props} />,
          ol: ({ ...props }) => <ol style={{ margin: 0, paddingLeft: 20 }} {...props} />,
          pre: ({ ...props }) => (
            <pre
              style={{
                margin: 0,
                padding: 12,
                borderRadius: 8,
                overflowX: 'auto',
                background: 'rgba(15, 23, 42, 0.65)',
              }}
              {...props}
            />
          ),
          code: ({ className, children, ...props }) => {
            const isInline = !className
            return (
              <code
                className={className}
                style={isInline ? { padding: '1px 4px', borderRadius: 4, background: 'rgba(15, 23, 42, 0.65)' } : undefined}
                {...props}
              >
                {children}
              </code>
            )
          },
          a: ({ ...props }) => <a style={{ color: '#93c5fd' }} target="_blank" rel="noreferrer" {...props} />,
        }}
      >
        {message.content}
      </ReactMarkdown>
    </div>
  )

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
        {content}
        {message.isStreaming && (
          <span data-testid="streaming-indicator" style={{ marginLeft: 4, opacity: 0.6 }}>▌</span>
        )}
      </div>
    </div>
  )
}
