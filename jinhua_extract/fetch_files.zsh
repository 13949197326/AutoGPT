#!/bin/zsh
set -euo pipefail
DEST="${HOME}/jinhua_extract"
BRANCH="cursor/jinhua-video-extract-6437"
BASE="https://raw.githubusercontent.com/13949197326/AutoGPT/${BRANCH}/jinhua_extract"
mkdir -p "${DEST}/jinhua_extract" "${DEST}/scripts" "${DEST}/configs" "${DEST}/tests"
files=(
  README.md
  SETUP_MAC.md
  requirements.txt
  pytest.ini
  bootstrap_mac.sh
  configs/playing_cards.yaml
  scripts/download_weights.py
  jinhua_extract/__init__.py
  jinhua_extract/__main__.py
  jinhua_extract/cards.py
  jinhua_extract/cli.py
  jinhua_extract/deal.py
  jinhua_extract/detect.py
  jinhua_extract/extract.py
  jinhua_extract/rules.py
  jinhua_extract/timeline.py
  tests/test_rules.py
  tests/test_extract.py
)
for f in "${files[@]}"; do
  echo "get ${f}"
  curl -fL --retry 5 --retry-delay 2 --connect-timeout 30 -o "${DEST}/${f}" "${BASE}/${f}"
done
chmod +x "${DEST}/bootstrap_mac.sh"
echo "files in ${DEST}"
ls "${DEST}/scripts"
