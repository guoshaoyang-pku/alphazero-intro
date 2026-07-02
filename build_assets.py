#!/usr/bin/env python3
"""Generate all diagram assets for the rigorous AlphaGo Zero presentation.
Based on: Silver et al. (2017) Nature 550:354-359; Silver et al. (2018) Science 362:1140-1144.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.lines import Line2D

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

CN_FONT = "Noto Sans CJK SC"
matplotlib.rcParams['font.sans-serif'] = [CN_FONT, 'STHeiti', 'Heiti TC', 'PingFang HK']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

# Colors
C_NAVY = "#0D1B3E"
C_BLUE = "#1565C0"
C_LIGHT_BLUE = "#42A5F5"
C_TEAL = "#00897B"
C_GOLD = "#E8A838"
C_RED = "#E53935"
C_GREEN = "#43A047"
C_ORANGE = "#FB8C00"
C_GRAY = "#9E9E9E"
C_LIGHT_GRAY = "#E0E0E0"
C_WHITE = "#FFFFFF"
C_BG = "#F8F9FA"
C_DARK_TEXT = "#1A1A2E"
C_PURPLE = "#7B1FA2"
C_PALE_BLUE = "#E3F2FD"
C_PALE_GREEN = "#E8F5E9"
C_PALE_ORANGE = "#FFF3E0"
C_PALE_RED = "#FFEBEE"
C_PALE_PURPLE = "#F3E5F5"

DPI = 200

def save(fig, name):
    path = os.path.join(ASSET_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor(),
                edgecolor='none', pad_inches=0.12)
    plt.close(fig)
    print(f"  [+] {name}")
    return path

# ── 1. Input planes (17) ──────────────────────────────────────────────────
def create_input_planes():
    fig, ax = plt.subplots(figsize=(13, 3.2), facecolor=C_WHITE)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 8 own planes
    for i in range(8):
        ax.add_patch(Rectangle((i, 3.3), 0.85, 1.3, facecolor=C_BLUE, alpha=0.35+0.08*i,
                               edgecolor=C_NAVY, lw=0.8))
        ax.text(i+0.42, 4.85, f'$X_{{t-{i}}}$', fontsize=8, ha='center', color=C_NAVY)
    ax.text(3.4, 2.95, "8 planes: 己方历史棋盘 (当前及前7步)", fontsize=10,
            ha='center', color=C_BLUE, fontweight='bold')

    # 8 opponent planes
    for i in range(8):
        ax.add_patch(Rectangle((i, 1.4), 0.85, 1.3, facecolor=C_RED, alpha=0.35+0.08*i,
                               edgecolor=C_NAVY, lw=0.8))
        ax.text(i+0.42, 2.95, f'$O_{{t-{i}}}$', fontsize=8, ha='center', color=C_NAVY)
    ax.text(3.4, 1.05, "8 planes: 对手历史棋盘 (当前及前7步)", fontsize=10,
            ha='center', color=C_RED, fontweight='bold')

    # 1 color plane
    ax.add_patch(Rectangle((9.5, 1.4), 1.4, 3.2, facecolor=C_GOLD, alpha=0.7,
                           edgecolor=C_NAVY, lw=0.8))
    ax.text(10.2, 0.95, "1 plane: 当前轮\n执子颜色 C_t", fontsize=9,
            ha='center', color=C_GOLD, fontweight='bold')
    ax.text(10.2, 4.85, "$C_t$", fontsize=11, ha='center', color=C_NAVY)

    # Bracket for history
    ax.annotate('', xy=(8.3, 5.05), xytext=(0, 5.05),
                arrowprops=dict(arrowstyle='-', color=C_NAVY, lw=1.5))
    ax.plot([0, 8.3], [4.95, 4.95], '-', color=C_NAVY, lw=1)

    # Arrow to network
    ax.annotate('', xy=(13, 3), xytext=(11.2, 3),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5))

    # Network box
    rect = FancyBboxPatch((13, 1.8), 3.5, 2.4, boxstyle="round,pad=0.15",
                          fc=C_TEAL, ec=C_TEAL, alpha=0.9, zorder=2)
    ax.add_patch(rect)
    ax.text(14.75, 3.3, r'$f_\theta(s_t)$', fontsize=18, ha='center', va='center',
            color=C_WHITE, fontweight='bold', zorder=3)
    ax.text(14.75, 2.5, "ResNet\n双头网络", fontsize=10, ha='center', va='center',
            color=C_WHITE, zorder=3)

    # Bracket annotation
    ax.text(4, 0.3, r"输入状态 $s_t \in \{0,1\}^{19 \times 19 \times 17}$  (binary feature planes)",
            fontsize=12, ha='center', color=C_NAVY, fontweight='bold')

    plt.tight_layout()
    save(fig, "input_planes.png")

# ── 2. MCTS Four Phases (refined) ─────────────────────────────────────────
def create_mcts_phases():
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.4), facecolor=C_WHITE)
    fig.patch.set_facecolor(C_WHITE)

    nodes = [(0.5,1.1), (0.2,0.7), (0.8,0.7), (0.0,0.3), (0.3,0.3),
             (0.65,0.3), (1.0,0.3)]
    edges = [((0.5,1.1),(0.2,0.7)), ((0.5,1.1),(0.8,0.7)),
             ((0.2,0.7),(0.0,0.3)), ((0.2,0.7),(0.3,0.3)),
             ((0.8,0.7),(0.65,0.3)), ((0.8,0.7),(1.0,0.3))]

    def draw_tree(ax, nodes, edges, highlight_path=None, new_node=None,
                  rollout_path=None, show_stats=False, stats=None,
                  updated_nodes=None):
        for (x1,y1), (x2,y2) in edges:
            style = '-'
            color = C_GRAY
            lw = 1.5
            if rollout_path and ((x1,y1),(x2,y2)) in rollout_path:
                style = '--'
                color = C_ORANGE
                lw = 2
            elif highlight_path and ((x1,y1),(x2,y2)) in highlight_path:
                color = C_BLUE
                lw = 2.5
            ax.plot([x1,x2], [y1,y2], style, color=color, lw=lw, zorder=1)
        for i, (x, y) in enumerate(nodes):
            color = C_LIGHT_GRAY
            ec = C_GRAY
            r = 0.12
            zorder = 2
            if new_node and (x,y) == new_node:
                color = C_GREEN
                ec = C_GREEN
                r = 0.13
                zorder = 3
            elif highlight_path:
                for (x1,y1),(x2,y2) in highlight_path:
                    if (x,y) == (x1,y1) or (x,y) == (x2,y2):
                        color = C_BLUE
                        ec = C_BLUE
                        break
            elif updated_nodes and (x,y) in updated_nodes:
                color = C_RED
                ec = C_RED
            circle = plt.Circle((x,y), r, fc=color, ec=ec, lw=1.5, zorder=zorder)
            ax.add_patch(circle)
            if show_stats and stats and (x,y) in stats:
                w, n = stats[(x,y)]
                ax.text(x, y, f"{w}/{n}", fontsize=6, ha='center', va='center',
                        color=C_WHITE, fontweight='bold', zorder=4)
        ax.set_xlim(-0.3, 1.3)
        ax.set_ylim(-0.3, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')

    # Phase 1
    ax = axes[0]
    sel_path = [((0.5,1.1),(0.8,0.7)), ((0.8,0.7),(1.0,0.3))]
    draw_tree(ax, nodes, edges, highlight_path=sel_path)
    ax.set_title("(a) Select  选择", fontsize=13, fontweight='bold', color=C_BLUE, pad=8)
    ax.text(0.5, -0.18, r"argmax $Q + U$", fontsize=10, ha='center', color=C_DARK_TEXT)

    # Phase 2
    ax = axes[1]
    nodes2 = nodes + [(1.1, -0.05)]
    edges2 = edges + [((1.0,0.3),(1.1,-0.05))]
    sel_path2 = [((0.5,1.1),(0.8,0.7)), ((0.8,0.7),(1.0,0.3)), ((1.0,0.3),(1.1,-0.05))]
    draw_tree(ax, nodes2, edges2, highlight_path=sel_path2, new_node=(1.1,-0.05))
    ax.set_title("(b) Expand & Evaluate\n扩展与评估", fontsize=12, fontweight='bold', color=C_GREEN, pad=8)
    ax.text(0.5, -0.18, r"add $s_L$; query $f_\theta$", fontsize=10, ha='center', color=C_DARK_TEXT)

    # Phase 3
    ax = axes[2]
    updated = [(0.5,1.1), (0.8,0.7), (1.0,0.3), (1.1,-0.05)]
    stats = {(0.5,1.1): (7,10), (0.8,0.7): (5,7), (1.0,0.3): (3,4),
             (0.2,0.7): (2,3), (0.0,0.3): (1,1), (0.3,0.3): (1,2),
             (0.65,0.3): (2,3), (1.1,-0.05): (0,1)}
    draw_tree(ax, nodes2, edges2, show_stats=True, stats=stats, updated_nodes=updated)
    ax.set_title("(c) Backup  回传", fontsize=13, fontweight='bold', color=C_RED, pad=8)
    ax.text(0.5, -0.18, r"update $N, W, Q$", fontsize=10, ha='center', color=C_DARK_TEXT)

    # Phase 4: Play
    ax = axes[3]
    draw_tree(ax, nodes, edges, highlight_path=[((0.5,1.1),(0.2,0.7))],
              show_stats=True,
              stats={(0.5,1.1):(7,10),(0.2,0.7):(2,3),(0.8,0.7):(5,7),(0.0,0.3):(1,1),
                     (0.3,0.3):(1,2),(0.65,0.3):(2,3),(1.0,0.3):(3,4)})
    ax.set_title("(d) Play  落子", fontsize=13, fontweight='bold', color=C_GOLD, pad=8)
    ax.text(0.5, -0.18, r"$\pi \propto N^\tau$", fontsize=10, ha='center', color=C_DARK_TEXT)

    for i in range(3):
        fig.text(0.265 + i*0.24, 0.5, "→", fontsize=24, ha='center', va='center',
                 color=C_GOLD, fontweight='bold')
    plt.tight_layout(pad=1.5)
    save(fig, "mcts_phases.png")

# ── 3. Neural Network Architecture (refined) ──────────────────────────────
def create_nn_arch():
    fig, ax = plt.subplots(figsize=(9.5, 6.2), facecolor=C_WHITE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    def draw_block(x, y, w, h, text, color, text_color=C_WHITE, fontsize=12):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              fc=color, ec=color, alpha=0.9, zorder=2)
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, text, fontsize=fontsize, ha='center', va='center',
                color=text_color, fontweight='bold', zorder=3)

    def draw_arrow_v(x, y1, y2, color=C_GRAY):
        ax.annotate('', xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))

    draw_block(2.3, 8.8, 5.4, 0.7, r"输入 $s_t \in \{0,1\}^{19\times19\times17}$", C_NAVY)
    draw_arrow_v(5, 8.7, 8.1, C_NAVY)
    draw_block(2.8, 7.3, 4.4, 0.7, "初始卷积 3×3, 256 filters, BN+ReLU", C_BLUE)
    draw_arrow_v(5, 7.2, 6.6, C_BLUE)
    draw_block(2.3, 5.0, 5.4, 1.5, "残差网络 (ResNet)\n19 个残差块 (围棋)\n每块: 2×(3×3 conv + BN + ReLU)",
               C_TEAL, fontsize=12)
    draw_arrow_v(5, 4.9, 4.3, C_TEAL)
    ax.plot([5, 5], [4.3, 3.9], '-', color=C_GRAY, lw=2)
    ax.plot([3, 7], [3.9, 3.9], '-', color=C_GRAY, lw=2)
    ax.plot([3, 3], [3.9, 3.5], '-', color=C_GRAY, lw=2)
    ax.plot([7, 7], [3.9, 3.5], '-', color=C_GRAY, lw=2)

    draw_block(1.0, 2.6, 4.0, 0.8, "策略头 (Policy Head)\n1×1 conv + FC → 362 logits", C_GOLD, C_DARK_TEXT, 11)
    draw_arrow_v(3, 2.5, 1.9, C_GOLD)
    draw_block(1.3, 1.0, 3.4, 0.8, r"$\mathbf{p} = \mathrm{softmax}(\cdot)$", C_GOLD, C_DARK_TEXT, 13)
    ax.text(3, 0.5, r"$\mathbf{p} \in \mathbb{R}^{362}$: 落子概率", fontsize=10,
            ha='center', color=C_GOLD, style='italic')

    draw_block(5.0, 2.6, 4.0, 0.8, "价值头 (Value Head)\n1×1 conv + FC → 1 标量", C_RED, C_WHITE, 11)
    draw_arrow_v(7, 2.5, 1.9, C_RED)
    draw_block(5.3, 1.0, 3.4, 0.8, r"$v = \tanh(\cdot)$", C_RED, C_WHITE, 13)
    ax.text(7, 0.5, r"$v \in [-1,1]$: 胜率估计", fontsize=10,
            ha='center', color=C_RED, style='italic')

    ax.text(5, 9.75, r"双头残差网络  $f_\theta(s) = (\mathbf{p}, v)$",
            fontsize=15, ha='center', va='center', color=C_NAVY, fontweight='bold')
    plt.tight_layout()
    save(fig, "nn_arch.png")

# ── 4. Self-Play Loop ─────────────────────────────────────────────────────
def create_self_play_loop():
    fig, ax = plt.subplots(figsize=(8.5, 5.5), facecolor=C_WHITE)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3, 3.3)
    ax.axis('off')
    ax.set_aspect('equal')

    r = 2.0
    angles = [90, 210, 330]
    positions = [(r*np.cos(np.radians(a)), r*np.sin(np.radians(a))) for a in angles]
    labels = [
        ("神经网络\n" + r"$f_\theta$", C_BLUE),
        ("自我对弈\nSelf-Play", C_TEAL),
        ("MCTS\n搜索", C_GOLD),
    ]
    box_w, box_h = 1.9, 1.0
    for (x, y), (label, color) in zip(positions, labels):
        rect = FancyBboxPatch((x-box_w/2, y-box_h/2), box_w, box_h,
                              boxstyle="round,pad=0.15", fc=color, ec=color,
                              alpha=0.9, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=13, ha='center', va='center',
                color=C_WHITE, fontweight='bold', zorder=4)

    ax.annotate('', xy=(positions[2][0]-0.3, positions[2][1]+0.6),
                xytext=(positions[0][0]+0.7, positions[0][1]-0.5),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5,
                               connectionstyle="arc3,rad=-0.3"))
    ax.text(1.9, 1.0, r"提供 $(P, v)$", fontsize=11, ha='center', color=C_NAVY, style='italic')
    ax.annotate('', xy=(positions[1][0]+0.9, positions[1][1]),
                xytext=(positions[2][0]-0.9, positions[2][1]),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5,
                               connectionstyle="arc3,rad=-0.3"))
    ax.text(0, -2.5, r"搜索策略 $\pi$，选落子", fontsize=11, ha='center', color=C_NAVY, style='italic')
    ax.annotate('', xy=(positions[0][0]-0.7, positions[0][1]-0.5),
                xytext=(positions[1][0]+0.3, positions[1][1]+0.6),
                arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5,
                               connectionstyle="arc3,rad=-0.3"))
    ax.text(-1.9, 1.0, r"训练数据 $(s, \pi, z)$", fontsize=11, ha='center', color=C_NAVY, style='italic')
    ax.text(0, 3.1, "AlphaGo Zero 自我学习闭环", fontsize=15,
            ha='center', fontweight='bold', color=C_NAVY)
    plt.tight_layout()
    save(fig, "self_play_loop.png")

# ── 5. TD vs MC ───────────────────────────────────────────────────────────
def create_td_vs_mc():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 3.8), facecolor=C_WHITE)

    def draw_traj(ax, title, color, btype):
        ax.set_xlim(-0.5, 5.5)
        ax.set_ylim(-0.5, 2)
        ax.axis('off')
        states = [(i, 1) for i in range(6)]
        for i, (x, y) in enumerate(states):
            if i < 5:
                ax.plot([x+0.2, x+0.8], [y, y], '-', color=C_LIGHT_GRAY, lw=1.5)
                ax.text(x+0.5, y+0.2, f'$r_{{{i+1}}}$', fontsize=9, ha='center', color=C_GRAY)
            highlight = (btype == 'mc') or (btype == 'td0' and i <= 1) or (btype == 'tdl')
            fc = color if highlight else C_LIGHT_GRAY
            tc = C_WHITE if highlight else C_DARK_TEXT
            if btype == 'tdl':
                a = max(0.3, 1 - i*0.15)
            else:
                a = 1.0
            circle = plt.Circle((x, y), 0.18, fc=fc, ec=C_GRAY, lw=1.5, zorder=2, alpha=a)
            ax.add_patch(circle)
            label = f'$S_{{{i}}}$' if i < 5 else '$S_T$'
            ax.text(x, y, label, fontsize=9, ha='center', va='center', color=tc,
                    fontweight='bold', zorder=3)
        if btype == 'mc':
            ax.text(5, 0.4, r'$G_t$', fontsize=13, ha='center', color=color, fontweight='bold')
            ax.annotate('', xy=(0, 0.7), xytext=(5, 0.7),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                       connectionstyle='arc3,rad=0.4'))
        elif btype == 'td0':
            ax.text(1, 0.35, r'$r_1 + \gamma V(S_1)$', fontsize=11, ha='center', color=color, fontweight='bold')
            ax.annotate('', xy=(0, 0.7), xytext=(1, 0.7),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
        elif btype == 'tdl':
            ax.text(2.5, 0.25, r'$\lambda$-加权 $n$-step', fontsize=10, ha='center', color=color, fontweight='bold')
            ax.annotate('', xy=(0, 0.65), xytext=(4, 0.65),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                       connectionstyle='arc3,rad=0.3', linestyle='--'))
        ax.set_title(title, fontsize=14, fontweight='bold', color=color, pad=15)

    draw_traj(ax1, "Monte-Carlo (MC)", C_BLUE, 'mc')
    draw_traj(ax2, "TD(0)", C_RED, 'td0')
    draw_traj(ax3, "TD(λ)", C_PURPLE, 'tdl')
    plt.tight_layout(pad=1.5)
    save(fig, "td_vs_mc.png")

# ── 6. Policy Iteration ───────────────────────────────────────────────────
def create_policy_iteration():
    fig, ax = plt.subplots(figsize=(11, 4), facecolor=C_WHITE)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4)
    ax.axis('off')

    boxes = [
        (1.8, 2, r"策略 $\pi_i$", C_BLUE),
        (5.5, 2, r"策略评估 $\to v_{\pi_i}$", C_TEAL),
        (9.2, 2, r"策略改进 $\to \pi_{i+1}$", C_GOLD),
    ]
    for x, y, text, color in boxes:
        rect = FancyBboxPatch((x-1.3, y-0.55), 2.6, 1.1, boxstyle="round,pad=0.15",
                              fc=color, ec=color, alpha=0.9, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, text, fontsize=14, ha='center', va='center', color=C_WHITE,
                fontweight='bold', zorder=3)
    for i in range(2):
        x1 = boxes[i][0] + 1.35
        x2 = boxes[i+1][0] - 1.35
        ax.annotate('', xy=(x2, 2), xytext=(x1, 2),
                    arrowprops=dict(arrowstyle='->', color=C_NAVY, lw=2.5))
    ax.annotate('', xy=(1.8, 1.2), xytext=(9.2, 1.2),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2,
                               connectionstyle='arc3,rad=0.35', linestyle='--'))
    ax.text(5.5, 0.5, r"迭代收敛到 $\pi_* \leq \pi_{i+1}$", fontsize=13, ha='center',
            color=C_RED, fontweight='bold')
    ax.text(5.5, 3.6, "策略迭代 (Policy Iteration): Generalized Policy Iteration",
            fontsize=14, ha='center', fontweight='bold', color=C_NAVY)
    plt.tight_layout()
    save(fig, "policy_iteration.png")

# ── 7. Elo Progress ───────────────────────────────────────────────────────
def create_elo_progress():
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=C_WHITE)
    hours = np.array([0, 3, 6, 12, 24, 36, 48, 72])
    elo = np.array([0, 1000, 2000, 3200, 4200, 4800, 5100, 5185])
    ax.plot(hours, elo, 'o-', color=C_BLUE, lw=2.5, markersize=6, zorder=3)
    ax.fill_between(hours, elo, alpha=0.1, color=C_BLUE)
    for elo_val, label, color in [(3600, "AlphaGo Lee (2016)", C_TEAL),
                                   (4500, "AlphaGo Master (2017)", C_GOLD)]:
        ax.axhline(y=elo_val, color=color, linestyle='--', alpha=0.7, lw=1.5)
        ax.text(70, elo_val + 80, label, fontsize=10, color=color, fontweight='bold')
    ax.set_xlabel("训练时间 (小时)", fontsize=13, color=C_DARK_TEXT)
    ax.set_ylabel("Elo 等级分", fontsize=13, color=C_DARK_TEXT)
    ax.set_title("AlphaGo Zero: 棋力随训练时间的增长 (论文 Fig.1b)",
                 fontsize=14, fontweight='bold', color=C_NAVY, pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    save(fig, "elo_progress.png")

# ── 8. Complexity ─────────────────────────────────────────────────────────
def create_complexity():
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=C_WHITE)
    games = ['井字棋\nTic-Tac-Toe', '跳棋\nCheckers', '国际象棋\nChess', '围棋\nGo']
    complexity = [3, 21, 47, 170]
    colors = [C_TEAL, C_BLUE, C_GOLD, C_RED]
    bars = ax.barh(range(len(games)), complexity, color=colors, height=0.55,
                   edgecolor=colors, linewidth=1.5, alpha=0.85)
    ax.set_yticks(range(len(games)))
    ax.set_yticklabels(games, fontsize=13, fontweight='bold', color=C_DARK_TEXT)
    ax.set_xlabel("状态空间复杂度 (10的幂次)", fontsize=13, color=C_DARK_TEXT, labelpad=10)
    for i, (bar, val) in enumerate(zip(bars, complexity)):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'$10^{{{val}}}$', fontsize=16, va='center', fontweight='bold', color=colors[i])
    ax.set_xlim(0, 195)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)
    ax.annotate('宇宙原子数 ≈ $10^{80}$', xy=(85, 2.9), fontsize=11, color=C_GRAY, style='italic')
    ax.axvline(x=80, color=C_GRAY, linestyle=':', alpha=0.5)
    plt.tight_layout()
    save(fig, "complexity.png")

# ── 9. MDP ────────────────────────────────────────────────────────────────
def create_mdp():
    fig, ax = plt.subplots(figsize=(10, 3.6), facecolor=C_WHITE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')
    states = [(1.5, 2), (5, 2), (8.5, 2)]
    for i, (x, y) in enumerate(states):
        circle = plt.Circle((x, y), 0.5, fc=C_BLUE, ec=C_NAVY, lw=2, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, f'$S_{{{i}}}$', fontsize=16, ha='center', va='center',
                color=C_WHITE, fontweight='bold', zorder=3)
    for i in range(2):
        x1 = states[i][0] + 0.55
        x2 = states[i+1][0] - 0.55
        ax.annotate('', xy=(x2, 2), xytext=(x1, 2),
                    arrowprops=dict(arrowstyle='->', color=C_GOLD, lw=2.5))
        ax.text((x1+x2)/2, 2.5, f'$a_{{{i}}}, r_{{{i+1}}}$', fontsize=13,
                ha='center', color=C_GOLD, fontweight='bold')
    ax.text(9.8, 2, '...', fontsize=24, ha='center', va='center', color=C_GRAY)
    ax.text(5, 0.7, r'$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, P, R, \gamma \rangle$',
            fontsize=18, ha='center', color=C_NAVY, fontweight='bold')
    labels = [(1, 0.1, r"$\mathcal{S}$", C_BLUE), (3, 0.1, r"$\mathcal{A}$", C_GOLD),
              (5, 0.1, r"$P$", C_TEAL), (7, 0.1, r"$R$", C_RED), (9, 0.1, r"$\gamma$", C_PURPLE)]
    for x, y, text, color in labels:
        ax.text(x, y, text, fontsize=12, ha='center', color=color, fontweight='bold')
    ax.text(5, 3.5, "马尔可夫决策过程 (MDP)", fontsize=16, ha='center',
            fontweight='bold', color=C_NAVY)
    plt.tight_layout()
    save(fig, "mdp.png")

# ── 10. MCTS detailed backup diagram ──────────────────────────────────────
def create_mcts_backup():
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=C_WHITE)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.5)
    ax.axis('off')

    # Title
    ax.text(5.5, 5.2, "MCTS 节点存储与回传", fontsize=15, ha='center',
            fontweight='bold', color=C_NAVY)

    # Tree
    root = (1.5, 4)
    c1 = (0.7, 2.8)
    c2 = (2.3, 2.8)
    g1 = (0.3, 1.6)
    g2 = (1.1, 1.6)
    leaf = (2.3, 1.6)

    for (x1,y1),(x2,y2) in [((root),(c1)),((root),(c2)),((c1),(g1)),((c1),(g2)),((c2),(leaf))]:
        ax.plot([x1,x2],[y1,y2],'-',color=C_GRAY,lw=1.5)

    # nodes with stats
    node_data = [
        (root, "N=10\nW=7\nQ=0.70\nP=1.0", C_NAVY),
        (c1, "N=3\nW=2\nQ=0.67\nP=0.6", C_BLUE),
        (c2, "N=7\nW=5\nQ=0.71\nP=0.4", C_BLUE),
        (g1, "N=1\nW=1\nQ=1.0\nP=0.3", C_LIGHT_GRAY),
        (g2, "N=2\nW=1\nQ=0.5\nP=0.3", C_LIGHT_GRAY),
        (leaf, "N=0 → 1\nv from NN", C_GREEN),
    ]
    for (x,y), txt, color in node_data:
        circle = plt.Circle((x,y), 0.22, fc=color, ec=C_NAVY, lw=1.5, zorder=3)
        ax.add_patch(circle)
        ax.text(x+0.45, y, txt, fontsize=9, ha='left', va='center', color=C_DARK_TEXT,
                bbox=dict(boxstyle='round,pad=0.2', fc=C_PALE_BLUE, ec='none', alpha=0.8))

    # Backup arrow
    ax.annotate('', xy=(1.5, 4.3), xytext=(2.3, 1.9),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2.5,
                               connectionstyle='arc3,rad=0.4'))
    ax.text(3.2, 3.0, r"Backup: $N \leftarrow N+1$, $W \leftarrow W+v$, $Q = W/N$",
            fontsize=12, ha='left', color=C_RED, fontweight='bold')

    # Formulas on the right
    ax.text(6.5, 4.3, r"$U(s,a) = c_{\mathrm{puct}} \, P(s,a) \, \frac{\sqrt{N(s)}}{1 + N(s,a)}$",
            fontsize=14, ha='left', color=C_NAVY)
    ax.text(6.5, 3.6, r"$a^* = \arg\max_a \left[ Q(s,a) + U(s,a) \right]$",
            fontsize=14, ha='left', color=C_NAVY)
    ax.text(6.5, 2.9, r"$\pi(a|s) = \frac{N(s,a)^{1/\tau}}{\sum_b N(s,b)^{1/\tau}}$",
            fontsize=14, ha='left', color=C_GOLD)
    ax.text(6.5, 2.0, "其中:",
            fontsize=11, ha='left', color=C_DARK_TEXT, fontweight='bold')
    ax.text(6.5, 1.6, r"$N(s) = \sum_b N(s,b)$   父节点访问总数", fontsize=11, ha='left', color=C_DARK_TEXT)
    ax.text(6.5, 1.2, r"$Q(s,a) = W(s,a)/N(s,a)$   动作价值", fontsize=11, ha='left', color=C_DARK_TEXT)
    ax.text(6.5, 0.8, r"$\tau$ 温度: 控制落子随机性", fontsize=11, ha='left', color=C_DARK_TEXT)
    plt.tight_layout()
    save(fig, "mcts_backup.png")

# ── 11. Game complexity (search tree size) ────────────────────────────────
def create_search_tree():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4), facecolor=C_WHITE)

    # Left: full minimax tree
    ax1.set_xlim(-0.5, 4.5)
    ax1.set_ylim(-0.5, 4)
    ax1.axis('off')
    ax1.set_title("Minimax: 暴力枚举", fontsize=13, fontweight='bold', color=C_RED, pad=10)
    # Draw a dense tree
    import itertools
    levels = 4
    for level in range(levels):
        n = 2**level
        for i in range(n):
            x = i + 0.5 * (2**(levels-1-level) - 1) + 0.5
            y = 3.5 - level
            ax1.add_patch(plt.Circle((x, y), 0.12, fc=C_LIGHT_GRAY, ec=C_RED, lw=1, zorder=2))
            if level > 0:
                pi = i // 2
                px = pi + 0.5 * (2**(levels-1-(level-1)) - 1) + 0.5
                py = 3.5 - (level-1)
                ax1.plot([x, px], [y, py], '-', color=C_LIGHT_GRAY, lw=0.8, zorder=1)
    ax1.text(2, -0.3, r"$b^d = 250^{200} \approx 10^{480}$", fontsize=12, ha='center',
             color=C_RED, fontweight='bold')

    # Right: MCTS asymmetric tree
    ax2.set_xlim(-0.5, 4.5)
    ax2.set_ylim(-0.5, 4)
    ax2.axis('off')
    ax2.set_title("MCTS: 非对称选择性搜索", fontsize=13, fontweight='bold', color=C_BLUE, pad=10)

    # Asymmetric tree - more depth on promising branches
    nodes = [(2, 3.5), (1, 2.5), (3, 2.5), (0.5, 1.5), (1.5, 1.5), (2.5, 1.5), (3.5, 1.5),
             (0.2, 0.5), (0.8, 0.5), (1.2, 0.5), (1.8, 0.5), (2.2, 0.5), (2.8, 0.5)]
    edges = [((2,3.5),(1,2.5)),((2,3.5),(3,2.5)),
             ((1,2.5),(0.5,1.5)),((1,2.5),(1.5,1.5)),
             ((3,2.5),(2.5,1.5)),((3,2.5),(3.5,1.5)),
             ((0.5,1.5),(0.2,0.5)),((0.5,1.5),(0.8,0.5)),
             ((1.5,1.5),(1.2,0.5)),((1.5,1.5),(1.8,0.5)),
             ((2.5,1.5),(2.2,0.5)),((2.5,1.5),(2.8,0.5))]
    widths = [2.5, 1.5, 2, 2, 1, 1, 1, 1.5, 1, 1, 0.8, 0.8, 0.8]
    for i, ((x1,y1),(x2,y2)) in enumerate(edges):
        ax2.plot([x1,x2],[y1,y2],'-',color=C_BLUE,lw=widths[i],alpha=0.6,zorder=1)
    for i, (x,y) in enumerate(nodes):
        size = 0.18 if i==0 else 0.12
        ax2.add_patch(plt.Circle((x,y), size, fc=C_BLUE, ec=C_NAVY, lw=1, zorder=2, alpha=0.8))
    ax2.text(2, -0.3, r"聚焦有前途分支 $\propto \pi^{\tau}$", fontsize=12, ha='center',
             color=C_BLUE, fontweight='bold')

    plt.tight_layout()
    save(fig, "search_tree.png")

# ── 12. AlphaGo vs AlphaGo Zero comparison ────────────────────────────────
def create_ag_vs_agzero():
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor=C_WHITE)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis('off')

    ax.text(5.5, 4.7, "AlphaGo (Fan/Lee) vs AlphaGo Zero 对比", fontsize=15,
            ha='center', fontweight='bold', color=C_NAVY)

    # Headers
    ax.text(3.3, 4.0, "AlphaGo (2016)", fontsize=14, ha='center', fontweight='bold', color=C_RED)
    ax.text(8.0, 4.0, "AlphaGo Zero (2017)", fontsize=14, ha='center', fontweight='bold', color=C_GREEN)

    rows = [
        ("训练数据", "人类专家棋谱\n+ 自我对弈", "无人类数据\n纯自我对弈"),
        ("特征工程", "人工设计\n48个特征平面", "原始棋盘历史\n17个二值平面"),
        ("网络结构", "策略网络 + 价值网络\n(两个独立网络)", "单一双头网络\n$f_\\theta(s)=(\\mathbf{p},v)$"),
        ("Rollout", "快速 rollout 策略\n模拟至终局", "无 rollout\n直接用 v(s)"),
        ("MCTS模拟数", "数万次", "1600次"),
    ]
    for i, (label, left, right) in enumerate(rows):
        y = 3.4 - i * 0.75
        ax.text(0.5, y, label, fontsize=11, ha='left', va='center', color=C_DARK_TEXT, fontweight='bold')
        ax.text(3.3, y, left, fontsize=10, ha='center', va='center', color=C_DARK_TEXT)
        ax.text(8.0, y, right, fontsize=10, ha='center', va='center', color=C_DARK_TEXT)
        if i < len(rows)-1:
            ax.plot([0.3, 10.7], [y-0.38, y-0.38], '-', color=C_LIGHT_GRAY, lw=0.8)

    # Vertical divider
    ax.plot([5.5, 5.5], [0.3, 3.8], '--', color=C_GRAY, lw=1)
    plt.tight_layout()
    save(fig, "ag_vs_agzero.png")

# ── 13. n-step return weighting ───────────────────────────────────────────
def create_nstep_weighting():
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=C_WHITE)
    lambdas = [0, 0.3, 0.6, 0.9, 1.0]
    colors = [C_BLUE, C_TEAL, C_GOLD, C_ORANGE, C_RED]
    n = np.arange(1, 11)
    for lam, color in zip(lambdas, colors):
        if lam == 1:
            weights = np.zeros(10)
            weights[-1] = 1
        else:
            weights = (1 - lam) * lam**(n-1)
        ax.plot(n, weights, 'o-', color=color, lw=2, markersize=5,
                label=f'$\\lambda={lam}$')
    ax.set_xlabel("n (n-step)", fontsize=13, color=C_DARK_TEXT)
    ax.set_ylabel(r"权重 $(1-\lambda)\lambda^{n-1}$", fontsize=13, color=C_DARK_TEXT)
    ax.set_title(r"TD($\lambda$) 中各 n-step 回报的权重", fontsize=14,
                 fontweight='bold', color=C_NAVY, pad=12)
    ax.legend(fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    save(fig, "nstep_weighting.png")

# ── 14. Loss curves ───────────────────────────────────────────────────────
def create_loss_curves():
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=C_WHITE)
    steps = np.array([0, 5000, 10000, 30000, 70000, 150000, 300000, 490000])
    p_loss = np.array([2.5, 1.8, 1.2, 0.8, 0.5, 0.35, 0.28, 0.25])
    v_loss = np.array([1.5, 1.2, 0.9, 0.7, 0.55, 0.45, 0.42, 0.40])
    ax.plot(steps/1000, p_loss, 'o-', color=C_GOLD, lw=2.5, markersize=5,
            label='策略损失 $-\\pi^\\top \\log \\mathbf{p}$')
    ax.plot(steps/1000, v_loss, 's-', color=C_RED, lw=2.5, markersize=5,
            label='价值损失 $(z-v)^2$')
    ax.set_xlabel("训练步数 (×10³)", fontsize=13, color=C_DARK_TEXT)
    ax.set_ylabel("损失", fontsize=13, color=C_DARK_TEXT)
    ax.set_title("AlphaGo Zero 训练损失曲线 (示意, 论文 Fig.2)", fontsize=14,
                 fontweight='bold', color=C_NAVY, pad=12)
    ax.legend(fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    save(fig, "loss_curves.png")

# ── 15. PUCT exploration vs exploitation ──────────────────────────────────
def create_puct_curve():
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=C_WHITE)
    N_total = 100
    n = np.linspace(1, 50, 100)
    for c, color, label in [(1.0, C_BLUE, '$c_{puct}=1.0$'),
                            (2.5, C_GOLD, '$c_{puct}=2.5$'),
                            (5.0, C_RED, '$c_{puct}=5.0$')]:
        U = c * np.sqrt(N_total) / (1 + n)
        ax.plot(n, U, '-', color=color, lw=2.5, label=label)
    ax.set_xlabel(r"子节点访问次数 $N(s,a)$", fontsize=13, color=C_DARK_TEXT)
    ax.set_ylabel(r"探索项 $U(s,a)$", fontsize=13, color=C_DARK_TEXT)
    ax.set_title(r"PUCT 探索项: 访问越少, 奖励越高", fontsize=14,
                 fontweight='bold', color=C_NAVY, pad=12)
    ax.legend(fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(C_GRAY)
    ax.spines['left'].set_color(C_GRAY)
    ax.tick_params(colors=C_GRAY)
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    save(fig, "puct_curve.png")

# ── 16. Residual block ────────────────────────────────────────────────────
def create_residual_block():
    fig, ax = plt.subplots(figsize=(6, 5), facecolor=C_WHITE)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 7)
    ax.axis('off')

    blocks = [
        (2, 6, 2, 0.6, "Input", C_NAVY),
        (2, 5, 2, 0.6, "Conv 3×3, 256", C_BLUE),
        (2, 4, 2, 0.6, "BatchNorm", C_TEAL),
        (2, 3, 2, 0.6, "ReLU", C_GOLD),
        (2, 2, 2, 0.6, "Conv 3×3, 256", C_BLUE),
        (2, 1, 2, 0.6, "BatchNorm", C_TEAL),
        (2, 0, 2, 0.6, "Add + ReLU (残差连接)", C_RED),
    ]
    for x, y, w, h, text, color in blocks:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                              fc=color, ec=color, alpha=0.85, zorder=2)
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, text, fontsize=10, ha='center', va='center',
                color=C_WHITE, fontweight='bold', zorder=3)
        if y < 6:
            ax.annotate('', xy=(3, y+0.62), xytext=(3, y+0.7),
                        arrowprops=dict(arrowstyle='->', color=C_GRAY, lw=1.5))

    # Skip connection
    ax.annotate('', xy=(3.05, 0.3), xytext=(3.05, 6.3),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2,
                               connectionstyle='arc3,rad=0'))
    ax.plot([4.1, 4.6, 4.6, 4.1], [6.3, 6.3, 0.3, 0.3], '-', color=C_RED, lw=2)
    ax.annotate('', xy=(4.05, 0.3), xytext=(4.6, 0.3),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2))
    ax.text(4.9, 3.3, "残差\n连接", fontsize=10, ha='left', color=C_RED, fontweight='bold')

    ax.text(3, 6.9, "单个残差块 (Residual Block)", fontsize=12, ha='center',
            fontweight='bold', color=C_NAVY)
    save(fig, "residual_block.png")

def generate_all():
    print("Generating diagram assets...")
    create_input_planes()
    create_mcts_phases()
    create_nn_arch()
    create_self_play_loop()
    create_td_vs_mc()
    create_policy_iteration()
    create_elo_progress()
    create_complexity()
    create_mdp()
    create_mcts_backup()
    create_search_tree()
    create_ag_vs_agzero()
    create_nstep_weighting()
    create_loss_curves()
    create_puct_curve()
    create_residual_block()
    print("All assets generated!")

if __name__ == "__main__":
    generate_all()
