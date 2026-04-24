export {}

declare global {
  type ServiceName = 'backend' | 'n8n'
  type ServiceState = 'stopped' | 'starting' | 'ready' | 'error'

  interface ServiceStatus {
    name: ServiceName
    state: ServiceState
    url: string
    message?: string
  }

  interface DesktopStatus {
    backend: ServiceStatus
    n8n: ServiceStatus
  }

  interface RuntimeConfig {
    apiBaseUrl: string
    workflowUrl: string
  }

  interface Window {
    shopbotDesktop?: {
      getRuntimeConfig(): Promise<RuntimeConfig>
      getStatus(): Promise<DesktopStatus>
      openWorkflow(): Promise<void>
      restoreDefaultWorkflow(): Promise<{ ok: boolean; message: string }>
      retryServices(): Promise<DesktopStatus>
      onStatusChange(callback: (status: DesktopStatus) => void): () => void
    }
  }
}
