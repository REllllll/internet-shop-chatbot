export type ServiceName = 'backend' | 'n8n'

export type ServiceState = 'stopped' | 'starting' | 'ready' | 'error'

export interface ServiceStatus {
  name: ServiceName
  state: ServiceState
  url: string
  message?: string
}

export interface DesktopStatus {
  backend: ServiceStatus
  n8n: ServiceStatus
}

export interface RuntimeConfig {
  apiBaseUrl: string
  workflowUrl: string
}

export interface ShopBotDesktopApi {
  getRuntimeConfig(): Promise<RuntimeConfig>
  getStatus(): Promise<DesktopStatus>
  openWorkflow(): Promise<void>
  restoreDefaultWorkflow(): Promise<{ ok: boolean; message: string }>
  retryServices(): Promise<DesktopStatus>
  onStatusChange(callback: (status: DesktopStatus) => void): () => void
}

declare global {
  interface Window {
    shopbotDesktop?: ShopBotDesktopApi
  }
}
