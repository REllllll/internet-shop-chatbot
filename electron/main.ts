import { app, BrowserWindow, dialog, ipcMain } from 'electron'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import type { DesktopStatus, RuntimeConfig } from './types.js'
import { ensureFirstRunData, getDesktopPaths } from './paths.js'

const BACKEND_PORT = 8000
const N8N_PORT = 5678

let mainWindow: BrowserWindow | null = null

const status: DesktopStatus = {
  backend: { name: 'backend', state: 'stopped', url: `http://127.0.0.1:${BACKEND_PORT}` },
  n8n: { name: 'n8n', state: 'stopped', url: `http://127.0.0.1:${N8N_PORT}` },
}

function runtimeConfig(): RuntimeConfig {
  return {
    apiBaseUrl: status.backend.url,
    workflowUrl: status.n8n.url,
  }
}

async function createWindow(): Promise<void> {
  const paths = getDesktopPaths(app)
  ensureFirstRunData(paths)

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1000,
    minHeight: 680,
    webPreferences: {
      preload: path.join(app.getAppPath(), 'dist-electron', 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  const rendererUrl = app.isPackaged
    ? pathToFileURL(paths.rendererIndexPath).toString()
    : 'http://127.0.0.1:5173'

  await mainWindow.loadURL(rendererUrl)
}

function handleStartupError(error: unknown): void {
  const message = error instanceof Error ? error.message : String(error)
  dialog.showErrorBox('ShopBot failed to start', message)
  app.quit()
}

ipcMain.handle('shopbot:getRuntimeConfig', () => runtimeConfig())
ipcMain.handle('shopbot:getStatus', () => status)
ipcMain.handle('shopbot:openWorkflow', async () => undefined)
ipcMain.handle('shopbot:restoreDefaultWorkflow', async () => ({ ok: false, message: 'Workflow restore is wired in Task 5.' }))
ipcMain.handle('shopbot:retryServices', async () => status)

app.whenReady().then(createWindow).catch(handleStartupError)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    void createWindow().catch(handleStartupError)
  }
})
