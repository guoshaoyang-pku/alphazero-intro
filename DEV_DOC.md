# AlphaGo Zero 介绍 PPT — 协同开发文档

> 本文档面向并行开发同一份「AlphaGo Zero 原理介绍」演示的 **3 个开发 agent**。
> 目标：用一份内容源，产出三个可交付物（PPTX / HTML 单页 / HTML 多页或其它变体），彼此不冲突、可独立构建。

---

## 1. 项目现状速览

仓库根目录已存在以下产物：

| 文件 | 角色 | 状态 |
|------|------|------|
| `build_spec.py` | **内容真相源**。Python 脚本，定义 24 页幻灯片，`json.dump` 输出 `spec.json` | ✅ 存在，是权威源 |
| `spec.json` | 24 页布局 DSL（13.333×7.5 英寸，16:9）。13 图 + 60 形状 + 108 文本 | ✅ 由 `build_spec.py` 生成 |
| `assets/*.png` | matplotlib 渲染的示意图（MCTS、网络结构、PUCT 曲线等） | ✅ 由绘图脚本生成 |
| `build_assets.py` / `regen_diagrams.py` / `gen_mcts_detail.py` | 绘图脚本，`fig.savefig` 输出 PNG 到 `assets/` | ✅ 存在 |
| `presentation.html` | **HTML 版本（自包含、硬编码）**。24 页，键盘左右翻页，KaTeX 渲染公式 | ⚠️ 内容已与 spec.json 脱钩，是独立硬编码 |
| `AlphaGoZero_Intro.pptx` | **PPTX 版本（手工拼装）**。插图以位图形式嵌入，不可逐元素编辑 | ⚠️ 当前是手工产物，**本 agent 负责将其程序化重建** |

> ⚠️ 已知问题：`spec.json` 中 13 处图片路径写死成绝对路径 `/Users/guoshaoyang/...`，换机即失效。文档第 5 节给出整改方案。

---

## 2. 三个 Agent 的分工

| Agent | 交付物 | 工作目录 / 产物 | 主要技术栈 |
|-------|--------|----------------|-----------|
| **A — PPTX agent（本 agent）** | `AlphaGoZero_Intro.pptx`（程序化、可编辑形状） | 新建 `build_pptx.py` | `python-pptx` |
| **B — HTML agent 1** | `presentation.html`（单文件、演讲用、键盘翻页） | 现有 `presentation.html` | 原生 HTML/CSS/JS + KaTeX |
| **C — HTML agent 2** | 多页/可滚动/可导出变体（如 `site/` 目录、reveal.js 或分页打印版） | 待定，建议 `site/` 或 `deck_reveal.html` | 同上，可选 reveal.js |

**三个 agent 共享同一份 `spec.json` + `assets/`，任何内容修改都必须回到 `build_spec.py` 改，再重新生成 spec。** 严禁任何 agent 直接手改 `spec.json`，也严禁在 HTML/PPTX 里硬编码新内容而不同步回 spec。

---

## 3. 统一内容契约：`spec.json`

这是三方协作的核心。所有 agent 都消费它，谁都不许私改它的格式。

### 3.1 顶层结构

```json
{
  "width": 13.333,
  "height": 7.5,
  "slides": [ { ... }, { ... } ]
}
```

- `width` / `height`：画布尺寸，**英寸**，固定 16:9。
- `slides`：有序数组，索引即页码（0-based）。

### 3.2 单页结构

```json
{
  "background": "0D1B3E",
  "elements": [ ... ]
}
```

- `background`：6 位十六进制颜色（无 `#`），如 `0D1B3E` / `FFFFFF`。

### 3.3 元素类型（共 3 种，不得新增）

**text**
```json
{
  "type": "text",
  "text": "AlphaGo Zero 原理介绍",
  "x": 1, "y": 1.5, "w": 11.333, "h": 1.5,
  "font_size": 42,
  "color": "FFFFFF",
  "bold": true,
  "align": "center",
  "font": "PingFang SC"
}
```

**shape**
```json
{
  "type": "shape",
  "shape": "rectangle",
  "x": 0, "y": 5.8, "w": 13.333, "h": 1.7,
  "fill": "0A1128"
}
```
- `shape` 当前仅用到 `rectangle`。PPTX agent 渲染为 `MSO_SHAPE.RECTANGLE`；HTML agent 渲染为 `<div>`。如需圆角/箭头等，**先在本文档登记新值，三方同步后再用**。

**image**
```json
{
  "type": "image",
  "path": "assets/complexity.png",
  "x": 0.5, "y": 1.3, "w": 12.3, "h": 5.5
}
```
- `path`：**必须用相对路径**（`assets/xxx.png`）。详见第 5 节整改。

### 3.4 坐标与单位约定

- 所有 `x/y/w/h` 单位为**英寸**，原点在左上角，y 向下。
- PPTX agent：英寸直接喂给 `python-pptx`（其 `Inches` 接受英寸值）。
- HTML agent：需把英寸换算成像素。约定基准 **96 px/inch**（即画布 1280×720），再用 CSS `transform: scale()` 自适应窗口。`presentation.html` 已采用此方案。

### 3.5 颜色与字体约定

- 颜色：6 位 HEX，无 `#`。三方各自在渲染层补 `#`。
- 字体：spec 里写 `PingFang SC` / `Menlo`。HTML 用 CSS `font-family` 回退链；PPTX 用 `font.name`。

---

## 4. 共享资产：`assets/`

### 4.1 谁能改图

- 图片由绘图脚本（`build_assets.py` 等）生成。**任何 agent 不得用图像编辑软件手动改 PNG**——会被下次脚本运行覆盖。
- 如需新图或改图：改对应脚本 → 重跑 → 提交 PNG + 脚本。

### 4.2 资产清单（当前 30 张）

主要分三类：
- MCTS 相关：`mcts_1_selection.png` … `mcts_4_backprop.png`、`mcts_phases.png`、`search_tree.png`、`puct.png`、`puct_curve.png`
- 网络/训练：`nn_arch.png`、`residual_block.png`、`input_planes.png`、`training_pipeline.png`、`loss_curves.png`、`self_play_loop.png`
- 对比/概念：`ag_vs_agzero.png`、`complexity.png`、`compute_compare.png`、`elo_progress.png`、`evolution.png`、`hardware.png`、`mdp.png`、`param_table.png`、`policy_iteration.png`、`td_vs_mc.png`、`nstep_weighting.png`、`formula_*.png`

### 4.3 文件命名

- 全小写 + 下划线，`.png` 结尾。
- 新增图片必须同时登记进 `build_spec.py` 的对应 `IMG(...)` 调用。

---

## 5. 待整改项（三方协同处理）

### 5.1 【高优先】`spec.json` 图片绝对路径 → 相对路径

**现状**：`build_spec.py` 用 `asset(name)` 返回绝对路径，导致 spec 里 13 处 `/Users/guoshaoyang/...`。

**整改方案**（由 PPTX agent 在重建脚本时一并执行）：
1. 改 `build_spec.py` 的 `asset()` 函数，返回相对路径 `"assets/" + name`。
2. 重跑 `python build_spec.py` 重新生成 `spec.json`。
3. 通知两个 HTML agent：渲染 image 时，相对路径相对**仓库根目录**解析。

**影响**：三方都受益，无破坏性。

### 5.2 【中优先】`presentation.html` 与 spec 脱钩

**现状**：HTML 是硬编码的，spec 改了 HTML 不会自动跟。

**建议**：HTML agent 评估是否改为「构建期读取 spec.json 生成 HTML」的模板方案（如 Jinja2）。若短期不做，至少建立「改 spec 后人工同步 HTML」的 checklist，放在第 7 节。

### 5.3 【低优先】`build_presentation.py` 命名歧义

**现状**：文件名叫 `build_presentation.py`，但实际只画图、不生成 pptx，容易误导。

**建议**：重命名为 `build_assets_v2.py` 或合并进 `build_assets.py`。需三方确认无引用后再改。

---

## 6. 各 Agent 的构建与验证流程

### 6.1 PPTX agent（A）

**新建文件**：`build_pptx.py`

**职责**：读 `spec.json` → 用 `python-pptx` 生成 `AlphaGoZero_Intro.pptx`，让每个 text/shape/image 都是**独立可编辑对象**（替换现有手工版本）。

**构建命令**：
```bash
python build_pptx.py          # 输出 AlphaGoZero_Intro.pptx
```

**自检清单**：
- [ ] 24 页全部生成，页序与 spec 一致
- [ ] 每个 text 是独立 textbox，字体/字号/颜色/对齐正确
- [ ] 每个 shape 是 `MSO_SHAPE.RECTANGLE`，填充色正确
- [ ] 每个 image 用相对路径加载，宽高保持比例不变形
- [ ] 画布 13.333×7.5 英寸（16:9）
- [ ] 打开 pptx 后，所有对象可单独选中编辑（非整张位图）

**依赖**：`python-pptx`（需加入 `requirements.txt`，当前仓库无该文件，建议新建）。

### 6.2 HTML agent 1（B，单文件演讲版）

**维护文件**：`presentation.html`

**构建命令**：无构建步骤，直接浏览器打开。如需导出 PDF：浏览器打印 → 另存 PDF。

**自检清单**：
- [ ] 24 页内容与 spec 一致（脱钩期间人工核对）
- [ ] 左右方向键翻页正常
- [ ] 公式由 KaTeX 正确渲染
- [ ] 1280×720 画布在常见分辨率下自适应缩放
- [ ] 图片用相对路径 `assets/xxx.png`

### 6.3 HTML agent 2（C，变体版）

**建议产物**：`site/` 目录（多页 HTML）或 `deck_reveal.html`（reveal.js 版）。

**自检清单**：
- [ ] 内容来自 `spec.json`（建议构建期读取，避免硬编码）
- [ ] 与 agent B 的版本在文字、公式、图位上一致
- [ ] 提供本版本独有的能力（如滚动浏览、深色模式、导出等），避免与 B 重复

---

## 7. 协作流程与同步机制

### 7.1 改内容（文字/布局/新页）的流程

```
改 build_spec.py
   ↓
python build_spec.py            # 重新生成 spec.json
   ↓
在群里 @另外两个 agent：「spec 已更新，第 N 页 xxx 改动」
   ↓
A: python build_pptx.py          # 重新生成 pptx
B: 人工同步 presentation.html（或跑模板构建）
C: 跑构建脚本
   ↓
各自自检 → 提交
```

### 7.2 改图（图片内容）的流程

```
改 build_assets.py / regen_diagrams.py / gen_mcts_detail.py
   ↓
python <对应脚本>.py             # 重新生成 assets/*.png
   ↓
提交 PNG + 脚本
   ↓
三个 agent 各自重跑构建即可（图片是引用，无需改 spec）
```

### 7.3 改契约（新增元素类型/字段）的流程

**这是最重的变更，必须三方达成一致：**
1. 提议者在本文档第 3.3 节追加新类型/字段定义 + 用途。
2. 三方确认各自渲染层的实现方案。
3. 同步实现 → 改 `build_spec.py` → 重生成 spec → 各自验证。
4. 任何一方未实现前，不得在 spec 里使用新类型/字段。

### 7.4 提交与分支约定

- 建议每 agent 一个分支：`pptx-build` / `html-single` / `html-variant`。
- `build_spec.py`、`spec.json`、`assets/` 是共享文件，改动走 PR，需至少一方 review。
- 各自的产物文件（`*.pptx`、`presentation.html`、`site/`）可在自己分支直接提交。

### 7.5 沟通锚点

每次同步消息建议包含三要素，避免歧义：
1. **改了什么**（哪个文件、第几页、哪个元素）
2. **为什么改**（内容订正 / 布局调整 / 新增图）
3. **需要对方做什么**（重跑构建 / 人工同步 / review 契约变更）

---

## 8. 验收标准（最终交付）

| 维度 | 标准 |
|------|------|
| 内容一致性 | 三版（PPTX / HTML×2）文字、公式、图位、页序完全一致 |
| 可编辑性 | PPTX 中每个元素可独立选中修改；HTML 源码结构清晰可改 |
| 可复现 | 从 `python build_spec.py` + 各构建脚本出发，能完整重建全部产物 |
| 可移植 | 无绝对路径，换机器克隆仓库即可构建 |
| 视觉 | 16:9 画布，配色字体统一（navy `0D1B3E` / gold `E8A838` / PingFang SC） |

---

## 9. 附：关键文件索引

| 文件 | 作用 |
|------|------|
| `build_spec.py` | 内容源，生成 spec.json |
| `spec.json` | 布局 DSL，三方共享 |
| `build_assets.py` / `regen_diagrams.py` / `gen_mcts_detail.py` | 绘图脚本 |
| `assets/*.png` | 图片资产 |
| `build_pptx.py` | **PPTX agent 新建**，读 spec 生成 pptx |
| `presentation.html` | HTML agent 1 维护 |
| `AlphaGoZero_Intro.pptx` | PPTX 最终产物（程序化重建后替换手工版） |
| `code_snippets.md` | 代码片段素材（如需引用代码） |
| `renders/` | 渲染预览图（slide-01.jpg 等，供核对视觉） |
| `papers/` | 核心论文 PDF（见第 10 节） |

---

## 10. 参考文献（核心论文 PDF）

三篇 DeepMind 原始论文 + KataGo 改进论文已下载到 `papers/`，三方撰写内容时一律以此为准，避免引用二手解读造成的符号/数值错误。

| 文件 | 论文 | 期刊 / 年份 | 说明 |
|------|------|------------|------|
| [AlphaGoLee_Nature2016.pdf](papers/AlphaGoLee_Nature2016.pdf) | Silver et al. *Mastering the game of Go with deep neural networks and tree search* | Nature 529:484-489 (2016) | AlphaGo Lee 版，48 特征面、策略+价值双网络、含 rollout，输给人类棋谱监督学习 |
| [AlphaGoZero_Nature2017.pdf](papers/AlphaGoZero_Nature2017.pdf) | Silver et al. *Mastering the game of Go without human knowledge* | Nature 550:354-359 (2017) | AlphaGo Zero，17 特征面、统一网络、去 rollout、纯 self-play，490 万局自我对弈 |
| [AlphaZero_Science2018_arxiv1712.01815.pdf](papers/AlphaZero_Science2018_arxiv1712.01815.pdf) | Silver et al. *A general reinforcement learning algorithm that masters chess, shogi, and Go* | Science 362:1140-1144 (2018) | AlphaZero，推广到象棋/将棋，去对称性增强、无 checkpoint 筛选、超参复用 Zero |
| [KataGo_arXiv2019_1902.10565.pdf](papers/KataGo_arXiv2019_1902.10565.pdf) | Wu. *Accelerating Self-Play Learning in Go* | arXiv:1902.10565 (2019) | 开源 AlphaZero 复现，50× 加速，引入辅助任务/forced playout/playout cap randomization 等 |

### 来源说明（便于追溯）

- AlphaGo (Lee)：DeepMind 官方开放存储 `storage.googleapis.com/deepmind-media/alphago/AlphaGoNaturePaper.pdf`
- AlphaGo Zero：UCL 发现仓库开放存档 `discovery.ucl.ac.uk/10045895/1/agz_unformatted_nature.pdf`（未排版版，含补充材料，42 页）
- AlphaZero：arXiv 预印本 `arxiv.org/abs/1712.01815`（与 Science 正式版内容一致）
- KataGo：arXiv 预印本 `arxiv.org/abs/1902.10565`

### 引用规范

- 文中涉及具体数值（如 490 万局、17 个特征面、1600 次模拟）必须与论文一致，有疑问先查 `papers/` 里的 PDF。
- 三版（PPTX / HTML×2）引用论文时，统一用上表"论文"列的标题写法。
- 需要补充其它论文（如 UCT 原始论文 Kocsis & Szepesvári 2006）时，下载到 `papers/` 并在本表追加一行，经三方确认。
