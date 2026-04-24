import net from 'node:net'

export async function isPortAvailable(port: number): Promise<boolean> {
  if (port === 0) return true

  return new Promise((resolve) => {
    const server = net.createServer()
    server.once('error', () => resolve(false))
    server.once('listening', () => {
      server.close(() => resolve(true))
    })
    server.listen(port, '127.0.0.1')
  })
}

export async function assertPortAvailable(port: number, label: string): Promise<void> {
  const available = await isPortAvailable(port)
  if (!available) {
    throw new Error(`${label} port ${port} is already in use on 127.0.0.1`)
  }
}
