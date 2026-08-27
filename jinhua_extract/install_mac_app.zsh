#!/bin/zsh
set -euo pipefail

ROOT="${HOME}/jinhua_extract"
RUN_SH="${ROOT}/mac_app/run.sh"
APP="${HOME}/Applications/DealExtract.app"
CMD="${HOME}/Desktop/发牌识别.command"

mkdir -p "${ROOT}/mac_app" "${HOME}/Applications"

cat > "${RUN_SH}" <<'RUN'
#!/bin/bash
set -u
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
export HOME="${HOME:-/Users/hong}"
ROOT="${HOME}/jinhua_extract"
PY="${ROOT}/.venv/bin/python"
WEIGHTS="${ROOT}/models/playing-cards.pt"
OUT_DIR="${ROOT}/out"
LOG="${OUT_DIR}/last_run.log"
DESKTOP_VIDEO="${HOME}/Desktop/deal.mp4"
mkdir -p "${OUT_DIR}"

if [[ ! -x "${PY}" ]]; then
  echo "missing python ${PY}" >&2
  exit 2
fi
if [[ ! -f "${WEIGHTS}" ]]; then
  echo "missing weights ${WEIGHTS}" >&2
  exit 3
fi

VIDEO="${1:-}"
if [[ -z "${VIDEO}" && -f "${DESKTOP_VIDEO}" ]]; then
  VIDEO="${DESKTOP_VIDEO}"
fi
if [[ -z "${VIDEO}" || ! -f "${VIDEO}" ]]; then
  echo "missing video (put deal.mp4 on Desktop)" >&2
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
  --annotate "${OUT_DIR}/annotated.mp4" >>"${LOG}" 2>&1
STATUS=$?
echo "exit=${STATUS}" >>"${LOG}"
exit ${STATUS}
RUN
chmod +x "${RUN_SH}"

cat > "${CMD}" <<EOF
#!/bin/bash
export HOME="\$HOME"
/usr/bin/osascript <<'AS'
try
  set cmd to "/bin/bash " & quoted form of (POSIX path of (path to home folder) & "jinhua_extract/mac_app/run.sh")
  with timeout of 86400 seconds
    do shell script cmd
  end timeout
  display notification "结果在 jinhua_extract/out" with title "发牌识别完成"
  do shell script "open " & quoted form of (POSIX path of (path to home folder) & "jinhua_extract/out")
on error errMsg
  display alert "发牌识别失败" message errMsg
end try
AS
EOF
chmod +x "${CMD}"
xattr -dr com.apple.quarantine "${CMD}" 2>/dev/null || true

rm -rf "${APP}"
osacompile -o "${APP}" <<'APPLESCRIPT'
on run
  my processVideo("")
end run

on open dropped
  set p to POSIX path of item 1 of dropped
  my processVideo(p)
end open

on processVideo(videoPath)
  set homePath to POSIX path of (path to home folder)
  set runsh to homePath & "jinhua_extract/mac_app/run.sh"
  set cmd to "/bin/bash " & quoted form of runsh
  if videoPath is not "" then
    set cmd to cmd & " " & quoted form of videoPath
  end if
  try
    do shell script cmd with timeout 86400
    display notification "结果在 jinhua_extract/out" with title "发牌识别完成"
    do shell script "open " & quoted form of (homePath & "jinhua_extract/out")
  on error errMsg number errNum
    display alert "发牌识别失败" message (errMsg & " (" & errNum & ")")
  end try
end processVideo
APPLESCRIPT

xattr -dr com.apple.quarantine "${APP}" 2>/dev/null || true
open -R "${APP}"
open -R "${CMD}"
echo "app=${APP}"
echo "command=${CMD}"
echo "If Dock icon is old, remove it, then drag DealExtract.app to Dock again."
