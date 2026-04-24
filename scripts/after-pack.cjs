const fs = require('fs')
const path = require('path')

exports.default = function (context) {
  const n8nSource = path.join(context.packager.projectDir, 'vendor', 'n8n', 'node_modules')
  const n8nDest = path.join(context.appOutDir, 'ShopBot.app', 'Contents', 'Resources', 'n8n', 'node_modules')

  if (!fs.existsSync(n8nSource)) {
    console.warn('n8n node_modules not found at', n8nSource)
    return Promise.resolve()
  }

  fs.mkdirSync(path.dirname(n8nDest), { recursive: true })

  function copyDir(src, dest) {
    fs.mkdirSync(dest, { recursive: true })
    for (const entry of fs.readdirSync(src)) {
      const srcPath = path.join(src, entry)
      const destPath = path.join(dest, entry)
      const stat = fs.statSync(srcPath)
      if (stat.isDirectory()) {
        copyDir(srcPath, destPath)
      } else {
        fs.copyFileSync(srcPath, destPath)
      }
    }
  }

  copyDir(n8nSource, n8nDest)
  console.log('Copied n8n node_modules to', n8nDest)
  return Promise.resolve()
}
