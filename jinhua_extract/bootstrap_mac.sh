#!/bin/zsh
set -euo pipefail

deactivate 2>/dev/null || true

if [[ -f scripts/download_weights.py && -f requirements.txt ]]; then
  echo "==> already in jinhua_extract: $(pwd)"
else
  echo "==> bootstrap_mac.sh must run inside jinhua_extract (do not clone all of AutoGPT)"
  exit 1
fi

PY=""
if command -v python3.12 >/dev/null 2>&1; then
  PY=python3.12
elif command -v python3.11 >/dev/null 2>&1; then
  PY=python3.11
else
  VER="$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 99)"
  if [[ "${VER}" -ge 14 ]]; then
    echo "==> installing python@3.12 via Homebrew"
    if ! command -v brew >/dev/null 2>&1; then
      echo "install Homebrew first: https://brew.sh"
      exit 1
    fi
    eval "$(/opt/homebrew/bin/brew shellenv)"
    brew install python@3.12
    PY="$(brew --prefix python@3.12)/bin/python3.12"
  else
    PY=python3
  fi
fi

echo "==> using ${PY} ($("${PY}" --version))"
rm -rf .venv
"${PY}" -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python scripts/download_weights.py --which both
ls -lh models
echo "==> done. next time: cd ~/jinhua_extract && source .venv/bin/activate"
