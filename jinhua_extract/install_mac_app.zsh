#!/bin/zsh
set -euo pipefail

ROOT="${HOME}/jinhua_extract"
RUN_SH="${ROOT}/mac_app/run.sh"
CMD="${HOME}/Desktop/DealExtract.command"
APP="${HOME}/Applications/DealExtract.app"

mkdir -p "${ROOT}/mac_app" "${HOME}/Applications" "${APP}/Contents/MacOS"

cat > "${RUN_SH}" <<'RUN'
#!/bin/bash
set -u
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
ROOT="${HOME}/jinhua_extract"
PY="${ROOT}/.venv/bin/python"
WEIGHTS="${ROOT}/models/playing-cards.pt"
OUT_DIR="${ROOT}/out"
LOG="${OUT_DIR}/last_run.log"
VIDEO="${1:-${HOME}/Desktop/deal.mp4}"
mkdir -p "${OUT_DIR}"

echo "python=${PY}"
echo "video=${VIDEO}"
if [[ ! -x "${PY}" ]]; then
  echo "ERROR: missing venv python"
  exit 2
fi
if [[ ! -f "${WEIGHTS}" ]]; then
  echo "ERROR: missing ${WEIGHTS}"
  exit 3
fi
if [[ ! -f "${VIDEO}" ]]; then
  echo "ERROR: missing video ${VIDEO}"
  exit 4
fi

cd "${ROOT}"
echo "=== $(date) ===" >"${LOG}"
echo "video=${VIDEO}" >>"${LOG}"
"${PY}" -m jinhua_extract.cli \
  --video "${VIDEO}" \
  --weights "${WEIGHTS}" \
  --num-cards 12 --players 4 --deal round_robin \
  --json "${OUT_DIR}/result.json" \
  --annotate "${OUT_DIR}/annotated.mp4" 2>&1 | tee -a "${LOG}"
STATUS=${PIPESTATUS[0]}
echo "exit=${STATUS}" | tee -a "${LOG}"
if [[ ${STATUS} -eq 0 ]]; then
  open "${OUT_DIR}"
  echo "done. result.json and annotated.mp4 are in ${OUT_DIR}"
else
  echo "failed. see ${LOG}"
fi
exit ${STATUS}
RUN
chmod +x "${RUN_SH}"

cat > "${CMD}" <<'EOF'
#!/bin/bash
cd "$HOME/jinhua_extract" || exit 1
bash "$HOME/jinhua_extract/mac_app/run.sh"
echo
read -r -p "press Return to close "
EOF
chmod +x "${CMD}"
xattr -dr com.apple.quarantine "${CMD}" 2>/dev/null || true

cat > "${APP}/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>run</string>
  <key>CFBundleIdentifier</key>
  <string>local.jinhua.deal-extract</string>
  <key>CFBundleName</key>
  <string>DealExtract</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>LSMinimumSystemVersion</key>
  <string>13.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

cat > "${APP}/Contents/MacOS/run" <<'EOF'
#!/bin/bash
exec /usr/bin/open -a Terminal "$HOME/Desktop/DealExtract.command"
EOF
chmod +x "${APP}/Contents/MacOS/run"
xattr -dr com.apple.quarantine "${APP}" 2>/dev/null || true

open -R "${CMD}"
echo "ok desktop=$CMD"
echo "double-click Desktop/DealExtract.command"
echo "or run: bash $RUN_SH"
