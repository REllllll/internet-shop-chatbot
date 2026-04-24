import { describe, expect, it, vi } from 'vitest'
import { ensureDefaultWorkflow, restoreDefaultWorkflow } from '../workflow.js'

describe('workflow management', () => {
  it('imports default workflow when no matching workflow exists', async () => {
    const fetch = vi.fn(async (url: string, init?: RequestInit) => {
      if (url.endsWith('/rest/workflows')) {
        return { ok: true, json: async () => ({ data: [] }) }
      }
      if (url.endsWith('/rest/workflows/import')) {
        expect(init?.method).toBe('POST')
        return { ok: true, json: async () => ({ id: 'wf-1' }) }
      }
      throw new Error(`unexpected url ${url}`)
    })

    const result = await ensureDefaultWorkflow('http://127.0.0.1:5678', '{"name":"Recommendation Pipeline"}', fetch as typeof globalThis.fetch)

    expect(result.imported).toBe(true)
  })

  it('skips import when recommendation workflow already exists', async () => {
    const fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ data: [{ id: 'wf-1', name: 'Recommendation Pipeline' }] }),
    }))

    const result = await ensureDefaultWorkflow('http://127.0.0.1:5678', '{"name":"Recommendation Pipeline"}', fetch as typeof globalThis.fetch)

    expect(result.imported).toBe(false)
  })

  it('restore always posts the default workflow import', async () => {
    const fetch = vi.fn(async () => ({ ok: true, json: async () => ({ id: 'wf-2' }) }))

    const result = await restoreDefaultWorkflow('http://127.0.0.1:5678', '{"name":"Recommendation Pipeline"}', fetch as typeof globalThis.fetch)

    expect(result).toEqual({ ok: true, message: 'Default workflow restored.' })
    expect(fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:5678/rest/workflows/import',
      expect.objectContaining({ method: 'POST' })
    )
  })
})
