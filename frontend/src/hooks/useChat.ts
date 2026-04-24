import { useState, useCallback } from 'react'
import type { Message, RecommendationResult } from '../types'

async function resolveApiBaseUrl(): Promise<string> {
  if (window.shopbotDesktop) {
    const config = await window.shopbotDesktop.getRuntimeConfig()
    return config.apiBaseUrl
  }
  return import.meta.env.VITE_API_URL ?? ''
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 'welcome', role: 'assistant', content: "Hi! I'm ShopBot. What are you looking for today?" },
  ])
  const [recommendations, setRecommendations] = useState<RecommendationResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(async (text: string) => {
    const assistantId = crypto.randomUUID()
    setRecommendations(null)
    setMessages(prev => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', content: text },
      { id: assistantId, role: 'assistant', content: '', isStreaming: true },
    ])
    setIsLoading(true)

    let retries = 0
    const attempt = async (): Promise<void> => {
      try {
        const apiBaseUrl = await resolveApiBaseUrl()
        const res = await fetch(`${apiBaseUrl}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ message: text }),
        })
        if (!res.ok || !res.body) {
          throw new Error(`Chat request failed with HTTP ${res.status}`)
        }
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buf = ''
        for (;;) {
          const { done, value } = await reader.read()
          if (done) break
          buf += decoder.decode(value, { stream: true })
          const parts = buf.split('\n\n')
          buf = parts.pop() ?? ''
          for (const part of parts) {
            if (!part.startsWith('data: ')) continue
            const payload = JSON.parse(part.slice(6))
            if (payload.type === 'text') {
              setMessages(prev =>
                prev.map(m => m.id === assistantId ? { ...m, content: m.content + payload.content } : m)
              )
            } else if (payload.type === 'products') {
              setRecommendations(payload.data)
            } else if (payload.type === 'done') {
              setMessages(prev =>
                prev.map(m => m.id === assistantId ? { ...m, isStreaming: false } : m)
              )
            }
          }
        }
      } catch {
        if (retries++ < 3) return attempt()
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? { ...m, content: 'Connection error. Please try again.', isStreaming: false }
              : m
          )
        )
      } finally {
        setIsLoading(false)
      }
    }
    await attempt()
  }, [])

  return { messages, recommendations, isLoading, sendMessage }
}
