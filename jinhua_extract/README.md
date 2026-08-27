# 炸金花发牌视频识别（4 人 / 12 张）

从**一段发牌录像**里按顺序读出 12 张牌的点数和花色，按 4 人、每人 3 张分组，再用常见炸金花规则比大小。

本目录是独立小工具，不依赖 AutoGPT 平台。面向本机（含 Mac M1 16GB）。

## 前提（做不到背面读牌）

视频里每张牌的**正面或角标**至少要清楚出现过。全程扣着发、只看见背面，无法读点数花色。

推荐：俯拍或斜俯拍桌面、光线均匀、发牌不要太快、尽量少挡角标。

## 规则（「正常」炸金花）

牌型从大到小：

1. 豹子（三条）
2. 同花顺
3. 同花
4. 顺子
5. 对子
6. 散牌

- `A` 最大；顺子里 `QKA` 最大，`A23` 最小；`KA2` 不算顺子。
- 同牌型先比点数；点数完全相同再比花色：黑桃 > 红桃 > 梅花 > 方块。
- 一副牌 12 张都不同，每人 3 张。

发牌顺序默认**轮发**：1→2→3→4→1→2→… 共 12 张。  
若实际是一次发满 3 张再换下一家，用 `--deal stacked`。

## 本机流程

1. 用公开扑克检测数据训练 YOLOv8n（52 类），最好再用你自己的牌微调。
2. 把权重放到 `models/cards.pt`（或用 `--weights`）。
3. 跑提取。

```bash
cd jinhua_extract
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# M1：确认 MPS
python -c "import torch; print(torch.backends.mps.is_available())"

python -m jinhua_extract.cli \
  --video /path/to/deal.mp4 \
  --num-cards 12 \
  --players 4 \
  --deal round_robin \
  --weights models/cards.pt \
  --annotate out/annotated.mp4 \
  --json out/result.json
```

训练示例（M1 16G，插电、关掉占内存的应用）：

```bash
yolo detect train model=yolov8n.pt data=configs/playing_cards.yaml \
  epochs=50 imgsz=640 batch=8 device=mps workers=0
```

数据集可从 Roboflow *Playing Cards* 导出 YOLO 格式，类别名需能解析成 `Ah` / `10s` 这种。

## 输出

- 12 张牌的发牌顺序、点数、花色
- 四人各 3 张及牌型
- 赢家（或平局）

规则与发牌分组不依赖 GPU，可用 pytest 单独测：

```bash
pip install pytest
python -m pytest tests -q
```
