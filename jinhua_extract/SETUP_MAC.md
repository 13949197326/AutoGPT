# Mac（M1）第一次怎么跑

你刚才的报错是两件事叠在一起：

1. **家目录里没有 `jinhua_extract`**。代码在 GitHub 仓库里，必须先 clone。
2. **没有 `python` 命令**。Apple Silicon 上要用 **`python3`**，没有的话先装 Python。

下面整段复制到终端，一行失败就停，把完整报错发回来。

## 双击应用（环境已经装好之后）

```bash
cd ~/jinhua_extract
curl -fL --retry 8 --retry-delay 3 -o install_mac_app.zsh "https://raw.githubusercontent.com/13949197326/AutoGPT/cursor/jinhua-video-extract-6437/jinhua_extract/install_mac_app.zsh"
mkdir -p mac_app/发牌识别.app/Contents/MacOS
curl -fL --retry 8 -o "mac_app/发牌识别.app/Contents/Info.plist" "https://raw.githubusercontent.com/13949197326/AutoGPT/cursor/jinhua-video-extract-6437/jinhua_extract/mac_app/发牌识别.app/Contents/Info.plist"
curl -fL --retry 8 -o "mac_app/发牌识别.app/Contents/MacOS/run" "https://raw.githubusercontent.com/13949197326/AutoGPT/cursor/jinhua-video-extract-6437/jinhua_extract/mac_app/发牌识别.app/Contents/MacOS/run"
chmod +x "mac_app/发牌识别.app/Contents/MacOS/run" install_mac_app.zsh
zsh install_mac_app.zsh
```

之后 Dock 或「应用程序」里打开 **发牌识别**。默认用桌面上的 `deal.mp4`，也可把视频拖到图标上。不用每次 `source .venv`。

## 0. 推荐：终端里一次性粘贴（从家目录也可以）

先执行 `deactivate`（如果你看到 `(.venv)` 且路径是 `~`）。然后整段粘贴：

```bash
deactivate 2>/dev/null
cd ~
git clone -b cursor/jinhua-video-extract-6437 https://github.com/13949197326/AutoGPT.git
cd ~/AutoGPT/jinhua_extract
zsh bootstrap_mac.sh
```

若 `AutoGPT` 目录已经存在，不要再 clone，改成：

```bash
deactivate 2>/dev/null
cd ~/AutoGPT
git fetch origin cursor/jinhua-video-extract-6437
git checkout cursor/jinhua-video-extract-6437
cd jinhua_extract
zsh bootstrap_mac.sh
```

**不要**在 `~`（`/Users/hong`）里执行 `pip install -r requirements.txt`：家目录那个文件是 gtts，不是本项目。

## 1. 看有没有 Python 3

```bash
python3 --version
```

- 若弹出「安装命令行工具」，点安装，装完再执行一次。
- 若仍然 `command not found`，先装 Homebrew，再装 Python：

```bash
# 没有 brew 时（需要输入开机密码）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

brew install python
python3 --version
```

确认类似 `Python 3.12.x` 或 `3.11.x` 后再继续。不要用 `python`，这台机器上它不存在。

## 2. 把代码拉到本机

仓库是 AutoGPT，工具在子目录 `jinhua_extract`。用带代码的分支：

```bash
cd ~
git clone -b cursor/jinhua-video-extract-6437 https://github.com/13949197326/AutoGPT.git
cd ~/AutoGPT/jinhua_extract
ls
```

应能看到 `requirements.txt`、`scripts`、`jinhua_extract`。

已有 AutoGPT 目录时不要再 clone，改为：

```bash
cd ~/AutoGPT
git fetch origin cursor/jinhua-video-extract-6437
git checkout cursor/jinhua-video-extract-6437
cd jinhua_extract
```

## 3. 建环境、装依赖、下权重

```bash
cd ~/AutoGPT/jinhua_extract
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
python3 scripts/download_weights.py --which both
```

成功的话会有 `models/playing-cards.pt`。以后每次开新终端先：

```bash
cd ~/AutoGPT/jinhua_extract
source .venv/bin/activate
```

提示符前面应出现 `(.venv)`。

## 4. 有发牌视频后再跑

```bash
cd ~/AutoGPT/jinhua_extract
source .venv/bin/activate
python3 -m jinhua_extract.cli \
  --video /把这里换成你的视频路径/deal.mp4 \
  --weights models/playing-cards.pt \
  --num-cards 12 --players 4 --deal round_robin \
  --json out/result.json --annotate out/annotated.mp4
```
