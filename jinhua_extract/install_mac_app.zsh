#!/bin/zsh
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/mac_app/发牌识别.app"
DEST="${HOME}/Applications/发牌识别.app"
mkdir -p "${HOME}/Applications"
rm -rf "${DEST}"
cp -R "${SRC}" "${DEST}"
chmod +x "${DEST}/Contents/MacOS/run"
xattr -dr com.apple.quarantine "${DEST}" 2>/dev/null || true
open -R "${DEST}"
echo "已安装到 ${DEST}"
echo "可把应用拖到 Dock。双击会优先用桌面 deal.mp4；也可把视频拖到应用图标上。"
