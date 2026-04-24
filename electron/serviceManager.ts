import { ChildProcess, spawn as nodeSpawn } from 'node:child_process'
import type { DesktopPaths } from './paths.js'
import type { DesktopStatus, ServiceName, ServiceStatus } from './types.js'

type SpawnFn = typeof nodeSpawn
type FetchFn = typeof fetch

interface ServiceManagerDeps {
  spawn?: SpawnFn
  fetch?: FetchFn
  waitMs?: (ms: number) => Promise<void>
}

const BACKEND_PORT = 8000
const N8N_PORT = 5678

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function initialStatus(name: ServiceName, port: number): ServiceStatus {
  return {
    name,
    state: 'stopped',
    url: `http://127.0.0.1:${port}`,
  }
}

export class ServiceManager {
  private backendProcess?: ChildProcess
  private n8nProcess?: ChildProcess
  private readonly spawn: SpawnFn
  private readonly fetch: FetchFn
  private readonly waitMs: (ms: number) => Promise<void>
  private status: DesktopStatus = {
    backend: initialStatus('backend', BACKEND_PORT),
    n8n: initialStatus('n8n', N8N_PORT),
  }

  constructor(private readonly paths: DesktopPaths, deps: ServiceManagerDeps = {}) {
    this.spawn = deps.spawn ?? nodeSpawn
    this.fetch = deps.fetch ?? fetch
    this.waitMs = deps.waitMs ?? wait
  }

  getStatus(): DesktopStatus {
    return structuredClone(this.status)
  }

  async start(): Promise<DesktopStatus> {
    await this.startN8n()
    await this.startBackend()
    return this.getStatus()
  }

  async restart(): Promise<DesktopStatus> {
    await this.stop()
    return this.start()
  }

  async stop(): Promise<void> {
    this.backendProcess?.kill()
    this.n8nProcess?.kill()
    this.backendProcess = undefined
    this.n8nProcess = undefined
    this.status.backend.state = 'stopped'
    this.status.n8n.state = 'stopped'
  }

  private async startN8n(): Promise<void> {
    this.status.n8n = { ...this.status.n8n, state: 'starting', message: undefined }
    try {
      this.n8nProcess = this.spawn(this.paths.nodeExecutablePath, [this.paths.n8nEntryPath, 'start'], {
        env: {
          ...process.env,
          N8N_USER_FOLDER: this.paths.n8nDataDir,
          N8N_HOST: '127.0.0.1',
          N8N_PORT: String(N8N_PORT),
          N8N_PROTOCOL: 'http',
          N8N_SECURE_COOKIE: 'false',
        },
        stdio: 'pipe',
      })
      await this.waitForHealth(`${this.status.n8n.url}/healthz`)
      this.status.n8n.state = 'ready'
    } catch (error) {
      this.status.n8n.state = 'error'
      this.status.n8n.message = error instanceof Error ? error.message : String(error)
    }
  }

  private async startBackend(): Promise<void> {
    this.status.backend = { ...this.status.backend, state: 'starting', message: undefined }
    try {
      this.backendProcess = this.spawn(this.paths.backendExecutablePath, [], {
        env: {
          ...process.env,
          DATABASE_PATH: this.paths.writableDatabasePath,
          N8N_WEBHOOK_URL: `${this.status.n8n.url}/webhook/recommend`,
          PORT: String(BACKEND_PORT),
        },
        stdio: 'pipe',
      })
      await this.waitForHealth(`${this.status.backend.url}/health`)
      this.status.backend.state = 'ready'
    } catch (error) {
      this.status.backend.state = 'error'
      this.status.backend.message = error instanceof Error ? error.message : String(error)
    }
  }

  private async waitForHealth(url: string): Promise<void> {
    let lastError = 'service did not become ready'
    for (let attempt = 0; attempt < 40; attempt += 1) {
      try {
        const response = await this.fetch(url)
        if (response.ok) return
        lastError = `health check returned HTTP ${response.status}`
      } catch (error) {
        lastError = error instanceof Error ? error.message : String(error)
      }
      await this.waitMs(500)
    }
    throw new Error(lastError)
  }
}
