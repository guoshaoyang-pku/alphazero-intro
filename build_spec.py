#!/usr/bin/env python3
"""Build AlphaGo Zero presentation spec — mirrors presentation.html (43 slides).
HTML is the single source of truth; this script reproduces it as a PPTX spec.
"""

import os, json

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
def asset(name): return os.path.join(ASSET_DIR, name)

# Palette (matches HTML :root)
BG_DARK = "0D1B3E"
BG_WHITE = "FFFFFF"
BG_SECTION = "102A56"
C_NAVY = "0D1B3E"
C_BLUE = "1565C0"
C_LBLUE = "E3F2FD"
C_TEAL = "00897B"
C_GREEN = "2E7D32"
C_LGREEN = "E8F5E9"
C_GOLD = "E8A838"
C_LORANGE = "FFF3E0"
C_ORANGE = "E65100"
C_RED = "E53935"
C_LRED = "FFEBEE"
C_PURPLE = "7B1FA2"
C_LPURPLE = "F3E5F5"
C_GRAY = "757575"
C_LGRAY = "E0E0E0"
C_DARK = "1A1A2E"
FONT = "PingFang SC"

# Helpers
def T(text, x, y, w, h, size, color, bold=False, align="left", font=FONT):
    return {"type": "text", "text": text, "x": x, "y": y, "w": w, "h": h,
            "font_size": size, "color": color, "bold": bold, "align": align, "font": font}

def S(shape, x, y, w, h, fill):
    return {"type": "shape", "shape": shape, "x": x, "y": y, "w": w, "h": h, "fill": fill}

def IMG(path, x, y, w, h):
    return {"type": "image", "path": path, "x": x, "y": y, "w": w, "h": h}

def accent(color):
    return S("rectangle", 0, 0, 13.333, 0.08, color)

def header(title, color=C_NAVY, bar=C_BLUE):
    return [accent(bar), T(title, 0.5, 0.25, 12.3, 0.65, 26, color, bold=True)]

def card(x, y, w, h, fill, title, title_color, body, body_color="333333"):
    return [
        S("rounded_rectangle", x, y, w, h, fill),
        T(title, x+0.15, y+0.08, w-0.3, 0.35, 14, title_color, bold=True),
        T(body, x+0.15, y+0.45, w-0.3, h-0.55, 12, body_color),
    ]

slides = []

# ═══ Slide 1: Cover ═══
slides.append({
    "background": BG_DARK,
    "elements": [
        S("rectangle", 0, 5.8, 13.333, 1.7, "0A1128"),
        T("AlphaGo Zero 原理介绍", 1, 1.6, 11.333, 1.4, 42, "FFFFFF", bold=True, align="center"),
        T("从蒙特卡洛树搜索到自我博弈强化学习", 1.5, 3.2, 10.333, 0.8, 20, C_GOLD, align="center"),
        T("汇报人：郭绍阳", 1, 6.0, 5, 0.6, 16, "90A4AE"),
        T("2026 年 7 月", 7, 6.0, 5, 0.6, 16, "90A4AE", align="right"),
    ]
})

# ═══ Slide 2: Outline ═══
slides.append({
    "background": BG_WHITE,
    "elements": [
        S("rectangle", 0, 0, 0.15, 7.5, C_NAVY),
        T("目录", 0.8, 0.4, 5, 0.7, 32, C_NAVY, bold=True),
        S("rectangle", 0.8, 1.2, 3, 0.05, C_GOLD),
        S("rounded_rectangle", 1.2, 2.0, 0.8, 0.8, C_BLUE),
        T("I", 1.2, 2.0, 0.8, 0.8, 24, "FFFFFF", bold=True, align="center"),
        T("蒙特卡洛树搜索 (MCTS)", 2.5, 2.0, 8, 0.4, 20, C_NAVY, bold=True),
        T("博弈树搜索 · UCT公式 · 四阶段流程 · 性质分析", 2.5, 2.5, 9, 0.4, 14, C_GRAY),
        S("rounded_rectangle", 1.2, 3.5, 0.8, 0.8, C_RED),
        T("II", 1.2, 3.5, 0.8, 0.8, 24, "FFFFFF", bold=True, align="center"),
        T("AlphaGo Zero：自我博弈的突破", 2.5, 3.5, 8, 0.4, 20, C_NAVY, bold=True),
        T("神经网络架构 · PUCT搜索 · 自我增强 · 训练循环", 2.5, 4.0, 9, 0.4, 14, C_GRAY),
        S("rounded_rectangle", 1.2, 5.0, 0.8, 0.8, C_TEAL),
        T("III", 1.2, 5.0, 0.8, 0.8, 24, "FFFFFF", bold=True, align="center"),
        T("强化学习基础", 2.5, 5.0, 8, 0.4, 20, C_NAVY, bold=True),
        T("MDP · 价值函数 · 蒙特卡洛方法 · 时序差分学习", 2.5, 5.5, 9, 0.4, 14, C_GRAY),
    ]
})

# ═══ Slide 3: Section I — MCTS ═══
slides.append({
    "background": BG_SECTION,
    "elements": [
        T("PART I", 1, 1.5, 11.333, 0.8, 18, C_GOLD, bold=True, align="center"),
        T("蒙特卡洛树搜索", 1, 2.5, 11.333, 1.2, 40, "FFFFFF", bold=True, align="center"),
        T("Monte Carlo Tree Search", 1, 3.8, 11.333, 0.8, 20, "90A4AE", align="center"),
        S("rectangle", 5.167, 5.0, 3, 0.05, C_GOLD),
        T("推荐教程：李理的博客 · AlphaZero（图解 MCTS 全过程）", 1, 5.6, 11.333, 0.5, 13, "90A4AE", align="center"),
    ]
})

# ═══ Slides 4-7: Minimax, Alpha-Beta, Heuristic, Why Go fails ═══
for title, img, sub in [
    ("Minimax 搜索", "minimax.png", "最坏情况下最大化收益 (冯·诺依曼)"),
    ("Alpha-Beta 剪枝", "alpha_beta.png", "剪掉不影响决策的分支"),
    ("Heuristic 启发式搜索", "heuristic.png", "优先搜子力优势大的走法"),
    ("为什么围棋不能用 Minimax？", "why_go_fails.png", "分支因子 + 估值函数"),
]:
    slides.append({
        "background": BG_WHITE,
        "elements": header(f"{title}  {sub}" if sub else title) + [
            IMG(asset(img), 1.0, 1.2, 11.3, 5.8),
        ]
    })

# ═══ Slide 8: Game Complexity ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("为什么围棋这么难？") + [
        IMG(asset("complexity.png"), 0.5, 1.2, 12.3, 5.5),
    ]
})

# ═══ Slide 9: MC from Physics to Games ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("蒙特卡洛方法：从物理到博弈") + [
        S("rounded_rectangle", 0.5, 1.3, 5.8, 4.3, C_LGREEN),
        T("物理中的蒙特卡洛", 0.8, 1.4, 5.2, 0.4, 17, C_GREEN, bold=True),
        T("• 格点QCD：用MC采样计算路径积分\n\n• Metropolis算法：按 exp(-S) 采样构型\n\n• 重要性采样：用概率分布引导采样\n\n• 核心思想：用随机采样近似复杂积分",
          0.8, 2.0, 5.2, 3.4, 13, "333333"),
        S("rounded_rectangle", 7.0, 1.3, 5.8, 4.3, C_LBLUE),
        T("博弈中的蒙特卡洛", 7.3, 1.4, 5.2, 0.4, 17, C_BLUE, bold=True),
        T("• 随机模拟对局至终局获得结果\n\n• 统计胜率来评估局面好坏\n\n• 用树结构组织搜索方向\n\n• 核心思想：用随机采样近似博弈值",
          7.3, 2.0, 5.2, 3.4, 13, "333333"),
        S("rounded_rectangle", 0.5, 5.9, 12.3, 0.7, C_LRED),
        T("本质相同：用随机采样解决精确计算不可行的问题", 0.5, 5.9, 12.3, 0.7, 15, C_RED, bold=True, align="center"),
    ]
})

# ═══ Slides 10-12: Traditional MCTS iter1, iter2, tree growth ═══
for title, img, sub in [
    ("传统 MCTS 第 1 次模拟", "ttt_iter1.png", "展开 + Rollout + 回传 (井字棋实例)"),
    ("传统 MCTS 第 2 次模拟", "ttt_iter2.png", "UCT 选择 → 展开 → 回传"),
    ("搜索树的非对称增长", "tree_growth.png", "算力集中 = 重要性采样"),
]:
    slides.append({
        "background": BG_WHITE,
        "elements": header(f"{title}  {sub}" if sub else title) + [
            IMG(asset(img), 1.0, 1.2, 11.3, 5.8),
        ]
    })

# ═══ Slide 13: MCTS Four Phases ═══
phases = [
    ("① 选择 Selection", "从根节点沿UCT最大的子节点下行", C_BLUE, C_LBLUE),
    ("② 扩展 Expansion", "到达叶节点后添加一个新子节点", C_GREEN, C_LGREEN),
    ("③ 模拟 Simulation", "从新节点随机走子直到游戏结束", C_ORANGE, C_LORANGE),
    ("④ 回传 Backpropagation", "将结果沿路径回传更新统计量", C_RED, C_LRED),
]
phase_els = header("MCTS 的四个阶段") + [
    IMG(asset("mcts_phases.png"), 0.5, 1.1, 12.3, 3.8),
    T("每次迭代执行这四个步骤，逐步积累统计信息，搜索精度随迭代次数增加而提高",
      0.5, 5.0, 12.3, 0.4, 13, C_GRAY, align="center"),
]
for i, (t, d, c, bg) in enumerate(phases):
    x = 0.5 + i * 3.15
    phase_els += [
        S("rounded_rectangle", x, 5.6, 2.95, 1.3, bg),
        T(t, x+0.1, 5.7, 2.75, 0.35, 13, c, bold=True),
        T(d, x+0.1, 6.1, 2.75, 0.7, 11, "333333"),
    ]
slides.append({"background": BG_WHITE, "elements": phase_els})

# ═══ Slides 14-17: Selection / Expansion / Simulation / Backprop (detail) ═══
detail_pages = [
    ("① Selection 选择", "mcts_1_selection.png", C_BLUE, C_LBLUE,
     "从根节点出发，对每个子节点计算 PUCT 值，选最大者下行，递归至叶节点。\n\nu = Q(s,a) + c_puct · P(s,a) · √N(s) / (1+N(s,a))\n\n利用-探索平衡：Q 大→历史好；N 小→多探索",
     "沿 UCT 最大路径下行至叶节点"),
    ("② Expansion 扩展", "mcts_2_expansion.png", C_GREEN, C_LGREEN,
     "到达叶节点后，若非终局，添加一个未尝试的合法动作作为新子节点。\n\nAlphaGo Zero 的特点：扩展即评估——首次访问叶节点时立即调用神经网络得到 (P, v)，扩展与模拟合二为一。\n\n对 P 做合法动作掩码后重归一化。",
     "在叶节点下添加新子节点"),
    ("③ Simulation 模拟", "mcts_3_simulation.png", C_ORANGE, C_LORANGE,
     "传统：从新节点随机 rollout 到终局，得 z=±1。质量差、计算量大（需上千次模拟）。\n\nAlphaGo Zero：不做 rollout。叶节点处直接用网络 v = fθ(s)，一次前向传播得到价值估计。\n\n→ 论文标题 \"without rollouts\" 的由来。25 次模拟即可下出好棋。",
     "评估新节点价值（关键差异）"),
    ("④ Backpropagation 回传", "mcts_4_backprop.png", C_RED, C_LRED,
     "沿选择路径回传，更新每条边的 N(s,a) 与 Q(s,a)：\n\nQ ← (N·Q + v) / (N+1),  N ← N+1\n\n关键 1：W/N = Q —— 累计价值除以访问次数即平均价值。\n关键 2：return -v —— 每上一层取负。W 相对于当前走棋玩家，这是 minimax 的体现。\n\n增量平均 O(1) 空间。本质是 TD 思想。",
     "沿路径更新 N 与 Q"),
]
for title, img, c, bg, body, sub in detail_pages:
    slides.append({
        "background": BG_WHITE,
        "elements": header(f"{title}  {sub}") + [
            IMG(asset(img), 0.4, 1.2, 6.2, 5.5),
            S("rounded_rectangle", 6.9, 1.2, 6.0, 5.5, bg),
            T("原理", 7.1, 1.3, 5.6, 0.35, 14, c, bold=True),
            T(body, 7.1, 1.75, 5.6, 4.8, 12, "333333"),
        ]
    })

# ═══ Slide 18: MCTS Evolution ═══
evo_cards = [
    ("(a) 传统 MCTS", "随机 rollout 到终局\n质量差、上千次模拟\nU ∝ √(ln Np / ni)", C_ORANGE, C_LORANGE),
    ("(b) + 策略网络", "P(s,a) 引导搜索方向\n好走法优先探索\n仍保留 rollout", C_BLUE, C_LBLUE),
    ("(c) + 价值网络", "v(s) 替代 rollout\n一次前向传播得价值\n\"without rollouts\"", C_GREEN, C_LGREEN),
    ("(d) AlphaZero", "单网络 f(s)→(p,v)\n策略+价值共享特征\n通吃棋类", C_RED, C_LRED),
]
evo_els = header("MCTS 的演进  Rollout → 策略网络 → 价值网络 → 单网络") + [
    IMG(asset("ttt_evolution.png"), 0.5, 1.1, 12.3, 4.0),
]
for i, (t, d, c, bg) in enumerate(evo_cards):
    x = 0.5 + i * 3.15
    evo_els += [
        S("rounded_rectangle", x, 5.3, 2.95, 1.6, bg),
        T(t, x+0.1, 5.4, 2.75, 0.35, 12, c, bold=True),
        T(d, x+0.1, 5.8, 2.75, 1.0, 10, "333333"),
    ]
slides.append({"background": BG_WHITE, "elements": evo_els})

# ═══ Slides 19-21: Design thinking 1/2/3 ═══
for title, img, sub in [
    ("设计思考 ①：为什么要下行到叶子？", "why_leaf.png", "只决策一层吗？"),
    ("设计思考 ②：模拟的复杂度", "complexity_compare.png", "\"只运行一次网络\"是什么意思？"),
    ("设计思考 ③：MCTS 在系统中的角色", "policy_operator.png", "策略改进算子"),
]:
    slides.append({
        "background": BG_WHITE,
        "elements": header(f"{title}  {sub}" if sub else title) + [
            IMG(asset(img), 1.0, 1.2, 11.3, 5.8),
        ]
    })

# ═══ Slide 22: UCT Formula ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("Selection: UCT 公式") + [
        T("Upper Confidence Bound applied to Trees", 0.5, 1.0, 12, 0.35, 14, C_GRAY),
        S("rounded_rectangle", 1.5, 1.5, 10.3, 1.0, C_LBLUE),
        T("UCT(i) = wᵢ/nᵢ + c · √( ln N / nᵢ )", 1.5, 1.5, 10.3, 1.0, 22, C_NAVY, bold=True, align="center"),
    ] + card(0.5, 2.8, 3.8, 1.8, C_LBLUE, "利用项 (Exploitation)", C_BLUE,
             "wᵢ/nᵢ = 第 i 个子节点的平均胜率，偏好好的走法")
    + card(4.75, 2.8, 3.8, 1.8, C_LORANGE, "探索项 (Exploration)", C_ORANGE,
           "√(ln N / nᵢ)：访问少的节点获得更高的探索奖励")
    + card(9.0, 2.8, 3.8, 1.8, C_LPURPLE, "探索常数 c", C_PURPLE,
           "控制利用与探索的平衡，常用 c = √2") + [
        S("rectangle", 0.5, 4.9, 12.3, 0.02, C_LGRAY),
        S("rounded_rectangle", 0.5, 5.1, 12.3, 0.7, C_LRED),
        T("核心性质：UCT 在无限采样下收敛到极小极大最优解 (Kocsis & Szepesvári, 2006)",
          0.5, 5.1, 12.3, 0.7, 14, C_RED, bold=True, align="center"),
        S("rounded_rectangle", 0.5, 6.0, 12.3, 0.7, C_LGREEN),
        T("类比物理：类似模拟退火中温度控制探索-利用平衡，或 Metropolis 中接受概率的作用",
          0.5, 6.0, 12.3, 0.7, 14, C_TEAL, bold=True, align="center"),
    ]
})

# ═══ Slide 23: MCTS Properties ═══
props = [
    ("渐近最优 (Asymptotic Optimality)", "随着模拟次数 N→∞，MCTS 的选择概率收敛到最优策略。这是 UCT 的理论保证。", C_BLUE, C_LBLUE),
    ("Anytime 算法", "可以随时中断并返回当前最优动作。计算资源越多，决策质量越高。天然适合有时间限制的实时决策。", C_GREEN, C_LGREEN),
    ("无需领域知识", "不需要人工设计评估函数。仅需知道游戏规则（合法动作和终止条件），即可通过模拟获取价值信息。", C_ORANGE, C_LORANGE),
    ("自适应搜索", "自动将更多计算资源分配给最有前途的分支。搜索树非对称增长，类似重要性采样。", C_PURPLE, C_LPURPLE),
]
prop_els = header("MCTS 的关键性质")
for i, (t, d, c, bg) in enumerate(props):
    x = 0.5 if i % 2 == 0 else 6.9
    y = 1.3 + (i // 2) * 2.7
    prop_els += [
        S("rounded_rectangle", x, y, 5.9, 2.4, bg),
        T(t, x+0.2, y+0.15, 5.5, 0.4, 15, c, bold=True),
        T(d, x+0.2, y+0.65, 5.5, 1.6, 13, "333333"),
    ]
slides.append({"background": BG_WHITE, "elements": prop_els})

# ═══ Slide 24: Section II — AlphaGo Zero ═══
slides.append({
    "background": BG_SECTION,
    "elements": [
        T("PART II", 1, 1.5, 11.333, 0.8, 18, C_GOLD, bold=True, align="center"),
        T("AlphaGo Zero", 1, 2.5, 11.333, 1.2, 40, "FFFFFF", bold=True, align="center"),
        T("自我博弈的突破 · Mastering the Game of Go without Human Knowledge",
          1, 3.8, 11.333, 0.8, 16, "90A4AE", align="center"),
        S("rectangle", 5.167, 5.0, 3, 0.05, C_GOLD),
    ]
})

# ═══ Slide 25: Evolution (AlphaGo → AGZ) ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("从 AlphaGo 到 AlphaGo Zero", C_NAVY, C_RED) + [
        IMG(asset("evolution.png"), 0.5, 1.1, 12.3, 4.3),
        S("rounded_rectangle", 0.5, 5.6, 12.3, 1.3, C_LRED),
        T("AlphaGo Zero 的三大简化", 0.8, 5.7, 11.7, 0.4, 15, C_RED, bold=True),
        T("① 不使用任何人类棋谱 (no human data)    ② 仅用棋盘状态作为输入 (no hand-crafted features)    ③ 单一神经网络替代策略网络+价值网络",
          0.8, 6.15, 11.7, 0.6, 13, "333333"),
    ]
})

# ═══ Slide 26: NN Architecture ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("双头神经网络架构  (OthelloNNet.py)", C_NAVY, C_RED) + [
        IMG(asset("nn_arch.png"), 1.5, 1.0, 10.3, 6.2),
    ]
})

# ═══ Slide 27: PUCT ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("MCTS + 神经网络：PUCT 搜索  (MCTS.py:112-115)", C_NAVY, C_RED) + [
        IMG(asset("puct.png"), 0.5, 1.0, 12.3, 4.3),
        S("rounded_rectangle", 0.5, 5.5, 12.3, 1.5, "F0F4F8"),
        T("与传统 MCTS 的关键区别", 0.8, 5.6, 11.7, 0.4, 15, C_NAVY, bold=True),
        T("① 用 P(s,a) 替代随机模拟 (Simulation)    ② 用 v(s) 替代终局结果    ③ 搜索效率大幅提升，少量模拟即可获得高质量策略",
          0.8, 6.1, 11.7, 0.7, 13, "333333"),
    ]
})

# ═══ Slide 28: Self-Play Loop ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("自我对弈与数据生成  MCTS → 落子策略 π → 训练数据 (s, π, z)", C_NAVY, C_RED) + [
        IMG(asset("self_play_loop.png"), 0.3, 1.1, 6.0, 5.5),
        S("rounded_rectangle", 6.6, 1.1, 6.4, 2.6, C_LBLUE),
        T("从搜索到落子：温度采样", 6.8, 1.2, 6.0, 0.35, 14, C_BLUE, bold=True),
        T("MCTS 跑完 N 次模拟后，根节点访问次数 N(s,a) 如何变成落子策略？\n\nπᵢ = N(s,aᵢ)^(1/τ)\n\n对弈 τ→0：选 N 最大的（确定性、最强）\n自对弈前期 τ=1：按比例随机采样（探索、防模式坍塌）\n教学版 tempThreshold=15：前 15 步探索，之后利用",
          6.8, 1.6, 6.0, 2.0, 12, "333333"),
        S("rounded_rectangle", 6.6, 3.9, 6.4, 2.7, C_LORANGE),
        T("训练数据 (s, π, z)", 6.8, 4.0, 6.0, 0.35, 14, C_ORANGE, bold=True),
        T("每步记录：\n• s：棋盘状态\n• π：MCTS 访问次数分布（温度采样后）\n• z：终局胜负 (±1)\n\n一局自对弈 → 一条轨迹 → 多个 (s,π,z)\n网络学：p → π（策略蒸馏），v → z（价值评估）",
          6.8, 4.4, 6.0, 2.1, 12, "333333"),
    ]
})

# ═══ Slides 29-31: Param table, Compute compare, Paper params ═══
for title, img, sub in [
    ("代码参数对照表", "param_table.png", "(alpha-zero-general 默认配置)"),
    ("复现算力对比", "compute_compare.png", "论文 vs 教学版"),
    ("论文参数量级对照", "paper_params.png", "Lee / AGZ / AZ · 参数量级 aware"),
]:
    slides.append({
        "background": BG_WHITE,
        "elements": header(f"{title}  {sub}" if sub else title, C_NAVY, C_RED) + [
            IMG(asset(img), 0.5, 1.1, 12.3, 5.8),
        ]
    })

# ═══ Slide 32: Loss Function ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("训练目标：损失函数  (NNet.py:96-100)", C_NAVY, C_RED) + [
        S("rounded_rectangle", 1.5, 1.3, 10.3, 0.9, C_LBLUE),
        T("ℓ = (z - v)²  −  πᵀ log p", 1.5, 1.3, 10.3, 0.9, 22, C_NAVY, bold=True, align="center"),
        T("注：论文含 c‖θ‖² 正则项，教学实现省略（靠 BN + Dropout 防过拟合）",
          0.5, 2.3, 12.3, 0.35, 12, C_GRAY, align="center"),
    ] + card(0.5, 2.8, 5.9, 2.2, C_LBLUE, "价值损失 (z-v)²", C_BLUE,
             "z: 自我对弈终局结果 (±1)\nv: 网络预测的价值 (tanh)\n\nloss_v = sum((target-output)²)/N\n让网络学会准确评估局面")
    + card(6.9, 2.8, 5.9, 2.2, C_LORANGE, "策略损失 −πᵀ log p", C_ORANGE,
           "π: MCTS 访问次数分布\np: 网络输出 log_softmax\n\nloss_pi = -sum(π·logp)/N\n本质是交叉熵 / 知识蒸馏") + [
        S("rounded_rectangle", 0.5, 5.3, 12.3, 1.6, C_NAVY),
        T("策略提升的闭环 (Coach.py)", 0.8, 5.4, 11.7, 0.4, 15, C_GOLD, bold=True),
        T("MCTS搜索 → 得到改进策略π → 训练网络逼近π → 网络指导MCTS → 更强的搜索 → ...",
          0.8, 5.85, 11.7, 0.4, 13, "FFFFFF"),
        T("类比物理中的自洽场方法 (SCF)：每轮迭代都以前一轮结果为基础，逐步逼近最优解",
          0.8, 6.35, 11.7, 0.4, 12, C_TEAL),
    ]
})

# ═══ Slide 33: Training Pipeline ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("完整训练流程  (Coach.py: learn)", C_NAVY, C_RED) + [
        IMG(asset("training_pipeline.png"), 0.3, 1.1, 12.7, 4.3),
        T("教学版：1 块 K80 GPU，~3 天，80 迭代收敛  |  AGZ：评估 4 TPU，1600 模拟/步，3 天 490 万局",
          0.5, 5.6, 12.3, 0.4, 13, C_GRAY, align="center"),
        S("rounded_rectangle", 0.5, 6.1, 12.3, 0.7, C_LGREEN),
        T("并行计算架构：自我对弈各 worker 独立，天然适合大规模并行加速（HPC 场景）",
          0.5, 6.1, 12.3, 0.7, 14, C_TEAL, bold=True, align="center"),
    ]
})

# ═══ Slide 34: Results (Elo) ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("训练效果", C_NAVY, C_RED) + [
        IMG(asset("elo_progress.png"), 0.5, 1.0, 12.3, 5.8),
    ]
})

# ═══ Slide 35: KataGo Elo vs MCTS visits ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("KataGo 强度 vs MCTS 搜索量  (对数线性标度律)", C_NAVY, C_RED) + [
        IMG(asset("katago_elo_vs_visits.png"), 0.5, 1.0, 12.3, 5.3),
        S("rounded_rectangle", 0.5, 6.4, 12.3, 0.7, C_LGREEN),
        T("Elo ≈ Elo₀ + k·log₁₀(visits)  |  每搜索量 ×10 ≈ +350–490 Elo  |  1 visit ≈ 业余 6–8 段",
          0.5, 6.4, 12.3, 0.7, 13, C_TEAL, bold=True, align="center"),
    ]
})

# ═══ Slide 36: KataGo optimizations ═══
katago_cards = [
    ("1. 多任务辅助训练", "• 目数预测 (Score Lead)\n• 子力归属预测 (Ownership)\n• 对手下一步预测\n• 效果：极快缩短摸索期", C_BLUE, C_LBLUE),
    ("2. 变化算力自弈", "• 90% 常规步用极低模拟量\n• 10% 关键点用完整模拟\n• 效果：自弈数据生成效率提升数倍", C_GREEN, C_LGREEN),
    ("3. 全局感知 SE 模块", "• 全局通道特征提取\n• 打破 CNN 长距离传导局限\n• 效果：提升死活和全局厚势直觉", C_ORANGE, C_LORANGE),
    ("4. 胜率-目数混合效用", "• 克服 AlphaZero 只看胜率弊端\n• 追求目数优势最大化\n• 效果：让子棋和逆风局表现极强", C_PURPLE, C_LPURPLE),
]
kat_els = [
    accent(C_RED),
    T("KataGo 核心算法优化：超越 AlphaZero 的秘诀", 0.5, 0.25, 12.3, 0.6, 24, C_NAVY, bold=True),
    T("相比于 AlphaGo Zero，KataGo (Wu 2019) 引入了多项关键改良，将训练效率提升了 50~100 倍",
      0.5, 0.85, 12.3, 0.35, 12, C_GRAY),
]
for i, (t, d, c, bg) in enumerate(katago_cards):
    x = 0.5 if i % 2 == 0 else 6.9
    y = 1.4 + (i // 2) * 2.3
    kat_els += [
        S("rounded_rectangle", x, y, 5.9, 2.1, bg),
        T(t, x+0.2, y+0.1, 5.5, 0.35, 14, c, bold=True),
        T(d, x+0.2, y+0.5, 5.5, 1.5, 11, "333333"),
    ]
kat_els += [
    S("rounded_rectangle", 0.5, 6.1, 12.3, 1.0, C_NAVY),
    T("规则兼容与工程大众化革新", 0.8, 6.15, 11.7, 0.35, 13, C_GOLD, bold=True),
    T("直接将贴目 (Komi) 和规则信息作为特征输入，支持单模型全规则兼容；引入 OpenCL/Vulkan/TensorRT，使普通家用显卡也能高效运行和训练超人类强度的围棋 AI。",
      0.8, 6.5, 11.7, 0.5, 11, "CFD8DC"),
]
slides.append({"background": BG_WHITE, "elements": kat_els})

# ═══ Slide 37: Section III — RL Foundations ═══
slides.append({
    "background": BG_SECTION,
    "elements": [
        T("PART III", 1, 1.5, 11.333, 0.8, 18, C_GOLD, bold=True, align="center"),
        T("强化学习基础", 1, 2.5, 11.333, 1.2, 40, "FFFFFF", bold=True, align="center"),
        T("Reinforcement Learning Foundations", 1, 3.8, 11.333, 0.8, 20, "90A4AE", align="center"),
        S("rectangle", 5.167, 5.0, 3, 0.05, C_GOLD),
    ]
})

# ═══ Slide 38: MDP ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("马尔可夫决策过程 (MDP)", C_NAVY, C_TEAL) + [
        IMG(asset("mdp.png"), 0.5, 1.1, 12.3, 4.0),
        S("rounded_rectangle", 0.5, 5.3, 12.3, 0.7, C_LRED),
        T("围棋天然是一个 MDP：状态 = 棋盘局面，动作 = 落子位置，奖励 = 终局胜负 (±1)",
          0.5, 5.3, 12.3, 0.7, 14, C_RED, bold=True, align="center"),
        T("RL 的目标：学习最优策略 π* 使得累积奖励最大", 0.5, 6.2, 12.3, 0.4, 14, C_GRAY, align="center"),
    ]
})

# ═══ Slide 39: Value Function ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("价值函数与策略", C_NAVY, C_TEAL) + [
        S("rounded_rectangle", 0.5, 1.2, 5.9, 2.4, C_LBLUE),
        T("策略 π(a|s)", 0.8, 1.3, 5.3, 0.4, 16, C_BLUE, bold=True),
        T("在状态 s 下选择动作 a 的概率分布\n\n策略是 agent 的\"行为准则\"\n\n目标：找到最优策略 π*", 0.8, 1.8, 5.3, 1.6, 13, "333333"),
        S("rounded_rectangle", 7.0, 1.2, 5.9, 2.4, C_LGREEN),
        T("状态价值函数 V(s)", 7.3, 1.3, 5.3, 0.4, 16, C_GREEN, bold=True),
        T("从状态 s 出发，遵循策略 π 的期望累积回报\n\nV^π(s) = E_π[Gₜ | Sₜ = s]\nGₜ = Rₜ₊₁ + γRₜ₊₂ + γ²Rₜ₊₃ + ...", 7.3, 1.8, 5.3, 1.6, 13, "333333"),
        S("rounded_rectangle", 0.5, 3.9, 12.4, 2.2, C_LORANGE),
        T("动作价值函数 Q(s, a)", 0.8, 4.0, 5.3, 0.4, 16, C_ORANGE, bold=True),
        T("在状态 s 执行动作 a 后，遵循策略 π 的期望累积回报：  Q^π(s,a) = E_π[Gₜ | Sₜ = s, Aₜ = a]\n\n在 AlphaGo 中: Q(s,a) 就是 MCTS 节点统计的平均回报，用来指导选择最优走法",
          0.8, 4.5, 11.8, 1.4, 13, "333333"),
    ]
})

# ═══ Slide 40: MC vs TD ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("蒙特卡洛方法 vs 时序差分学习", C_NAVY, C_TEAL) + [
        IMG(asset("td_vs_mc.png"), 0.2, 1.1, 12.9, 3.5),
        S("rounded_rectangle", 0.5, 4.8, 6.0, 1.9, C_LBLUE),
        T("MC 更新：等到终局", 0.8, 4.9, 5.4, 0.35, 14, C_BLUE, bold=True),
        T("V(Sₜ) ← V(Sₜ) + α[Gₜ - V(Sₜ)]\n\n无偏但高方差，必须完成完整轨迹", 0.8, 5.3, 5.4, 1.3, 12, "333333"),
        S("rounded_rectangle", 6.9, 4.8, 6.0, 1.9, C_LRED),
        T("TD(0) 更新：每步即学", 7.2, 4.9, 5.4, 0.35, 14, C_RED, bold=True),
        T("V(Sₜ) ← V(Sₜ) + α[Rₜ₊₁ + γV(Sₜ₊₁) - V(Sₜ)]\n\n有偏但低方差，用估计值 bootstrap", 7.2, 5.3, 5.4, 1.3, 12, "333333"),
    ]
})

# ═══ Slide 41: TD(λ) ═══
slides.append({
    "background": BG_WHITE,
    "elements": header("TD(λ)：MC 与 TD 的统一框架", C_NAVY, C_TEAL) + [
        S("rounded_rectangle", 1, 1.2, 11.3, 0.6, C_LBLUE),
        T("TD(0)  λ=0                              TD(λ)  λ=0.5                              MC  λ=1",
          1, 1.2, 11.3, 0.6, 13, C_NAVY, bold=True, align="center"),
        T("n-step 回报", 0.5, 2.1, 12, 0.4, 18, C_NAVY, bold=True),
        T("1-step:  G⁽¹⁾ = Rₜ₊₁ + γV(Sₜ₊₁)                          ← TD(0)\n\n2-step:  G⁽²⁾ = Rₜ₊₁ + γRₜ₊₂ + γ²V(Sₜ₊₂)\n\nn-step:  G⁽ⁿ⁾ = Rₜ₊₁ + γRₜ₊₂ + ... + γⁿV(Sₜ₊ₙ)\n\n∞-step:  G⁽∞⁾ = Rₜ₊₁ + γRₜ₊₂ + ...                       ← MC",
          0.8, 2.6, 11.5, 2.4, 14, "333333"),
        S("rounded_rectangle", 0.5, 5.3, 12.3, 1.2, C_LPURPLE),
        T("Gₜ^λ = (1-λ) Σₙ₌₁^∞ λⁿ⁻¹ G⁽ⁿ⁾,   λ ∈ [0,1] 控制看多远",
          0.5, 5.3, 12.3, 1.2, 16, C_PURPLE, bold=True, align="center"),
    ]
})

# ═══ Slide 42: Summary ═══
summ_cards = [
    ("MCTS", C_BLUE, C_LBLUE, "通过蒙特卡洛模拟在博弈树中进行高效的选择性搜索\n\nUCT 平衡利用与探索\n无需评估函数"),
    ("RL 基础", C_GREEN, C_LGREEN, "TD 学习：每步更新\n结合估计与真实回报\n\n从 MC 到 TD 的统一框架 TD(λ)"),
    ("AlphaGo Zero", C_RED, C_LRED, "神经网络替代模拟\nMCTS 提供策略改进\n自我对弈生成数据\n\n从零开始超越人类"),
]
summ_els = header("总结", C_NAVY, C_NAVY)
for i, (t, c, bg, d) in enumerate(summ_cards):
    x = 0.5 + i * 4.25
    summ_els += [
        S("rounded_rectangle", x, 1.3, 4.0, 2.6, bg),
        T(t, x, 1.4, 4.0, 0.4, 18, c, bold=True, align="center"),
        T(d, x+0.2, 1.9, 3.6, 1.9, 12, "333333", align="center"),
    ]
summ_els += [
    S("rounded_rectangle", 0.5, 4.2, 12.3, 2.6, C_NAVY),
    T("核心洞察", 0.8, 4.3, 11.7, 0.4, 18, C_GOLD, bold=True),
    T("搜索 (MCTS) + 评估 (Neural Network) + 学习 (Self-Play RL) = 从零开始的超人智能",
      0.8, 4.8, 11.7, 0.5, 15, "FFFFFF"),
    T("类比物理：就像变分蒙特卡洛 (VMC) —— 用参数化的试探波函数 (神经网络) 引导蒙特卡洛采样 (MCTS)，然后通过优化变分参数 (训练) 来逼近基态 (最优策略)",
      0.8, 5.5, 11.7, 1.0, 13, C_TEAL),
]
slides.append({"background": BG_WHITE, "elements": summ_els})

# ═══ Slide 43: Thank You ═══
slides.append({
    "background": BG_DARK,
    "elements": [
        T("谢谢！", 1, 2.5, 11.333, 1.2, 44, "FFFFFF", bold=True, align="center"),
        S("rectangle", 5.167, 4.0, 3, 0.05, C_GOLD),
    ]
})

# ═══ Write spec ═══
spec = {"width": 13.333, "height": 7.5, "slides": slides}
spec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec.json")
with open(spec_path, 'w', encoding='utf-8') as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
print(f"Spec written: {len(slides)} slides -> {spec_path}")
