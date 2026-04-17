# Assistant Markdown Rendering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render assistant chat messages as markdown while preserving plain-text rendering for user messages.

**Architecture:** Keep the rendering boundary inside `MessageBubble.tsx`. Assistant messages use a markdown component with GFM support, while user messages continue to render the raw string. Tests in the existing message bubble test file verify both behaviors and the streaming indicator.

**Tech Stack:** React 19, TypeScript, Vitest, Testing Library, `react-markdown`, `remark-gfm`

---

### Task 1: Add the failing markdown-rendering test

**Files:**
- Modify: `frontend/src/__tests__/MessageBubble.test.tsx`
- Test: `frontend/src/__tests__/MessageBubble.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
it('renders assistant markdown as formatted content', () => {
  render(<MessageBubble message={{ id: '4', role: 'assistant', content: '**Bold** item' }} />)
  expect(screen.getByText('Bold')).toBeInTheDocument()
  expect(screen.getByText('Bold').tagName).toBe('STRONG')
})

it('keeps user markdown-like text as plain text', () => {
  render(<MessageBubble message={{ id: '5', role: 'user', content: '**Bold** item' }} />)
  expect(screen.queryByText('Bold')?.tagName).not.toBe('STRONG')
  expect(screen.getByText('**Bold** item')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- MessageBubble.test.tsx`
Expected: FAIL because assistant content still renders as a plain text node.

### Task 2: Implement assistant-only markdown rendering

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Modify: `frontend/src/components/MessageBubble.tsx`
- Test: `frontend/src/__tests__/MessageBubble.test.tsx`

- [ ] **Step 1: Write minimal implementation**

```tsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const content = isUser ? (
  message.content
) : (
  <ReactMarkdown remarkPlugins={[remarkGfm]}>
    {message.content}
  </ReactMarkdown>
)
```

- [ ] **Step 2: Keep the streaming indicator outside the markdown content**

```tsx
{content}
{message.isStreaming && (
  <span data-testid="streaming-indicator" style={{ marginLeft: 4, opacity: 0.6 }}>▌</span>
)}
```

- [ ] **Step 3: Add runtime dependencies**

Run: `npm install react-markdown remark-gfm`
Expected: `frontend/package.json` and `frontend/package-lock.json` updated with the new dependencies.

### Task 3: Verify the change

**Files:**
- Test: `frontend/src/__tests__/MessageBubble.test.tsx`

- [ ] **Step 1: Run the targeted test suite**

Run: `npm test -- MessageBubble.test.tsx`
Expected: PASS

- [ ] **Step 2: Run the full frontend test suite**

Run: `npm test`
Expected: PASS
