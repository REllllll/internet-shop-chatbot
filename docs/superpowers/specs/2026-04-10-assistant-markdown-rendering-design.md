# Assistant Markdown Rendering Design

## Goal

Render chatbot assistant responses as markdown in the frontend chat window while leaving user messages as plain text.

## Scope

- Update the message bubble component to render assistant content through a markdown renderer.
- Keep user messages unchanged so user-entered markdown syntax remains literal text.
- Preserve the existing streaming indicator behavior.
- Add tests covering assistant markdown rendering and user plain-text rendering.

## Design

The current chat UI renders `message.content` directly in `frontend/src/components/MessageBubble.tsx`, so markdown tokens such as `**bold**`, lists, and links appear as raw text. The frontend should switch only assistant bubbles to a markdown renderer.

`react-markdown` with `remark-gfm` is the preferred implementation because it supports common chatbot output patterns such as emphasis, lists, links, tables, and fenced code blocks without requiring custom parsing. The streaming cursor should remain outside the markdown renderer so partial responses continue to show progress consistently.

## Affected Files

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/components/MessageBubble.tsx`
- `frontend/src/__tests__/MessageBubble.test.tsx`

## Testing

- Verify assistant markdown renders semantic HTML for emphasis or lists.
- Verify user content containing markdown markers remains literal text.
- Verify the streaming indicator still appears for streaming assistant messages.
