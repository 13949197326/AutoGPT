#!/bin/zsh
set -euo pipefail

APP="${HOME}/Applications/DealExtract.app"
MACOS="${APP}/Contents/MacOS"
mkdir -p "${MACOS}" "${HOME}/Applications"

cat > "${APP}/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>zh_CN</string>
  <key>CFBundleExecutable</key>
  <string>run</string>
  <key>CFBundleIdentifier</key>
  <string>local.jinhua.deal-extract</string>
  <key>CFBundleName</key>
  <string>发牌识别</string>
  <key>CFBundleDisplayName</key>
  <string>发牌识别</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>LSMinimumSystemVersion</key>
  <string>13.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>CFBundleDocumentTypes</key>
  <array>
    <dict>
      <key>CFBundleTypeRole</key>
      <string>Viewer</string>
      <key>LSItemContentTypes</key>
      <array>
        <string>public.mpeg-4</string>
        <string>public.movie</string>
      </array>
    </dict>
  </array>
</dict>
</plist>
PLIST

cat > "${MACOS}/run" <<'RUN'
#!/bin/bash
set -u
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
ROOT="${HOME}/jinhua_extract"
PY="${ROOT}/.venv/bin/python"
WEIGHTS="${ROOT}/models/playing-cards.pt"
OUT_DIR="${ROOT}/out"
LOG="${OUT_DIR}/last_run.log"
DESKTOP_VIDEO="${HOME}/Desktop/deal.mp4"

fail() {
  /usr/bin/osascript -e "display alert \"发牌识别失败\" message \"$1\" as critical"
  exit 1
}

mkdir -p "${OUT_DIR}"
[[ -x "${PY}" ]] || fail "找不到 ${PY}，请先完成 bootstrap。"
[[ -f "${WEIGHTS}" ]] || fail "找不到权重 ${WEIGHTS}。"

VIDEO=""
if [[ "${1:-}" != "" ]]; then
  VIDEO="$1"
elif [[ -f "${DESKTOP_VIDEO}" ]]; then
  VIDEO="${DESKTOP_VIDEO}"
else
  VIDEO="$(/usr/bin/osascript <<'APPLESCRIPT'
try
  set theFile to choose file with prompt "选择发牌视频" of type {"public.mpeg-4", "public.movie"}
  return POSIX path of theFile
on error
  return ""
end try
APPLESCRIPT
)"
fi
VIDEO="$(echo "${VIDEO}" | tr -d '\r' | sed 's/[[:space:]]*$//')"
[[ -n "${VIDEO}" && -f "${VIDEO}" ]] || fail "没有可用的视频（默认桌面 deal.mp4）。"

cd "${ROOT}" || fail "无法进入 ${ROOT}"
echo "=== $(date) ===" >"${LOG}"
echo "video=${VIDEO}" >>"${LOG}"
set +e
"${PY}" -m jinhua_extract.cli \
  --video "${VIDEO}" \
  --weights "${WEIGHTS}" \
  --num-cards 12 --players 4 --deal round_robin \
  --json "${OUT_DIR}/result.json" \
  --annotate "${OUT_DIR}/annotated.mp4" >>"${LOG}" 2>&1
STATUS=$?
echo "exit=${STATUS}" >>"${LOG}"
[[ ${STATUS} -eq 0 ]] || fail "识别未完成，见 ${LOG}"

/usr/bin/open "${OUT_DIR}"
/usr/bin/osascript -e "display notification \"结果在 jinhua_extract/out\" with title \"发牌识别完成\""
exit 0
RUN

chmod +x "${MACOS}/run"
xattr -dr com.apple.quarantine "${APP}" 2>/dev/null || true
open -R "${APP}"
echo "installed ${APP}"
