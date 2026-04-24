import { contextBridge, ipcRenderer } from 'electron'
import type { DesktopStatus, RuntimeConfig, ShopBotDesktopApi } from './types.js'

const api: ShopBotDesktopApi = {
  getRuntimeConfig: () => ipcRenderer.invoke('shopbot:getRuntimeConfig') as Promise<RuntimeConfig>,
  getStatus: () => ipcRenderer.invoke('shopbot:getStatus') as Promise<DesktopStatus>,
  openWorkflow: () => ipcRenderer.invoke('shopbot:openWorkflow') as Promise<void>,
  restoreDefaultWorkflow: () => ipcRenderer.invoke('shopbot:restoreDefaultWorkflow') as Promise<{ ok: boolean; message: string }>,
  retryServices: () => ipcRenderer.invoke('shopbot:retryServices') as Promise<DesktopStatus>,
  onStatusChange: (callback) => {
    const listener = (_event: Electron.IpcRendererEvent, status: DesktopStatus) => callback(status)
    ipcRenderer.on('shopbot:statusChanged', listener)
    return () => ipcRenderer.removeListener('shopbot:statusChanged', listener)
  },
}

contextBridge.exposeInMainWorld('shopbotDesktop', api)
