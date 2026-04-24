import net from 'node:net'
import { afterEach, describe, expect, it } from 'vitest'
import { assertPortAvailable, isPortAvailable } from '../ports.js'

let server: net.Server | undefined

afterEach(async () => {
  if (!server) return
  await new Promise<void>((resolve) => server!.close(() => resolve()))
  server = undefined
})

describe('port checks', () => {
  it('reports an unused loopback port as available', async () => {
    expect(await isPortAvailable(0)).toBe(true)
  })

  it('throws a clear error when a fixed port is occupied', async () => {
    server = net.createServer()
    await new Promise<void>((resolve) => server!.listen(0, '127.0.0.1', resolve))
    const address = server.address()
    if (!address || typeof address === 'string') throw new Error('expected tcp address')

    await expect(assertPortAvailable(address.port, 'FastAPI')).rejects.toThrow(
      `FastAPI port ${address.port} is already in use on 127.0.0.1`
    )
  })
})
