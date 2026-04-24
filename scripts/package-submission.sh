#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="$ROOT_DIR/submission"
NAME="${SUBMISSION_NAME:-surname_forename}"
TARGET="$OUT_ROOT/$NAME"

rm -rf "$TARGET"
mkdir -p "$TARGET/executable" "$TARGET/source"

cp "$ROOT_DIR/build-resources/readme-template.txt" "$TARGET/readme.txt"

if [[ -f "$ROOT_DIR/docs/MaintenanceManual.pdf" ]]; then
  cp "$ROOT_DIR/docs/MaintenanceManual.pdf" "$TARGET/MaintenanceManual.pdf"
else
  echo "MaintenanceManual.pdf is missing from docs/." > "$TARGET/MaintenanceManual.pdf.missing.txt"
fi

if [[ -d "$ROOT_DIR/release/mac/ShopBot.app" ]]; then
  cp -R "$ROOT_DIR/release/mac/ShopBot.app" "$TARGET/executable/ShopBot.app"
else
  echo "Build ShopBot.app with npm run desktop:dist before final archive." > "$TARGET/executable/ShopBot.app.missing.txt"
fi

rsync -a "$ROOT_DIR/" "$TARGET/source/" \
  --exclude ".git/" \
  --exclude "node_modules/" \
  --exclude "frontend/node_modules/" \
  --exclude "backend/.venv/" \
  --exclude ".venv/" \
  --exclude "dist/" \
  --exclude "dist-electron/" \
  --exclude "release/" \
  --exclude "submission/" \
  --exclude "vendor/node/" \
  --exclude "vendor/n8n/" \
  --exclude ".env" \
  --exclude "*.log"

pushd "$OUT_ROOT" >/dev/null
zip -qry "$NAME.zip" "$NAME"
popd >/dev/null

echo "Created $OUT_ROOT/$NAME.zip"
