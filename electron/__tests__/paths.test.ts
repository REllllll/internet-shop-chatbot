import path from 'node:path'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { afterEach, describe, expect, it } from 'vitest'
import { ensureFirstRunData, getDesktopPaths } from '../paths.js'

const originalResourcesPath = process.resourcesPath
const tempDirs: string[] = []

function makeTempDir(): string {
  const dir = mkdtempSync(path.join(tmpdir(), 'shopbot-electron-'))
  tempDirs.push(dir)
  return dir
}

function makeApp(options: { isPackaged: boolean; appPath: string; appDataDir: string }) {
  return {
    isPackaged: options.isPackaged,
    getAppPath: () => options.appPath,
    getPath: (name: string) => {
      if (name !== 'appData') {
        throw new Error(`Unexpected path request: ${name}`)
      }
      return options.appDataDir
    },
  }
}

afterEach(() => {
  Object.defineProperty(process, 'resourcesPath', {
    configurable: true,
    value: originalResourcesPath,
  })

  for (const dir of tempDirs.splice(0)) {
    rmSync(dir, { recursive: true, force: true })
  }
})

describe('getDesktopPaths', () => {
  it('resolves development assets from the app source path', () => {
    const appPath = path.join(makeTempDir(), 'repo')
    const appDataDir = path.join(makeTempDir(), 'app-data')

    const paths = getDesktopPaths(makeApp({ isPackaged: false, appPath, appDataDir }))

    expect(paths.seedDatabasePath).toBe(path.join(appPath, 'data', 'products.db'))
    expect(paths.workflowPath).toBe(path.join(appPath, 'workflows', 'recommendation-pipeline.json'))
    expect(paths.rendererIndexPath).toBe(path.join(appPath, 'frontend', 'dist', 'index.html'))
    expect(paths.backendExecutablePath).toBe(path.join(appPath, 'backend', process.platform === 'win32' ? 'shopbot-backend.exe' : 'shopbot-backend'))
    expect(paths.nodeExecutablePath).toBe(path.join(appPath, 'node', 'bin', process.platform === 'win32' ? 'node.exe' : 'node'))
  })

  it('resolves packaged runtime assets from Electron resources', () => {
    const resourcesPath = path.join(makeTempDir(), 'ShopBot.app', 'Contents', 'Resources')
    const appPath = path.join(resourcesPath, 'app.asar')
    const appDataDir = path.join(makeTempDir(), 'app-data')

    Object.defineProperty(process, 'resourcesPath', {
      configurable: true,
      value: resourcesPath,
    })

    const paths = getDesktopPaths(makeApp({ isPackaged: true, appPath, appDataDir }))

    expect(paths.seedDatabasePath).toBe(path.join(resourcesPath, 'data', 'products.db'))
    expect(paths.workflowPath).toBe(path.join(resourcesPath, 'workflows', 'recommendation-pipeline.json'))
    expect(paths.rendererIndexPath).toBe(path.join(resourcesPath, 'frontend', 'dist', 'index.html'))
    expect(paths.backendExecutablePath).toBe(path.join(resourcesPath, 'backend', process.platform === 'win32' ? 'shopbot-backend.exe' : 'shopbot-backend'))
    expect(paths.n8nEntryPath).toBe(path.join(resourcesPath, 'n8n', 'node_modules', 'n8n', 'bin', 'n8n'))
  })
})

describe('ensureFirstRunData', () => {
  it('copies the seed database only when the writable database is missing', () => {
    const appDataDir = makeTempDir()
    const seedDatabasePath = path.join(makeTempDir(), 'products.db')
    const writableDatabasePath = path.join(appDataDir, 'products.db')

    writeFileSync(seedDatabasePath, 'seed')

    ensureFirstRunData({
      appDataDir,
      seedDatabasePath,
      writableDatabasePath,
      workflowPath: 'unused',
      backendExecutablePath: 'unused',
      nodeExecutablePath: 'unused',
      n8nEntryPath: 'unused',
      n8nDataDir: path.join(appDataDir, 'n8n'),
      envFilePath: path.join(appDataDir, '.env'),
      rendererIndexPath: 'unused',
    })

    expect(readFileSync(writableDatabasePath, 'utf8')).toBe('seed')

    writeFileSync(writableDatabasePath, 'user data')
    writeFileSync(seedDatabasePath, 'new seed')

    ensureFirstRunData({
      appDataDir,
      seedDatabasePath,
      writableDatabasePath,
      workflowPath: 'unused',
      backendExecutablePath: 'unused',
      nodeExecutablePath: 'unused',
      n8nEntryPath: 'unused',
      n8nDataDir: path.join(appDataDir, 'n8n'),
      envFilePath: path.join(appDataDir, '.env'),
      rendererIndexPath: 'unused',
    })

    expect(readFileSync(writableDatabasePath, 'utf8')).toBe('user data')
  })
})
