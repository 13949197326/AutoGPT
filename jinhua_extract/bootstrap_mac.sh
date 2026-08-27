#!/bin/zsh
# 在 Mac 终端整段粘贴即可（不要先 cd 到家目录的错误 venv）。
# 用法: zsh bootstrap_mac.sh
set -euo pipefail

echo "==> 退出家目录里误建的 venv（若有）"
deactivate 2>/dev/null || true

REPO_DIR="${HOME}/AutoGPT"
BRANCH="cursor/jinhua-video-extract-6437"

if [[ ! -d "${REPO_DIR}/jinhua_extract" ]]; then
  echo "==> clone ${BRANCH}"
  if [[ -d "${REPO_DIR}/.git" ]]; then
    cd "${REPO_DIR}"
    git fetch origin "${BRANCH}"
    git checkout "${BRANCH}"
  else
    git clone --depth 1 -b "${BRANCH}" https://github.com/13949197326/AutoGPT.git "${REPO_DIR}"
  fi
fi

cd "${REPO_DIR}/jinhua_extract"
echo "==> 当前目录: $(pwd)"
test -f scripts/download_weights.py
test -f requirements.txt

PY=""
if command -v python3.12 >/dev/null 2>&1; then
  PY=python3.12
elif command -v python3.11 >/dev/null 2>&1; then
  PY=python3.11
else
  VER="$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 99)"
  if [[ "${VER}" -ge 14 ]]; then
    echo "==> Python 3.14 装 PyTorch/YOLO 很容易失败，改用 Homebrew python@3.12"
    if ! command -v brew >/dev/null 2>&1; then
      echo "请先安装 Homebrew: https://brew.sh"
      exit 1
    fi
    eval "$(/opt/homebrew/bin/brew shellenv)"
    brew install python@3.12
    PY="$(brew --prefix python@3.12)/bin/python3.12"
  else
    PY=python3
  fi
fi

echo "==> 使用 ${PY} ($("${PY}" --version))"
rm -rf .venv
"${PY}" -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python scripts/download_weights.py --which both
ls -lh models
echo "==> 完成。以后每次："
echo "    cd ${REPO_DIR}/jinhua_extract && source .venv/bin/activate"
