import { app, BrowserWindow, dialog, ipcMain } from 'electron'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { readFileSync } from 'node:fs'
import type { DesktopStatus, RuntimeConfig } from './types.js'
import { ensureFirstRunData, getDesktopPaths } from './paths.js'
import { assertPortAvailable } from './ports.js'
import { ServiceManager } from './serviceManager.js'
import { ensureDefaultWorkflow, restoreDefaultWorkflow } from './workflow.js'

let mainWindow: BrowserWindow | null = null
let serviceManager: ServiceManager | null = null

function currentStatus(): DesktopStatus {
  if (!serviceManager) {
    return {
      backend: { name: 'backend', state: 'stopped', url: 'http://127.0.0.1:8000' },
      n8n: { name: 'n8n', state: 'stopped', url: 'http://127.0.0.1:5678' },
    }
  }
  return serviceManager.getStatus()
}

function runtimeConfig(): RuntimeConfig {
  const status = currentStatus()
  return {
    apiBaseUrl: status.backend.url,
    workflowUrl: status.n8n.url,
  }
}

function broadcastStatus(): void {
  if (mainWindow) {
    mainWindow.webContents.send('shopbot:statusChanged', currentStatus())
  }
}

async function startServices(): Promise<DesktopStatus> {
  const paths = getDesktopPaths(app)
  await assertPortAvailable(8000, 'FastAPI')
  await assertPortAvailable(5678, 'n8n')
  ensureFirstRunData(paths)
  serviceManager = new ServiceManager(paths)
  const status = await serviceManager.start()
  if (status.n8n.state === 'ready') {
    const workflowJson = readFileSync(paths.workflowPath, 'utf8')
    await ensureDefaultWorkflow(status.n8n.url, workflowJson)
  }
  broadcastStatus()
  return serviceManager.getStatus()
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
  void startServices().catch(handleStartupError)
}

function handleStartupError(error: unknown): void {
  const message = error instanceof Error ? error.message : String(error)
  dialog.showErrorBox('ShopBot failed to start', message)
  app.quit()
}

ipcMain.handle('shopbot:getRuntimeConfig', () => runtimeConfig())
ipcMain.handle('shopbot:getStatus', () => currentStatus())
ipcMain.handle('shopbot:openWorkflow', async () => undefined)
ipcMain.handle('shopbot:restoreDefaultWorkflow', async () => {
  const paths = getDesktopPaths(app)
  const status = currentStatus()
  if (status.n8n.state !== 'ready') {
    return { ok: false, message: 'n8n is not ready.' }
  }
  try {
    const workflowJson = readFileSync(paths.workflowPath, 'utf8')
    return await restoreDefaultWorkflow(status.n8n.url, workflowJson)
  } catch (error) {
    return {
      ok: false,
      message: error instanceof Error ? error.message : String(error),
    }
  }
})
ipcMain.handle('shopbot:retryServices', async () => startServices())

app.whenReady().then(createWindow).catch(handleStartupError)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  void serviceManager?.stop()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    void createWindow().catch(handleStartupError)
  }
})
