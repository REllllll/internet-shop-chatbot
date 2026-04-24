#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$ROOT_DIR/vendor"
N8N_DIR="$VENDOR_DIR/n8n"
NODE_DIR="$VENDOR_DIR/node"

mkdir -p "$VENDOR_DIR"

if [[ ! -x "$NODE_DIR/bin/node" ]]; then
  echo "Missing $NODE_DIR/bin/node"
  echo "Place a macOS Node.js runtime in vendor/node before packaging."
  exit 1
fi

rm -rf "$N8N_DIR"
mkdir -p "$N8N_DIR"

pushd "$N8N_DIR" >/dev/null
"$NODE_DIR/bin/node" "$NODE_DIR/bin/npm" init -y
"$NODE_DIR/bin/node" "$NODE_DIR/bin/npm" install n8n@latest --omit=dev
popd >/dev/null

test -f "$N8N_DIR/node_modules/n8n/bin/n8n"
echo "n8n runtime prepared at $N8N_DIR"
