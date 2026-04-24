import path from 'node:path'
import { mkdirSync, copyFileSync, existsSync } from 'node:fs'
import type { App } from 'electron'

export interface DesktopPaths {
  appDataDir: string
  seedDatabasePath: string
  writableDatabasePath: string
  workflowPath: string
  backendExecutablePath: string
  nodeExecutablePath: string
  n8nEntryPath: string
  n8nDataDir: string
  envFilePath: string
  rendererIndexPath: string
}

export function resolveAppSourcePath(app: Pick<App, 'getAppPath'>, relativePath: string): string {
  return path.join(app.getAppPath(), relativePath)
}

export function resolveRuntimeResourcePath(app: Pick<App, 'isPackaged' | 'getAppPath'>, relativePath: string): string {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, relativePath)
  }
  return resolveAppSourcePath(app, relativePath)
}

export function getDesktopPaths(app: Pick<App, 'isPackaged' | 'getAppPath' | 'getPath'>): DesktopPaths {
  const appDataDir = path.join(app.getPath('appData'), 'ShopBot')
  const backendName = process.platform === 'win32' ? 'shopbot-backend.exe' : 'shopbot-backend'
  const nodeName = process.platform === 'win32' ? 'node.exe' : 'node'

  return {
    appDataDir,
    seedDatabasePath: resolveRuntimeResourcePath(app, 'data/products.db'),
    writableDatabasePath: path.join(appDataDir, 'products.db'),
    workflowPath: resolveRuntimeResourcePath(app, 'workflows/recommendation-pipeline.json'),
    backendExecutablePath: resolveRuntimeResourcePath(app, path.join('backend', backendName)),
    nodeExecutablePath: resolveRuntimeResourcePath(app, path.join('node', 'bin', nodeName)),
    n8nEntryPath: resolveRuntimeResourcePath(app, path.join('n8n', 'node_modules', 'n8n', 'bin', 'n8n')),
    n8nDataDir: path.join(appDataDir, 'n8n'),
    envFilePath: path.join(appDataDir, '.env'),
    rendererIndexPath: resolveRuntimeResourcePath(app, path.join('frontend', 'dist', 'index.html')),
  }
}

export function ensureFirstRunData(paths: DesktopPaths): void {
  mkdirSync(paths.appDataDir, { recursive: true })
  mkdirSync(paths.n8nDataDir, { recursive: true })

  if (!existsSync(paths.writableDatabasePath)) {
    copyFileSync(paths.seedDatabasePath, paths.writableDatabasePath)
  }
}
