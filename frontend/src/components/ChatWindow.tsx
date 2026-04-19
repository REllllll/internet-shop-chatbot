import { useRef, useEffect, useState } from 'react'
import type { Message } from '../types'
import { MessageBubble } from './MessageBubble'

interface Props {
  messages: Message[]
  isLoading: boolean
  onSend: (text: string) => void
}

export function ChatWindow({ messages, isLoading, onSend }: Props) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading) return
    setInput('')
    onSend(text)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
        {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit}
        style={{ padding: 16, borderTop: '1px solid #1e293b', display: 'flex', gap: 8 }}>
        <input
          id="chat-message"
          name="message"
          aria-label="Chat message"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={isLoading}
          style={{
            flex: 1, padding: '10px 14px', borderRadius: 8,
            border: '1px solid #334155', background: '#1e293b',
            color: '#f1f5f9', fontSize: 14,
          }}
        />
        <button type="submit" disabled={isLoading || !input.trim()}
          style={{
            padding: '10px 20px', borderRadius: 8, background: '#2563eb',
            color: '#fff', border: 'none',
            cursor: isLoading ? 'not-allowed' : 'pointer', fontSize: 14,
          }}>
          Send
        </button>
      </form>
    </div>
  )
}
