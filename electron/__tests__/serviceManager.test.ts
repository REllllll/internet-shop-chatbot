import { EventEmitter } from 'node:events'
import { describe, expect, it, vi } from 'vitest'
import { ServiceManager } from '../serviceManager.js'
import type { DesktopPaths } from '../paths.js'

const paths: DesktopPaths = {
  appDataDir: '/tmp/shopbot',
  seedDatabasePath: '/tmp/shopbot-seed/products.db',
  writableDatabasePath: '/tmp/shopbot/products.db',
  workflowPath: '/tmp/shopbot/recommendation-pipeline.json',
  backendExecutablePath: '/tmp/shopbot-backend',
  nodeExecutablePath: '/tmp/node',
  n8nEntryPath: '/tmp/n8n',
  n8nDataDir: '/tmp/shopbot/n8n',
  envFilePath: '/tmp/shopbot/.env',
  rendererIndexPath: '/tmp/shopbot/index.html',
}

describe('ServiceManager', () => {
  it('marks both services ready after health checks pass', async () => {
    const child = new EventEmitter() as EventEmitter & { kill: ReturnType<typeof vi.fn>; pid: number }
    child.kill = vi.fn()
    child.pid = 123

    const spawn = vi.fn(() => child)
    const fetch = vi.fn(async () => ({ ok: true }))
    const manager = new ServiceManager(paths, { spawn, fetch, waitMs: async () => undefined })

    await manager.start()

    expect(manager.getStatus().backend.state).toBe('ready')
    expect(manager.getStatus().n8n.state).toBe('ready')
    expect(spawn).toHaveBeenCalledTimes(2)
  })

  it('records startup errors without losing service urls', async () => {
    const spawn = vi.fn(() => {
      throw new Error('missing executable')
    })
    const fetch = vi.fn()
    const manager = new ServiceManager(paths, { spawn, fetch, waitMs: async () => undefined })

    await manager.start()

    expect(manager.getStatus().backend.state).toBe('error')
    expect(manager.getStatus().backend.message).toContain('missing executable')
    expect(manager.getStatus().backend.url).toBe('http://127.0.0.1:8000')
  })
})
