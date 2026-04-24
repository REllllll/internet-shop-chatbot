import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

interface ExtraResource {
  from: string
  to: string
}

interface PackageJson {
  scripts: Record<string, string>
  build: {
    files: string[]
    extraResources: ExtraResource[]
  }
}

const packageJson = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8')) as PackageJson

describe('desktop package config', () => {
  it('places runtime-read assets in Electron resources', () => {
    expect(packageJson.build.files).not.toContain('frontend/dist/**/*')
    expect(packageJson.build.files).not.toContain('workflows/recommendation-pipeline.json')
    expect(packageJson.build.files).not.toContain('data/products.db')

    expect(packageJson.build.extraResources).toEqual(
      expect.arrayContaining([
        { from: 'frontend/dist', to: 'frontend/dist' },
        { from: 'workflows/recommendation-pipeline.json', to: 'workflows/recommendation-pipeline.json' },
        { from: 'data/products.db', to: 'data/products.db' },
      ]),
    )
  })

  it('seeds the product database before desktop packaging commands', () => {
    expect(packageJson.scripts['data:seed']).toBe('test -f data/products.db || python3 data/seed.py')
    expect(packageJson.scripts['desktop:build']).toContain('npm run data:seed')
    expect(packageJson.scripts['desktop:dist']).toContain('npm run data:seed')
  })
})
